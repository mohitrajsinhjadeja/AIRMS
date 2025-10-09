import uvicorn
import click
from pathlib import Path
import sys
import os  # Add this import
from typing import Optional
from pythonjsonlogger import jsonlogger



@click.command()
@click.option(
    '--env',
    type=click.Choice(['dev', 'staging', 'prod']),
    default='dev',
    help='Environment to run'
)
@click.option('--port', default=8000, help='Port to run on')
@click.option('--reload/--no-reload', default=True, help='Enable auto-reload')
@click.option('--log-level', default='info', help='Logging level')
def main(env: str, port: int, reload: bool, log_level: str):
    """Development server for AIRMS backend"""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    
    # Load environment-specific settings
    os.environ['APP_ENV'] = env
    
    # Configure logging
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json'
            }
        },
        'root': {
            'handlers': ['console'],
            'level': log_level.upper()
        }
    }
    
    # Run development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_config=logging_config,
        log_level=log_level
    )

if __name__ == "__main__":
    main()