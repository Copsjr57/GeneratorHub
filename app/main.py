import os
import sys


def main() -> None:
    """Entry point used by root-level main.py."""
    # Ensure project root is on sys.path when launched directly
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)

    from app.app_window import GeneratorHubApp

    app = GeneratorHubApp()
    app.mainloop()
