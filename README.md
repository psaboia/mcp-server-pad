# MCP Server for Paper Analytical Devices (PAD)

An MCP server implementation that provides a standardized interface to interact with the Paper Analytical Devices (PAD) system at Notre Dame (pad.crc.nd.edu). This server enables LLM-based tools and agents to access and process PAD data through the Model Context Protocol.

## Features

- Card Management:
  - Retrieve and list PAD test cards
  - Access individual card details
  - Process card images
- Neural Network Integration:
  - List available neural networks
  - Access network configurations
  - Interface with analysis systems
- Project Organization:
  - Manage PAD projects
  - Handle card groups
- Image Processing:
  - Card geometry handling
  - Image analysis tools

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
 python main.py
```

The server exposes the following MCP tools:

- `get_v2_cards()`: List all available cards
- `get_v2_card_by_id(card_id)`: Get details for a specific card
- `get_v2_neural_networks()`: List available neural networks
- `get_v2_neural_network_by_id(nn_id)`: Get specific neural network details
- `get_v2_projects()`: List all projects
- `get_card_image_by_id(card_id)`: Retrieve and process card images
- `load_image(path)`: Load image from disk
- `load_card_geometry(path)`: Load v2 card geometry

## API Integration

The server communicates with the PAD API at `https://pad.crc.nd.edu` and provides a standardized interface through MCP. This allows seamless integration with LLM-based tools while maintaining security and structure.

## Dependencies

- httpx: For API communication
- mcp[cli]: MCP server functionality
- Pillow: Image processing

## Development

This server is built using FastMCP and follows the Model Context Protocol for tool definitions and interactions. For more information about MCP, visit [modelcontextprotocol.io](https://modelcontextprotocol.io).

## Security

All interactions with the PAD API are handled securely through the server. Data storage is managed locally in the configured filesystem location.

