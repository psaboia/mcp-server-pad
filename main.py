import io
import json
import os
import sys
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP, Image
from PIL import Image as PILImage

# Set up the MCP server
mcp = FastMCP("paper_analytical_devices")

BASE_URL = "https://pad.crc.nd.edu"

# Configure filesystem storage location
FILESYSTEM_STORAGE = os.getenv('FILESYSTEM_STORAGE', os.path.expanduser('~/Documents/pad_storage'))

IMAGE_WIDTH = 300

async def call_api_get(endpoint: str, params: dict[str, Any] | None = None) -> Any:
    """
    A helper for GET requests to the PAD API. Returns:
      - dict with {"error": <some_message>} on error
      - raw JSON (dict or list) from the server on success
    """
    url = f"{BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e), "endpoint": endpoint, "params": params}

def make_error_result(error_message: str) -> dict[str, Any]:
    """
    Return a standardized error result with the known schema:
      {
        "success": False,
        "data": [],
        "error": error_message,
        "description": str
      }
    """
    return {
        "success": False,
        "data": [],
        "error": error_message,
        "description": f"An error occurred: {error_message}"
    }

#
# Example transformations: 
#  - Return "data" as a list of simplified dicts
#  - Or if the API returns a single dict, wrap it in "data" or store directly in "data"
#

@mcp.tool()
async def get_v2_cards() -> dict[str, Any]:
    """
    Retrieve a list of cards (v2 endpoint) using default skip=0, limit=100,
    then transform to a consistent structure.

    Returns:
        {
            "success": True/False,
            "data": [
                {
                  "id": int,
                  "sample": str,
                  ...
                }, ...
            ],
            "error": str or "",
            "description": str
        }
    """
    params = {"skip": 0, "limit": 100}
    raw_data = await call_api_get("/api/v2/cards", params=params)

    # Check for error
    if isinstance(raw_data, dict) and "error" in raw_data:
        return make_error_result(raw_data["error"])

    # raw_data is likely a list of card objects
    # e.g. [ { "id": 42, "sample_name": "...", "test_name": "...", ... }, ... ]
    transformed_list = []
    if isinstance(raw_data, list):
        for card in raw_data:
            transformed_list.append({
                "id": card.get("id"),
                "sample": card.get("sample_name"),
                "test": card.get("test_name"),
                "notes": card.get("notes"),
                # ... keep or omit other fields
            })

    return {
        "success": True,
        "data": transformed_list,
        "error": "",
        "description": "Retrieved a list of PAD cards. Each card represents a physical analytical test strip with multiple lanes treated with chemical reagents. Samples are applied to these lanes to produce a Color Barcode, analyzed by neural networks to identify drugs."
    }


