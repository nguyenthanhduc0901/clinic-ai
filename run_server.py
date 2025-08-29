try:
    # When executed as a module: python -m ai_server.run_server
    from . import create_app
    from .config import Config
except ImportError:
    # Fallback for running as a script: python ai_server/run_server.py
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from ai_server import create_app  # type: ignore
    from ai_server.config import Config  # type: ignore


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)


