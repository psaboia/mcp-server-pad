# MCP Server for Paper Analytical Devices (PAD)

An MCP server implementation that provides a standardized interface to interact with the Paper Analytical Devices (PAD) system at Notre Dame (pad.crc.nd.edu). This server enables LLM-based tools and agents to access and process PAD data through the Model Context Protocol.

## Features

- Card Management:
  - Retrieve and list PAD test cards with comprehensive metadata
  - Access individual card details including camera type, quantities, and IDs
  - Process and store card images with high-quality resizing
- Neural Network Integration:
  - List available neural networks
  - Access network configurations
  - Interface with analysis systems
- Project Organization:
  - Manage PAD projects
  - Handle card groups
  - Track issues and samples
- Image Processing:
  - High-quality image resizing using Lanczos resampling
  - Automatic image optimization (300px max width)
  - Card geometry handling with coordinate scaling
  - Detailed image metadata (dimensions, paths)

## Setup

### For Claude Desktop Users

1. Ensure you have Python 3.12 or higher installed
2. Clone this repository
3. Configure Claude Desktop with the settings below (no manual package installation needed)

## Configuration

### Claude Desktop Configuration

To use this server with Claude Desktop, add the following configuration to your Claude settings:

```json
{
    "pad": {
        "command": "<path-to-uv>",
        "args": [
            "--directory",
            "<path-to-repository>",
            "run",
            "main.py"
        ],
        "env": {
            "FILESYSTEM_STORAGE": "<path-to-storage-directory>"
        }
    }
}
```

Configuration parameters:
- `<path-to-uv>`: Path to your uv installation (e.g., `~/.local/bin/uv`)
- `<path-to-repository>`: Absolute path to where you cloned this repository
- `<path-to-storage-directory>`: Directory where you want to store PAD files (optional)

This configuration:
- Uses `uv` to automatically manage Python dependencies - no manual installation needed
- Sets the correct working directory
- Runs the server through `main.py`
- Configures the storage location (defaults to `~/Documents/pad_storage` if not specified)

After configuring Claude Desktop with these settings, all PAD server tools (cards, neural networks, image processing) will be available through the MCP interface.

### Storage Settings

The server uses filesystem storage for data persistence. Configure the storage location using:

- Environment variable: `FILESYSTEM_STORAGE`
- Default location: `~/Documents/pad_storage`

## Usage

Start the server manually:

```bash
uv run python pad.py
```

The server exposes the following MCP tools:

- `get_v2_cards()`: List all available cards with comprehensive metadata (camera type, quantities, IDs)
- `get_v2_card_by_id(card_id)`: Get detailed card information including all metadata fields
- `get_v2_neural_networks()`: List available neural networks
- `get_v2_neural_network_by_id(nn_id)`: Get specific neural network details
- `get_v2_projects()`: List all projects
- `get_card_image_by_id(card_id)`: Retrieve, process, and optimize card images with metadata
- `load_image(path)`: Load and process images from disk
- `load_card_geometry(path)`: Load and scale v2 card geometry
- `multiply_coordinates(data, factor)`: Scale geometry coordinates for processing

## API Integration

The server communicates with the PAD API at `https://pad.crc.nd.edu` and provides a standardized interface through MCP. This allows seamless integration with LLM-based tools while maintaining security and structure.

## Dependencies

Managed automatically by `uv` through Claude Desktop:

- httpx (>=0.28.1): For API communication
- mcp[cli] (>=1.3.0): MCP server functionality
- Pillow (>=11.1.0): High-quality image processing

## Examples

### Using with Claude Desktop

When using the PAD server with Claude Desktop, you can have natural conversations about your PAD cards. Here are some example interactions:

```
User: Can you list all PAD cards that use Camera Type 1?

Claude: I'll help you find all cards that use Camera Type 1.
Let me search through the available cards...

I found the following cards:
- Card 42 - Sample A123
- Card 56 - Sample B456
- Card 78 - Sample C789

User: Can you show me the image for card 51866?

Claude: I'll retrieve and process the image for card 51866.
I've processed the image, which is now saved at ~/Documents/pad_storage/card_51866.jpg
The image dimensions are 300x500 pixels.
```

Behind the scenes, Claude uses these MCP tools:
- `get_v2_cards()` to list and filter cards
- `get_card_image_by_id()` to process and display images
- Automatic image scaling for Claude Desktop's display

### Working with Cards

```python
# List all cards with metadata
result = await get_v2_cards()
if result["success"]:
    cards = result["data"]
    for card in cards:
        print(f"Card {card['id']}:")
        print(f"  Sample: {card['sample']}")
        print(f"  Camera: {card['camera']}")
        print(f"  Project ID: {card['project_id']}")

# Get a specific card with full details
card_result = await get_v2_card_by_id(42)
if card_result["success"]:
    card = card_result["data"]
    print(f"Retrieved card {card['id']} from project {card['project_id']}")
```

### Image Processing

```python
# Retrieve and process a card image
image_result = await get_card_image_by_id(42)
if image_result["success"]:
    image_data = image_result["data"]
    print(f"Processed image saved to: {image_data['image_path']}")
    print(f"Dimensions: {image_data['width']}x{image_data['height']}")
```

### Working with Geometry

When using with Claude Desktop, the geometry is automatically scaled to match Claude's image width restrictions (300px). This ensures consistent analysis regardless of the display environment.

```python
# Load card geometry (automatically scaled for Claude Desktop)
result = load_card_geometry()
if result["success"]:
    geometry = result["data"]
    # Access lane positions (example with lane A)
    lane_a = geometry["lane_boxes"][0]["A"]
    print(f"Lane A coordinates: {lane_a}")
    
    # Scale coordinates if needed for different display sizes
    scaled = multiply_coordinates(geometry, 1.5)
    scaled_lane_a = scaled["lane_boxes"][0]["A"]
    print(f"Scaled lane A: {scaled_lane_a}")
```

The geometry includes:
- Card dimensions (scaled from 730x1220)
- 12 lanes (A through L) with precise coordinates
- Fiducial markers for alignment
- QR code position
- Swipe line location

### Error Handling

```python
# Example of error handling with descriptive messages
result = await get_v2_card_by_id(99999)  # Non-existent card
if not result["success"]:
    print(f"Error: {result['error']}")
    print(f"Description: {result['description']}")
    # Output might be:
    # Error: Card not found
    # Description: An error occurred: Card with ID 99999 does not exist
```

### Storage Configuration

```bash
# Configure custom storage location
export FILESYSTEM_STORAGE="/custom/path/to/storage"
uv run python pad.py

# Or use default location (~/Documents/pad_storage)
uv run python pad.py
```

## Development

This server is built using FastMCP and follows the Model Context Protocol for tool definitions and interactions. For more information about MCP, visit [modelcontextprotocol.io](https://modelcontextprotocol.io).

## Security

All interactions with the PAD API are handled securely through the server. Data storage is managed locally in the configured filesystem location.