@mcp.tool()
async def get_v2_card_by_id(card_id: int) -> dict[str, Any]:
    """
    Retrieve a single card by its integer ID (v2 endpoint), then standardize the result.

    Returns:
        {
            "success": True/False,
            "data": {
              "id": int,
              "sample": str,
              ...
            } or {},
            "error": "",
            "description": str
        }
    """
    endpoint = f"/api/v2/cards/{card_id}"
    raw_data = await call_api_get(endpoint)

    if isinstance(raw_data, dict) and "error" in raw_data:
        return make_error_result(raw_data["error"])

    # raw_data is presumably a dict describing the card
    # e.g. { "id": 42, "sample_name": "...", "test_name": "...", ... }
    processed_file_location = raw_data.get("processed_file_location", "")

    # 4) Extract the filename from processed_file_location, e.g. "51871_processed.png"
    filename = os.path.basename(processed_file_location)
    if not filename:
        filename = "downloaded_image.png"

    # Join prefix path + filename
    full_filepath = os.path.join(FILESYSTEM_STORAGE, filename)

    transformed = {
        "id": raw_data.get("id"),
        "sample": raw_data.get("sample_name"),
        "test": raw_data.get("test_name"),
        "notes": raw_data.get("notes"),
        "camera": raw_data.get("camera_type_1"),
        "quantity": raw_data.get("quantity"),
        "sample_id": raw_data.get("sample_id"),
        "project_id": raw_data.get("project_id"),
        "issue_id": raw_data.get("issue_id"),
        "image_path": full_filepath
        #"processed_file_location": processed_file_location
        # ... keep or omit other fields
    }

    # lets grab the image and download
    image_url = f"{BASE_URL}{processed_file_location}"
    
    # 3) Download the image
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url, timeout=30)
            resp.raise_for_status()
            image_bytes = resp.content
    except Exception as e:
        return make_error_result(str(e))
    
    # 4) Create a PIL Image object from those bytes (in-memory)
    img = PILImage.open(io.BytesIO(image_bytes))

    # For example, let's enforce a max width of 100 px
    w, h = img.size
    if w > IMAGE_WIDTH:
        new_height = int(h * IMAGE_WIDTH / w)
        img = img.resize((IMAGE_WIDTH, new_height), PILImage.Resampling.LANCZOS)
    
    # 5) Save raw bytes
    img.save(full_filepath)

    # Return a standardized structure
    return {
        "success": True,
        "data": transformed,
        "error": "",
        "description":  """
                        This PAD card (Q133248639) represents a chromatography-based analytical device printed on a 3″ x 4″ card.
                        It features 12 lanes delineated by wax barriers, a swipe line for sample application, and a unique Color Barcode produced
                        by the reaction of the drug sample with pre-treated reagents, mixed by immersing the bottom 0.5" of the card in water. 
                        Metadata includes sample name (the drug), test type (the reagents/lanes matrix used), camera, quantity (concentration), 
                        sample_id (card number in QR code), project_id, issue_id and image file location 
                        on the local filesystem. You can use MCP tool "load_image(path: str)" to load the image from disk.
                        The card's geometry is available using tool "load_card_geometry()" and is defined by a dictionary with units, card size, 
                        active area, lane number, lane boxes, outer fiducials, QR fiducials, wax fiducials, edges of QR code, and swipe line.
                        """
    }

@mcp.tool()
async def get_v2_neural_networks() -> dict[str, Any]:
    """
    Retrieve neural networks (v2 endpoint), default skip=0, limit=100.
    Return a standardized structure.

    Returns:
        {
          "success": bool,
          "data": [
             {
               "network_id": int,
               "name": str,
               "drugs": [...],
               ...
             },
             ...
          ],
          "error": str,
          "description": str
        }
    """
    params = {"skip": 0, "limit": 100}
    raw_data = await call_api_get("/api/v2/neural-networks", params=params)

    if isinstance(raw_data, dict) and "error" in raw_data:
        return make_error_result(raw_data["error"])

    networks = []
    if isinstance(raw_data, list):
        for net in raw_data:
            networks.append({
                "network_id": net.get("id"),
                "name": net.get("name"),
                "drugs": net.get("drugs", []),
                "description": net.get("description", ""),
                # omit or rename fields you don't need
            })

    return {
        "success": True,
        "data": networks,
        "error": "",
        "description": "Retrieved a list of neural networks utilized to interpret Color Barcodes produced by PAD test cards, enabling identification of drugs based on reagent-sample reactions."
    }


@mcp.tool()
async def get_v2_neural_network_by_id(nn_id: int) -> dict[str, Any]:
    """
    Retrieve a single neural network, standardized.
    
    Args:
        nn_id: The neural network ID.
    
    Returns:
      {
          "success": True/False,
          "data": {
              "network_id": int,
              "name": str,
              "drugs": [...],
              "description": str
          },
          "error": "",
          "description": str   # A summary describing the neural network details.
      }
    """
    endpoint = f"/api/v2/neural-networks/{nn_id}"
    raw_data = await call_api_get(endpoint)

    if isinstance(raw_data, dict) and "error" in raw_data:
        return make_error_result(raw_data["error"])

    # raw_data is presumably a dict with fields like id, name, drugs, etc.
    transformed = {
        "network_id": raw_data.get("id"),
        "name": raw_data.get("name"),
        "drugs": raw_data.get("drugs", []),
        "description": raw_data.get("description", ""),
    }

    return {
        "success": True,
        "data": transformed,
        "error": "",
        "description": f"Retrieved detailed information for neural network ID {nn_id}, including its name, description, and associated drug list."
    }


