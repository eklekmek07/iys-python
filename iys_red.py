from requests import session
from json import loads as json_loads, dumps as json_dumps
from time import sleep

SLEEP_DURATION = 1

SMS_VERIFICATION_URL = "https://vatandas.iys.org.tr/api/v1/cbff/recipients"
LOGIN_URL = "https://giris.iys.org.tr/auth/realms/citizen/protocol/openid-connect/token"
BRAND_LIST_URL = "https://vatandas.iys.org.tr/api/v1/cgw/recipients/BIREYSEL/brands/search/"


# Session object
s = session()

# Get sms verification code
phone_number = input("Telefon numarası=> ")
payload = {"recipient": phone_number}
sms_verification_response = s.post(SMS_VERIFICATION_URL, data=payload)
oid = json_loads(sms_verification_response.content.decode())["payload"]["id"]

# Get token with sms verification code
sms_code = input("Sms kodu=> ")
payload = {
    "client_id": "e-devlet",
    "grant_type": "password",
    "recipient": phone_number,
    "oid": oid,
    "code": sms_code
}
login_response = s.post(LOGIN_URL, data=payload)
token = json_loads(login_response.content)["access_token"]

# Get brand list
headers = {'Authorization': f'Bearer {token}'}
payload = json_dumps({"recipient": phone_number})
list_response = s.post(BRAND_LIST_URL, headers=headers, data=payload)
brand_list = json_loads(list_response.content)["list"]

headers = {
  'Authorization': f'Bearer {token}',
  'Content-Type': 'application/json'
}
for brand in brand_list:
    if brand["status"] == "ONAY":
        update_url = f"https://vatandas.iys.org.tr/api/v1/cgw/recipients/BIREYSEL/brands/{brand['brandCode']}/consent/update"
        payload = json_dumps({
            "recipient": phone_number,
            "status": "RET",
            "type": brand["type"]
            })
        response = s.request("POST", update_url, headers=headers, data=payload)
        sleep(SLEEP_DURATION)
        if response.status_code != 200:
            print("Error with the transaction")
            break
        print(brand["brandName"], brand["type"], "RET")