from datetime import datetime
# ais.usvisa-info.com credentials
username = 'user_name@used.to.log.in'
password = 'your_password'

# List of appointment urls to check in the format:
# Country, URL to check, XPath to check
# Replace appointment IDs with your actual IDs for each of the locations
# XPaths might be different for countries with multiple applciation locations, for example
urls = [['Serbia', f'rs/niv/schedule/<appointment_id1>/payment', "(//div[@id='paymentOptions']/div  [contains(@class,'column')]/table/tbody//td[@class='text-right'])[1]"]
        # ,
        ['Cyprus', f'cy/niv/schedule/<appointment_id2>/payment', "(//div[@id='paymentOptions']/div  [contains(@class,'column')]/table/tbody//td[@class='text-right'])[1]"],
        ['Armenia', f'am/niv/schedule/<appointment_id3>/payment', "//div[@id='paymentOptions']/div[contains(@class,'column')]/table/tbody//td[@class='text-right']"]
        # ,
        # ['Italia', f'it/niv/schedule/<appointment_id4>/payment', "(//div[@id='paymentOptions']/div[contains(@class,'column')])[2]"]
        ]

# Notify for rescheduling only if a new appointment found BEFORE this date
look_for_appointments_before = datetime(2024,3,4)

# Telegram bot token and chat
token = 'prefixt:bot_token'
chat_id = 'chat_id'
