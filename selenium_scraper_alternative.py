# Alternative base url and page layout, which is implemented on force.com platform
# Not sure if it's still applicable, leaving it just in case it might be needed in the future

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
from telegram import send_message, send_photo
from creds import usernameF, passwordF
from sound import play_sound
from helpers import prn, print_exception

base_url_f = f'https://cgifederal.secure.force.com/updatedata'
heart_beat = 0
cell_text = ''
seconds_between_checks = 39

def run_visa_scraper():
    def is_logged_in():
        # Getting the website to check
        url = base_url_f
        try:
            driver.get(url)
        except Exception as e:
            print_exception(e, "Cannot load login URL.")
            return False

        if len(driver.find_elements("id", "logo")) > 0:
            # Checking if website is still logged
            el_name = "Unauthorized:SiteTemplate:siteLogin:loginComponent:loginForm:username"
            el_pwd = "Unauthorized:SiteTemplate:siteLogin:loginComponent:loginForm:password"
            el_chkbox = "//*/table/tbody/tr[3]/td/label/input"
            el_captcha_response = "Unauthorized:SiteTemplate:siteLogin:loginComponent:loginForm:recaptcha_response_field"
            el_captcha = "Unauthorized:SiteTemplate:siteLogin:loginComponent:loginForm:theId"
            el_login = "Unauthorized:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton"
            if len(driver.find_elements("name", el_name)) > 0:
                prn('Logging in.')
                # Clicking the first prompt, if there is one
                try:
                    driver.find_element("xpath", el_chkbox).click()
                    # Filling the user and password
                    user_box = driver.find_element("name", el_name)
                    user_box.send_keys(usernameF)
                    password_box = driver.find_element("name", el_pwd)
                    password_box.send_keys(passwordF)
                    # Clicking the checkbox
                    driver.find_element("id",el_captcha).screenshot('captcha.png')
                    send_photo("captcha.png")
                    # Clicking 'Sign in'
                    driver.find_element("id",
                        el_captcha_response).send_keys(input("Enter captcha: "))
                    driver.find_element("id", el_login).click()

                    # Logging to screen
                    prn('Logged in.')
                except Exception as e:
                    print_exception(e, 'Cannot log in.')
                    return False
        else:
            prn(f'Cannot log in, no "sign in" on the page. Current URL: {driver.current_url}')
            return False
        return True


    def notify_about_appointment(url):
        global cell_text
        city = url[0]
        link = base_url_f
        msg = f'An appointment was found in {city}. \nClick here to see it: {link}'
        prn(msg)
        # driver.find_element("xpath","(//div[@id='paymentOptions']/div[contains(@class,'column')])[2]").screenshot("table.png")
        send_message(msg)
        send_message(cell_text)
        play_sound(3)
        return

    def is_appointment_available():
        global cell_text
        print(f'\rChecking for changes on Finland.{" "*20}')
        url = base_url_f
        try:
            if driver.current_url != url:
                driver.get(url)
        except Exception as e:
            print_exception(e)
            return False

        if "429" in driver.title:
            prn('429 error: too many requessts')
            return False

        # Getting main text
        try:
            cell_text = driver.find_element("xpath",'//*[@id="ctl00_nav_side1"]/ul/div').text
        except Exception as e:
            print_exception(e, "Cannot find cell")
            return False
        if "2022" in cell_text:
            print(cell_text)
            return  "August" in cell_text or "September" in cell_text
        return False


    # Setting Chrome options to run the scraper headless.
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--headless") # Comment for visualy debugging

    # Initialize the chromediver (must be installed and in PATH)
    # Needed to implement the headless option
    driver = webdriver.Chrome(options=chrome_options)
    # chrome_options.add_argument("--no-sandbox") # linux only

    while True:
        prn(f'Round {heart_beat}. {" "*20} ')

        if is_logged_in():
            if is_appointment_available():
                notify_about_appointment()

        sleep()


def sleep(seconds = seconds_between_checks):
    global heart_beat
    heart_beat += 1
    if heart_beat % 100 == 0:
        send_message(f'Heart beat: {heart_beat}')
    for seconds_remaining in range(int(seconds), 0, -1):
        print(
            f'\rChecking again in {("000" + str(seconds_remaining))[-2:]} seconds.', end='')
        time.sleep(1)
    print("\r",end='')


if __name__ == "__main__":
    #test_sound()
    send_message('Starting the scraper.')
    run_visa_scraper()