#
# Repeat the same pattern for the other v2 endpoints: card groups, projects, etc.
# We'll show one more example below for brevity.
#

@mcp.tool()
async def get_v2_projects() -> dict[str, Any]:
    """
    Retrieve a list of projects (v2 endpoint) with default skip=0, limit=100,
    then transform to a consistent structure.
    
    Returns:
      {
          "success": True/False,
          "data": [
              {
                "project_id": int,
                "project_name": str,
                "test_name": str,
                "user_name": str,
                "notes": str,
                ...
              },
              ...
          ],
          "error": "",
          "description": str   # A summary describing the project list.
      }
    """
    params = {"skip": 0, "limit": 100}
    raw_data = await call_api_get("/api/v2/projects", params=params)

    if isinstance(raw_data, dict) and "error" in raw_data:
        return make_error_result(raw_data["error"])

    projects_list = []
    if isinstance(raw_data, list):
        for p in raw_data:
            projects_list.append({
                "project_id": p.get("id"),
                "project_name": p.get("project_name"),
                "test_name": p.get("test_name"),
                "user_name": p.get("user_name"),
                "notes": p.get("notes", ""),
                # rename or remove other fields as needed
            })

    return {
        "success": True,
        "data": projects_list,
        "error": "",
        "description": "Retrieved a list of projects in the PAD system. Each project groups together multiple cards and includes details like project name, test name, and user information."
    }

# Load an image from disk
@mcp.tool()
def load_image(path: str) -> Image:
    """Load an image from disk"""
    # FastMCP handles reading and format detection
    return Image(path=path)


# Geometry definitions for the card, version 2
# This is a dictionary defining the geometry of the card
# It includes units, card size, active area, lane number, lane boxes,
# outer fiducials, QR fiducials, wax fiducials, edges of QR code, and swipe line
# The geometry is used to define the layout of the card and the location of the fiducials
geometry = {
    "units": "pixels",
    "id": "padproject.nd.edu/?t=",
    "date": "11/13/19",
    "version": "2.0",
    "card_size": {"x":730, "y":1220},
    "active_area": [
        {"x": 71, "y": 359},
        {"x": 707, "y": 849}
    ],
    "lane_number": 12,
    "lane_boxes": [
        {
            "A": [
                {"x": 17,  "y": 359},
                {"x": 17,  "y": 1095},
                {"x": 70,  "y": 1095},
                {"x": 70,  "y": 359}
            ]
        },
        {
            "B": [
                {"x": 70,  "y": 359},
                {"x": 70,  "y": 1095},
                {"x": 123, "y": 1095},
                {"x": 123, "y": 359}
            ]
        },
        {
            "C": [
                {"x": 123, "y": 359},
                {"x": 123, "y": 1095},
                {"x": 176, "y": 1095},
                {"x": 176, "y": 359}
            ]
        },
        {
            "D": [
                {"x": 176, "y": 359},
                {"x": 176, "y": 1095},
                {"x": 229, "y": 1095},
                {"x": 229, "y": 359}
            ]
        },
        {
            "E": [
                {"x": 229, "y": 359},
                {"x": 229, "y": 1095},
                {"x": 282, "y": 1095},
                {"x": 282, "y": 359}
            ]
        },
        {
            "F": [
                {"x": 282, "y": 359},
                {"x": 282, "y": 1095},
                {"x": 335, "y": 1095},
                {"x": 335, "y": 359}
            ]
        },
        {
            "G": [
                {"x": 335, "y": 359},
                {"x": 335, "y": 1095},
                {"x": 388, "y": 1095},
                {"x": 388, "y": 359}
            ]
        },
        {
            "H": [
                {"x": 388, "y": 359},
                {"x": 388, "y": 1095},
                {"x": 441, "y": 1095},
                {"x": 441, "y": 359}
            ]
        },
        {
            "I": [
                {"x": 441, "y": 359},
                {"x": 441, "y": 1095},
                {"x": 494, "y": 1095},
                {"x": 494, "y": 359}
            ]
        },
        {
            "J": [
                {"x": 494, "y": 359},
                {"x": 494, "y": 1095},
                {"x": 547, "y": 1095},
                {"x": 547, "y": 359}
            ]
        },
        {
            "K": [
                {"x": 547, "y": 359},
                {"x": 547, "y": 1095},
                {"x": 600, "y": 1095},
                {"x": 600, "y": 359}
            ]
        },
        {
            "L": [
                {"x": 600, "y": 359},
                {"x": 600, "y": 1095},
                {"x": 653, "y": 1095},
                {"x": 653, "y": 359}
            ]
        }
    ],
    "outer_fiducials": [
        {"x": 85,  "y": 1163},
        {"x": 686, "y": 1163},
        {"x": 686, "y": 77}
    ],
    "qr_fiducials": [
        {"x": 82,  "y": 64},
        {"x": 82,  "y": 237},
        {"x": 255, "y": 64}
    ],
    "wax_fiducials": [
        {"x": 387, "y": 214},
        {"x": 387, "y": 1164}
    ],
    "edges_of_qr_code": [
        {"x": 54,  "y": 37},
        {"x": 54,  "y": 269},
        {"x": 286, "y": 269},
        {"x": 286, "y": 37}
    ],
    "swipe_line": {"y": 620}
}

