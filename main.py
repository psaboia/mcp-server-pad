from pad import mcp

def main():
    """Initialize and run the PAD MCP server"""
    print("Starting PAD MCP server...")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
