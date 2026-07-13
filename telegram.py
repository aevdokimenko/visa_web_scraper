import requests
from config import token, chat_id
from helpers import prn

def _check_response(response):
    data = response.json()
    if not data.get('ok'):
        prn(f"Telegram API error: {data.get('description', data)}")
    return data

def send_message(text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    parameters = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, parameters)
    except requests.RequestException as e:
        prn(f"Error sending message via Telegram: {e}")
        return None
    return _check_response(response)



def send_photo(photo_file):
    url = f'https://api.telegram.org/bot{token}/sendPhoto'
    parameters = {
        'chat_id': chat_id
    }
    try:
        with open(photo_file, 'rb') as f:
            response = requests.post(url, parameters, files={'photo': f})
    except (requests.RequestException, OSError) as e:
        prn(f"Error sending photo via Telegram: {e}")
        return None
    return _check_response(response)


if __name__ == "__main__":
    import pprint as pp
    response = send_message('Starting scrapping')
    pp.pprint(response)