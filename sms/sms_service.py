import os
import requests
from dotenv import load_dotenv


# =========================================================
# LOAD .ENV
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)


# =========================================================
# TEXTBEE SETTINGS
# =========================================================

TEXTBEE_API_KEY = os.getenv("TEXTBEE_API_KEY")
TEXTBEE_DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID")

TEXTBEE_URL = "https://api.textbee.dev/api/v1/gateway/send-sms"


# =========================================================
# NORMALIZE PHONE NUMBER
# =========================================================

def normalize_tanzania_number(phone):

    phone = str(phone).strip()

    # +255698162036
    if phone.startswith("+255"):
        return phone

    # 255698162036
    if phone.startswith("255"):
        return "+" + phone

    # 0698162036
    if phone.startswith("0"):
        return "+255" + phone[1:]

    return phone


# =========================================================
# SEND SMS
# =========================================================

def send_sms_api(recipients, message):

    print("\n========== TEXTBEE ==========")

    # -----------------------------------------------------
    # API KEY
    # -----------------------------------------------------

    if not TEXTBEE_API_KEY:

        return {
            "success": False,
            "error": "TEXTBEE_API_KEY haijawekwa kwenye .env"
        }

    # -----------------------------------------------------
    # DEVICE ID
    # -----------------------------------------------------

    if not TEXTBEE_DEVICE_ID:

        return {
            "success": False,
            "error": "TEXTBEE_DEVICE_ID haijawekwa kwenye .env"
        }

    # =====================================================
    # MUHIMU:
    # Kama recipient ni STRING moja, iweke ndani ya LIST
    # =====================================================

    if isinstance(recipients, str):

        recipients = [recipients]

    else:

        recipients = list(recipients)


    # =====================================================
    # NORMALIZE NUMBERS
    # =====================================================

    normalized_recipients = []

    for phone in recipients:

        if not phone:
            continue

        phone = normalize_tanzania_number(phone)

        normalized_recipients.append(phone)


    # =====================================================
    # PRINT FOR DEBUGGING
    # =====================================================

    print("RECIPIENTS:", normalized_recipients)

    print("MESSAGE:", message)

    print("DEVICE ID EXISTS:", bool(TEXTBEE_DEVICE_ID))

    print("=============================")


    # =====================================================
    # CHECK RECIPIENTS
    # =====================================================

    if not normalized_recipients:

        return {
            "success": False,
            "error": "Hakuna namba ya simu iliyopatikana."
        }


    # =====================================================
    # HEADERS
    # =====================================================

    headers = {

        "x-api-key": TEXTBEE_API_KEY,

        "Content-Type": "application/json",

    }


    # =====================================================
    # PAYLOAD
    # =====================================================

    payload = {

        "recipients": normalized_recipients,

        "message": message,

        "deviceId": TEXTBEE_DEVICE_ID,

    }


    print("\n🔥 SENDING TO TEXTBEE...")

    print("PAYLOAD RECIPIENTS:", normalized_recipients)


    # =====================================================
    # SEND REQUEST
    # =====================================================

    try:

        response = requests.post(

            TEXTBEE_URL,

            json=payload,

            headers=headers,

            timeout=30,

        )


        print("\n========== TEXTBEE RESPONSE ==========")

        print("STATUS:", response.status_code)

        print("RESPONSE:", response.text)

        print("======================================\n")


        # =================================================
        # JSON RESPONSE
        # =================================================

        try:

            data = response.json()

        except ValueError:

            data = {
                "raw_response": response.text
            }


        # =================================================
        # SUCCESS
        # =================================================

        if response.ok:

            return {

                "success": True,

                "status_code": response.status_code,

                "data": data,

            }


        # =================================================
        # FAILED
        # =================================================

        return {

            "success": False,

            "status_code": response.status_code,

            "error": data,

        }


    except requests.RequestException as e:

        print("🔥 TEXTBEE REQUEST ERROR:", str(e))

        return {

            "success": False,

            "error": str(e),

        }