import requests
from django.conf import settings


API_URL = "https://api.smsmobileapi.com/sendsms/"


def send_sms(phone_number, message):

    data = {
        "apikey": settings.SMS_API_KEY,
        "recipients": phone_number,
        "message": message,
        "sendsms": "1",
    }

    try:

        response = requests.post(
            API_URL,
            data=data,
            timeout=30
        )

        return response.json()

    except requests.RequestException as e:

        return {
            "error": 1,
            "message": str(e)
        }