import requests

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Test Android SMS Gateway"

    def handle(self, *args, **options):

        url = "https://api.smsmobileapi.com/sendsms/"

        api_key = settings.SMS_API_KEY

        if not api_key:
            self.stdout.write(
                self.style.ERROR(
                    "SMS_API_KEY haijawekwa kwenye .env"
                )
            )
            return

        recipient = input(
            "Ingiza namba ya simu: "
        ).strip()

        message = input(
            "Ingiza ujumbe: "
        ).strip()

        if recipient.startswith("0"):
            recipient = "+255" + recipient[1:]

        elif recipient.startswith("255"):
            recipient = "+" + recipient

        data = {
            "apikey": api_key,
            "recipients": recipient,
            "message": message,
        }

        self.stdout.write(
            f"Sending SMS to {recipient}..."
        )

        try:

            response = requests.post(
                url,
                data=data,
                timeout=30
            )

            self.stdout.write(
                f"HTTP Status: {response.status_code}"
            )

            self.stdout.write(
                f"Response: {response.text}"
            )

        except Exception as e:

            self.stdout.write(
                self.style.ERROR(
                    f"Error: {e}"
                )
            )