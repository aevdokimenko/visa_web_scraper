import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# ais.usvisa-info.com credentials
username = os.environ['VISA_USERNAME']
password = os.environ['VISA_PASSWORD']

# Telegram bot token and chat
token = os.environ['TELEGRAM_BOT_TOKEN']
chat_id = os.environ['TELEGRAM_CHAT_ID']

# List of appointment urls to check in the format:
# Country, URL to check, XPath to check
# Replace appointment IDs with your actual IDs for each of the locations
# XPaths might be different for countries with multiple applciation locations, for example
urls = [['Kazakhstan', f'kz/niv/schedule/75178318/payment', "(//div[@id='paymentOptions']/div  [contains(@class,'column')]/table/tbody//td[@class='text-right'])[1]"]
        # ,
        # ['Cyprus', f'cy/niv/schedule/<appointment_id2>/payment', "(//div[@id='paymentOptions']/div  [contains(@class,'column')]/table/tbody//td[@class='text-right'])[1]"],
        # ['Armenia', f'am/niv/schedule/<appointment_id3>/payment', "//div[@id='paymentOptions']/div[contains(@class,'column')]/table/tbody//td[@class='text-right']"]
        # ,
        # ['Italia', f'it/niv/schedule/<appointment_id4>/payment', "(//div[@id='paymentOptions']/div[contains(@class,'column')])[2]"]
        ]

# Notify for rescheduling only if a new appointment found BEFORE this date
look_for_appointments_before = datetime(2027, 3, 4)
