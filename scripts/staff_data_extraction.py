import subprocess
from pathlib import Path

from config.settings import RSCRIPT_FILE, STAFF_HTML_FILE
from core.logger import log
from core.runner import run_step
from core.utils import ensure_path


def run_r_script(live_staff_url):
    log.title('HTML Data Extraction')
    ensure_path(STAFF_HTML_FILE)
    output_file = Path(STAFF_HTML_FILE)
    try:
        subprocess.run(["Rscript", RSCRIPT_FILE, live_staff_url, output_file], check=True)
    except subprocess.CalledProcessError as e:
        raise Exception({"r_script_error": f"R script execution failed: {e}"})

    if not output_file.exists() or output_file.stat().st_size==0:
        raise Exception({"r_script_error": "R script produced empty output file:"})

    log.success('Data obtained successfully') 
    log.end_title()
    return str(output_file)


def read_staff_html(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        log.error(f"File {filepath} not found after running the R script.")
        raise FileNotFoundError

def extract_staff_html(live_staff_url):
    run_step(
        run_r_script,
        "Extract staff HTML",
        live_staff_url,
        manual_message=f"Please paste the HTML container of the staff widget onto the file: {STAFF_HTML_FILE}"
    )
    return read_staff_html(STAFF_HTML_FILE)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run R script and extract staff HTML.")
    parser.add_argument("live_staff_url", help="The URL to the live staff page to scrape.")
    args = parser.parse_args()

    extract_staff_html(args.live_staff_url)