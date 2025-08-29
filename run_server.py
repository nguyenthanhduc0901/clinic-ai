try:
    # When executed as a package module (python -m <pkg>.run_server)
    from . import create_app  # type: ignore
    from .config import Config  # type: ignore
except Exception:
    # Fallback for direct module import (e.g., gunicorn run_server:app)
    from __init__ import create_app  # type: ignore
    from config import Config  # type: ignore


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)


