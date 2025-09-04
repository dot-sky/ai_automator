class XPATH:
    dealer_username = '//*[@id="username"]'
    dealer_signin_btn = '//*[@id="signIn"]'
    cox_email = '//*[@id="input28"]'
    cox_next_btn = '//*[@id="form20"]/div[2]/input'
    cox_password = '//*[@id="i0118"]'
    cox_submit_btn = '//*[@id="idSIButton9"]'
    cox_2fa_prompt = '//*[@id="idRichContext_DisplaySign"]'

    staff_iframe = '//*[@id="site-iframe"]'
    staff_widget = '//*[@id="staff-listing1-app-root"]'
    # staff_error_msg = '/html/body/div[11]/div/div/div/div/h1'
    staff_error_msg = '//*[@id="cmsc-staff-editor-ct"]/div/h1'
    staff_error_close_btn = '/html/body/div[11]/div/div/div/div/button'
    staff_add_btn = '//*[@id="cmsc-scroll-container"]/div[2]/button'
    staff_name = '//*[@id="staffName"]'
    staff_title = '//*[@id="staffTitle"]'
    staff_phone = '//*[@id="staffPhone"]'
    staff_email = '//*[@id="staffEmail"]'
    staff_bio = '//*[@id="staffBio"]'
    staff_department = '//*[@id="staffDepartment"]'

    department_add_btn = '//*[@id="cmsc-scroll-container"]/div[1]/button'
    department_name = '//*[@id="departmentName"]'
    submit_department_btn = '/html/body/div[12]/div/div/div/div/div[3]/button[1]'
    submit_staff_btn = '//*[@id="cmsc-staff-editor-ct"]/div/div[3]/button[1]'

class WAIT:
    EXTRA_SHORT = 3
    SHORT = 5
    MEDIUM = 15 
    LONG = 30
    EXTRA_LONG = 60
    TWO_FA = 180
    UPLOAD = 300

class MEDIA_LIB_FOLDER:
    parent ="Do Not Delete"
    staff = "Staff"

class KEY:
    DDC = 'DDC_USERNAME'
    COX = 'COX_EMAIL'
    COX_PASSWORD = 'COX_PASSWORD'
    GEMINI_API = 'GEMINI_API_KEY'