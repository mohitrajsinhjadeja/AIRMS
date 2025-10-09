import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
from core.config import get_settings

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['service'] = 'airms'

def configure_logging():
    settings = get_settings()
    
    # Create JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for non-development environments
    if settings.ENVIRONMENT != "development":
        file_handler = logging.FileHandler("logs/airms.log")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)