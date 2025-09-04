import json
import re

from crewai import Crew, Process

from config.settings import STAFF_DATA_FILE, STAFF_HTML_FILE
from core.logger import log
from core.runner import run_step
from crew.image_verifier import create_image_verification_task, create_image_verifier
from crew.shared_llm import get_gemini_llm
from crew.staff_analyst import create_analysis_task, create_analyst
from scripts.staff_data_extraction import read_staff_html


def crew_data_processing():

    staff_data = read_staff_html(STAFF_HTML_FILE)

    llm = get_gemini_llm()
    analyst = create_analyst(llm)
    image_verifier = create_image_verifier(llm)

    analysis_task = create_analysis_task(staff_data, analyst)
    image_verification_task = create_image_verification_task(image_verifier)

    crew = Crew(
        agents=[analyst, image_verifier],
        tasks=[analysis_task, image_verification_task],
        process=Process.sequential,
        verbose=True 
    )

    result = crew.kickoff()

    if hasattr(result, "raw"):
        raw = result.raw.strip()

        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)         

        try:
            parsed_output = json.loads(raw)
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON: {e}")
            parsed_output = raw
    else:
        parsed_output = result

    output_file = STAFF_DATA_FILE
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            if isinstance(parsed_output, (dict, list)):
                json.dump(parsed_output, f, indent=2, ensure_ascii=False)
            else:
                f.write(str(parsed_output))
        log.success(f"Clean result saved to {output_file}")
    except Exception as e:
        log.error(f"Could not save the output: {e}")

def process_staff_data():
    run_step(
        crew_data_processing,                 
        "Process data",                              
        manual_message=f"Please paste the processed data into the staff file: {STAFF_DATA_FILE}"
    )   
