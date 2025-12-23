import logging
import sys

def get_logger(name):
    """
    Creates a configured logger.
    
    Why: In production, you don't look at the console. You look at logs files.
    'print' statements are bad practice in industrial code because they don't have
    timestamps or severity levels (INFO/WARN/ERROR).
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Create formatter (Timestamp - Name - Level - Message)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
    return logger
