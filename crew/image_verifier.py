from crewai import Agent, Task

def create_image_verifier(llm):
    return Agent(
        role='Image Verifier',
        goal='Verify that the images belong to real people and are not placeholder images.',
        backstory='You are an expert in identifying human faces in images.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def verify_images_task_func(staff_json):
    staff_verificado = []
    for miembro in staff_json:
        img_url = miembro.get("imagen") or miembro.get("image") or miembro.get("foto")
        miembro['photo_verified'] = False
        if not img_url:
            continue
        prompt = (
            f"Carefully analyze the image at this URL: {img_url}\n"
            "Does the image show a real human face, an animal, a generic silhouette, or something else? "
            "Respond ONLY with one of these words: persona, animal, silueta, otro. "
            "DO NOT explain your answer."
        )
        try:
            result = llm(prompt)
            print(f"Image for {miembro.get('nombre', '[NO NAME]')}: {result}")
            if "persona" in result.lower():
                miembro['photo_verified'] = True
            staff_verificado.append(miembro)
        except Exception as e:
            print(f"Error verifying image for {miembro.get('nombre','[NO NAME]')}: {e}")
            staff_verificado.append(miembro)
    return staff_verificado

def create_image_verification_task(image_verifier):
    return Task(
        description=(
            "Verify if the image of each staff member is of a real person. "
            "You will receive a list in JSON format with each member's data and image URL. "
            "For each image, respond with 'persona', 'animal', 'silueta', or 'otro'. "
            "If the image is of a real person, add the field 'photo_verified': true to that member's object. "
            "Otherwise, add 'photo_verified': false."
        ),
        expected_output=(
            "The original JSON list, but each member includes the 'photo_verified' field indicating image validity."
        ),
        agent=image_verifier,
        run=verify_images_task_func
    )
