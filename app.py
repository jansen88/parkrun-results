"""Application entry point."""
from dash_app import create_app

server = create_app(
    dash_debug=False, 
    dash_auto_reload=False
)

if __name__ == "__main__":
    server.run()
