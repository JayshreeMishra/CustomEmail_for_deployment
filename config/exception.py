import sys
from config.logging_config import logger

def error_message_detail(error, error_detail: sys):
    try:
        _, _, exc_tb = error_detail.exc_info()
        if exc_tb is None:
            return f"Error message: [{error}]. Traceback information is unavailable."
        
        file_name = exc_tb.tb_frame.f_code.co_filename
        error_message = (
            f"Error occurred in python script: [{file_name}] "
            f"at line number: [{exc_tb.tb_lineno}] "
            f"with error message: [{error}]"
        )
        return error_message
    except Exception as exc:
        # Log the error in traceback handling
        logger.error(f"Failed to process error details: {exc}")
        # Return a fallback error message
        return f"Error message: [{error}] with traceback processing failure."


class CustomException(Exception):
    def __init__(self, message, sys_info):
        super().__init__(message)
        self.message = message
        self.sys_info = sys_info

    def __str__(self):
        return f"CustomException: {self.message}"
