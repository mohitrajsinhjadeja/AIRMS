from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_DIRS = [
    "app/api/v1",
    "app/core",
    "app/schemas",
    "app/services",
    "app/middleware",
    "tests/unit",
    "tests/integration"
]

REQUIRED_FILES = [
    "app/__init__.py",
    "app/api/__init__.py",
    "app/api/v1/__init__.py",
    "app/core/__init__.py",
    "app/schemas/__init__.py",
    "app/services/__init__.py",
    "app/middleware/__init__.py",
]

SCHEMA_FILES = [
    "analytics.py",
    "auth.py",
    "base.py",
    "pii.py",
    "risk.py",
    "fact_checking.py"
]

def ensure_directory(path: Path):
    """Create directory if it doesn't exist"""
    if not path.exists():
        path.mkdir(parents=True)
        logger.info(f"Created directory: {path}")

def ensure_file(path: Path):
    """Create empty file if it doesn't exist"""
    if not path.exists():
        path.touch()
        logger.info(f"Created file: {path}")

def verify_structure():
    root = Path(__file__).parent.parent
    
    # Create required directories
    for dir_path in REQUIRED_DIRS:
        ensure_directory(root / dir_path)
    
    # Create required __init__.py files
    for file_path in REQUIRED_FILES:
        ensure_file(root / file_path)
    
    # Create schema files
    schemas_dir = root / "app" / "schemas"
    for schema_file in SCHEMA_FILES:
        ensure_file(schemas_dir / schema_file)

if __name__ == "__main__":
    verify_structure()