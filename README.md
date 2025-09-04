# AI Automator

**AI Automator** is an internal Python tool that automates staff requests. It leverages Crew AI and Gemini 2.5 Flash to process data and uses Selenium to automate task execution.

## Features

- Extracts information from live websites.
- Processes data using Gemini 2.5 Flash and Crew AI.
- Automates logins, tool integrations, and task execution using Selenium.

---

## Requirements

### Python dependencies

All required Python libraries are automatically installed via `pip`:

- `crewai==0.175.0`
- `ipython==8.12.3`
- `keyring==25.6.0`
- `protobuf==6.32.0`
- `python-dotenv==1.1.1`
- `requests==2.32.5`
- `selenium==4.35.0`
- `traitlets==5.14.3`
- `wcwidth==0.2.13`
- `webdriver_manager==4.0.2`

### R dependency

This tool requires **R** and the `rvest` package for certain tasks. Follow the steps below to install R and the required package:

1. **Install R:**
   - **Windows:** Download and run the installer from [CRAN](https://cran.r-project.org/bin/windows/base/).
   - **Mac:** Download and run the installer from [CRAN](https://cran.r-project.org/bin/macosx/).
   - **Linux (Debian/Ubuntu):**
     ```bash
     sudo apt update
     sudo apt install r-base
     ```
2. **Install the `rvest` package:**
   Open R and run:
   ```R
   R
   install.packages("rvest")
   ```

## Installation

### Install from source

1. Clone the repository

```bash
git clone https://github.com/dot-sky/ai_automator.git
```

2. Navigate to the project directory:

```bash
cd crew_ai_automator
```

3. Install the package:

```bash
pip install -r requirements.txt
```

This will automatically install all required Python dependencies.

## Usage

After installation, run the tool from the command line:

```bash
ai_automator
```

This executes the main() function in main.py.
