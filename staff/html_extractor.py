def read_staff_html(filepath):
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERROR] File {filepath} not found after running the R script.")
        exit(1)
