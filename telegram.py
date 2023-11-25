import requests
from creds import token, chat_id
from helpers import prn

def send_message(text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    parameters = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, parameters)
        return response.json()
    except Exception as e:
        prn("Error sending message via Telegram.")



def send_photo(photo_file):
    url = f'https://api.telegram.org/bot{token}/sendPhoto'
    parameters = {
        'chat_id': chat_id
    }
    response = requests.post(url, parameters, files={'photo': open(photo_file, 'rb')})
    return response.json()


if __name__ == "__main__":
    import pprint as pp
    response = send_photo('table.png')
    pp.pprint(response)