from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from telegram import send_message, send_photo
from config import username, password, urls, months_to_iterate
from sound import play_sound, test_sound
from helpers import prn, print_exception
from datetime import datetime
from selenium.common.exceptions import WebDriverException

# run for Chrome standalone Selenium container
# docker run -d --name sel \
#   -p 4444:4444 -p 7900:7900 \
#   --shm-size=2g \
#   selenium/standalone-chromium:latest
# Port 7900 is noVNC: open http://localhost:7900 (password secret) 

def dump(driver, tag="fail"):
    print("URL      :", driver.current_url)
    print("TITLE    :", driver.title)
    print("WINDOW   :", driver.get_window_size())
    print("VIEWPORT :", driver.execute_script(
        "return [window.innerWidth, window.innerHeight]"))
    print("UA       :", driver.execute_script("return navigator.userAgent"))
    if driver.title != "Under construction (503)":
        driver.save_screenshot(f"screenshot_{int(time.time())}.png")
        with open(f"screenshot_{int(time.time())}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

# Init global variables

base_url = f'https://ais.usvisa-info.com/en-'

heart_beat = 0
cell_text = ''
seconds_between_checks = 59
heart_beat_count = 1000   # Send heartbeet message after running this number of checks
driver = None
chrome_options = None
remote = True

def init_driver():
    global driver
    # Setting Chrome options to run the scraper headless.
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless") # Comment for visualy debugging, uncomment for headless runs

    connected = False
    while not connected:
        try:
            driver = webdriver.Remote(command_executor='http://localhost:4444', options=chrome_options) if remote \
                  else webdriver.Chrome(options=chrome_options)
            driver.get("https://www.google.com")
            connected = True
        except WebDriverException as e:
            dump(driver, "init_driver_error")
            print_exception(e, "Cannot connect to Selenium server. Retrying in 30 seconds.")
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
                time.sleep(1)  # Wait for the prompt to appear
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
                time.sleep(1)  # Wait for the page to process the login information
                driver.find_element("xpath",
                    '//*[@id="sign_in_form"]/p[1]/input').click()

                # Logging to screen
                time.sleep(1)
                if not "Applicant Summary Page" in driver.title:
                    prn('Failed to log in.')
                    driver.save_screenshot(f"screenshot_{int(time.time())}.png")
                    return False
                prn('Logged in.')
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
    msg = f'An appointment was found in {city}. \nClick here to see it: {link}\n'
    if appts:
        msg += "Available appointments:\n" + "\n".join(appts) + f"\n({' | '.join(appts)})"

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
        if "Applicant Summary Page" in driver.title:
            driver.get(url)
        if "Schedule Appointments" in driver.title:
            # We are at appointment selection page
            dropdown = driver.find_element(By.NAME, "appointments[consulate_appointment][facility_id]")
            option = dropdown.find_element(By.XPATH, "//*[@id='appointments_consulate_appointment_facility_id']/option[3]")
            option.click()
            time.sleep(5)
            text = driver.find_element(By.XPATH, "//*[@id='consulate_date_time_not_available']/small").text
            if "System is busy" in text:
                return False
            else:
                driver.save_screenshot(f"screenshot_{int(time.time())}.png")
                return True
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
    time.sleep(3)
    try:
        cell_text = driver.find_element("xpath","(//div[@id='paymentOptions']/div[contains(@class,'column')])[2]").text
    except Exception as e:
        driver.save_screenshot(f"screenshot_{int(time.time())}.png")
        print_exception(e, "Cannot find cell")
        return False

    if cell_text == 'First Available Appointments\nAstana No Appointments Available\nAlmaty No Appointments Available':
        return False
    print(cell_text)
    # Can add additional logic here if needed
    # if "2023" in cell_text:
    # if "2023" in cell_text:
    #    return  True #"May" in cell_text or "June" in cell_text
    driver.save_screenshot(f"screenshot_{int(time.time())}.png")
    return True

def is_reschedule_available(u):
    global cell_text

    url = base_url + u[1].replace('payment', 'appointment?confirmed_limit_message=1&commit=Continue')
    try:
        if driver.current_url != url:
            driver.get(url)
        if "429" in driver.title:
            prn('429 error: too many requessts')
            return False
        if driver.title == 'ais.usvisa-info.com':
            prn('Empty response')
            return False
        time.sleep(5)
        text = driver.find_element(By.XPATH, "//*[@id='consulate_date_time_not_available']/small").text
        if "System is busy" in text:
            return False
        else:
            driver.save_screenshot(f"screenshot_{int(time.time())}.png")
    except Exception as e:
        dump(driver, "reschedule_error")
        return False

    send_notification = False
    # Getting main text
    appts = []
    try:
        # div_error = driver.find_element(By.ID, "consulate_date_time_not_available")
        # div_note = driver.find_element(By.ID, "appointments_consulate_notes")
        # div_list = driver.find_element(By.ID, "consulate_date_time")
        date_text = driver.find_element(By.ID, "appointments_consulate_appointment_date")


        date_text.click()
        class_name = "hasDatepicker"
        for k in range(months_to_iterate):

            div_month = driver.find_element(By.CLASS_NAME, "ui-datepicker-group-last")
            month = div_month.find_element(By.CLASS_NAME, "ui-datepicker-month").text
            m = iterate_month(div_month)
            if m:
                str = f'{month}\'{"26" if k<6 else "27" if k<18 else "28" }: {m}'
                appts.append(str)
                if not send_notification:
                    send_notification = "\n".join(appts)
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
    # test_sound(3)

    send_message('Starting the scraper.')
    # Set initial_pay = True for scheduling appointment, False to rescheduling
    run_visa_scraper(urls, initial_pay = False)
