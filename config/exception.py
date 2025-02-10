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
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        try:
            self.error_message = error_message_detail(
                error_message, error_detail=error_detail
            )
        except Exception as exc:
            # Fallback if error_message_detail fails
            self.error_message = f"{error_message}. Additionally, failed to generate detailed traceback: {exc}"

    def __str__(self):
        return self.error_message

