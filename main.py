from core.logger import log
from core.prompter import prompter
from core.secrets_manager import setup_credentials
from scripts import staff_crew_ai, staff_data_extraction, staff_submission_automation


def automator():
    log.clear()
    log.title('AI Automator')

    live_staff_url = prompter.ask("Enter live staff URL")
    ddc_id = prompter.ask("Enter DDC site ID")

    log.end_title()
    # live_staff_url = 'https://www.uebelhortoyota.com/dealership/staff.htm'
    # ddc_id = 'mojix'

    setup_credentials()

    staff_data_extraction.extract_staff_html(live_staff_url)
    staff_crew_ai.process_staff_data()
    staff_submission_automation.automation_script(ddc_id, live_staff_url)


if __name__ == "__main__":
    automator()
