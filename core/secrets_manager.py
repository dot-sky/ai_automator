import os

import keyring
from dotenv import find_dotenv, load_dotenv, set_key

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

def get_or_set_password(service_name, username):
    password = keyring.get_password(service_name, username)
    if password is None:
        print(f"⚠️  No stored password found for '{service_name}' ({username}).")
        password = input(f"➡️ Enter password for {service_name}: ").strip()
        keyring.set_password(service_name, username, password)
        print(f"✅ Password for '{service_name}' stored securely.")
    return password

def get_or_set_username(env_var):
    username = os.getenv(env_var)
    if username is None:
        print(f"⚠️  No username found for '{env_var}'.")
        username = input(f"➡️ Enter username for {env_var}: ").strip()
        set_key(find_dotenv(), env_var, username)
        print(f"✅ Username for '{env_var}' stored in .env file.")
    return username

def update_password():
    pass

def load_credentials():
    ddc_username = get_or_set_username('ddc')
    cox_email = get_or_set_username('cox')
    cox_password = get_or_set_password('cox', cox_email)
    return ddc_username, cox_email, cox_password
