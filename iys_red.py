import requests
from json import loads as json_loads, dumps as json_dumps
from time import sleep

SMS_VERIFICATION_URL = "https://vatandas.iys.org.tr/api/v1/cbff/recipients"
LOGIN_URL = "https://giris.iys.org.tr/auth/realms/citizen/protocol/openid-connect/token"
BRAND_LIST_URL = "https://vatandas.iys.org.tr/api/v1/cgw/recipients/BIREYSEL/brands/search/"

generic_try_again_error_msg = 'Beklenmeyen bir hata oluştu, lütfen kısa bir süre içerisinde tekrar deneyiniz.'

phone_number = input("Telefon numarası=> ")
s = requests.session()

# Get sms verification code
payload = {"recipient": phone_number}
sms_verification_response = s.post(SMS_VERIFICATION_URL, data=payload)
try:
    #if json_loads(sms_verification_response.content)["error"]["summary"] == generic_try_again_error_msg:
    print(json_loads(sms_verification_response.content)["error"]["summary"])
    print("Lütfen 1 dakika bekleyin..")
except KeyError:
    oid = json_loads(sms_verification_response.content.decode())["payload"]["id"]

# Get token with sms verification code
sms_code = input("Sms kodu=> ")
login_response = s.post(LOGIN_URL, data= {
    "client_id": "e-devlet",
    "grant_type": "password",
    "recipient": phone_number,
    "oid": oid,
    "code": sms_code
})
token = json_loads(login_response.content)["access_token"]

# Authorizated header
headers = {'Authorization': f'Bearer {token}',}

# Get brand list
payload = json_dumps({"recipient": phone_number})
list_response = s.post(BRAND_LIST_URL, headers=headers, data=payload)
brand_list = json_loads(list_response.content)["list"]

headers = {
  'Authorization': f'Bearer {token}',
  'Connection': 'keep-alive',
  'Content-Type': 'application/json',
  'DNT': '1',
  'Origin': 'https://vatandas.iys.org.tr',
  'Referer': 'https://vatandas.iys.org.tr/izinlerim/onay-ret',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-GPC': '1',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"'
}
for brand in brand_list:
    reach_type = brand["type"]
    brand_code = brand["brandCode"]
    if brand["status"] == "ONAY":
        url = f"https://vatandas.iys.org.tr/api/v1/cgw/recipients/BIREYSEL/brands/{brand_code}/consent/update"
        payload = json_dumps({
            "recipient": phone_number,
            "status": "RET",
            "type": reach_type
            })
        response = s.request("POST", url, headers=headers, data=payload)
        sleep(3)
        if response.status_code != 200:
            print("Error with the transaction")
            break
        print(brand["brandCode"],brand["brandName"], brand["type"], "RET")
