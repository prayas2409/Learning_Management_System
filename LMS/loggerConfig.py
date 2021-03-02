import logging
import os

file_name = "Logs/LMS.log"
os.makedirs(os.path.dirname(file_name), exist_ok=True)

logging.basicConfig(filename=file_name, level=logging.INFO, filemode='w',
                    format="%(asctime)s:%(levelname)s:%(message)s")
log = logging.getLogger()
