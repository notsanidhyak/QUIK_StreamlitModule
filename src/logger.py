import os
from dotenv import load_dotenv
load_dotenv()
LOG_DIR = os.getenv("LOG_DIR")

os.makedirs(LOG_DIR, exist_ok=True)

# Setting page config here because this file runs before app.py
# st.set_page_config(page_title="QUIK", layout="wide", page_icon="📂")

def clear_logs():
    """Clears the log file."""
    global LOG_DIR
    with open(f"{LOG_DIR}buildLogs.txt", "w") as log:
        log.write("------------------- QUIK VSM BUILD LOGS -------------------\n")

def log(line):
    global LOG_DIR
    """Logs a line to the log file."""
    with open(f"{LOG_DIR}buildLogs.txt", "a") as log:
        log.write(line[1:] + "\n") # Remove the first character (emoji) before logging