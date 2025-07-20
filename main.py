from scripts.run_r_script import run_r_script
from staff.html_extractor import read_staff_html
from crew.staff_analyst import get_gemini_llm, create_analyst, create_analysis_task, run_crew
from config.settings import STAFF_HTML_FILE

def main():
    # Step 1: Run the R script
    run_r_script()
    # Step 2: Read the generated HTML content
    staff_html = read_staff_html(STAFF_HTML_FILE)
    # Step 3: Set up agents and task
    llm = get_gemini_llm()
    analyst = create_analyst(llm)
    analysis_task = create_analysis_task(staff_html, analyst)
    # Step 4: Run the crew
    run_crew(analyst, analysis_task)

if __name__ == "__main__":
    main()
