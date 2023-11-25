from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from telegram import send_message, send_photo
from creds import username, password, urls, look_for_appointments_before
from sound import play_sound, test_sound
from helpers import prn, print_exception
from datetime import datetime

# Init global variables

base_url = f'https://ais.usvisa-info.com/en-'

heart_beat = 0
cell_text = ''
seconds_between_checks = 119
heart_beat_count = 1000   # Send heartbeet message after running this number of checks
driver = None
chrome_options = None

def init_driver():
    global driver
    # Setting Chrome options to run the scraper headless.
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    #chrome_options.add_argument("--headless") # Comment for visualy debugging, uncomment for headless runs

    connected = False
    while not connected:
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://www.google.com")
            connected = True
        except WebDriverException:
            connected = False
            time.sleep(30)

def is_logged_in(url):
    global driver
    # Getting the website to check
    try:
        driver.get(url)
    except WebDriverException as e:
        driver.quit()
        init_driver()
        driver.get(url)
    except Exception as e:
        print_exception(e, "Cannot load login URL.")
        return False

    # Checking if we are still logged in
    if driver.current_url != url:
        if 'sign_in' in driver.current_url:
            prn('Logging in.')
            # Clicking the first prompt, if there is one
            try:
                sign_in_ok = driver.find_element("xpath",
                    '/html/body/div[7]/div[3]/div/button')
                if sign_in_ok:
                    sign_in_ok.click()
                # Filling the user and password
                user_box = driver.find_element("name", 'user[email]')
                user_box.send_keys(username)
                password_box = driver.find_element("name", 'user[password]')
                password_box.send_keys(password)
                # Clicking the checkbox
                policy_confirmed = driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/div[3]/label/div')

                policy_confirmed.click()
                # Clicking 'Sign in'
                driver.find_element("xpath",
                    '//*[@id="sign_in_form"]/p[1]/input').click()

                # Logging to screen
                prn('Logged in.')
                time.sleep(1)
            except Exception as e:
                print_exception(e, 'Cannot log in.')
                return False
        else:
            prn(f'Cannot log in, no "sign in" on the page. Current URL: {driver.current_url}')
            return False
    return True

def notify_about_appointment(url, appts = None):
    global cell_text
    city = url[0]
    link = base_url+url[1]
    msg = f'An appointment was found in {city}. \nClick here to see it: {link}\n{" | ".join(appts)}'
    prn(msg)
    send_message(msg)
    send_message(cell_text)
    play_sound(3) # Play sound locally a few times
    return

def is_appointment_available(u):
    global cell_text

    url = base_url + u[1]
    try:
        if driver.current_url != url:
            driver.get(url)
        if "429" in driver.title:
            prn('429 error: too many requessts')
            return False
        if driver.title == 'ais.usvisa-info.com':
            prn('Empty response')
            return False
    except Exception as e:
        print_exception(e)
        return False


    # Getting main text
    try:
        cell_text = driver.find_element("xpath","(//div[@id='paymentOptions']/div[contains(@class,'column')])[2]").text
    except Exception as e:
        print_exception(e, "Cannot find cell")
        return False
    if "No Appointments Available" in cell_text:
        return False
    print(cell_text)
    # Can add additional logic here if needed
    # if "2023" in cell_text:
    #    return  True #"May" in cell_text or "June" in cell_text
    return True

def is_reschedule_available(u):
    global cell_text

    url = base_url + u[1].replace('payment', 'appointment')
    try:
        if driver.current_url != url:
            driver.get(url)
        if "429" in driver.title:
            prn('429 error: too many requessts')
            return False
        if driver.title == 'ais.usvisa-info.com':
            prn('Empty response')
            return False
    except Exception as e:
        print_exception(e)
        return False

    print()
    send_notification = False
    # Getting main text
    try:
        # div_error = driver.find_element(By.ID, "consulate_date_time_not_available")
        # div_note = driver.find_element(By.ID, "appointments_consulate_notes")
        # div_list = driver.find_element(By.ID, "consulate_date_time")
        txt = driver.find_element(By.ID, "appointments_consulate_appointment_date")
        time.sleep(1)
        txt.click()
        class_name = "ui-datepicker-group-first"
        appts = []
        for _ in range(7):

            div_month = driver.find_element(By.CLASS_NAME, class_name)
            month = div_month.find_element(By.CLASS_NAME, "ui-datepicker-title").text
            m = iterate_month(div_month)
            if m:
                str = f'{month}: {m}'
                appts.append(str)
                if not send_notification:
                    m = m.split(', ')
                    send_notification = datetime.strptime(f'{month} {m[0]}', '%B %Y %d') < look_for_appointments_before

            else:
                pass
            driver.find_element(By.CLASS_NAME, 'ui-datepicker-next').click()
            if 'first' in class_name:
                class_name = "ui-datepicker-group-last"
        if appts:

            print(f'\n{appts}')
    except Exception as e:
        print_exception(e, "Cannot find cell")
        return False

    return send_notification, appts

# If several appointments available for rescheduling, visually iterate months
def iterate_month(div_month):
    appts = []
    for date_element in div_month.find_elements(By.CLASS_NAME, "ui-state-default"):
        # You can interact with each date element here, for example:
        parent = date_element.find_element(By.XPATH, '..')
        css_class = parent.get_attribute('class')
        if not 'ui-datepicker-unselectable' in css_class:
            date_text = date_element.text
            appts.append(date_text)
    if appts:
        return ", ".join(appts)

def run_visa_scraper(urls, initial_pay = True):
    init_driver()
    while True:
        prn(f'Round {heart_beat}. {" "*20} ')

        for u in urls:
            url = base_url + "/".join(u[1].split("/")[:-1])
            if is_logged_in(url):
                if initial_pay:
                    if is_appointment_available(u):
                        notify_about_appointment(u)
                else:  #reschedule
                    result = is_reschedule_available(u)
                    if isinstance(result, tuple):
                        result, appts = result
                        if result:
                            notify_about_appointment(u, appts)


        hibernate()




def hibernate(seconds = seconds_between_checks):
    global heart_beat
    heart_beat += 1
    if heart_beat % heart_beat_count == 0:
        send_message(f'Heart beat: {heart_beat}')
    for seconds_remaining in range(int(seconds), 0, -1):
        print(
            f'\rChecking again in {("000" + str(seconds_remaining))[-3:]} seconds.', end='')
        time.sleep(1)
    print("\r",end='')


if __name__ == "__main__":
    # Uncomment if you want to test your local sound
    # test_sound()

    send_message('Starting the scraper.')
    # Set initial_pay = True for scheduling appointment, False to rescheduling
    run_visa_scraper(urls, initial_pay = False)
