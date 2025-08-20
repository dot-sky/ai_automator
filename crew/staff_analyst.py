from crewai import Agent, Task

def create_analyst(llm):
    return Agent(
        role='Senior Data Analyst',
        goal='Analyze the provided HTML content.',
        backstory='You are an expert in finding patterns in HTML code.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_analysis_task(staff_html, analyst):
    return Task(
        description=(
            "Below is the HTML of the main staff container extracted from the R script:\n\n"
            f"{staff_html}\n\n"
            "Analyze the received HTML text. For each staff member, extract and organize the following fields in a Markdown list if they are present:\n"
            "- Name\n"
            "- Department\n"
            "- Position\n"
            "- Phone (if available else N/A)\n"
            "- Email (if available with format xyz@example.com else N/A)\n"
            "- Biography (if available else N/A)\n"
            "- Image link (URL taken from the <img> src attribute) else N/A\n"
        ),
        expected_output=(
            "A list in JSON format, where each staff member is represented as an object containing the following fields if present: "
            "name, department, position, phone, email, biography, image_url.\n"
            "DO NOT explain your answer, do not explain your thought process, the only output should be the list in json format\n"
        ),
        agent=analyst
    )
