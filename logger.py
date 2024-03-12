import logging

def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Add any other configuration setup here (handlers, formatters, etc.)

def get_logger(name):
    return logging.getLogger(name)