# Function to multiply x and y coordinates by a given factor
# we need this since the image sent to Claude is 300px wide, 
# but the geometry is for a full sized card
def multiply_coordinates(data: Any, factor: float) -> Any:
    """
    Recursively traverse a nested dictionary or list and multiply
    all numeric values associated with keys "x" or "y" by the given factor.
    
    Args:
        data: The input data (dict, list, or other) to process.
        factor: The multiplier to apply to each x and y value.
    
    Returns:
        The modified data with updated x and y values.
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # If the key is "x" or "y" and the value is a number, multiply it.
            if key in ("x", "y") and isinstance(value, (int, float)):
                new_dict[key] = int(value * factor + 0.5)  # Round to nearest integer
            else:
                new_dict[key] = multiply_coordinates(value, factor)
        return new_dict
    elif isinstance(data, list):
        return [multiply_coordinates(item, factor) for item in data]
    else:
        return data
    
@mcp.tool()
def load_card_geometry() ->  dict[str, Any]:
    """
    Load the geometry for a v2 PAD card.
    
    The geometry includes the card dimensions, active area, lane boxes,
    outer fiducials, QR fiducials, wax fiducials, edges of the QR code, and the swipe line.
    
    Args:
      path (str): The file path from which to load the geometry configuration.
    
    Returns:
      {
          "success": True,
          "data": <geometry dict>,
          "error": "",
          "description": "A detailed layout configuration for a PAD card, including coordinate positions for lanes and fiducials."
      }
    """
    # do we need to scale the coordinates?
    geom_width = float(geometry["card_size"]["x"])
    if geom_width != IMAGE_WIDTH:
        scale_factor = IMAGE_WIDTH / geom_width
        scaled_geometry = multiply_coordinates(geometry, scale_factor)
    else:
        scaled_geometry = geometry
    # Return standardized structure
    return {
        "success": True,
        "data": scaled_geometry,
        "error": "",
        "description": f"Loaded the PAD card geometry configuration, which defines the layout of the card including dimensions, active area, lane boxes, and fiducial markers. Note that this is scaled to the image you get since MCP->Claude restricts width to {IMAGE_WIDTH}px."
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")