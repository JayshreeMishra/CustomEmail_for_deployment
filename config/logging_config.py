import os
import sys
import logging

logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"

log_dir = "logs"

log_filepath= os.path.join(log_dir, "runnung_log.log")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format= logging_str,
    
    handlers=[
        logging.FileHandler(log_filepath),  #file handeler write logs in the log_filepath
        logging.StreamHandler(sys.stdout)   #stream handelar shows log in the terminal as a output
        ]
)

logger = logging.getLogger("CostomEmailLogger")