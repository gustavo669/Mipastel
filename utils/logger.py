import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
from config.settings import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'message': record.getMessage(),
            'line': record.lineno
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logging():
    logger = logging.getLogger('mipastel')
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    fh = RotatingFileHandler(
        settings.LOGS_DIR / 'mipastel.log',
        maxBytes=10485760,
        backupCount=5
    )
    fh.setFormatter(JSONFormatter())
    
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = setup_logging()
