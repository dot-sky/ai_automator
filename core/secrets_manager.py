import os

import keyring
from dotenv import find_dotenv, load_dotenv, set_key, unset_key

from config.const import KEY
from core.logger import log
from core.prompter import prompter

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

def get_or_set_password(service_name, username):
    password = keyring.get_password(service_name, username)
    if password is None:
        log.warning(f"No stored password found for '{service_name}' ({username}).")
        password = prompter.ask_password(f"Enter password for {service_name}: ").strip()
        keyring.set_password(service_name, username, password)
        log.success("Password saved.")
    return password

def get_or_set_env_var(env_var):
    username = os.getenv(env_var)
    if username is None:
        log.warning(f"No value found for '{env_var}'.")
        username = prompter.ask(f"Enter value for {env_var}: ").strip()
        set_key(find_dotenv(), env_var, username)
        log.success(f"Value for '{env_var}' stored successfully.\n")
    return username

def delete_credentials():
    log.title('Removing credentials')
    dotenv_path = find_dotenv()
    if not dotenv_path:
        log.warning(".env file not found. ")

    username = os.getenv(KEY.COX)
    if username:
        try:
            keyring.delete_password(KEY.COX, username)
            log.info(f"Deleted keyring password for '{KEY.COX}' ({username}).")
        except keyring.errors.PasswordDeleteError:
            log.info(f"Deleted keyring password for '{KEY.COX}' ({username}).")

    # Remove environment variables from .env
    for env_var in [KEY.COX, KEY.DDC, KEY.GEMINI_API]:
        if os.getenv(env_var):
            unset_key(dotenv_path, env_var)
            log.info(f"Removed '{env_var}' from .env file.")
    log.plain('Search completed.')
    log.end_title()

def load_credentials():
    ddc_username = get_or_set_env_var(KEY.DDC)
    cox_email = get_or_set_env_var(KEY.COX)
    cox_password = get_or_set_password(KEY.COX, cox_email)
    return ddc_username, cox_email, cox_password

def setup_credentials():
    ddc = os.getenv(KEY.DDC)
    cox = os.getenv(KEY.COX)
    gemini = os.getenv(KEY.GEMINI_API)
    password = None
    if cox is not None:
        password =  keyring.get_password(KEY.COX, cox)

    if ddc is None or cox is None or gemini is None or password is None:
        log.title('Credentials Setup')

        get_or_set_env_var(KEY.DDC)
        cox_email = get_or_set_env_var(KEY.COX)
        get_or_set_env_var(KEY.GEMINI_API)
        get_or_set_password(KEY.COX, cox_email)

        log.end_title()

