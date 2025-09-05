import sys

from core.logger import log
from core.prompter import prompter
from core.secrets_manager import setup_credentials
from scripts import staff_crew_ai, staff_data_extraction, staff_submission_automation


def automator(steps):
    setup_credentials()

    log.clear()
    log.title('AI Automator')

    live_staff_url = prompter.ask("Enter live staff URL")
    ddc_id = prompter.ask("Enter DDC site ID")

    log.end_title()


    # Default: run all steps if steps is None or empty
    if not steps:
        steps = "a"

    if "e" in steps or "a" in steps: # extract
        staff_data_extraction.extract_staff_html(live_staff_url)
    if "p" in steps or "a" in steps: # process
        staff_crew_ai.process_staff_data()
    if "s" in steps or "a" in steps: # submit
        staff_submission_automation.automation_script(ddc_id, live_staff_url)

if __name__ == "__main__":
    step_arg = sys.argv[1].lower() if len(sys.argv) > 1 else None

    valid_chars = {"e", "p", "s", "a"}
    if step_arg and not set(step_arg).issubset(valid_chars):
        print("Invalid argument. Choose any combination of: e (extract), p (process), s (submit), a (all)")
        sys.exit(1)

    automator(step_arg)
