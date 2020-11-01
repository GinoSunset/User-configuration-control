import argparse
import aiohttp
from app import create_app
from app.settings import load_config


parser = argparse.ArgumentParser(description=" project")
parser.add_argument("--host", help="Host to listen", default="0.0.0.0")
parser.add_argument("--port", help="Port to accept connections", default=8000)
parser.add_argument("--reload", action="store_true", help="Autoreload code on change")
parser.add_argument(
    "-c", "--config", type=argparse.FileType("r"), help="Path to configuration file"
)

args = parser.parse_args()

app = create_app(config=load_config(args.config))

if __name__ == "__main__":
    aiohttp.web.run_app(app, host=args.host, port=args.port)
