import logging

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

        # Log to a file
        file_handler = logging.FileHandler("process_emails.log")
        file_handler.setFormatter(formatter)

        # Log to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger

