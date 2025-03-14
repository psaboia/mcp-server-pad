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
  "mcpServers": {
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
}

```

Configuration parameters:
- `<path-to-uv>`: Path to your uv installation (e.g., `~/.local/bin/uv`)
- `<path-to-repository>`: Absolute path to where you cloned this repository
- `<path-to-storage-directory>`: Directory where you want to store PAD files (defaults to `~/Documents/pad_storage` if not specified)

This configuration:
- Uses `uv` to automatically manage Python dependencies - no manual installation needed
- Sets the correct working directory
- Runs the server through `main.py`
- Configures the storage location (defaults to `~/Documents/pad_storage` if not specified)

After configuring Claude Desktop with these settings, all PAD server tools (cards, neural networks, image processing) will be available through the MCP interface.


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

#### **Prompt: Can you show the image for the card 51866?**

![image](https://github.com/user-attachments/assets/e7092ac4-95da-4de2-ab3a-350f91159997)

#### **Prompt: List PAD projects created after Jully 2024.**
![image](https://github.com/user-attachments/assets/0a582721-c879-42b4-b8cf-31aeec1ebe1a)

#### **Prompt: Can you list the neural networks added via PAD API after July 2024**
![image](https://github.com/user-attachments/assets/10f35f0d-b9e9-49b7-85e5-5ed13730f710)



## Development

This server is built using FastMCP and follows the Model Context Protocol for tool definitions and interactions. For more information about MCP, visit [modelcontextprotocol.io](https://modelcontextprotocol.io).

## Security

All interactions with the PAD API are handled securely through the server. Data storage is managed locally in the configured filesystem location.

# JSON-LD API for GPTs
Code is in the `openapi-ld` directory. This is a JSON-LD API for GPTs that provides a standardized interface for interacting with the PAD system. It allows developers to create and manage PAD projects, cards, and neural networks through a RESTful API.

## Running code
To run the code, 

```bash
uv run json_ld_api.py --proxy-headers --forwarded-allow-ips="*" --root-path /api-ld/v3
```

## API Endpoints
The API provides the following endpoints:

### Get Cards By Sample

```http
/api-ld/v3/cards/by-sample/{sample_id}
```

### Get Card image by ID

```http
/api-ld/v3/cards/{id}/download-image
```
