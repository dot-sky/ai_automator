from core import browser
from core.logger import log
from core.prompter import prompter


def run_step(step_fn, step_name, *args, manual_message=None, **kwargs):
    while True:
        try:
            result = step_fn(*args, **kwargs)
            return result

        except Exception as e:
            #reset 
            browser.switch_to_default() 

            failed_args = None
            if e.args and isinstance(e.args[0], dict) and "failed_members" in e.args[0]:
                failed_args = e.args[0]['failed_members']
                log.error(f"Step '{step_name}' failed for {len(failed_args)} members")
                log.plain("Failed members:")
                for m in failed_args:
                    log.warning(m.get("name"))
                log.dedent()
            elif e.args and isinstance(e.args[0], dict) and "failed_imgs" in e.args[0]:
                failed_args = e.args[0]['failed_imgs']
                log.error(f"Step '{step_name}' failed for {len(failed_args)} members")
                log.plain("Failed images:")
                for m in failed_args:
                    log.warning(f'{m.get("file")} - {m.get("error")}')
                log.dedent()
            else:
                log.error(f"Step '{step_name}' execution failed")
                print(e)

            choice = '' 
            while choice not in 'rsm':
                print()
                choice = prompter.ask("Choose an option [R]etry, [S]kip, [M]anual") 

            if choice == "r":
                log.warning("Retrying step...")
                log.end_title()
                if failed_args and "failed_members" in e.args[0]:
                    # complete
                    return run_step(step_fn,
                            step_name,
                            failed_args, *args[1:],
                            manual_message=manual_message, **kwargs)
                
                elif failed_args and "failed_imgs" in e.args[0]:
                    return run_step(step_fn, step_name, *args, manual_message=manual_message, selected_imgs=failed_args)  
                continue

            elif choice == "s":
                log.warning(f"Skipping step: {step_name}")
                log.end_title()
                return None

            elif choice == "m":
                if manual_message:
                    log.warning("Manual action required:")
                    log.info(manual_message)
                else:
                    log.warning(f"Please complete step '{step_name}' manually.")

                confirm = prompter.ask("Type 'done' once you have completed this step manually",1).lower()
                while confirm != "done":
                    confirm = prompter.ask("Not confirmed. Please type 'done' when finished",1).lower()

                log.success(f"Step '{step_name}' confirmed as done manually.")
                log.end_title()
                return "manual"

            else:
                log.warning("Invalid choice, please enter R, S, or M.")