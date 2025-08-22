import json
import re

from crewai import Crew, Process

import scripts.automator_live
from config.settings import STAFF_HTML_FILE
from crew.image_verifier import create_image_verification_task, create_image_verifier
from crew.shared_llm import get_gemini_llm
from crew.staff_analyst import create_analysis_task, create_analyst
from scripts.run_r_script import run_r_script
from staff.html_extractor import read_staff_html


def main(live_staff_url):
    # Step 1: Run the R script to generate the staff HTML
    run_r_script(live_staff_url)

    staff_html = read_staff_html(STAFF_HTML_FILE)

    # Step 2: Create agents
    llm = get_gemini_llm()
    analyst = create_analyst(llm)
    image_verifier = create_image_verifier(llm)

    # Step 3: Define tasks
    analysis_task = create_analysis_task(staff_html, analyst)
    image_verification_task = create_image_verification_task(image_verifier)

    # Step 4: Set up and run the Crew process
    crew = Crew(
        agents=[analyst, image_verifier],
        tasks=[analysis_task, image_verification_task],
        process=Process.sequential,
        verbose=True
    )

    print("Running Crew...\n")
    result = crew.kickoff()

    # Step 5: Extract the raw field from the result
    if hasattr(result, "raw"):
        raw = result.raw.strip()

        # Step 6: Remove code block markers like ```json ... ```
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\n?", "", raw)  # remove opening
            raw = re.sub(r"\n?```$", "", raw)           # remove closing

        # Step 7: Parse the cleaned JSON
        try:
            parsed_output = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            parsed_output = raw
    else:
        parsed_output = result

    # Step 8: Save the output in a pretty format
    output_file = "output_staff.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            if isinstance(parsed_output, (dict, list)):
                json.dump(parsed_output, f, indent=2, ensure_ascii=False)
            else:
                f.write(str(parsed_output))
        print(f"\n✅ Clean result saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Could not save the output: {e}")


if __name__ == "__main__":
    # live_staff_url = input("➡️  Enter live staff URL: ").strip()
    # ddc_id = input("➡️  Enter DDC site ID: ").strip()

    live_staff_url = 'https://www.joefergusonbuickgmc.com/staff.aspx'
    ddc_id = 'mojix'

    #main(live_staff_url)
    scripts.automator_live.automation_script(ddc_id, live_staff_url)

