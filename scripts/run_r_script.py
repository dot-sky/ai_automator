import subprocess
from config.settings import RSCRIPT_FILE

def run_r_script():
    try:
        subprocess.run(["Rscript", RSCRIPT_FILE], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] R script execution failed: {e}")
        exit(1)
