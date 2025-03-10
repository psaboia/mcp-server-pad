import io
import os
from typing import Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP, Image
from PIL import Image  as PILImage
import sys

# Set up the MCP server
mcp = FastMCP("paper_analytical_devices")

BASE_URL = "https://pad.crc.nd.edu"

# find filesystem location
if sys.argv[1]:
    FILESYSTEM_STORAGE = sys.argv[1]
else:
    FILESYSTEM_STORAGE = "/Users/csweet1/Documents/projects/earth616/weather/"

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
        "error": error_message
      }
    """
    return {
        "success": False,
        "data": [],
        "error": error_message,
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
            "error": str or ""
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
        "error": ""
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
            "error": ""
        }
    """
    endpoint = f"/api/v2/cards/{card_id}"
    raw_data = await call_api_get(endpoint)

    if isinstance(raw_data, dict) and "error" in raw_data:
        return make_error_result(raw_data["error"])

    # raw_data is presumably a dict describing the card
    # e.g. { "id": 42, "sample_name": "...", "test_name": "...", ... }
    transformed = {
        "id": raw_data.get("id"),
        "sample": raw_data.get("sample_name"),
        "test": raw_data.get("test_name"),
        "notes": raw_data.get("notes")
        #"processed_file_location": raw_data.get("processed_file_location"),
        # ... keep or omit other fields
    }

    return {
        "success": True,
        "data": transformed,
        "error": ""
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
          "error": str
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
        "error": ""
    }


@mcp.tool()
async def get_v2_neural_network_by_id(nn_id: int) -> dict[str, Any]:
    """
    Retrieve a single neural network, standardized.

    Args:
        nn_id: The neural network ID
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
        "error": ""
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
        "error": ""
    }

@mcp.tool()
async def get_card_image_by_id(card_id: int) -> dict[str, Any]:
    """
    Retrieve the processed card image for a given card ID.
    
    Steps:
      1) Calls get_v2_card_by_id(card_id)
      2) Extracts 'processed_file_location' from the returned 'data'
      3) Prepends 'https://pad.crc.nd.edu' to form the full image URL
      4) Downloads the image
      5) Returns it as a base64-encoded string
    
    Returns:
      {
        "success": bool,
        "data": {
           "image_path": str
        },
        "error": str
      }
    """
    # 1) Grab the card info from the API
    endpoint = f"/api/v2/cards/{card_id}"
    raw_data = await call_api_get(endpoint)

    if isinstance(raw_data, dict) and "error" in raw_data:
        return make_error_result(raw_data["error"])

    # 2) Build the full image URL
    processed_file_location = raw_data.get("processed_file_location", "")
    
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
    max_width = 300
    w, h = img.size
    if w > max_width:
        new_height = int(h * max_width / w)
        img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)
    
    # 4) Extract the filename from the path, e.g. "51871_processed.png"

    # Extract filename from processed_file_location (e.g. "51871_processed.png")
    filename = os.path.basename(processed_file_location)
    if not filename:
        filename = "downloaded_image.png"

    # Join prefix path + filename
    full_filepath = os.path.join(FILESYSTEM_STORAGE, filename)

    # 5) Save raw bytes
    img.save(full_filepath)

    # Return standardized structure
    return {
        "success": True,
        "data": {
            "image_path": full_filepath  # Return the image location
        },
        "error": ""
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
    "card_size": [730, 1220],
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

@mcp.tool()
def load_card_geometry(path: str) ->  dict[str, Any]:
    """Load the geometry for a v2 pad card"""
    # Return standardized structure
    return {
        "success": True,
        "data": geometry,
        "error": ""
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
