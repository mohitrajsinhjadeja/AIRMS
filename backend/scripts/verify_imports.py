import importlib
import logging
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_module_imports(module_path: str) -> Tuple[bool, str]:
    """Verify that a module can be imported without circular dependencies"""
    try:
        start_time = time.time()
        importlib.import_module(module_path)
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ Successfully imported {module_path} ({duration}ms)")
        return True, ""
    except ImportError as e:
        logger.error(f"❌ Failed to import {module_path}: {str(e)}")
        return False, str(e)

def verify_package_structure() -> bool:
    """Verify required package directories and files exist"""
    required_paths = [
        "app/__init__.py",
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/core/__init__.py",
        "app/schemas/__init__.py",
        "app/services/__init__.py",
        "pyproject.toml"  # Added pyproject.toml check
    ]
    
    missing_files: List[str] = []
    for path in required_paths:
        full_path = backend_dir / path
        if not full_path.exists():
            missing_files.append(path)
    
    if missing_files:
        logger.error("❌ Missing required files:")
        for file in missing_files:
            logger.error(f"  - {file}")
        return False
    
    logger.info("✅ Package structure verified")
    return True

def verify_package_installation() -> bool:
    """Verify that the package is installed and importable"""
    try:
        import app
        version = getattr(app, '__version__', 'unknown')
        logger.info(f"✅ Package 'app' installed (version: {version})")
        return True
    except ImportError as e:
        logger.error(f"❌ Package 'app' not installed: {str(e)}")
        logger.info("💡 Try running: pip install -e .")
        return False

def main():
    logger.info("🚀 Starting AIRMS+ Backend verification")
    
    # First verify package installation
    if not verify_package_installation():
        logger.error("❌ Package installation verification failed")
        return

    # Then verify package structure
    if not verify_package_structure():
        logger.error("❌ Package structure verification failed")
        return

    # Core modules that must be present
    modules = [
        "app.api.v1.auth",
        "app.api.v1.notifications",
        "app.api.v1.analytics",
        "app.api.v1.pii_safety",
        "app.api.v1.fact_checking",
        "app.api.v1.enhanced_risk",
        "app.api.v1.education",
        "app.api.v1.chat",
        "app.api.v1.api_keys",
        "app.api.v1.test_suite",
        "app.api.v1.mitigation",
        "app.api.v1.airms_plus"
    ]
    
    # Verify each module
    results = [verify_module_imports(module) for module in modules]
    success_count = sum(1 for success, _ in results if success)
    
    # Print summary
    logger.info("\n📊 Verification Summary:")
    logger.info(f"Total modules: {len(modules)}")
    logger.info(f"Successfully imported: {success_count}")
    logger.info(f"Failed imports: {len(modules) - success_count}")
    
    if success_count == len(modules):
        logger.info("✅ All modules verified successfully")
    else:
        logger.error("❌ Some modules failed verification")

if __name__ == "__main__":
    main()