import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STAFF_HTML_FILE = os.path.join("data", "staff_container.txt")
STAFF_DATA_FILE = os.path.join("data", "output.json")
LOCAL_IMG_FOLDER = os.path.join("data", "staff_images")
RSCRIPT_FILE = os.path.join("r_scripts","extract_staff_container.R")