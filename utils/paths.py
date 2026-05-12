import os


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def assets_dir() -> str:
    return os.path.join(project_root(), "assets")


def exports_dir() -> str:
    return os.path.join(project_root(), "exports")


def data_dir() -> str:
    return os.path.join(project_root(), "app", "_data")


def ensure_app_dirs() -> None:
    for p in (assets_dir(), exports_dir(), data_dir()):
        os.makedirs(p, exist_ok=True)
