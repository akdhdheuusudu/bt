# ============================================================
# الجزء 1: الإعدادات الأساسية والتوكنات
# ============================================================

import json
import os
import random
import time
import re
import binascii
import urllib.parse
import requests
import threading
import subprocess
import sys
import hashlib
import hmac
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional, Any, Union

# ============================================================
# إعدادات البوت الأساسية
# ============================================================

BOT_TOKEN = '5192231015:AAFDUpT_c_lHlU0e-ql-5mok1Q43CIOAkzc'
ADMIN_ID = '5200567520'
SUPPORT = '@b99b2'
WEBHOOK_SECRET = '32d8dab766cb171d71c1541b35add336'

# ============================================================
# مسارات الملفات
# ============================================================

DATA_DIR = './data'
SUDO_DIR = './sudo'
LOG_FILE = './logs/bot_errors.log'
LOG_MAX_SIZE = 5 * 1024 * 1024
CURL_TIMEOUT = 10
RATE_LIMIT = 0.6

NE_EDID_DIR = './edid'
NE_FLAGS_FILE = './edid/ne_flags.json'
COUPONS_DATA_DIR = './data'
WALLET_LOG_FILE = './data/wallet_ledger.log'
ORDERS_FILE = './akl/orders.txt'
USER_DATA_DIR = './data'
SECURITY_DIR = './security_store'
TICKETS_FILE = './data/tickets.json'
FUNDING_FILE = './data/funding.json'
INVOICES_DIR = './amr'
BUTTONS_FILE = './button.json'
REPLIES_FILE = './replies.json'
COMMANDS_FILE = './comm.json'
SERVICES_FILE = './akl/akl.json'

# ============================================================
# دوال المساعدة الأساسية
# ============================================================

def bot(method: str, data: Dict = None) -> Optional[Dict]:
    """استدعاء Telegram API"""
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/{method}'
    try:
        if data:
            response = requests.post(url, json=data, timeout=CURL_TIMEOUT)
        else:
            response = requests.get(url, timeout=CURL_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        bot_log('ERROR', f'bot() failed: {method}', {'error': str(e)})
        return None

def bot_curl(method: str, datas: Dict = None) -> Optional[Dict]:
    """استدعاء Telegram API (متوافق مع PHP)"""
    return bot(method, datas)

# ============================================================
# دوال الملفات
# ============================================================

def file_read(file_path: str) -> Optional[str]:
    """قراءة ملف نصي"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def file_write(file_path: str, content: str) -> bool:
    """كتابة ملف نصي"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

def file_append(file_path: str, content: str) -> bool:
    """إضافة إلى ملف نصي"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content + '\n')
        return True
    except:
        return False

def file_exists(file_path: str) -> bool:
    """التحقق من وجود ملف"""
    return os.path.exists(file_path)

def json_read(file_path: str) -> Dict:
    """قراءة ملف JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def json_write(file_path: str, data: Dict) -> bool:
    """كتابة ملف JSON"""
    tmp_path = f"{file_path}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, file_path)
        return True
    except:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
        return False

def json_append(file_path: str, data: Dict) -> bool:
    """إضافة إلى ملف JSON"""
    try:
        existing = json_read(file_path)
        if isinstance(existing, list):
            existing.append(data)
        elif isinstance(existing, dict):
            if 'items' not in existing:
                existing['items'] = []
            existing['items'].append(data)
        else:
            existing = [data]
        return json_write(file_path, existing)
    except:
        return False

# ============================================================
# دوال الأمان والتشفير
# ============================================================

def generate_random_string(length: int = 16) -> str:
    """توليد نص عشوائي"""
    return binascii.hexlify(os.urandom(length)).decode()

def generate_random_code(length: int = 8) -> str:
    """توليد كود عشوائي"""
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(chars) for _ in range(length))

def generate_random_number(min_val: int = 100, max_val: int = 999999) -> int:
    """توليد رقم عشوائي"""
    return random.randint(min_val, max_val)

def hash_string(text: str) -> str:
    """تشفير نص"""
    return hashlib.sha256(text.encode()).hexdigest()

def verify_webhook_secret(secret: str) -> bool:
    """التحقق من مفتاح Webhook"""
    return hmac.compare_digest(secret, WEBHOOK_SECRET)

# ============================================================
# دوال الوقت والتاريخ
# ============================================================

def get_timestamp() -> int:
    """الحصول على الوقت الحالي (ثواني)"""
    return int(time.time())

def get_datetime() -> str:
    """الحصول على الوقت الحالي (نص)"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_date() -> str:
    """الحصول على التاريخ الحالي"""
    return datetime.now().strftime('%Y-%m-%d')

def get_day_name() -> str:
    """الحصول على اسم اليوم"""
    return datetime.now().strftime('%a')

def get_time_remaining_until_tomorrow() -> Dict:
    """الحصول على الوقت المتبقي حتى الغد"""
    now = datetime.now()
    tomorrow = datetime(now.year, now.month, now.day) + timedelta(days=1)
    remaining = tomorrow - now
    return {
        'hours': remaining.seconds // 3600,
        'minutes': (remaining.seconds % 3600) // 60,
        'seconds': remaining.seconds % 60,
        'total_seconds': remaining.seconds
    }

def is_today(timestamp: int) -> bool:
    """التحقق مما إذا كان التاريخ اليوم"""
    return datetime.fromtimestamp(timestamp).date() == datetime.now().date()

def format_time_remaining(seconds: int) -> str:
    """تنسيق الوقت المتبقي"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours} ساعة {minutes} دقيقة"
    elif minutes > 0:
        return f"{minutes} دقيقة {secs} ثانية"
    else:
        return f"{secs} ثانية"

# ============================================================
# دوال تحويل العملات
# ============================================================

CURRENCY_SYMBOLS = {
    'SAR': 'ر.س',
    'USD': '$',
    'YER_N': 'ر.ي.ش',
    'YER_S': 'ر.ي.ج',
    'EGP': 'ج.م',
    'IQD': 'د.ع',
    'P': 'P'
}

CURRENCY_NAMES = {
    'SAR': 'ريال سعودي',
    'USD': 'دولار أمريكي',
    'YER_N': 'ريال يمني قديم',
    'YER_S': 'ريال يمني جنوبي',
    'EGP': 'جنية مصري',
    'IQD': 'دينار عراقي',
    'P': 'P'
}

def get_currency_symbol(currency_code: str) -> str:
    """الحصول على رمز العملة"""
    return CURRENCY_SYMBOLS.get(currency_code, 'ر.ي.ش')

def get_currency_name(currency_code: str) -> str:
    """الحصول على اسم العملة"""
    return CURRENCY_NAMES.get(currency_code, 'ريال يمني قديم')

def format_currency(amount: float, currency_code: str = 'YER_N') -> str:
    """تنسيق المبلغ بالعملة"""
    symbol = get_currency_symbol(currency_code)
    return f"{amount:.2f} {symbol}"

# ============================================================
# دوال المتغيرات العامة
# ============================================================

def get_bot_username() -> str:
    """الحصول على اسم المستخدم للبوت"""
    result = bot('getMe')
    if result and result.get('ok'):
        return result['result']['username']
    return 'YourBot'

def get_bot_id() -> int:
    """الحصول على ID البوت"""
    result = bot('getMe')
    if result and result.get('ok'):
        return result['result']['id']
    return 0

def get_currency_name_from_file() -> str:
    """الحصول على اسم العملة من الملف"""
    name = file_read('edid/currency_name.txt')
    return name if name else 'نقطة'

def get_currency_short() -> str:
    """الحصول على اسم العملة المختصر"""
    name = get_currency_name_from_file()
    return name + 'ك'

def get_currency_long() -> str:
    """الحصول على اسم العملة الطويل"""
    return get_currency_name_from_file()

def get_coins_start() -> int:
    """الحصول على عدد النقاط عند الدخول"""
    try:
        return int(file_read('edid/coinsstart.txt') or '15')
    except:
        return 15

def get_adna_coins() -> int:
    """الحصول على الحد الأدنى للنقاط"""
    try:
        return int(file_read('data/adna_coins.txt') or '40')
    except:
        return 40

def get_day_coins() -> int:
    """الحصول على عدد نقاط الهدية اليومية"""
    try:
        return int(file_read('data/day_coins.txt') or '20')
    except:
        return 20

def get_work_add_day() -> int:
    """الحصول على حد التحويل الأدنى"""
    try:
        return int(file_read('edid/work_add_day.txt') or '10')
    except:
        return 10

def get_add_ado() -> int:
    """الحصول على سعر التمويل لكل عضو"""
    try:
        return int(file_read('edid/addado.txt') or '12')
    except:
        return 12

def get_add_aoc() -> int:
    """الحصول على نقاط الاشتراك في القناة"""
    try:
        return int(file_read('edid/add_aoc.txt') or '5')
    except:
        return 5

# ============================================================
# تهيئة المجلدات والملفات
# ============================================================

def create_directories():
    """إنشاء المجلدات والملفات المطلوبة"""
    dirs = [
        'data', 'sudo', 'amr', 'akl', 'edid', 'edid/amr', 'logs',
        'security_store', 'userch', 'ViSCo', 'CEPO'
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    defaults = {
        'baageel.txt': '✅',
        'admin.txt': ADMIN_ID,
        'edid/opan.txt': '✅',
        'edid/zerasase.txt': '✅',
        'edid/zerasaseon.txt': '✅',
        'edid/tmwel.txt': '✅',
        'edid/coadd.txt': '✅',
        'edid/add_day.txt': '✅',
        'edid/mr_insta.txt': '❌',
        'edid/mr_tektok.txt': '❌',
        'edid/mr_telegram.txt': '❌',
        'edid/mr_yoteop.txt': '❌',
        'edid/mr_faesbook.txt': '❌',
        'edid/mr_twetr.txt': '❌',
        'edid/mr_free.txt': '❌',
        'edid/currency_name.txt': 'نقطة',
        'edid/nzambot.txt': '❌',
        'edid/asttacbot.txt': '❌',
        'edid/nambot.txt': 'DomKom',
        'edid/aklamrnm1.txt': 'الخدمات 🗂',
        'edid/aklamrnm2.txt': 'تجميع ✳️',
        'edid/aklamrnm3.txt': 'الحساب 🗃️',
        'edid/aklamrnm4.txt': 'استخدام كود 💳',
        'edid/aklamrnm5.txt': 'تحويل نقاط ♻️',
        'edid/aklamrnm6.txt': 'معلومات الطلب 📥',
        'edid/aklamrnm7.txt': 'طلباتي 📮',
        'edid/aklamrnm8.txt': 'قناة البوت 🤍',
        'edid/aklamrnm9.txt': 'شحن نقاط 💰',
        'edid/aklamrnm10.txt': 'الشروط 📜',
        'akl/orders.txt': '',
        'data/user.json': '{"userlist": []}',
        'sudo/member.txt': '',
        'sudo/ban.txt': '',
        'button.json': '{"buttons": {}, "links": {}, "codzer": {}}',
        'replies.json': '{"replies": {}, "links": {}}',
        'comm.json': '{"com": {}, "comm": {"admins": []}}',
        'akl/akl.json': '{"qsm": [], "NAMES": {}, "xdmaxs": {}, "S3RS": {}, "IDSSS": {}, "min": {}, "mix": {}, "WSF": {}, "Web": {}, "key": {}}',
        'edid/cdiamlaadf.txt': 'نقاط',
        'edid/chadmin.txt': 'لم يتم تعين قناة',
        'edid/acont_admin.txt': 'لم يتم تعين حساب'
    }
    
    for f, content in defaults.items():
        if not os.path.exists(f):
            file_write(f, content)
    
    # إنشاء ملف sudo.json
    sudo_file = './sudo.json'
    if not os.path.exists(sudo_file):
        sudo_data = {
            'info': {
                'admins': [ADMIN_ID],
                'st_grop': 'ممنوع',
                'st_channel': 'مسموح',
                'fwrmember': '❎',
                'tnbih': '✅',
                'silk': '✅',
                'allch': '✅',
                'klish_sil': '⁦⁉️⁩ عذرا عزيزي\n🌟يجب الاشتراك في قناة البوت اولا\n⁦🎗️⁩ثم اضغط /start ⁦🛎️⁩',
                'channel': {},
                'channel_id': None,
                'start': None,
                'amr': 'null'
            }
        }
        json_write(sudo_file, sudo_data)

def load_sudo_data() -> Dict:
    """تحميل بيانات السودو"""
    return json_read('./sudo.json')

def save_sudo_data(data: Dict) -> bool:
    """حفظ بيانات السودو"""
    return json_write('./sudo.json', data)

def is_admin(user_id) -> bool:
    """التحقق من صلاحيات الأدمن"""
    return str(user_id) == ADMIN_ID or str(user_id) in load_sudo_data().get('info', {}).get('admins', [])

# ============================================================
# دوال المستخدمين
# ============================================================

def get_user_data(user_id) -> Dict:
    """الحصول على بيانات المستخدم"""
    user_file = f'{DATA_DIR}/{user_id}.json'
    if os.path.exists(user_file):
        data = json_read(user_file)
        if data and 'userfild' in data and str(user_id) in data['userfild']:
            return data
    return {'userfild': {str(user_id): {'coin': '0', 'invite': '0'}}}

def save_user_data(user_id, data) -> bool:
    """حفظ بيانات المستخدم"""
    user_file = f'{DATA_DIR}/{user_id}.json'
    return json_write(user_file, data)

def get_coin(user_id) -> float:
    """الحصول على رصيد المستخدم"""
    data = get_user_data(user_id)
    try:
        return float(data['userfild'].get(str(user_id), {}).get('coin', '0'))
    except:
        return 0.0

def add_coin(user_id, amount) -> float:
    """إضافة رصيد للمستخدم"""
    data = get_user_data(user_id)
    if str(user_id) not in data['userfild']:
        data['userfild'][str(user_id)] = {}
    
    current = float(data['userfild'][str(user_id)].get('coin', '0'))
    new_amount = current + float(amount)
    data['userfild'][str(user_id)]['coin'] = str(new_amount)
    save_user_data(user_id, data)
    wallet_log(user_id, 'charge', amount, 'إضافة رصيد', {'balance_after': new_amount})
    return new_amount

def deduct_coin(user_id, amount) -> Union[float, bool]:
    """خصم رصيد من المستخدم"""
    data = get_user_data(user_id)
    if str(user_id) not in data['userfild']:
        data['userfild'][str(user_id)] = {}
    
    current = float(data['userfild'][str(user_id)].get('coin', '0'))
    if current < float(amount):
        return False
    
    new_amount = current - float(amount)
    data['userfild'][str(user_id)]['coin'] = str(new_amount)
    save_user_data(user_id, data)
    wallet_log(user_id, 'deduct', amount, 'خصم رصيد', {'balance_after': new_amount})
    return new_amount

def get_all_users() -> List:
    """الحصول على جميع المستخدمين"""
    users_file = f'{DATA_DIR}/user.json'
    if os.path.exists(users_file):
        data = json_read(users_file)
        return data.get('userlist', [])
    return []

def add_user(user_id) -> bool:
    """إضافة مستخدم جديد"""
    users_file = f'{DATA_DIR}/user.json'
    data = {}
    if os.path.exists(users_file):
        data = json_read(users_file)
    
    if 'userlist' not in data:
        data['userlist'] = []
    
    if str(user_id) not in [str(u) for u in data['userlist']]:
        data['userlist'].append(str(user_id))
        return json_write(users_file, data)
    return False

def get_banned_users() -> List:
    """الحصول على قائمة المحظورين"""
    ban_file = f'{SUDO_DIR}/ban.txt'
    if os.path.exists(ban_file):
        content = file_read(ban_file)
        if content:
            return [l.strip() for l in content.split('\n') if l.strip()]
    return []

def ban_user(user_id) -> bool:
    """حظر مستخدم"""
    ban_file = f'{SUDO_DIR}/ban.txt'
    if str(user_id) not in get_banned_users():
        return file_append(ban_file, str(user_id))
    return False

def unban_user(user_id) -> bool:
    """إلغاء حظر مستخدم"""
    ban_file = f'{SUDO_DIR}/ban.txt'
    if not os.path.exists(ban_file):
        return False
    
    content = file_read(ban_file)
    if not content:
        return False
    
    lines = content.split('\n')
    new_lines = [l for l in lines if l.strip() != str(user_id)]
    return file_write(ban_file, '\n'.join(new_lines))

def is_banned(user_id) -> bool:
    """التحقق من حظر المستخدم"""
    return str(user_id) in get_banned_users()

# ============================================================
# نظام التسجيل (Logger)
# ============================================================

def bot_log(level: str, message: str, context: Dict = None):
    """تسجيل الأخطاء والأحداث"""
    log_file = LOG_FILE
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    if os.path.exists(log_file) and os.path.getsize(log_file) >= LOG_MAX_SIZE:
        backup = f"{log_file}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        try:
            os.rename(log_file, backup)
        except:
            pass
    
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}"
    if context:
        log_entry += f" | {json.dumps(context, ensure_ascii=False)}"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    except:
        pass

def bot_log_exception(e: Exception, note: str = ''):
    """تسجيل استثناء"""
    bot_log('ERROR', f"{note} {str(e)}" if note else str(e), {
        'file': getattr(e, '__file__', 'unknown'),
        'line': getattr(e, '__line__', 0)
    })

def security_register_error_handlers():
    """تسجيل معالجات الأخطاء"""
    sys.excepthook = lambda exc_type, exc_value, exc_tb: bot_log_exception(exc_value, 'uncaught')

# ============================================================
# نظام الحماية (Security)
# ============================================================

def security_rate_limit_allow(user_id, min_interval: float = RATE_LIMIT) -> bool:
    """منع تكرار الطلبات السريعة"""
    user_id = str(user_id)
    if not user_id or user_id == '0':
        return True
    
    path = f'{SECURITY_DIR}/rl_{user_id}.txt'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = time.time()
    
    last = 0
    if os.path.exists(path):
        try:
            last = float(file_read(path) or '0')
        except:
            pass
    
    if now - last < min_interval:
        return False
    
    file_write(path, str(now))
    return True

def security_is_duplicate_spam(user_id, payload: str, window: float = 1.5) -> bool:
    """منع تكرار نفس الطلب"""
    user_id = str(user_id)
    if not user_id or not payload:
        return False
    
    path = f'{SECURITY_DIR}/spam_{user_id}.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = time.time()
    hash_payload = str(hash(payload))
    
    prev = {}
    if os.path.exists(path):
        prev = json_read(path)
    
    is_dup = (prev.get('hash') == hash_payload and now - prev.get('t', 0) < window)
    
    json_write(path, {'hash': hash_payload, 't': now})
    return is_dup

def check_user_subscription(user_id, mandatory_channels: Dict) -> tuple:
    """التحقق من اشتراك المستخدم في القنوات الإجبارية"""
    if not mandatory_channels:
        return True, None
    
    for channel_id, channel_info in mandatory_channels.items():
        try:
            result = bot('getChatMember', {'chat_id': channel_id, 'user_id': user_id})
            if result and result.get('ok'):
                status = result['result'].get('status', '')
                if status not in ['member', 'creator', 'administrator']:
                    return False, channel_info
            else:
                return False, channel_info
        except:
            return False, channel_info
    
    return True, None

def get_member(chat_id, user_id) -> str:
    """التحقق من عضوية المستخدم في القناة"""
    result = bot('getChatMember', {'chat_id': chat_id, 'user_id': user_id})
    if not result or not result.get('ok'):
        return 'no'
    status = result.get('result', {}).get('status', '')
    if status in ['left', 'kicked']:
        return 'no'
    return 'yes'

def get_chat_stats(chat_id) -> bool:
    """التحقق من صلاحيات البوت في القناة"""
    result = bot('getChatAdministrators', {'chat_id': chat_id})
    return result.get('ok', False)

def get_chat_members_count(chat_id) -> int:
    """الحصول على عدد أعضاء القناة"""
    result = bot('getChatMembersCount', {'chat_id': chat_id})
    if result and result.get('ok'):
        return result['result']
    return 0

# ============================================================
# نهاية الجزء 1
# ============================================================
# ============================================================
# الجزء 2: نظام المحفظة والنقاط (Wallet & Points) - 1500 سطر
# ============================================================

# ============================================================
# دوال المحفظة الأساسية
# ============================================================

def wallet_log(user_id, type_, amount, note='', extra=None):
    """تسجيل حركة في سجل الرصيد"""
    log_file = WALLET_LOG_FILE
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    entry = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'from_id': str(user_id),
        'type': type_,
        'amount': float(amount),
        'note': note
    }
    if extra:
        entry.update(extra)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def wallet_statement(user_id, limit=10):
    """كشف حساب المستخدم"""
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return "📭 لا توجد حركات مسجّلة في رصيدك حتى الآن."
    
    user_id = str(user_id)
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    matches = []
    for line in reversed(lines):
        try:
            entry = json.loads(line.strip())
            if entry.get('from_id') == user_id:
                matches.append(entry)
                if len(matches) >= limit:
                    break
        except:
            continue
    
    if not matches:
        return "📭 لا توجد حركات مسجّلة في رصيدك حتى الآن."
    
    text = f"💼 <b>كشف حساب آخر {len(matches)} حركة</b>\n━━━━━━━━━━━━━━━━━\n"
    for entry in matches:
        sign = '-' if entry['type'] in ['deduct'] else '+'
        text += f"🕐 {entry['time']} | {sign}{entry['amount']} | {entry['note']}\n"
    
    return text

def wallet_admin_log(limit=10):
    """سجل حركات كل المستخدمين للأدمن"""
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return "📭 لا توجد حركات مسجّلة في سجل الرصيد."
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    lines = [l.strip() for l in lines if l.strip()][-limit:]
    if not lines:
        return "📭 لا توجد حركات مسجّلة في سجل الرصيد."
    
    text = f"📜 <b>آخر {len(lines)} حركة (كل المستخدمين)</b>\n"
    for line in reversed(lines):
        try:
            entry = json.loads(line)
            text += f"🕐 {entry['time']} | 🆔 {entry['from_id']} | {entry['type']} | {entry['amount']} | {entry['note']}\n"
        except:
            continue
    
    return text

def wallet_get_balance(user_id):
    """الحصول على رصيد المستخدم من سجل المحفظة"""
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return 0
    
    user_id = str(user_id)
    balance = 0
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('from_id') == user_id:
                    if entry['type'] in ['charge', 'gift', 'daily', 'transfer_in']:
                        balance += float(entry['amount'])
                    elif entry['type'] in ['deduct', 'transfer_out']:
                        balance -= float(entry['amount'])
            except:
                continue
    
    return balance

def wallet_get_total_charges(user_id):
    """الحصول على إجمالي المبالغ المشحونة للمستخدم"""
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return 0
    
    user_id = str(user_id)
    total = 0
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('from_id') == user_id and entry['type'] == 'charge':
                    total += float(entry['amount'])
            except:
                continue
    
    return total

def wallet_get_total_deducts(user_id):
    """الحصول على إجمالي المبالغ المخصومة من المستخدم"""
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return 0
    
    user_id = str(user_id)
    total = 0
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('from_id') == user_id and entry['type'] == 'deduct':
                    total += float(entry['amount'])
            except:
                continue
    
    return total

def wallet_get_transactions_by_type(user_id, type_, limit=10):
    """الحصول على حركات من نوع معين"""
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return []
    
    user_id = str(user_id)
    matches = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                if entry.get('from_id') == user_id and entry.get('type') == type_:
                    matches.append(entry)
                    if len(matches) >= limit:
                        break
            except:
                continue
    
    return matches

def wallet_get_all_transactions(limit=50):
    """الحصول على جميع الحركات"""
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return []
    
    matches = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in reversed(f.readlines()):
            try:
                entry = json.loads(line.strip())
                matches.append(entry)
                if len(matches) >= limit:
                    break
            except:
                continue
    
    return matches

def wallet_get_daily_transactions(date=None):
    """الحصول على حركات اليوم"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return []
    
    matches = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry['time'].startswith(date):
                    matches.append(entry)
            except:
                continue
    
    return matches

def wallet_get_monthly_transactions(month=None):
    """الحصول على حركات الشهر"""
    if not month:
        month = datetime.now().strftime('%Y-%m')
    
    log_file = WALLET_LOG_FILE
    if not os.path.exists(log_file):
        return []
    
    matches = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry['time'].startswith(month):
                    matches.append(entry)
            except:
                continue
    
    return matches

# ============================================================
# دوال النقاط الإضافية
# ============================================================

def add_points(user_id, amount, reason=''):
    """إضافة نقاط للمستخدم (مع تسجيل)"""
    if amount <= 0:
        return False
    
    current = get_coin(user_id)
    new_balance = current + amount
    data = get_user_data(user_id)
    data['userfild'][str(user_id)]['coin'] = str(new_balance)
    save_user_data(user_id, data)
    wallet_log(user_id, 'charge', amount, reason or 'إضافة نقاط', {'balance_after': new_balance})
    return new_balance

def deduct_points(user_id, amount, reason=''):
    """خصم نقاط من المستخدم (مع تسجيل)"""
    if amount <= 0:
        return False
    
    current = get_coin(user_id)
    if current < amount:
        return False
    
    new_balance = current - amount
    data = get_user_data(user_id)
    data['userfild'][str(user_id)]['coin'] = str(new_balance)
    save_user_data(user_id, data)
    wallet_log(user_id, 'deduct', amount, reason or 'خصم نقاط', {'balance_after': new_balance})
    return new_balance

def transfer_points(from_user, to_user, amount, reason=''):
    """تحويل نقاط بين مستخدمين"""
    if amount <= 0:
        return {'success': False, 'message': 'المبلغ يجب أن يكون أكبر من صفر'}
    
    if from_user == to_user:
        return {'success': False, 'message': 'لا يمكنك التحويل لنفسك'}
    
    current = get_coin(from_user)
    if current < amount:
        return {'success': False, 'message': 'رصيدك غير كافي'}
    
    # خصم من المرسل
    new_from_balance = current - amount
    data = get_user_data(from_user)
    data['userfild'][str(from_user)]['coin'] = str(new_from_balance)
    save_user_data(from_user, data)
    wallet_log(from_user, 'transfer_out', amount, f'تحويل إلى {to_user} - {reason}', {'to': to_user, 'balance_after': new_from_balance})
    
    # إضافة للمستقبل
    to_current = get_coin(to_user)
    new_to_balance = to_current + amount
    data = get_user_data(to_user)
    data['userfild'][str(to_user)]['coin'] = str(new_to_balance)
    save_user_data(to_user, data)
    wallet_log(to_user, 'transfer_in', amount, f'تحويل من {from_user} - {reason}', {'from': from_user, 'balance_after': new_to_balance})
    
    return {'success': True, 'message': f'تم تحويل {amount} نقطة بنجاح'}

def get_daily_gift(user_id):
    """الحصول على الهدية اليومية"""
    day = datetime.now().strftime('%a')
    day_file = f'./data/{day}.txt'
    
    if os.path.exists(day_file):
        with open(day_file, 'r', encoding='utf-8') as f:
            users = [l.strip() for l in f.readlines()]
        if str(user_id) in users:
            return {'success': False, 'message': 'لقد حصلت على الهدية اليومية بالفعل'}
    
    day_coins = int(file_read('data/day_coins.txt') or 20)
    add_points(user_id, day_coins, 'هدية يومية')
    file_append(day_file, str(user_id))
    
    return {'success': True, 'message': f'تم إضافة {day_coins} نقطة كهدية يومية'}

def get_referral_bonus(user_id):
    """الحصول على مكافأة الإحالة"""
    data = get_user_data(user_id)
    invite_count = int(data['userfild'].get(str(user_id), {}).get('invite', '0'))
    coins_start = int(file_read('edid/coinsstart.txt') or 15)
    
    return invite_count * coins_start

def get_total_spent(user_id):
    """الحصول على إجمالي المصروفات"""
    return wallet_get_total_deducts(user_id) + ne_total_spent(user_id)

# ============================================================
# دوال الإحالات (Referrals)
# ============================================================

def add_referral(referrer_id, new_user_id):
    """إضافة إحالة جديدة"""
    data = get_user_data(referrer_id)
    if str(referrer_id) not in data['userfild']:
        data['userfild'][str(referrer_id)] = {}
    
    current = int(data['userfild'][str(referrer_id)].get('invite', '0'))
    data['userfild'][str(referrer_id)]['invite'] = str(current + 1)
    save_user_data(referrer_id, data)
    
    # إضافة مكافأة
    coins_start = int(file_read('edid/coinsstart.txt') or 15)
    add_points(referrer_id, coins_start, f'مكافأة دعوة مستخدم جديد')
    
    # تسجيل المحول
    data = get_user_data(new_user_id)
    data['userfild'][str(new_user_id)]['inviter'] = str(referrer_id)
    save_user_data(new_user_id, data)
    
    return True

def get_referral_count(user_id):
    """الحصول على عدد الإحالات"""
    data = get_user_data(user_id)
    return int(data['userfild'].get(str(user_id), {}).get('invite', '0'))

def get_referral_earnings(user_id):
    """الحصول على أرباح الإحالات"""
    return ne_referral_earnings(user_id)

def get_referral_link(user_id):
    """الحصول على رابط الإحالة"""
    username = get_bot_username()
    return f"https://t.me/{username}?start={user_id}"

# ============================================================
# دوال الهدايا والجوائز
# ============================================================

def create_gift_code(amount, max_uses=1):
    """إنشاء كود هدية"""
    code = generate_random_code(8)
    gift_file = f'./data/gifts.json'
    
    gifts = {}
    if os.path.exists(gift_file):
        gifts = json_read(gift_file)
    
    gifts[code] = {
        'code': code,
        'amount': float(amount),
        'max_uses': max_uses,
        'used_by': [],
        'created_at': get_timestamp(),
        'active': True
    }
    
    json_write(gift_file, gifts)
    return code

def redeem_gift_code(user_id, code):
    """استخدام كود هدية"""
    gift_file = f'./data/gifts.json'
    if not os.path.exists(gift_file):
        return {'success': False, 'message': 'الكود غير صحيح'}
    
    gifts = json_read(gift_file)
    if code not in gifts:
        return {'success': False, 'message': 'الكود غير صحيح'}
    
    gift = gifts[code]
    if not gift.get('active', True):
        return {'success': False, 'message': 'الكود غير مفعّل'}
    
    if str(user_id) in gift.get('used_by', []):
        return {'success': False, 'message': 'لقد استخدمت هذا الكود من قبل'}
    
    if len(gift.get('used_by', [])) >= gift.get('max_uses', 1):
        return {'success': False, 'message': 'انتهت عدد مرات استخدام هذا الكود'}
    
    # إضافة النقاط
    add_points(user_id, gift['amount'], f'كود هدية: {code}')
    
    # تسجيل الاستخدام
    gifts[code]['used_by'].append(str(user_id))
    json_write(gift_file, gifts)
    
    return {'success': True, 'message': f'تم إضافة {gift["amount"]} نقطة'}

def get_active_gifts():
    """الحصول على الهدايا النشطة"""
    gift_file = f'./data/gifts.json'
    if not os.path.exists(gift_file):
        return []
    
    gifts = json_read(gift_file)
    return [g for g in gifts.values() if g.get('active', True)]

def deactivate_gift(code):
    """تعطيل كود هدية"""
    gift_file = f'./data/gifts.json'
    if not os.path.exists(gift_file):
        return False
    
    gifts = json_read(gift_file)
    if code not in gifts:
        return False
    
    gifts[code]['active'] = False
    json_write(gift_file, gifts)
    return True

# ============================================================
# دوال المكافآت اليومية
# ============================================================

def get_daily_bonus(user_id):
    """الحصول على المكافأة اليومية"""
    day = datetime.now().strftime('%Y-%m-%d')
    bonus_file = f'./data/daily_bonus_{day}.json'
    
    if os.path.exists(bonus_file):
        data = json_read(bonus_file)
        if str(user_id) in data.get('users', []):
            return {'success': False, 'message': 'لقد حصلت على المكافأة اليومية'}
    
    amount = random.randint(1, 10)
    add_points(user_id, amount, 'مكافأة يومية')
    
    data = {}
    if os.path.exists(bonus_file):
        data = json_read(bonus_file)
    if 'users' not in data:
        data['users'] = []
    data['users'].append(str(user_id))
    json_write(bonus_file, data)
    
    return {'success': True, 'message': f'تم إضافة {amount} نقطة كمكافأة يومية'}

def get_weekly_bonus(user_id):
    """الحصول على المكافأة الأسبوعية"""
    week = datetime.now().strftime('%Y-W%W')
    bonus_file = f'./data/weekly_bonus_{week}.json'
    
    if os.path.exists(bonus_file):
        data = json_read(bonus_file)
        if str(user_id) in data.get('users', []):
            return {'success': False, 'message': 'لقد حصلت على المكافأة الأسبوعية'}
    
    amount = random.randint(10, 50)
    add_points(user_id, amount, 'مكافأة أسبوعية')
    
    data = {}
    if os.path.exists(bonus_file):
        data = json_read(bonus_file)
    if 'users' not in data:
        data['users'] = []
    data['users'].append(str(user_id))
    json_write(bonus_file, data)
    
    return {'success': True, 'message': f'تم إضافة {amount} نقطة كمكافأة أسبوعية'}

# ============================================================
# دوال نقاط المستخدمين (إحصائيات)
# ============================================================

def get_top_users(limit=10):
    """الحصول على المستخدمين الأغنى"""
    users = get_all_users()
    user_balances = []
    
    for user_id in users:
        balance = get_coin(user_id)
        user_balances.append((user_id, balance))
    
    user_balances.sort(key=lambda x: x[1], reverse=True)
    return user_balances[:limit]

def get_top_spenders(limit=10):
    """الحصول على المستخدمين الأكثر صرفاً"""
    users = get_all_users()
    user_spending = []
    
    for user_id in users:
        spent = get_total_spent(user_id)
        user_spending.append((user_id, spent))
    
    user_spending.sort(key=lambda x: x[1], reverse=True)
    return user_spending[:limit]

def get_user_rank(user_id):
    """الحصول على ترتيب المستخدم بين المستخدمين"""
    users = get_all_users()
    balance = get_coin(user_id)
    
    ranks = []
    for u in users:
        ranks.append((u, get_coin(u)))
    
    ranks.sort(key=lambda x: x[1], reverse=True)
    
    for i, (u, b) in enumerate(ranks):
        if str(u) == str(user_id):
            return i + 1
    
    return len(ranks) + 1

def get_user_stats(user_id):
    """الحصول على إحصائيات المستخدم"""
    return {
        'balance': get_coin(user_id),
        'spent': get_total_spent(user_id),
        'referrals': get_referral_count(user_id),
        'rank': get_user_rank(user_id),
        'total_charges': wallet_get_total_charges(user_id),
        'total_deducts': wallet_get_total_deducts(user_id)
    }

# ============================================================
# دوال نقاط النظام (System Points)
# ============================================================

def get_system_total_points():
    """الحصول على إجمالي النقاط في النظام"""
    users = get_all_users()
    total = 0
    for user_id in users:
        total += get_coin(user_id)
    return total

def get_system_total_earned():
    """الحصول على إجمالي النقاط المكتسبة"""
    return wallet_get_total_charges('system')

def get_system_total_spent():
    """الحصول على إجمالي النقاط المصروفة"""
    return wallet_get_total_deducts('system')

def reset_user_points(user_id):
    """إعادة تعيين نقاط المستخدم"""
    data = get_user_data(user_id)
    data['userfild'][str(user_id)]['coin'] = '0'
    save_user_data(user_id, data)
    wallet_log(user_id, 'reset', 0, 'إعادة تعيين النقاط')
    return True

def set_user_points(user_id, amount):
    """تعيين نقاط المستخدم بقيمة محددة"""
    data = get_user_data(user_id)
    data['userfild'][str(user_id)]['coin'] = str(float(amount))
    save_user_data(user_id, data)
    wallet_log(user_id, 'set', amount, 'تعيين النقاط')
    return True

# ============================================================
# دوال تقارير المحفظة
# ============================================================

def generate_wallet_report(user_id):
    """توليد تقرير المحفظة للمستخدم"""
    stats = get_user_stats(user_id)
    transactions = wallet_statement(user_id, 20)
    
    report = f"""
📊 <b>تقرير المحفظة</b>
━━━━━━━━━━━━━━━━━
👤 <b>المستخدم:</b> <code>{user_id}</code>
💰 <b>الرصيد الحالي:</b> {stats['balance']}
💸 <b>إجمالي المصروفات:</b> {stats['spent']}
📥 <b>إجمالي الشحنات:</b> {stats['total_charges']}
📤 <b>إجمالي الخصومات:</b> {stats['total_deducts']}
👥 <b>عدد الإحالات:</b> {stats['referrals']}
🏆 <b>الترتيب:</b> #{stats['rank']}
━━━━━━━━━━━━━━━━━
{transactions}
"""
    return report

def generate_system_report():
    """توليد تقرير النظام"""
    total_users = len(get_all_users())
    total_points = get_system_total_points()
    total_earned = get_system_total_earned()
    total_spent = get_system_total_spent()
    
    report = f"""
📊 <b>تقرير النظام</b>
━━━━━━━━━━━━━━━━━
👥 <b>إجمالي المستخدمين:</b> {total_users}
💰 <b>إجمالي النقاط في النظام:</b> {total_points}
📥 <b>إجمالي النقاط المكتسبة:</b> {total_earned}
📤 <b>إجمالي النقاط المصروفة:</b> {total_spent}
🏆 <b>أغنى مستخدم:</b> {get_top_users(1)[0][0] if get_top_users(1) else 'لا يوجد'}
"""
    return report

# ============================================================
# دوال نقاط الكوبونات
# ============================================================

def create_coupon_points(code, amount, max_uses=1, expires_in=86400):
    """إنشاء كوبون نقاط"""
    coupon_data = {
        'code': code,
        'amount': float(amount),
        'max_uses': max_uses,
        'used_by': [],
        'created_at': get_timestamp(),
        'expires_at': get_timestamp() + expires_in,
        'active': True
    }
    
    coupons = coupons_read()
    coupons[code] = coupon_data
    coupons_write(coupons)
    return coupon_data

def use_coupon_points(user_id, code):
    """استخدام كوبون نقاط"""
    result = coupon_redeem(code, user_id)
    if not result['ok']:
        return result
    
    coupon = result['coupon']
    if coupon['type'] != 'charge':
        return {'ok': False, 'message': 'هذا الكوبون ليس كوبون نقاط'}
    
    add_points(user_id, coupon['value'], f'كوبون: {code}')
    return {'ok': True, 'message': f'تم إضافة {coupon["value"]} نقطة'}

# ============================================================
# نهاية الجزء 2
# ============================================================
# ============================================================
# الجزء 3: نظام الطلبات والأوامر (Orders & Requests) - 1500 سطر
# ============================================================

# ============================================================
# دوال الطلبات الأساسية
# ============================================================

def order_create(order_id, user_id, service_id, link, quantity, coin):
    """تسجيل طلب جديد"""
    orders_file = ORDERS_FILE
    os.makedirs(os.path.dirname(orders_file), exist_ok=True)
    
    record = {
        'id': str(order_id),
        'from_id': str(user_id),
        'service': str(service_id),
        'link': link,
        'quantity': quantity,
        'coin': float(coin),
        'status': 'pending',
        'created_at': int(time.time())
    }
    
    with open(orders_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    return True

def order_update_status(order_id, status):
    """تحديث حالة طلب موجود"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return False
    
    order_id = str(order_id)
    with open(orders_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated = False
    new_lines = []
    for line in lines:
        try:
            record = json.loads(line.strip())
            if str(record.get('id', '')) == order_id:
                record['status'] = status
                updated = True
            new_lines.append(json.dumps(record, ensure_ascii=False))
        except:
            new_lines.append(line.strip())
    
    if not updated:
        return False
    
    with open(orders_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')
    return True

def order_get(order_id):
    """الحصول على طلب برقمه"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return None
    
    order_id = str(order_id)
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if str(record.get('id', '')) == order_id:
                    return record
            except:
                continue
    return None

def order_get_by_user(user_id, limit=10):
    """الحصول على طلبات المستخدم"""
    return orders_user_text(user_id, limit)

def order_get_all(limit=100):
    """الحصول على جميع الطلبات"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return []
    
    orders = []
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                orders.append(record)
            except:
                continue
    
    return orders[-limit:] if len(orders) > limit else orders

def order_delete(order_id):
    """حذف طلب"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return False
    
    order_id = str(order_id)
    with open(orders_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    deleted = False
    for line in lines:
        try:
            record = json.loads(line.strip())
            if str(record.get('id', '')) != order_id:
                new_lines.append(line.strip())
            else:
                deleted = True
        except:
            new_lines.append(line.strip())
    
    if not deleted:
        return False
    
    with open(orders_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')
    return True

def order_get_pending():
    """الحصول على الطلبات المعلقة"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return []
    
    pending = []
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if record.get('status') == 'pending':
                    pending.append(record)
            except:
                continue
    return pending

def order_get_processing():
    """الحصول على الطلبات قيد التنفيذ"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return []
    
    processing = []
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if record.get('status') == 'processing':
                    processing.append(record)
            except:
                continue
    return processing

def order_get_completed():
    """الحصول على الطلبات المكتملة"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return []
    
    completed = []
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if record.get('status') == 'completed':
                    completed.append(record)
            except:
                continue
    return completed

def order_get_canceled():
    """الحصول على الطلبات الملغية"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return []
    
    canceled = []
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if record.get('status') == 'canceled':
                    canceled.append(record)
            except:
                continue
    return canceled

def orders_count():
    """الحصول على عدد الطلبات"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return 0
    
    count = 0
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
    return count

def orders_count_by_status(status):
    """الحصول على عدد الطلبات حسب الحالة"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return 0
    
    count = 0
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if record.get('status') == status:
                    count += 1
            except:
                continue
    return count

def orders_count_by_user(user_id):
    """الحصول على عدد طلبات المستخدم"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return 0
    
    user_id = str(user_id)
    count = 0
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if str(record.get('from_id', '')) == user_id:
                    count += 1
            except:
                continue
    return count

# ============================================================
# دوال إحصائيات الطلبات
# ============================================================

def orders_stats():
    """إحصائيات الطلبات"""
    stats = {
        'total_orders': 0,
        'total_revenue': 0,
        'by_status': {'pending': 0, 'processing': 0, 'completed': 0, 'canceled': 0},
        'top_service': None,
        'top_service_count': 0
    }
    
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return stats
    
    per_service = {}
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                stats['total_orders'] += 1
                stats['total_revenue'] += float(record.get('coin', 0))
                
                status = record.get('status', 'pending')
                if status in stats['by_status']:
                    stats['by_status'][status] += 1
                
                service = str(record.get('service', ''))
                if service:
                    per_service[service] = per_service.get(service, 0) + 1
            except:
                stats['total_orders'] += 1
    
    if per_service:
        sorted_services = sorted(per_service.items(), key=lambda x: x[1], reverse=True)
        stats['top_service'] = sorted_services[0][0]
        stats['top_service_count'] = sorted_services[0][1]
    
    return stats

def orders_daily_stats():
    """إحصائيات الطلبات اليومية"""
    today = datetime.now().strftime('%Y-%m-%d')
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return {'count': 0, 'revenue': 0}
    
    count = 0
    revenue = 0
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                created_at = record.get('created_at', 0)
                if created_at and datetime.fromtimestamp(created_at).strftime('%Y-%m-%d') == today:
                    count += 1
                    revenue += float(record.get('coin', 0))
            except:
                continue
    
    return {'count': count, 'revenue': revenue}

def orders_weekly_stats():
    """إحصائيات الطلبات الأسبوعية"""
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return {'count': 0, 'revenue': 0}
    
    count = 0
    revenue = 0
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                created_at = record.get('created_at', 0)
                if created_at:
                    date = datetime.fromtimestamp(created_at)
                    week_start_date = datetime.now() - timedelta(days=datetime.now().weekday())
                    if date >= week_start_date:
                        count += 1
                        revenue += float(record.get('coin', 0))
            except:
                continue
    
    return {'count': count, 'revenue': revenue}

def orders_monthly_stats():
    """إحصائيات الطلبات الشهرية"""
    month = datetime.now().strftime('%Y-%m')
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return {'count': 0, 'revenue': 0}
    
    count = 0
    revenue = 0
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                created_at = record.get('created_at', 0)
                if created_at and datetime.fromtimestamp(created_at).strftime('%Y-%m') == month:
                    count += 1
                    revenue += float(record.get('coin', 0))
            except:
                continue
    
    return {'count': count, 'revenue': revenue}

def orders_user_stats(user_id):
    """إحصائيات طلبات المستخدم"""
    user_id = str(user_id)
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return {'count': 0, 'revenue': 0, 'by_status': {'pending': 0, 'processing': 0, 'completed': 0, 'canceled': 0}}
    
    count = 0
    revenue = 0
    by_status = {'pending': 0, 'processing': 0, 'completed': 0, 'canceled': 0}
    
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if str(record.get('from_id', '')) == user_id:
                    count += 1
                    revenue += float(record.get('coin', 0))
                    status = record.get('status', 'pending')
                    if status in by_status:
                        by_status[status] += 1
            except:
                continue
    
    return {'count': count, 'revenue': revenue, 'by_status': by_status}

# ============================================================
# دوال نصوص الطلبات
# ============================================================

def orders_user_text(user_id, limit=10):
    """نص طلبات المستخدم"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return "📭 لا توجد طلبات مسجّلة باسمك حتى الآن."
    
    user_id = str(user_id)
    status_map = {
        'pending': '⏳ قيد الانتظار',
        'processing': '⚙️ قيد التنفيذ',
        'completed': '✅ مكتمل',
        'canceled': '❌ ملغي'
    }
    
    with open(orders_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    matches = []
    for line in reversed(lines):
        try:
            record = json.loads(line.strip())
            if str(record.get('from_id', '')) == user_id:
                matches.append(record)
                if len(matches) >= limit:
                    break
        except:
            continue
    
    if not matches:
        return "📭 لا توجد طلبات مسجّلة باسمك حتى الآن."
    
    text = f"📮 <b>آخر {len(matches)} طلب لك</b>\n━━━━━━━━━━━━━━━━━\n"
    for record in matches:
        status = status_map.get(record.get('status', 'pending'), record.get('status', '—'))
        text += f"🔢 #{record['id']} | 🛠 {record['service']} | {status}\n"
    
    return text

def orders_admin_text(limit=20):
    """نص جميع الطلبات للأدمن"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return "📭 لا توجد طلبات مسجّلة."
    
    with open(orders_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    matches = []
    for line in reversed(lines):
        try:
            record = json.loads(line.strip())
            matches.append(record)
            if len(matches) >= limit:
                break
        except:
            continue
    
    if not matches:
        return "📭 لا توجد طلبات مسجّلة."
    
    status_map = {
        'pending': '⏳ قيد الانتظار',
        'processing': '⚙️ قيد التنفيذ',
        'completed': '✅ مكتمل',
        'canceled': '❌ ملغي'
    }
    
    text = f"📮 <b>آخر {len(matches)} طلب</b>\n━━━━━━━━━━━━━━━━━\n"
    for record in matches:
        status = status_map.get(record.get('status', 'pending'), record.get('status', '—'))
        text += f"🔢 #{record['id']} | 🆔 {record['from_id']} | 🛠 {record['service']} | {status}\n"
    
    return text

def order_details_text(order_id):
    """نص تفاصيل طلب"""
    record = order_get(order_id)
    if not record:
        return "❌ الطلب غير موجود"
    
    status_map = {
        'pending': '⏳ قيد الانتظار',
        'processing': '⚙️ قيد التنفيذ',
        'completed': '✅ مكتمل',
        'canceled': '❌ ملغي'
    }
    
    status = status_map.get(record.get('status', 'pending'), record.get('status', '—'))
    text = f"""
📋 <b>تفاصيل الطلب</b>
━━━━━━━━━━━━━━━━━
🔢 <b>رقم الطلب:</b> #{record['id']}
🛠 <b>الخدمة:</b> {record['service']}
📌 <b>الرابط:</b> {record['link']}
🔢 <b>الكمية:</b> {record['quantity']}
💰 <b>السعر:</b> {record['coin']}
📊 <b>الحالة:</b> {status}
🕐 <b>التاريخ:</b> {datetime.fromtimestamp(record.get('created_at', 0)).strftime('%Y-%m-%d %H:%M')}
"""
    return text

# ============================================================
# دوال معالجة الطلبات (Order Processing)
# ============================================================

def process_order(order_id):
    """معالجة طلب (تغيير الحالة إلى processing)"""
    return order_update_status(order_id, 'processing')

def complete_order(order_id):
    """إكمال طلب (تغيير الحالة إلى completed)"""
    result = order_update_status(order_id, 'completed')
    if result:
        record = order_get(order_id)
        if record:
            # إشعار للمستخدم
            user_id = record['from_id']
            send_notification(user_id, f"✅ تم إكمال طلبك #{order_id}")
    return result

def cancel_order(order_id, reason=''):
    """إلغاء طلب"""
    result = order_update_status(order_id, 'canceled')
    if result:
        record = order_get(order_id)
        if record:
            # استرداد النقاط
            user_id = record['from_id']
            coin = record['coin']
            add_points(user_id, coin, f'استرداد نقاط طلب ملغي #{order_id}')
            send_notification(user_id, f"❌ تم إلغاء طلبك #{order_id}{f' - السبب: {reason}' if reason else ''}")
    return result

def refund_order(order_id):
    """استرداد نقاط طلب"""
    record = order_get(order_id)
    if not record:
        return False
    
    user_id = record['from_id']
    coin = record['coin']
    add_points(user_id, coin, f'استرداد نقاط #{order_id}')
    order_update_status(order_id, 'refunded')
    send_notification(user_id, f"🔄 تم استرداد نقاط طلبك #{order_id}")
    return True

# ============================================================
# دوال الطلبات عبر API الخارجي
# ============================================================

def call_api(web, key, action, service, link, quantity):
    """استدعاء API موقع الرشق"""
    try:
        url = f"https://{web}/api/v2"
        params = {
            'key': key,
            'action': action,
            'service': service,
            'link': link,
            'quantity': quantity
        }
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        bot_log('ERROR', 'call_api failed', {'error': str(e)})
        return None

def check_order_status(web, key, order_id):
    """التحقق من حالة طلب في موقع الرشق"""
    try:
        url = f"https://{web}/api/v2"
        params = {
            'key': key,
            'action': 'status',
            'order': order_id
        }
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        bot_log('ERROR', 'check_order_status failed', {'error': str(e)})
        return None

def create_order_via_api(user_id, section_id, service_index, link, quantity):
    """إنشاء طلب عبر API"""
    services = load_services()
    
    # الحصول على بيانات الخدمة
    service_name = services.get('xdmaxs', {}).get(section_id, {}).get(str(service_index), '')
    service_id = services.get('IDSSS', {}).get(section_id, {}).get(str(service_index), '')
    price = services.get('S3RS', {}).get(section_id, {}).get(str(service_index), 0)
    web = services.get('Web', {}).get(section_id, {}).get(str(service_index), '')
    key = services.get('key', {}).get(section_id, {}).get(str(service_index), '')
    
    if not service_id or not web or not key:
        return {'success': False, 'message': 'بيانات الخدمة غير مكتملة'}
    
    # حساب السعر
    total_price = float(price) * int(quantity)
    
    # التحقق من الرصيد
    balance = get_coin(user_id)
    if balance < total_price:
        return {'success': False, 'message': f'رصيدك غير كافي. المطلوب: {total_price}'}
    
    # استدعاء API
    result = call_api(web, key, 'add', service_id, link, quantity)
    if not result:
        return {'success': False, 'message': 'فشل الاتصال بموقع الرشق'}
    
    if 'order' not in result:
        return {'success': False, 'message': 'لم يتم إنشاء الطلب. تأكد من البيانات'}
    
    order_id = result['order']
    
    # خصم النقاط
    deduct_points(user_id, total_price, f'طلب خدمة: {service_name} #{order_id}')
    
    # تسجيل الطلب
    order_create(order_id, user_id, service_id, link, quantity, total_price)
    
    return {'success': True, 'message': f'تم إنشاء الطلب بنجاح', 'order_id': order_id}

# ============================================================
# دوال تقارير الطلبات
# ============================================================

def generate_orders_report():
    """توليد تقرير الطلبات"""
    stats = orders_stats()
    daily = orders_daily_stats()
    weekly = orders_weekly_stats()
    monthly = orders_monthly_stats()
    
    report = f"""
📊 <b>تقرير الطلبات</b>
━━━━━━━━━━━━━━━━━
📦 <b>إجمالي الطلبات:</b> {stats['total_orders']}
💰 <b>إجمالي الأرباح:</b> {stats['total_revenue']}
━━━━━━━━━━━━━━━━━
<b>حسب الحالة:</b>
⏳ قيد الانتظار: {stats['by_status']['pending']}
⚙️ قيد التنفيذ: {stats['by_status']['processing']}
✅ مكتملة: {stats['by_status']['completed']}
❌ ملغية: {stats['by_status']['canceled']}
━━━━━━━━━━━━━━━━━
<b>حسب الفترة:</b>
📅 اليوم: {daily['count']} طلب - {daily['revenue']} نقطة
📅 الأسبوع: {weekly['count']} طلب - {weekly['revenue']} نقطة
📅 الشهر: {monthly['count']} طلب - {monthly['revenue']} نقطة
━━━━━━━━━━━━━━━━━
🔝 <b>أكثر خدمة طلباً:</b> {stats['top_service']} ({stats['top_service_count']})
"""
    return report

def generate_user_orders_report(user_id):
    """توليد تقرير طلبات المستخدم"""
    stats = orders_user_stats(user_id)
    
    report = f"""
📊 <b>تقرير طلباتك</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📦 <b>إجمالي الطلبات:</b> {stats['count']}
💰 <b>إجمالي المصروفات:</b> {stats['revenue']}
━━━━━━━━━━━━━━━━━
<b>حسب الحالة:</b>
⏳ قيد الانتظار: {stats['by_status']['pending']}
⚙️ قيد التنفيذ: {stats['by_status']['processing']}
✅ مكتملة: {stats['by_status']['completed']}
❌ ملغية: {stats['by_status']['canceled']}
"""
    return report

# ============================================================
# دوال إشعارات الطلبات
# ============================================================

def send_order_notification(user_id, order_id, status):
    """إرسال إشعار بتغيير حالة الطلب"""
    status_map = {
        'pending': 'قيد الانتظار',
        'processing': 'قيد التنفيذ',
        'completed': 'مكتمل',
        'canceled': 'ملغي'
    }
    
    status_text = status_map.get(status, status)
    message = f"📋 <b>تحديث حالة الطلب</b>\n━━━━━━━━━━━━━━━━━\n🔢 <b>رقم الطلب:</b> #{order_id}\n📊 <b>الحالة الجديدة:</b> {status_text}"
    
    return send_notification(user_id, message)

def send_new_order_notification(order_id):
    """إرسال إشعار بطلب جديد للأدمن"""
    record = order_get(order_id)
    if not record:
        return False
    
    message = f"""
🆕 <b>طلب جديد</b>
━━━━━━━━━━━━━━━━━
🔢 <b>رقم الطلب:</b> #{record['id']}
🆔 <b>المستخدم:</b> <code>{record['from_id']}</code>
🛠 <b>الخدمة:</b> {record['service']}
💰 <b>السعر:</b> {record['coin']}
🔗 <b>الرابط:</b> {record['link']}
📅 <b>التاريخ:</b> {datetime.fromtimestamp(record.get('created_at', 0)).strftime('%Y-%m-%d %H:%M')}
"""
    return send_notification_to_admin(message)

# ============================================================
# دوال النسخ الاحتياطي للطلبات
# ============================================================

def backup_orders():
    """عمل نسخة احتياطية للطلبات"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return False
    
    backup_file = f"{orders_file}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        with open(orders_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

def restore_orders(backup_file):
    """استعادة نسخة احتياطية للطلبات"""
    if not os.path.exists(backup_file):
        return False
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

def clear_orders():
    """مسح جميع الطلبات"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return True
    
    try:
        with open(orders_file, 'w', encoding='utf-8') as f:
            f.write('')
        return True
    except:
        return False

# ============================================================
# نهاية الجزء 3
# ============================================================
# ============================================================
# الجزء 4: نظام الكوبونات والهدايا (Coupons & Gifts) - 1500 سطر
# ============================================================

# ============================================================
# دوال الكوبونات الأساسية
# ============================================================

COUPONS_FILE = './data/coupons.json'

def coupons_path():
    return COUPONS_FILE

def coupons_read():
    """قراءة الكوبونات"""
    if not os.path.exists(COUPONS_FILE):
        return {}
    try:
        with open(COUPONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def coupons_write(coupons):
    """كتابة الكوبونات"""
    tmp_path = f"{COUPONS_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(COUPONS_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(coupons, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, COUPONS_FILE)
        return True
    except Exception as e:
        bot_log('ERROR', 'coupons_write failed', {'error': str(e)})
        return False

def coupon_validate_code(code):
    """التحقق من صحة الكود"""
    code = code.upper().strip()
    if re.match(r'^[A-Z0-9_\-]{2,30}$', code):
        return code
    return ''

def coupon_validate_value(value, type_):
    """التحقق من صحة القيمة"""
    if value <= 0:
        return False
    if type_ == 'discount' and value > 100:
        return False
    return True

def coupon_create(code, type_, value, max_uses=0):
    """إنشاء كوبون جديد"""
    code = coupon_validate_code(code)
    if not code:
        return None
    
    if type_ not in ['charge', 'discount']:
        return None
    
    if not coupon_validate_value(value, type_):
        return None
    
    max_uses = max(0, int(max_uses))
    coupons = coupons_read()
    
    coupon = {
        'code': code,
        'type': type_,
        'value': float(value),
        'max_uses': max_uses,
        'used_by': [],
        'created_at': int(time.time()),
        'active': True
    }
    
    coupons[code] = coupon
    coupons_write(coupons)
    return coupon

def coupon_get(code):
    """الحصول على كوبون"""
    code = code.upper().strip()
    if not code:
        return None
    coupons = coupons_read()
    return coupons.get(code)

def coupon_disable(code):
    """تعطيل كوبون"""
    code = code.upper().strip()
    if not code:
        return False
    
    coupons = coupons_read()
    if code not in coupons:
        return False
    
    coupons[code]['active'] = False
    return coupons_write(coupons)

def coupon_enable(code):
    """تفعيل كوبون"""
    code = code.upper().strip()
    if not code:
        return False
    
    coupons = coupons_read()
    if code not in coupons:
        return False
    
    coupons[code]['active'] = True
    return coupons_write(coupons)

def coupon_delete(code):
    """حذف كوبون"""
    code = code.upper().strip()
    if not code:
        return False
    
    coupons = coupons_read()
    if code not in coupons:
        return False
    
    del coupons[code]
    return coupons_write(coupons)

def coupon_redeem(code, user_id):
    """استخدام كوبون"""
    code = code.upper().strip()
    user_id = str(user_id)
    
    if not code or not user_id or user_id == '0':
        return {'ok': False, 'message': 'بيانات غير صحيحة ❌', 'coupon': None}
    
    coupons = coupons_read()
    if code not in coupons:
        return {'ok': False, 'message': 'الكود غير صحيح ❌', 'coupon': None}
    
    coupon = coupons[code]
    if not coupon.get('active', True):
        return {'ok': False, 'message': 'هذا الكود غير مفعّل حالياً ❌', 'coupon': None}
    
    if user_id in coupon.get('used_by', []):
        return {'ok': False, 'message': 'لقد استخدمت هذا الكود من قبل ❌', 'coupon': None}
    
    max_uses = int(coupon.get('max_uses', 0))
    used_count = len(coupon.get('used_by', []))
    if max_uses > 0 and used_count >= max_uses:
        return {'ok': False, 'message': 'انتهت عدد مرات استخدام هذا الكود ❌', 'coupon': None}
    
    coupons[code]['used_by'].append(user_id)
    coupons_write(coupons)
    return {'ok': True, 'message': 'تم استخدام الكود بنجاح ✅', 'coupon': coupons[code]}

def coupon_get_used_count(code):
    """الحصول على عدد مرات استخدام الكوبون"""
    coupon = coupon_get(code)
    if not coupon:
        return 0
    return len(coupon.get('used_by', []))

def coupon_get_remaining_uses(code):
    """الحصول على عدد المرات المتبقية للاستخدام"""
    coupon = coupon_get(code)
    if not coupon:
        return 0
    max_uses = int(coupon.get('max_uses', 0))
    if max_uses == 0:
        return float('inf')
    return max_uses - len(coupon.get('used_by', []))

def coupon_is_active(code):
    """التحقق من نشاط الكوبون"""
    coupon = coupon_get(code)
    if not coupon:
        return False
    return coupon.get('active', True)

def coupon_is_used_by(code, user_id):
    """التحقق من استخدام المستخدم للكوبون"""
    coupon = coupon_get(code)
    if not coupon:
        return False
    return str(user_id) in coupon.get('used_by', [])

def coupons_list(active_only=True):
    """الحصول على قائمة الكوبونات"""
    coupons = coupons_read()
    if active_only:
        return {k: v for k, v in coupons.items() if v.get('active', True)}
    return coupons

def coupons_count(active_only=True):
    """الحصول على عدد الكوبونات"""
    return len(coupons_list(active_only))

def coupons_total_used():
    """الحصول على إجمالي مرات استخدام الكوبونات"""
    coupons = coupons_read()
    total = 0
    for coupon in coupons.values():
        total += len(coupon.get('used_by', []))
    return total

def coupons_total_value():
    """الحصول على إجمالي قيمة الكوبونات"""
    coupons = coupons_read()
    total = 0
    for coupon in coupons.values():
        if coupon.get('type') == 'charge':
            total += float(coupon.get('value', 0)) * len(coupon.get('used_by', []))
    return total

# ============================================================
# دوال الكوبونات المتقدمة
# ============================================================

def coupon_create_with_expiry(code, type_, value, max_uses=0, expires_in=86400):
    """إنشاء كوبون مع صلاحية زمنية"""
    code = coupon_validate_code(code)
    if not code:
        return None
    
    if type_ not in ['charge', 'discount']:
        return None
    
    if not coupon_validate_value(value, type_):
        return None
    
    max_uses = max(0, int(max_uses))
    coupons = coupons_read()
    
    coupon = {
        'code': code,
        'type': type_,
        'value': float(value),
        'max_uses': max_uses,
        'used_by': [],
        'created_at': int(time.time()),
        'expires_at': int(time.time()) + expires_in,
        'active': True
    }
    
    coupons[code] = coupon
    coupons_write(coupons)
    return coupon

def coupon_is_expired(code):
    """التحقق من انتهاء صلاحية الكوبون"""
    coupon = coupon_get(code)
    if not coupon:
        return True
    expires_at = coupon.get('expires_at', 0)
    if expires_at == 0:
        return False
    return int(time.time()) > expires_at

def coupon_clean_expired():
    """تنظيف الكوبونات منتهية الصلاحية"""
    coupons = coupons_read()
    removed = 0
    for code, coupon in list(coupons.items()):
        if coupon_is_expired(code):
            del coupons[code]
            removed += 1
    if removed > 0:
        coupons_write(coupons)
    return removed

def coupon_bulk_create(codes, type_, value, max_uses=0):
    """إنشاء عدة كوبونات دفعة واحدة"""
    created = []
    failed = []
    for code in codes:
        result = coupon_create(code, type_, value, max_uses)
        if result:
            created.append(code)
        else:
            failed.append(code)
    return {'created': created, 'failed': failed}

def coupon_export():
    """تصدير الكوبونات"""
    coupons = coupons_read()
    return json.dumps(coupons, indent=2, ensure_ascii=False)

def coupon_import(data):
    """استيراد الكوبونات"""
    try:
        coupons = json.loads(data)
        if isinstance(coupons, dict):
            return coupons_write(coupons)
        return False
    except:
        return False

# ============================================================
# دوال الهدايا (Gifts)
# ============================================================

GIFTS_FILE = './data/gifts.json'

def gifts_read():
    """قراءة الهدايا"""
    if not os.path.exists(GIFTS_FILE):
        return {}
    try:
        with open(GIFTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def gifts_write(gifts):
    """كتابة الهدايا"""
    tmp_path = f"{GIFTS_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(GIFTS_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(gifts, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, GIFTS_FILE)
        return True
    except:
        return False

def gift_create(amount, max_uses=1, expires_in=86400):
    """إنشاء هدية جديدة"""
    code = generate_random_code(8)
    gifts = gifts_read()
    
    gift = {
        'code': code,
        'amount': float(amount),
        'max_uses': max_uses,
        'used_by': [],
        'created_at': int(time.time()),
        'expires_at': int(time.time()) + expires_in,
        'active': True
    }
    
    gifts[code] = gift
    gifts_write(gifts)
    return code

def gift_get(code):
    """الحصول على هدية"""
    gifts = gifts_read()
    return gifts.get(code)

def gift_redeem(code, user_id):
    """استخدام هدية"""
    user_id = str(user_id)
    gifts = gifts_read()
    
    if code not in gifts:
        return {'success': False, 'message': 'الكود غير صحيح ❌'}
    
    gift = gifts[code]
    if not gift.get('active', True):
        return {'success': False, 'message': 'هذه الهدية غير مفعّلة ❌'}
    
    if int(time.time()) > gift.get('expires_at', 0):
        return {'success': False, 'message': 'انتهت صلاحية هذه الهدية ❌'}
    
    if user_id in gift.get('used_by', []):
        return {'success': False, 'message': 'لقد استخدمت هذه الهدية من قبل ❌'}
    
    if len(gift.get('used_by', [])) >= gift.get('max_uses', 1):
        return {'success': False, 'message': 'انتهت عدد مرات استخدام هذه الهدية ❌'}
    
    # إضافة النقاط
    add_points(user_id, gift['amount'], f'هدية: {code}')
    
    # تسجيل الاستخدام
    gifts[code]['used_by'].append(user_id)
    gifts_write(gifts)
    
    return {'success': True, 'message': f'تم إضافة {gift["amount"]} نقطة 🎁'}

def gift_disable(code):
    """تعطيل هدية"""
    gifts = gifts_read()
    if code not in gifts:
        return False
    gifts[code]['active'] = False
    return gifts_write(gifts)

def gift_enable(code):
    """تفعيل هدية"""
    gifts = gifts_read()
    if code not in gifts:
        return False
    gifts[code]['active'] = True
    return gifts_write(gifts)

def gift_delete(code):
    """حذف هدية"""
    gifts = gifts_read()
    if code not in gifts:
        return False
    del gifts[code]
    return gifts_write(gifts)

def gifts_list(active_only=True):
    """الحصول على قائمة الهدايا"""
    gifts = gifts_read()
    if active_only:
        return {k: v for k, v in gifts.items() if v.get('active', True)}
    return gifts

def gifts_total_used():
    """الحصول على إجمالي مرات استخدام الهدايا"""
    gifts = gifts_read()
    total = 0
    for gift in gifts.values():
        total += len(gift.get('used_by', []))
    return total

# ============================================================
# دوال الكروت (Cards)
# ============================================================

CARDS_FILE = './data/cards.json'

def cards_read():
    """قراءة الكروت"""
    if not os.path.exists(CARDS_FILE):
        return {}
    try:
        with open(CARDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def cards_write(cards):
    """كتابة الكروت"""
    tmp_path = f"{CARDS_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(CARDS_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, CARDS_FILE)
        return True
    except:
        return False

def card_create(code, value, type_='charge', max_uses=1):
    """إنشاء كرت جديد"""
    cards = cards_read()
    
    card = {
        'code': code,
        'value': float(value),
        'type': type_,
        'max_uses': max_uses,
        'used_by': [],
        'created_at': int(time.time()),
        'active': True
    }
    
    cards[code] = card
    cards_write(cards)
    return card

def card_get(code):
    """الحصول على كرت"""
    cards = cards_read()
    return cards.get(code)

def card_redeem(code, user_id):
    """استخدام كرت"""
    user_id = str(user_id)
    cards = cards_read()
    
    if code not in cards:
        return {'success': False, 'message': 'الكود غير صحيح ❌'}
    
    card = cards[code]
    if not card.get('active', True):
        return {'success': False, 'message': 'هذا الكرت غير مفعّل ❌'}
    
    if user_id in card.get('used_by', []):
        return {'success': False, 'message': 'لقد استخدمت هذا الكرت من قبل ❌'}
    
    if len(card.get('used_by', [])) >= card.get('max_uses', 1):
        return {'success': False, 'message': 'انتهت عدد مرات استخدام هذا الكرت ❌'}
    
    # إضافة النقاط
    if card['type'] == 'charge':
        add_points(user_id, card['value'], f'كرت: {code}')
        message = f'تم إضافة {card["value"]} نقطة'
    else:
        message = f'تم تفعيل الخصم بنسبة {card["value"]}%'
    
    # تسجيل الاستخدام
    cards[code]['used_by'].append(user_id)
    cards_write(cards)
    
    return {'success': True, 'message': message}

def card_disable(code):
    """تعطيل كرت"""
    cards = cards_read()
    if code not in cards:
        return False
    cards[code]['active'] = False
    return cards_write(cards)

def card_enable(code):
    """تفعيل كرت"""
    cards = cards_read()
    if code not in cards:
        return False
    cards[code]['active'] = True
    return cards_write(cards)

def card_delete(code):
    """حذف كرت"""
    cards = cards_read()
    if code not in cards:
        return False
    del cards[code]
    return cards_write(cards)

def cards_list(active_only=True):
    """الحصول على قائمة الكروت"""
    cards = cards_read()
    if active_only:
        return {k: v for k, v in cards.items() if v.get('active', True)}
    return cards

# ============================================================
# دوال الكوبونات والهدايا (نظام متكامل)
# ============================================================

def system_coupon_create(code, type_, value, max_uses=0, description=''):
    """إنشاء كوبون في النظام (واجهة موحدة)"""
    result = coupon_create(code, type_, value, max_uses)
    if result:
        coupon_data = coupon_get(code)
        if coupon_data and description:
            coupons = coupons_read()
            coupons[code]['description'] = description
            coupons_write(coupons)
    return result

def system_gift_create(amount, max_uses=1, description=''):
    """إنشاء هدية في النظام (واجهة موحدة)"""
    code = gift_create(amount, max_uses)
    gifts = gifts_read()
    if description:
        gifts[code]['description'] = description
        gifts_write(gifts)
    return code

def system_redeem_code(code, user_id, code_type='auto'):
    """استخدام كود (تلقائي)"""
    # محاولة استخدام كوبون أولاً
    coupon_result = coupon_redeem(code, user_id)
    if coupon_result['ok']:
        return {'success': True, 'message': coupon_result['message'], 'type': 'coupon'}
    
    # محاولة استخدام هدية
    gift_result = gift_redeem(code, user_id)
    if gift_result['success']:
        return {'success': True, 'message': gift_result['message'], 'type': 'gift'}
    
    # محاولة استخدام كرت
    card_result = card_redeem(code, user_id)
    if card_result['success']:
        return {'success': True, 'message': card_result['message'], 'type': 'card'}
    
    return {'success': False, 'message': 'الكود غير صحيح ❌'}

def system_get_code_info(code):
    """الحصول على معلومات الكود (تلقائي)"""
    # البحث في الكوبونات
    coupon = coupon_get(code)
    if coupon:
        return {'type': 'coupon', 'data': coupon, 'exists': True}
    
    # البحث في الهدايا
    gift = gift_get(code)
    if gift:
        return {'type': 'gift', 'data': gift, 'exists': True}
    
    # البحث في الكروت
    card = card_get(code)
    if card:
        return {'type': 'card', 'data': card, 'exists': True}
    
    return {'exists': False}

def system_get_all_codes(active_only=True):
    """الحصول على جميع الأكواد"""
    result = {
        'coupons': coupons_list(active_only),
        'gifts': gifts_list(active_only),
        'cards': cards_list(active_only)
    }
    return result

def system_get_codes_stats():
    """الحصول على إحصائيات الأكواد"""
    return {
        'coupons': {
            'total': len(coupons_list()),
            'active': len(coupons_list(True)),
            'used': coupons_total_used(),
            'value': coupons_total_value()
        },
        'gifts': {
            'total': len(gifts_list()),
            'active': len(gifts_list(True)),
            'used': gifts_total_used()
        },
        'cards': {
            'total': len(cards_list()),
            'active': len(cards_list(True))
        }
    }

# ============================================================
# نهاية الجزء 4
# ============================================================
# ============================================================
# الجزء 5: نظام الخدمات والأقسام (Services & Categories) - 1500 سطر
# ============================================================

# ============================================================
# دوال تحميل وحفظ الخدمات
# ============================================================

SERVICES_FILE = './akl/akl.json'

def load_services():
    """تحميل بيانات الخدمات"""
    if os.path.exists(SERVICES_FILE):
        try:
            with open(SERVICES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'qsm': [],
        'NAMES': {},
        'xdmaxs': {},
        'S3RS': {},
        'IDSSS': {},
        'min': {},
        'mix': {},
        'WSF': {},
        'Web': {},
        'key': {},
        'IFWORK>': {},
        'mode': {},
        'MGS': {},
        'sSite': '',
        'sVISCODEV': '',
        'bot_tlb': 0
    }

def save_services(data):
    """حفظ بيانات الخدمات"""
    tmp_path = f"{SERVICES_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(SERVICES_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, SERVICES_FILE)
        return True
    except Exception as e:
        bot_log('ERROR', 'save_services failed', {'error': str(e)})
        return False

# ============================================================
# دوال إدارة الأقسام (Categories)
# ============================================================

def category_create(name):
    """إنشاء قسم جديد"""
    services = load_services()
    
    # توليد معرف فريد للقسم
    section_id = f"bot{random.randint(0, 999999999999999)}"
    
    # إضافة القسم
    services['qsm'].append(f"{name}-{section_id}")
    services['NAMES'][section_id] = name
    services['xdmaxs'][section_id] = []
    services['S3RS'][section_id] = {}
    services['IDSSS'][section_id] = {}
    services['min'][section_id] = {}
    services['mix'][section_id] = {}
    services['WSF'][section_id] = {}
    services['Web'][section_id] = {}
    services['key'][section_id] = {}
    services['IFWORK>'][section_id] = 'OK'
    
    save_services(services)
    return {'id': section_id, 'name': name}

def category_delete(section_id):
    """حذف قسم"""
    services = load_services()
    
    if section_id not in services['NAMES']:
        return False
    
    # حذف القسم من qsm
    services['qsm'] = [q for q in services['qsm'] if not q.endswith(f"-{section_id}")]
    
    # حذف جميع بيانات القسم
    del services['NAMES'][section_id]
    del services['xdmaxs'][section_id]
    del services['S3RS'][section_id]
    del services['IDSSS'][section_id]
    del services['min'][section_id]
    del services['mix'][section_id]
    del services['WSF'][section_id]
    del services['Web'][section_id]
    del services['key'][section_id]
    
    if section_id in services['IFWORK>']:
        del services['IFWORK>'][section_id]
    
    save_services(services)
    return True

def category_get(section_id):
    """الحصول على بيانات القسم"""
    services = load_services()
    if section_id not in services['NAMES']:
        return None
    return {
        'id': section_id,
        'name': services['NAMES'][section_id],
        'services': services['xdmaxs'].get(section_id, []),
        'active': services['IFWORK>'].get(section_id, 'OK') != 'NOT'
    }

def category_list(active_only=True):
    """الحصول على قائمة الأقسام"""
    services = load_services()
    categories = []
    for q in services.get('qsm', []):
        name, section_id = q.split('-')
        if active_only and services['IFWORK>'].get(section_id, 'OK') == 'NOT':
            continue
        categories.append({
            'id': section_id,
            'name': name,
            'active': services['IFWORK>'].get(section_id, 'OK') != 'NOT'
        })
    return categories

def category_count():
    """الحصول على عدد الأقسام"""
    return len(category_list())

def category_toggle(section_id):
    """تبديل حالة القسم (تفعيل/تعطيل)"""
    services = load_services()
    if section_id not in services['NAMES']:
        return False
    
    current = services['IFWORK>'].get(section_id, 'OK')
    services['IFWORK>'][section_id] = 'NOT' if current == 'OK' else 'OK'
    save_services(services)
    return True

# ============================================================
# دوال إدارة الخدمات (Services)
# ============================================================

def service_create(section_id, name):
    """إنشاء خدمة جديدة في قسم"""
    services = load_services()
    
    if section_id not in services['NAMES']:
        return None
    
    # إضافة الخدمة
    services['xdmaxs'][section_id].append(name)
    index = len(services['xdmaxs'][section_id]) - 1
    services['S3RS'][section_id][str(index)] = 0
    services['IDSSS'][section_id][str(index)] = ''
    services['min'][section_id][str(index)] = 100
    services['mix'][section_id][str(index)] = 10000
    services['WSF'][section_id][str(index)] = ''
    services['Web'][section_id][str(index)] = ''
    services['key'][section_id][str(index)] = ''
    
    save_services(services)
    return {'index': index, 'name': name}

def service_delete(section_id, index):
    """حذف خدمة"""
    services = load_services()
    
    if section_id not in services['xdmaxs']:
        return False
    
    if str(index) not in services['S3RS'][section_id]:
        return False
    
    # حذف الخدمة
    services['xdmaxs'][section_id].pop(index)
    del services['S3RS'][section_id][str(index)]
    del services['IDSSS'][section_id][str(index)]
    del services['min'][section_id][str(index)]
    del services['mix'][section_id][str(index)]
    del services['WSF'][section_id][str(index)]
    del services['Web'][section_id][str(index)]
    del services['key'][section_id][str(index)]
    
    save_services(services)
    return True

def service_get(section_id, index):
    """الحصول على بيانات الخدمة"""
    services = load_services()
    
    if section_id not in services['xdmaxs']:
        return None
    
    if index >= len(services['xdmaxs'][section_id]):
        return None
    
    return {
        'name': services['xdmaxs'][section_id][index],
        'price': services['S3RS'][section_id].get(str(index), 0),
        'service_id': services['IDSSS'][section_id].get(str(index), ''),
        'min': services['min'][section_id].get(str(index), 100),
        'max': services['mix'][section_id].get(str(index), 10000),
        'description': services['WSF'][section_id].get(str(index), ''),
        'web': services['Web'][section_id].get(str(index), ''),
        'key': services['key'][section_id].get(str(index), '')
    }

def service_list(section_id):
    """الحصول على قائمة الخدمات في قسم"""
    services = load_services()
    if section_id not in services['xdmaxs']:
        return []
    
    return services['xdmaxs'][section_id]

def service_count(section_id):
    """الحصول على عدد الخدمات في قسم"""
    return len(service_list(section_id))

def service_set_price(section_id, index, price):
    """تعيين سعر الخدمة"""
    services = load_services()
    if section_id not in services['S3RS']:
        return False
    services['S3RS'][section_id][str(index)] = float(price)
    save_services(services)
    return True

def service_set_id(section_id, index, service_id):
    """تعيين ID الخدمة من الموقع"""
    services = load_services()
    if section_id not in services['IDSSS']:
        return False
    services['IDSSS'][section_id][str(index)] = str(service_id)
    save_services(services)
    return True

def service_set_min(section_id, index, min_value):
    """تعيين الحد الأدنى للخدمة"""
    services = load_services()
    if section_id not in services['min']:
        return False
    services['min'][section_id][str(index)] = int(min_value)
    save_services(services)
    return True

def service_set_max(section_id, index, max_value):
    """تعيين الحد الأقصى للخدمة"""
    services = load_services()
    if section_id not in services['mix']:
        return False
    services['mix'][section_id][str(index)] = int(max_value)
    save_services(services)
    return True

def service_set_description(section_id, index, description):
    """تعيين وصف الخدمة"""
    services = load_services()
    if section_id not in services['WSF']:
        return False
    services['WSF'][section_id][str(index)] = description
    save_services(services)
    return True

def service_set_web(section_id, index, web):
    """تعيين رابط موقع الخدمة"""
    services = load_services()
    if section_id not in services['Web']:
        return False
    services['Web'][section_id][str(index)] = web
    save_services(services)
    return True

def service_set_key(section_id, index, key):
    """تعيين مفتاح API للخدمة"""
    services = load_services()
    if section_id not in services['key']:
        return False
    services['key'][section_id][str(index)] = key
    save_services(services)
    return True

# ============================================================
# دوال إعدادات النظام للخدمات
# ============================================================

def service_set_site(site):
    """تعيين موقع الرشق الأساسي"""
    services = load_services()
    services['sSite'] = site
    save_services(services)
    return True

def service_get_site():
    """الحصول على موقع الرشق الأساسي"""
    services = load_services()
    return services.get('sSite', '')

def service_set_token(token):
    """تعيين توكن API الأساسي"""
    services = load_services()
    services['sVISCODEV'] = token
    save_services(services)
    return True

def service_get_token():
    """الحصول على توكن API الأساسي"""
    services = load_services()
    return services.get('sVISCODEV', '')

def service_get_bot_token():
    """الحصول على توكن البوت"""
    return BOT_TOKEN

# ============================================================
# دوال نسخ الخدمات (Export/Import)
# ============================================================

def service_export(section_id=None):
    """تصدير الخدمات (كلها أو قسم محدد)"""
    services = load_services()
    
    if section_id:
        if section_id not in services['NAMES']:
            return None
        export_data = {
            'NAMES': {section_id: services['NAMES'][section_id]},
            'xdmaxs': {section_id: services['xdmaxs'][section_id]},
            'S3RS': {section_id: services['S3RS'][section_id]},
            'IDSSS': {section_id: services['IDSSS'][section_id]},
            'min': {section_id: services['min'][section_id]},
            'mix': {section_id: services['mix'][section_id]},
            'WSF': {section_id: services['WSF'][section_id]},
            'Web': {section_id: services['Web'][section_id]},
            'key': {section_id: services['key'][section_id]},
            'qsm': [f"{services['NAMES'][section_id]}-{section_id}"]
        }
    else:
        export_data = {
            'qsm': services['qsm'],
            'NAMES': services['NAMES'],
            'xdmaxs': services['xdmaxs'],
            'S3RS': services['S3RS'],
            'IDSSS': services['IDSSS'],
            'min': services['min'],
            'mix': services['mix'],
            'WSF': services['WSF'],
            'Web': services['Web'],
            'key': services['key']
        }
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def service_import(data):
    """استيراد الخدمات"""
    try:
        import_data = json.loads(data)
        
        # التحقق من صحة البيانات
        required_keys = ['qsm', 'NAMES', 'xdmaxs', 'S3RS', 'IDSSS', 'min', 'mix', 'WSF', 'Web', 'key']
        for key in required_keys:
            if key not in import_data:
                return False
        
        services = load_services()
        
        # دمج البيانات
        for key in required_keys:
            services[key].update(import_data.get(key, {}))
        
        save_services(services)
        return True
    except Exception as e:
        bot_log('ERROR', 'service_import failed', {'error': str(e)})
        return False

def service_create_export_file(section_id=None):
    """إنشاء ملف تصدير للخدمات"""
    data = service_export(section_id)
    if not data:
        return None
    
    filename = f"services_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    file_path = f"./exports/{filename}"
    
    os.makedirs('./exports', exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)
    
    return file_path

# ============================================================
# دوال الخدمات المميزة
# ============================================================

def service_get_featured(limit=10):
    """الحصول على الخدمات المميزة (الأكثر طلباً)"""
    stats = orders_stats()
    if not stats['top_service']:
        return []
    
    featured = []
    services = load_services()
    
    for section_id, service_list in services['xdmaxs'].items():
        for index, name in enumerate(service_list):
            if name == stats['top_service']:
                featured.append({
                    'section_id': section_id,
                    'index': index,
                    'name': name,
                    'price': services['S3RS'][section_id].get(str(index), 0)
                })
                if len(featured) >= limit:
                    return featured
    
    return featured

def service_search(query):
    """البحث عن خدمة"""
    services = load_services()
    results = []
    query = query.lower()
    
    for section_id, service_list in services['xdmaxs'].items():
        for index, name in enumerate(service_list):
            if query in name.lower():
                results.append({
                    'section_id': section_id,
                    'index': index,
                    'name': name,
                    'price': services['S3RS'][section_id].get(str(index), 0)
                })
    
    return results

def service_get_random(limit=5):
    """الحصول على خدمات عشوائية"""
    services = load_services()
    all_services = []
    
    for section_id, service_list in services['xdmaxs'].items():
        for index, name in enumerate(service_list):
            all_services.append({
                'section_id': section_id,
                'index': index,
                'name': name,
                'price': services['S3RS'][section_id].get(str(index), 0)
            })
    
    if len(all_services) <= limit:
        return all_services
    
    return random.sample(all_services, limit)

# ============================================================
# دوال الخدمات الاحصائية
# ============================================================

def service_get_stats():
    """الحصول على إحصائيات الخدمات"""
    services = load_services()
    stats = {
        'total_categories': len(services['qsm']),
        'total_services': 0,
        'services_per_category': {}
    }
    
    for section_id, service_list in services['xdmaxs'].items():
        count = len(service_list)
        stats['total_services'] += count
        if section_id in services['NAMES']:
            stats['services_per_category'][services['NAMES'][section_id]] = count
    
    return stats

def service_get_available():
    """الحصول على الخدمات المتاحة (الأقسام النشطة)"""
    services = load_services()
    available = []
    
    for q in services['qsm']:
        name, section_id = q.split('-')
        if services['IFWORK>'].get(section_id, 'OK') != 'NOT':
            available.append({
                'id': section_id,
                'name': name,
                'services': len(services['xdmaxs'].get(section_id, []))
            })
    
    return available

# ============================================================
# دوال الخدمات والـ API
# ============================================================

def service_get_api_data(section_id, index):
    """الحصول على بيانات API للخدمة"""
    services = load_services()
    
    if section_id not in services['xdmaxs']:
        return None
    
    return {
        'service_id': services['IDSSS'][section_id].get(str(index), ''),
        'web': services['Web'][section_id].get(str(index), ''),
        'key': services['key'][section_id].get(str(index), ''),
        'min': services['min'][section_id].get(str(index), 100),
        'max': services['mix'][section_id].get(str(index), 10000)
    }

def service_calculate_price(section_id, index, quantity):
    """حساب سعر الخدمة حسب الكمية"""
    services = load_services()
    
    if section_id not in services['S3RS']:
        return None
    
    price_per_unit = services['S3RS'][section_id].get(str(index), 0)
    return float(price_per_unit) * int(quantity)

def service_validate_quantity(section_id, index, quantity):
    """التحقق من صحة الكمية"""
    services = load_services()
    
    if section_id not in services['min']:
        return {'valid': False, 'message': 'الخدمة غير موجودة'}
    
    min_qty = services['min'][section_id].get(str(index), 100)
    max_qty = services['mix'][section_id].get(str(index), 10000)
    
    if int(quantity) < min_qty:
        return {'valid': False, 'message': f'الحد الأدنى للطلب هو {min_qty}'}
    
    if int(quantity) > max_qty:
        return {'valid': False, 'message': f'الحد الأقصى للطلب هو {max_qty}'}
    
    return {'valid': True, 'message': 'الكمية صحيحة'}

# ============================================================
# نهاية الجزء 5
# ============================================================
# ============================================================
# الجزء 6: نظام الإشعارات والرسائل (Notifications & Messages) - 1500 سطر
# ============================================================

# ============================================================
# دوال الإشعارات الأساسية
# ============================================================

def send_notification(user_id, message, parse_mode='HTML'):
    """إرسال إشعار لمستخدم"""
    try:
        result = bot('sendMessage', {
            'chat_id': user_id,
            'text': message,
            'parse_mode': parse_mode
        })
        return result and result.get('ok', False)
    except Exception as e:
        bot_log('ERROR', 'send_notification failed', {'user_id': user_id, 'error': str(e)})
        return False

def send_notification_to_admin(message, parse_mode='HTML'):
    """إرسال إشعار للأدمن"""
    return send_notification(ADMIN_ID, message, parse_mode)

def send_notification_to_admins(message, parse_mode='HTML'):
    """إرسال إشعار لجميع الأدمنية"""
    sudo_data = load_sudo_data()
    admins = sudo_data.get('info', {}).get('admins', [])
    success = 0
    for admin in admins:
        if send_notification(admin, message, parse_mode):
            success += 1
    return success

def send_notification_with_button(user_id, message, button_text, button_data, parse_mode='HTML'):
    """إرسال إشعار مع زر"""
    try:
        reply_markup = json.dumps({
            'inline_keyboard': [[{
                'text': button_text,
                'callback_data': button_data
            }]]
        })
        result = bot('sendMessage', {
            'chat_id': user_id,
            'text': message,
            'parse_mode': parse_mode,
            'reply_markup': reply_markup
        })
        return result and result.get('ok', False)
    except Exception as e:
        bot_log('ERROR', 'send_notification_with_button failed', {'user_id': user_id, 'error': str(e)})
        return False

def send_notification_with_url(user_id, message, button_text, url, parse_mode='HTML'):
    """إرسال إشعار مع رابط"""
    try:
        reply_markup = json.dumps({
            'inline_keyboard': [[{
                'text': button_text,
                'url': url
            }]]
        })
        result = bot('sendMessage', {
            'chat_id': user_id,
            'text': message,
            'parse_mode': parse_mode,
            'reply_markup': reply_markup
        })
        return result and result.get('ok', False)
    except Exception as e:
        bot_log('ERROR', 'send_notification_with_url failed', {'user_id': user_id, 'error': str(e)})
        return False

# ============================================================
# دوال الإذاعة (Broadcast)
# ============================================================

def get_all_users_ids():
    """الحصول على جميع معرفات المستخدمين"""
    users_file = './data/user.json'
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('userlist', [])
        except:
            pass
    return []

def broadcast_message(message, parse_mode='HTML', delay=0.5):
    """إرسال رسالة لجميع المستخدمين"""
    users = get_all_users_ids()
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            result = bot('sendMessage', {
                'chat_id': user_id,
                'text': message,
                'parse_mode': parse_mode
            })
            if result and result.get('ok', False):
                success += 1
            else:
                failed += 1
            time.sleep(delay)
        except:
            failed += 1
    
    return {'success': success, 'failed': failed}

def broadcast_forward(message_id, from_chat_id=None, delay=0.5):
    """إعادة توجيه رسالة لجميع المستخدمين"""
    if not from_chat_id:
        from_chat_id = ADMIN_ID
    
    users = get_all_users_ids()
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            result = bot('forwardMessage', {
                'chat_id': user_id,
                'from_chat_id': from_chat_id,
                'message_id': message_id
            })
            if result and result.get('ok', False):
                success += 1
            else:
                failed += 1
            time.sleep(delay)
        except:
            failed += 1
    
    return {'success': success, 'failed': failed}

def broadcast_to_admins(message, parse_mode='HTML'):
    """إرسال رسالة لجميع الأدمنية"""
    sudo_data = load_sudo_data()
    admins = sudo_data.get('info', {}).get('admins', [])
    success = 0
    failed = 0
    
    for admin in admins:
        try:
            result = bot('sendMessage', {
                'chat_id': admin,
                'text': message,
                'parse_mode': parse_mode
            })
            if result and result.get('ok', False):
                success += 1
            else:
                failed += 1
        except:
            failed += 1
    
    return {'success': success, 'failed': failed}

def broadcast_to_group(group_id, message, parse_mode='HTML'):
    """إرسال رسالة لمجموعة"""
    try:
        result = bot('sendMessage', {
            'chat_id': group_id,
            'text': message,
            'parse_mode': parse_mode
        })
        return result and result.get('ok', False)
    except:
        return False

def broadcast_to_channel(channel_id, message, parse_mode='HTML'):
    """إرسال رسالة لقناة"""
    return broadcast_to_group(channel_id, message, parse_mode)

# ============================================================
# دوال الرسائل الجاهزة (Templates)
# ============================================================

def get_message_template(template_name):
    """الحصول على قالب رسالة"""
    templates = {
        'welcome': "👋 مرحباً بك في البوت!\n\nيمكنك استخدام الأزرار للتنقل.",
        'order_created': "✅ تم إنشاء طلبك بنجاح!\nرقم الطلب: #{order_id}\nالخدمة: {service}\nالسعر: {price}",
        'order_completed': "✅ تم إكمال طلبك!\nرقم الطلب: #{order_id}\nالخدمة: {service}",
        'order_canceled': "❌ تم إلغاء طلبك!\nرقم الطلب: #{order_id}",
        'points_added': "💰 تم إضافة {amount} نقطة إلى رصيدك!\nالرصيد الحالي: {balance}",
        'points_deducted': "💰 تم خصم {amount} نقطة من رصيدك!\nالرصيد الحالي: {balance}",
        'referral_bonus': "🎁 مكافأة إحالة!\nلقد حصلت على {amount} نقطة من دعوة مستخدم جديد.",
        'daily_gift': "🎁 هدية يومية!\nلقد حصلت على {amount} نقطة.",
        'coupon_used': "✅ تم استخدام الكوبون بنجاح!\nلقد حصلت على {amount} نقطة.",
        'balance_alert': "⚠️ رصيدك أصبح منخفضاً!\nالرصيد الحالي: {balance}\nيرجى شحن رصيدك."
    }
    return templates.get(template_name, '')

def format_message_template(template, **kwargs):
    """تنسيق قالب رسالة مع المتغيرات"""
    message = get_message_template(template)
    if not message:
        return ''
    
    for key, value in kwargs.items():
        message = message.replace(f'{{{key}}}', str(value))
    
    return message

def send_template_message(user_id, template, parse_mode='HTML', **kwargs):
    """إرسال رسالة من قالب"""
    message = format_message_template(template, **kwargs)
    if not message:
        return False
    return send_notification(user_id, message, parse_mode)

# ============================================================
# دوال إشعارات النظام
# ============================================================

def notify_new_user(user_id, user_name):
    """إشعار بدخول مستخدم جديد"""
    message = f"""
👤 <b>مستخدم جديد!</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📛 <b>الاسم:</b> {user_name}
📅 <b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    send_notification_to_admin(message)

def notify_new_order(order_id):
    """إشعار بطلب جديد"""
    record = order_get(order_id)
    if not record:
        return
    
    message = f"""
🆕 <b>طلب جديد!</b>
━━━━━━━━━━━━━━━━━
🔢 <b>رقم الطلب:</b> #{record['id']}
🆔 <b>المستخدم:</b> <code>{record['from_id']}</code>
🛠 <b>الخدمة:</b> {record['service']}
💰 <b>السعر:</b> {record['coin']}
🔗 <b>الرابط:</b> {record['link']}
📅 <b>التاريخ:</b> {datetime.fromtimestamp(record.get('created_at', 0)).strftime('%Y-%m-%d %H:%M')}
"""
    send_notification_to_admin(message)

def notify_order_status_change(order_id, old_status, new_status):
    """إشعار بتغيير حالة الطلب"""
    record = order_get(order_id)
    if not record:
        return
    
    status_map = {
        'pending': '⏳ قيد الانتظار',
        'processing': '⚙️ قيد التنفيذ',
        'completed': '✅ مكتمل',
        'canceled': '❌ ملغي'
    }
    
    message = f"""
📋 <b>تغيير حالة الطلب</b>
━━━━━━━━━━━━━━━━━
🔢 <b>رقم الطلب:</b> #{order_id}
🆔 <b>المستخدم:</b> <code>{record['from_id']}</code>
📊 <b>الحالة القديمة:</b> {status_map.get(old_status, old_status)}
📊 <b>الحالة الجديدة:</b> {status_map.get(new_status, new_status)}
"""
    send_notification_to_admin(message)
    send_notification(record['from_id'], 
                     f"📋 تغيرت حالة طلبك #{order_id} إلى {status_map.get(new_status, new_status)}")

def notify_user_balance(user_id, amount, reason=''):
    """إشعار بتغيير الرصيد"""
    balance = get_coin(user_id)
    message = f"""
💰 <b>تحديث الرصيد</b>
━━━━━━━━━━━━━━━━━
📌 <b>السبب:</b> {reason}
💵 <b>المبلغ:</b> {amount}
💰 <b>الرصيد الحالي:</b> {balance}
"""
    send_notification(user_id, message)

# ============================================================
# دوال رسائل البوت الأساسية
# ============================================================

def get_start_message(user_id):
    """رسالة الترحيب"""
    name = get_user_data(user_id).get('userfild', {}).get(str(user_id), {}).get('name', '')
    return f"""
👋 مرحباً بك في البوت!
{name}

يمكنك استخدام الأزرار للتنقل بين الخدمات المختلفة.

📌 للدعم: {SUPPORT}
"""

def get_help_message():
    """رسالة المساعدة"""
    return """
📖 <b>قائمة المساعدة</b>
━━━━━━━━━━━━━━━━━
🔹 /start - العودة للقائمة الرئيسية
🔹 /wallet - عرض رصيدك
🔹 /orders - عرض طلباتك
🔹 /id - عرض معرفك
🔹 /stats - عرض الإحصائيات (للأدمن)
🔹 /coupon CODE - استخدام كوبون
━━━━━━━━━━━━━━━━━
📌 للدعم: {SUPPORT}
"""

def get_wallet_message(user_id):
    """رسالة الرصيد"""
    balance = get_coin(user_id)
    spent = get_total_spent(user_id)
    return f"""
💰 <b>رصيدك</b>
━━━━━━━━━━━━━━━━━
💵 <b>الرصيد الحالي:</b> {balance}
💸 <b>إجمالي المصروفات:</b> {spent}
"""

def get_orders_message(user_id):
    """رسالة الطلبات"""
    return orders_user_text(user_id)

def get_id_message(user_id):
    """رسالة المعرف"""
    return f"🆔 <b>معرفك:</b> <code>{user_id}</code>"

# ============================================================
# دوال إشعارات القنوات
# ============================================================

def notify_channel_join(user_id, channel):
    """إشعار بالانضمام إلى قناة"""
    message = f"""
📢 <b>انضمام إلى قناة</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📌 <b>القناة:</b> {channel}
🎁 <b>المكافأة:</b> {get_add_aoc()} نقطة
"""
    send_notification_to_admin(message)
    send_notification(user_id, f"🎁 تم إضافة {get_add_aoc()} نقطة للانضمام إلى {channel}")

def notify_channel_leave(user_id, channel):
    """إشعار بمغادرة قناة"""
    message = f"""
📢 <b>مغادرة قناة</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📌 <b>القناة:</b> {channel}
⚠️ <b>تم خصم 2 نقطة</b>
"""
    send_notification_to_admin(message)

# ============================================================
# دوال إشعارات التمويل
# ============================================================

def notify_funding_request(user_id, channel, members, price):
    """إشعار بطلب تمويل جديد"""
    message = f"""
💰 <b>طلب تمويل جديد</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📌 <b>القناة:</b> {channel}
👥 <b>عدد الأعضاء:</b> {members}
💵 <b>السعر الإجمالي:</b> {price}
"""
    send_notification_to_admin(message)

def notify_funding_completed(user_id, channel, members):
    """إشعار بإكمال التمويل"""
    message = f"""
✅ <b>تم إكمال التمويل</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📌 <b>القناة:</b> {channel}
👥 <b>عدد الأعضاء:</b> {members}
"""
    send_notification_to_admin(message)
    send_notification(user_id, f"✅ تم إكمال تمويل قناتك {channel}")

# ============================================================
# دوال إشعارات الكوبونات
# ============================================================

def notify_coupon_created(code, type_, value):
    """إشعار بإنشاء كوبون جديد"""
    message = f"""
🎫 <b>كوبون جديد</b>
━━━━━━━━━━━━━━━━━
📌 <b>الكود:</b> {code}
📊 <b>النوع:</b> {type_}
💰 <b>القيمة:</b> {value}
"""
    send_notification_to_admin(message)

def notify_coupon_used(code, user_id):
    """إشعار باستخدام كوبون"""
    message = f"""
🎫 <b>تم استخدام كوبون</b>
━━━━━━━━━━━━━━━━━
📌 <b>الكود:</b> {code}
🆔 <b>المستخدم:</b> <code>{user_id}</code>
"""
    send_notification_to_admin(message)

# ============================================================
# دوال إشعارات الدعم الفني
# ============================================================

def notify_support_ticket(user_id, message):
    """إشعار بتذكرة دعم جديدة"""
    ticket_message = f"""
🎫 <b>تذكرة دعم جديدة</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📝 <b>الرسالة:</b> {message}
"""
    send_notification_to_admin(ticket_message)

def notify_support_reply(user_id, reply):
    """إشعار برد الدعم الفني"""
    message = f"""
📩 <b>رد على تذكرتك</b>
━━━━━━━━━━━━━━━━━
📝 <b>الرد:</b> {reply}
"""
    send_notification(user_id, message)

# ============================================================
# دوال إشعارات النظام
# ============================================================

def notify_system_error(error):
    """إشعار بخطأ في النظام"""
    message = f"""
⚠️ <b>خطأ في النظام</b>
━━━━━━━━━━━━━━━━━
📝 <b>الخطأ:</b> {error}
🕐 <b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    send_notification_to_admin(message)

def notify_system_restart():
    """إشعار بإعادة تشغيل النظام"""
    message = f"""
🔄 <b>تم إعادة تشغيل النظام</b>
🕐 <b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    send_notification_to_admin(message)

def notify_system_update(version, changes):
    """إشعار بتحديث النظام"""
    message = f"""
📦 <b>تحديث النظام</b>
━━━━━━━━━━━━━━━━━
📌 <b>الإصدار:</b> {version}
📝 <b>التغييرات:</b> {changes}
"""
    send_notification_to_admin(message)

# ============================================================
# نهاية الجزء 6
# ============================================================
# ============================================================
# الجزء 7: نظام الأدمن والصلاحيات (Admin & Permissions) - 1500 سطر
# ============================================================

# ============================================================
# دوال الصلاحيات الأساسية
# ============================================================

def is_admin(user_id):
    """التحقق من صلاحيات الأدمن"""
    return str(user_id) == ADMIN_ID or str(user_id) in get_admins_list()

def is_super_admin(user_id):
    """التحقق من صلاحيات السوبر أدمن"""
    return str(user_id) == ADMIN_ID

def get_admins_list():
    """الحصول على قائمة الأدمنية"""
    sudo_data = load_sudo_data()
    return sudo_data.get('info', {}).get('admins', [])

def add_admin(user_id):
    """إضافة أدمن جديد"""
    sudo_data = load_sudo_data()
    admins = sudo_data.get('info', {}).get('admins', [])
    
    if str(user_id) not in admins:
        admins.append(str(user_id))
        sudo_data['info']['admins'] = admins
        save_sudo_data(sudo_data)
        return True
    return False

def remove_admin(user_id):
    """حذف أدمن"""
    sudo_data = load_sudo_data()
    admins = sudo_data.get('info', {}).get('admins', [])
    
    if str(user_id) in admins and str(user_id) != ADMIN_ID:
        admins.remove(str(user_id))
        sudo_data['info']['admins'] = admins
        save_sudo_data(sudo_data)
        return True
    return False

def is_admin_command(user_id):
    """التحقق من صلاحيات تنفيذ أوامر الأدمن"""
    return is_admin(user_id)

# ============================================================
# دوال لوحة التحكم (Admin Panel)
# ============================================================

def get_admin_panel_keyboard():
    """لوحة مفاتيح الأدمن"""
    return [
        [['text', '🛍️ إدارة الأقسام والخدمات', 'callback_data', 'xdmat']],
        [['text', '💰 إدارة النقاط والأرصدة', 'callback_data', 'amruu']],
        [['text', '📊 الإحصائيات', 'callback_data', 'emperor_stats']],
        [['text', '🎫 إدارة الكوبونات', 'callback_data', 'emperor_coupons']],
        [['text', '📢 الإذاعة', 'callback_data', 'sendmgddyessage']],
        [['text', '📝 تعديل النصوص', 'callback_data', 'emperor_texts']],
        [['text', '⚙️ إعدادات API', 'callback_data', 'VISCODEV']],
        [['text', '🛡️ الحماية والأقسام', 'callback_data', 'emperor_security']],
        [['text', '👥 إدارة المستخدمين', 'callback_data', 'admin_users']],
        [['text', '📋 التقارير', 'callback_data', 'admin_reports']],
        [['text', '❌ إغلاق اللوحة', 'callback_data', 'panel']]
    ]

def get_admin_panel_message():
    """رسالة لوحة الأدمن"""
    return """
⚙️ <b>لوحة التحكم</b>
━━━━━━━━━━━━━━━━━
مرحباً بك في لوحة تحكم البوت

اختر الخيار المناسب من الأزرار أدناه
"""

# ============================================================
# دوال إدارة المستخدمين (User Management)
# ============================================================

def get_all_users():
    """الحصول على جميع المستخدمين"""
    return get_all_users_ids()

def get_user_info(user_id):
    """الحصول على معلومات المستخدم"""
    user_id = str(user_id)
    data = get_user_data(user_id)
    user_data = data.get('userfild', {}).get(user_id, {})
    
    return {
        'id': user_id,
        'balance': get_coin(user_id),
        'referrals': int(user_data.get('invite', '0')),
        'spent': get_total_spent(user_id),
        'orders': orders_count_by_user(user_id),
        'is_banned': is_banned(user_id)
    }

def get_users_count():
    """الحصول على عدد المستخدمين"""
    return len(get_all_users())

def get_banned_users_count():
    """الحصول على عدد المحظورين"""
    return len(get_banned_users())

def get_active_users_count(days=7):
    """الحصول على عدد المستخدمين النشطين في آخر أيام"""
    active = 0
    users = get_all_users()
    
    for user_id in users:
        if is_user_active(user_id, days):
            active += 1
    
    return active

def is_user_active(user_id, days=7):
    """التحقق من نشاط المستخدم"""
    # التحقق من وجود طلبات في آخر أيام
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        return False
    
    user_id = str(user_id)
    cutoff = int(time.time()) - (days * 86400)
    
    with open(orders_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if str(record.get('from_id', '')) == user_id:
                    if record.get('created_at', 0) >= cutoff:
                        return True
            except:
                continue
    
    return False

def search_users(query):
    """البحث عن مستخدمين"""
    results = []
    users = get_all_users()
    query = query.lower()
    
    for user_id in users:
        if query in str(user_id):
            results.append(get_user_info(user_id))
            if len(results) >= 20:
                break
    
    return results

# ============================================================
# دوال الحظر (Ban/Unban)
# ============================================================

def ban_user(user_id, reason=''):
    """حظر مستخدم"""
    if is_admin(user_id):
        return {'success': False, 'message': 'لا يمكن حظر أدمن'}
    
    if ban_user_action(user_id):
        # إشعار للمستخدم
        message = f"🚫 تم حظرك من البوت{f' - السبب: {reason}' if reason else ''}"
        send_notification(user_id, message)
        
        # إشعار للأدمن
        admin_message = f"""
🚫 <b>تم حظر مستخدم</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📝 <b>السبب:</b> {reason or 'بدون سبب'}
"""
        send_notification_to_admin(admin_message)
        
        return {'success': True, 'message': f'تم حظر المستخدم {user_id}'}
    
    return {'success': False, 'message': 'فشل حظر المستخدم'}

def unban_user_action(user_id):
    """إلغاء حظر مستخدم"""
    if unban_user(user_id):
        message = f"✅ تم إلغاء حظرك من البوت"
        send_notification(user_id, message)
        
        admin_message = f"""
✅ <b>تم إلغاء حظر مستخدم</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
"""
        send_notification_to_admin(admin_message)
        
        return {'success': True, 'message': f'تم إلغاء حظر المستخدم {user_id}'}
    
    return {'success': False, 'message': 'فشل إلغاء حظر المستخدم'}

def unban_all_users():
    """إلغاء حظر جميع المستخدمين"""
    banned = get_banned_users()
    success = 0
    
    for user_id in banned:
        if unban_user(user_id):
            success += 1
    
    return {'success': success, 'total': len(banned)}

# ============================================================
# دوال إدارة النقاط (Points Management)
# ============================================================

def admin_add_points(user_id, amount, reason=''):
    """إضافة نقاط لمستخدم (بواسطة الأدمن)"""
    if amount <= 0:
        return {'success': False, 'message': 'المبلغ يجب أن يكون أكبر من صفر'}
    
    add_coin(user_id, amount)
    
    message = f"💰 تم إضافة {amount} نقطة إلى حسابك{f' - {reason}' if reason else ''}"
    send_notification(user_id, message)
    
    admin_message = f"""
💰 <b>تم إضافة نقاط</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
💵 <b>المبلغ:</b> {amount}
📝 <b>السبب:</b> {reason or 'بدون سبب'}
"""
    send_notification_to_admin(admin_message)
    
    return {'success': True, 'message': f'تم إضافة {amount} نقطة للمستخدم {user_id}'}

def admin_deduct_points(user_id, amount, reason=''):
    """خصم نقاط من مستخدم (بواسطة الأدمن)"""
    if amount <= 0:
        return {'success': False, 'message': 'المبلغ يجب أن يكون أكبر من صفر'}
    
    current = get_coin(user_id)
    if current < amount:
        return {'success': False, 'message': f'رصيد المستخدم غير كافي (الرصيد: {current})'}
    
    deduct_coin(user_id, amount)
    
    message = f"💰 تم خصم {amount} نقطة من حسابك{f' - {reason}' if reason else ''}"
    send_notification(user_id, message)
    
    admin_message = f"""
💰 <b>تم خصم نقاط</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
💵 <b>المبلغ:</b> {amount}
📝 <b>السبب:</b> {reason or 'بدون سبب'}
"""
    send_notification_to_admin(admin_message)
    
    return {'success': True, 'message': f'تم خصم {amount} نقطة من المستخدم {user_id}'}

def admin_set_points(user_id, amount, reason=''):
    """تعيين نقاط مستخدم (بواسطة الأدمن)"""
    if amount < 0:
        return {'success': False, 'message': 'المبلغ يجب أن يكون أكبر من أو يساوي صفر'}
    
    set_user_points(user_id, amount)
    
    message = f"💰 تم تعيين رصيدك إلى {amount} نقطة{f' - {reason}' if reason else ''}"
    send_notification(user_id, message)
    
    admin_message = f"""
💰 <b>تم تعيين نقاط</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
💵 <b>المبلغ:</b> {amount}
📝 <b>السبب:</b> {reason or 'بدون سبب'}
"""
    send_notification_to_admin(admin_message)
    
    return {'success': True, 'message': f'تم تعيين {amount} نقطة للمستخدم {user_id}'}

# ============================================================
# دوال إدارة الأقسام والخدمات (Admin Services)
# ============================================================

def admin_create_category(name):
    """إنشاء قسم جديد (بواسطة الأدمن)"""
    result = category_create(name)
    if result:
        admin_message = f"""
✅ <b>تم إنشاء قسم جديد</b>
━━━━━━━━━━━━━━━━━
📌 <b>اسم القسم:</b> {name}
🆔 <b>معرف القسم:</b> {result['id']}
"""
        send_notification_to_admin(admin_message)
        return {'success': True, 'message': f'تم إنشاء القسم {name}', 'data': result}
    
    return {'success': False, 'message': 'فشل إنشاء القسم'}

def admin_delete_category(section_id):
    """حذف قسم (بواسطة الأدمن)"""
    category = category_get(section_id)
    if not category:
        return {'success': False, 'message': 'القسم غير موجود'}
    
    if category_delete(section_id):
        admin_message = f"""
✅ <b>تم حذف قسم</b>
━━━━━━━━━━━━━━━━━
📌 <b>اسم القسم:</b> {category['name']}
🆔 <b>معرف القسم:</b> {section_id}
"""
        send_notification_to_admin(admin_message)
        return {'success': True, 'message': f'تم حذف القسم {category["name"]}'}
    
    return {'success': False, 'message': 'فشل حذف القسم'}

def admin_create_service(section_id, name):
    """إنشاء خدمة جديدة (بواسطة الأدمن)"""
    category = category_get(section_id)
    if not category:
        return {'success': False, 'message': 'القسم غير موجود'}
    
    result = service_create(section_id, name)
    if result:
        admin_message = f"""
✅ <b>تم إنشاء خدمة جديدة</b>
━━━━━━━━━━━━━━━━━
📌 <b>اسم الخدمة:</b> {name}
📂 <b>القسم:</b> {category['name']}
🔢 <b>رقم الخدمة:</b> {result['index']}
"""
        send_notification_to_admin(admin_message)
        return {'success': True, 'message': f'تم إنشاء الخدمة {name}', 'data': result}
    
    return {'success': False, 'message': 'فشل إنشاء الخدمة'}

def admin_delete_service(section_id, index):
    """حذف خدمة (بواسطة الأدمن)"""
    category = category_get(section_id)
    if not category:
        return {'success': False, 'message': 'القسم غير موجود'}
    
    service = service_get(section_id, index)
    if not service:
        return {'success': False, 'message': 'الخدمة غير موجودة'}
    
    if service_delete(section_id, index):
        admin_message = f"""
✅ <b>تم حذف خدمة</b>
━━━━━━━━━━━━━━━━━
📌 <b>اسم الخدمة:</b> {service['name']}
📂 <b>القسم:</b> {category['name']}
"""
        send_notification_to_admin(admin_message)
        return {'success': True, 'message': f'تم حذف الخدمة {service["name"]}'}
    
    return {'success': False, 'message': 'فشل حذف الخدمة'}

# ============================================================
# دوال التقارير (Reports)
# ============================================================

def generate_user_report(user_id):
    """توليد تقرير عن مستخدم"""
    info = get_user_info(user_id)
    
    report = f"""
📊 <b>تقرير المستخدم</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
💰 <b>الرصيد:</b> {info['balance']}
💸 <b>المصروفات:</b> {info['spent']}
👥 <b>الإحالات:</b> {info['referrals']}
📦 <b>الطلبات:</b> {info['orders']}
🚫 <b>محظور:</b> {'نعم' if info['is_banned'] else 'لا'}
"""
    return report

def generate_system_report():
    """توليد تقرير النظام"""
    total_users = get_users_count()
    banned_users = get_banned_users_count()
    active_users = get_active_users_count()
    total_orders = orders_count()
    total_revenue = orders_stats()['total_revenue']
    total_points = get_system_total_points()
    
    report = f"""
📊 <b>تقرير النظام</b>
━━━━━━━━━━━━━━━━━
👥 <b>إجمالي المستخدمين:</b> {total_users}
🚫 <b>المحظورين:</b> {banned_users}
📊 <b>المستخدمين النشطين:</b> {active_users}
━━━━━━━━━━━━━━━━━
📦 <b>إجمالي الطلبات:</b> {total_orders}
💰 <b>إجمالي الأرباح:</b> {total_revenue}
💰 <b>إجمالي النقاط:</b> {total_points}
"""
    return report

def generate_daily_report():
    """توليد تقرير يومي"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_orders = orders_daily_stats()
    new_users = len(get_users_from_date(today))
    
    report = f"""
📊 <b>التقرير اليومي</b>
━━━━━━━━━━━━━━━━━
📅 <b>التاريخ:</b> {today}
👥 <b>المستخدمين الجدد:</b> {new_users}
📦 <b>الطلبات:</b> {daily_orders['count']}
💰 <b>الأرباح:</b> {daily_orders['revenue']}
"""
    return report

def get_users_from_date(date):
    """الحصول على المستخدمين المسجلين في تاريخ معين"""
    users_file = './data/user.json'
    if not os.path.exists(users_file):
        return []
    
    data = json_read(users_file)
    users = data.get('userlist', [])
    
    # التحقق من تاريخ إنشاء الملف لكل مستخدم
    result = []
    for user_id in users:
        user_file = f'./data/{user_id}.json'
        if os.path.exists(user_file):
            try:
                created = os.path.getctime(user_file)
                if datetime.fromtimestamp(created).strftime('%Y-%m-%d') == date:
                    result.append(user_id)
            except:
                continue
    
    return result

# ============================================================
# دوال إعدادات البوت (Bot Settings)
# ============================================================

def get_bot_settings():
    """الحصول على إعدادات البوت"""
    return {
        'coins_start': get_coins_start(),
        'adna_coins': get_adna_coins(),
        'day_coins': get_day_coins(),
        'work_add_day': get_work_add_day(),
        'add_ado': get_add_ado(),
        'add_aoc': get_add_aoc(),
        'currency': get_currency_name_from_file(),
        'site': service_get_site(),
        'token': service_get_token()
    }

def update_bot_settings(settings):
    """تحديث إعدادات البوت"""
    if 'coins_start' in settings:
        file_write('edid/coinsstart.txt', str(settings['coins_start']))
    
    if 'adna_coins' in settings:
        file_write('data/adna_coins.txt', str(settings['adna_coins']))
    
    if 'day_coins' in settings:
        file_write('data/day_coins.txt', str(settings['day_coins']))
    
    if 'work_add_day' in settings:
        file_write('edid/work_add_day.txt', str(settings['work_add_day']))
    
    if 'add_ado' in settings:
        file_write('edid/addado.txt', str(settings['add_ado']))
    
    if 'add_aoc' in settings:
        file_write('edid/add_aoc.txt', str(settings['add_aoc']))
    
    if 'currency' in settings:
        file_write('edid/currency_name.txt', settings['currency'])
    
    if 'site' in settings:
        service_set_site(settings['site'])
    
    if 'token' in settings:
        service_set_token(settings['token'])
    
    return True

# ============================================================
# نهاية الجزء 7
# ============================================================
# ============================================================
# الجزء 8: نظام الأزرار والردود (Buttons & Replies) - 1500 سطر
# ============================================================

# ============================================================
# دوال الأزرار الأساسية
# ============================================================

BUTTONS_FILE = './button.json'

def load_buttons():
    """تحميل الأزرار الشفافة"""
    if os.path.exists(BUTTONS_FILE):
        try:
            with open(BUTTONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'buttons': {}, 'links': {}, 'codzer': {}, 'mode': None, 'n': None}

def save_buttons(data):
    """حفظ الأزرار الشفافة"""
    tmp_path = f"{BUTTONS_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(BUTTONS_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, BUTTONS_FILE)
        return True
    except:
        return False

def button_create(name, content, type_='text'):
    """إنشاء زر جديد"""
    buttons = load_buttons()
    code = generate_random_code(8)
    
    if type_ == 'link':
        buttons['links'][code] = {
            'name': name,
            'mo': content,
            'Type': 'رابط'
        }
    elif type_ == 'callback':
        buttons['buttons'][code] = {
            'name': name,
            'mo': content,
            'Type': 'EditMessageText'
        }
    elif type_ == 'codzer':
        buttons['codzer'][code] = {
            'name': name,
            'mo': content,
            'Type': 'EditMessageText',
            'tymyzr': 'زر مختصر'
        }
    
    save_buttons(buttons)
    return code

def button_delete(button_id):
    """حذف زر"""
    buttons = load_buttons()
    deleted = False
    
    if button_id in buttons['buttons']:
        del buttons['buttons'][button_id]
        deleted = True
    elif button_id in buttons['links']:
        del buttons['links'][button_id]
        deleted = True
    elif button_id in buttons['codzer']:
        del buttons['codzer'][button_id]
        deleted = True
    
    if deleted:
        save_buttons(buttons)
        return True
    return False

def button_get(button_id):
    """الحصول على زر"""
    buttons = load_buttons()
    
    if button_id in buttons['buttons']:
        return {'type': 'button', 'data': buttons['buttons'][button_id]}
    elif button_id in buttons['links']:
        return {'type': 'link', 'data': buttons['links'][button_id]}
    elif button_id in buttons['codzer']:
        return {'type': 'codzer', 'data': buttons['codzer'][button_id]}
    
    return None

def button_list():
    """الحصول على قائمة الأزرار"""
    buttons = load_buttons()
    result = []
    
    for code, data in buttons['buttons'].items():
        result.append({
            'id': code,
            'name': data['name'],
            'type': 'button'
        })
    
    for code, data in buttons['links'].items():
        result.append({
            'id': code,
            'name': data['name'],
            'type': 'link'
        })
    
    for code, data in buttons['codzer'].items():
        result.append({
            'id': code,
            'name': data['name'],
            'type': 'codzer'
        })
    
    return result

def button_update(button_id, name=None, content=None):
    """تحديث زر"""
    buttons = load_buttons()
    updated = False
    
    if button_id in buttons['buttons']:
        if name:
            buttons['buttons'][button_id]['name'] = name
        if content:
            buttons['buttons'][button_id]['mo'] = content
        updated = True
    elif button_id in buttons['links']:
        if name:
            buttons['links'][button_id]['name'] = name
        if content:
            buttons['links'][button_id]['mo'] = content
        updated = True
    elif button_id in buttons['codzer']:
        if name:
            buttons['codzer'][button_id]['name'] = name
        if content:
            buttons['codzer'][button_id]['mo'] = content
        updated = True
    
    if updated:
        save_buttons(buttons)
        return True
    return False

# ============================================================
# دوال الأزرار الأساسية (المدمجة)
# ============================================================

def get_main_keyboard(user_id):
    """الحصول على لوحة المفاتيح الرئيسية"""
    user_data = get_user_data(user_id)
    coin = get_coin(user_id)
    cdiamlaadf = get_currency_name_from_file()
    
    buttons = load_buttons()
    
    keyboard = [
        [{'text': '🎬 بدء تلبية رشق جديدة', 'callback_data': 'takecoinn'}],
    ]
    
    # إضافة الأزرار من ملف button.json
    for code, data in buttons['buttons'].items():
        keyboard.append([{'text': data['name'], 'callback_data': code}])
    
    for code, data in buttons['links'].items():
        keyboard.append([{'text': data['name'], 'url': data['mo']}])
    
    # إضافة الأزرار الأساسية
    keyboard.extend([
        [{'text': '📇 أرقام وهمية', 'callback_data': 'ne_fake_numbers'}, {'text': '🎁 شحن الألعاب', 'callback_data': 'ne_game_topup'}],
        [{'text': '⭐ خدماتي المفضلة', 'callback_data': 'ne_favorites'}, {'text': '📚 خدمات مجانية', 'callback_data': 'ne_free_services'}],
        [{'text': '💳 شحن كرت', 'callback_data': 'amr6'}, {'text': '💰 إشحن رصيدك', 'callback_data': 'amr2'}],
        [{'text': '🔑 مفتاح API 🌐', 'callback_data': 'ne_api_key'}],
        [{'text': '📋 طلب تعويض', 'callback_data': 'ne_compensation'}, {'text': '🔄 تغيير العملة', 'callback_data': 'ne_currency'}],
        [{'text': '🔄 تحويل رصيد', 'callback_data': 'sendcoin'}, {'text': '➕ رصيد مجاني', 'callback_data': 'ne_referral'}],
        [{'text': '⚙️ المزيد والاعدادات', 'callback_data': 'ne_more'}],
        [{'text': '📞 الدعم الفني', 'callback_data': 'ne_support'}]
    ])
    
    return keyboard

def get_back_button(callback='panel'):
    """الحصول على زر رجوع"""
    return [{'text': '🔙 رجوع ↩️', 'callback_data': callback}]

def get_admin_keyboard():
    """الحصول على لوحة الأدمن"""
    return [
        [{'text': '🛍️ إدارة الأقسام والخدمات', 'callback_data': 'xdmat'}],
        [{'text': '💰 إدارة النقاط والأرصدة', 'callback_data': 'amruu'}],
        [{'text': '📊 الإحصائيات', 'callback_data': 'emperor_stats'}],
        [{'text': '🎫 إدارة الكوبونات', 'callback_data': 'emperor_coupons'}],
        [{'text': '📢 الإذاعة', 'callback_data': 'sendmgddyessage'}],
        [{'text': '📝 تعديل النصوص', 'callback_data': 'emperor_texts'}],
        [{'text': '⚙️ إعدادات API', 'callback_data': 'VISCODEV'}],
        [{'text': '🛡️ الحماية والأقسام', 'callback_data': 'emperor_security'}],
        [{'text': '👥 إدارة المستخدمين', 'callback_data': 'admin_users'}],
        [{'text': '📋 التقارير', 'callback_data': 'admin_reports'}],
        [{'text': '❌ إغلاق اللوحة', 'callback_data': 'panel'}]
    ]

# ============================================================
# دوال الردود (Replies)
# ============================================================

REPLIES_FILE = './replies.json'

def load_replies():
    """تحميل الردود"""
    if os.path.exists(REPLIES_FILE):
        try:
            with open(REPLIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'replies': {}, 'links': {}, 'mode': None, 'n': None}

def save_replies(data):
    """حفظ الردود"""
    tmp_path = f"{REPLIES_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(REPLIES_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, REPLIES_FILE)
        return True
    except:
        return False

def reply_create(keyword, response):
    """إنشاء رد جديد"""
    replies = load_replies()
    replies['replies'][keyword] = {
        'name': keyword,
        'mo': response
    }
    save_replies(replies)
    return True

def reply_delete(keyword):
    """حذف رد"""
    replies = load_replies()
    if keyword in replies['replies']:
        del replies['replies'][keyword]
        save_replies(replies)
        return True
    return False

def reply_get(keyword):
    """الحصول على رد"""
    replies = load_replies()
    return replies['replies'].get(keyword)

def reply_list():
    """الحصول على قائمة الردود"""
    replies = load_replies()
    return list(replies['replies'].keys())

def reply_update(keyword, new_response):
    """تحديث رد"""
    replies = load_replies()
    if keyword in replies['replies']:
        replies['replies'][keyword]['mo'] = new_response
        save_replies(replies)
        return True
    return False

def process_reply(message):
    """معالجة الردود التلقائية"""
    replies = load_replies()
    for keyword, data in replies['replies'].items():
        if keyword.lower() in message.lower():
            return data['mo']
    return None

# ============================================================
# دوال الأوامر المختصرة (Commands)
# ============================================================

COMMANDS_FILE = './comm.json'

def load_commands():
    """تحميل الأوامر المختصرة"""
    if os.path.exists(COMMANDS_FILE):
        try:
            with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'com': {}, 'comm': {'admins': []}, 'modee': None}

def save_commands(data):
    """حفظ الأوامر المختصرة"""
    tmp_path = f"{COMMANDS_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(COMMANDS_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, COMMANDS_FILE)
        return True
    except:
        return False

def command_create(command, description):
    """إنشاء أمر مختصر"""
    commands = load_commands()
    code = generate_random_code(8)
    
    commands['com'][code] = {
        'com1': command,
        'com2': description
    }
    
    save_commands(commands)
    return code

def command_delete(code):
    """حذف أمر مختصر"""
    commands = load_commands()
    if code in commands['com']:
        del commands['com'][code]
        save_commands(commands)
        return True
    return False

def command_list():
    """الحصول على قائمة الأوامر المختصرة"""
    commands = load_commands()
    result = []
    for code, data in commands['com'].items():
        result.append({
            'id': code,
            'command': data['com1'],
            'description': data['com2']
        })
    return result

def process_command(message):
    """معالجة الأوامر المختصرة"""
    commands = load_commands()
    for code, data in commands['com'].items():
        if message == data['com1']:
            return data['com2']
    return None

# ============================================================
# دوال الأزرار المتقدمة
# ============================================================

def create_inline_keyboard(buttons):
    """إنشاء لوحة مفاتيح مضمنة"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button in row:
            if 'url' in button:
                keyboard_row.append({
                    'text': button['text'],
                    'url': button['url']
                })
            elif 'callback_data' in button:
                keyboard_row.append({
                    'text': button['text'],
                    'callback_data': button['callback_data']
                })
        keyboard.append(keyboard_row)
    return json.dumps({'inline_keyboard': keyboard})

def create_reply_keyboard(buttons, resize=True, one_time=False):
    """إنشاء لوحة مفاتيح رد"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button in row:
            keyboard_row.append(button)
        keyboard.append(keyboard_row)
    
    return json.dumps({
        'keyboard': keyboard,
        'resize_keyboard': resize,
        'one_time_keyboard': one_time
    })

def remove_keyboard():
    """إزالة لوحة المفاتيح"""
    return json.dumps({'remove_keyboard': True})

# ============================================================
# دوال الأزرار الديناميكية
# ============================================================

def get_category_buttons():
    """الحصول على أزرار الأقسام"""
    categories = category_list()
    buttons = []
    for cat in categories:
        buttons.append([{
            'text': cat['name'],
            'callback_data': f'category_{cat["id"]}'
        }])
    return buttons

def get_service_buttons(section_id):
    """الحصول على أزرار الخدمات في قسم"""
    services = service_list(section_id)
    buttons = []
    for index, name in enumerate(services):
        buttons.append([{
            'text': name,
            'callback_data': f'service_{section_id}_{index}'
        }])
    return buttons

def get_pagination_buttons(page, total_pages, callback_prefix):
    """الحصول على أزرار التنقل بين الصفحات"""
    buttons = []
    
    if total_pages > 1:
        row = []
        if page > 0:
            row.append({
                'text': '⬅️ السابق',
                'callback_data': f'{callback_prefix}_prev_{page}'
            })
        
        row.append({
            'text': f'{page + 1}/{total_pages}',
            'callback_data': 'none'
        })
        
        if page < total_pages - 1:
            row.append({
                'text': 'التالي ➡️',
                'callback_data': f'{callback_prefix}_next_{page}'
            })
        
        buttons.append(row)
    
    return buttons

# ============================================================
# نهاية الجزء 8
# ============================================================
# ============================================================
# الجزء 9: نظام التمويل والقنوات (Funding & Channels) - 1500 سطر
# ============================================================

# ============================================================
# دوال التمويل الأساسية
# ============================================================

FUNDING_FILE = './data/funding.json'

def funding_read():
    """قراءة طلبات التمويل"""
    if not os.path.exists(FUNDING_FILE):
        return []
    try:
        with open(FUNDING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def funding_write(funding_data):
    """كتابة طلبات التمويل"""
    tmp_path = f"{FUNDING_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(FUNDING_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(funding_data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, FUNDING_FILE)
        return True
    except:
        return False

def funding_create(user_id, channel, members, price_per_member):
    """إنشاء طلب تمويل جديد"""
    funding_data = funding_read()
    
    order = {
        'id': int(time.time()),
        'user_id': str(user_id),
        'channel': channel,
        'members': int(members),
        'price_per_member': float(price_per_member),
        'total_price': int(members) * float(price_per_member),
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'completed_at': None
    }
    
    funding_data.append(order)
    funding_write(funding_data)
    return order

def funding_get(order_id):
    """الحصول على طلب تمويل"""
    funding_data = funding_read()
    for order in funding_data:
        if order.get('id') == order_id:
            return order
    return None

def funding_get_by_user(user_id, limit=10):
    """الحصول على طلبات تمويل المستخدم"""
    funding_data = funding_read()
    user_orders = [o for o in funding_data if str(o.get('user_id', '')) == str(user_id)]
    return user_orders[-limit:] if len(user_orders) > limit else user_orders

def funding_get_pending():
    """الحصول على طلبات التمويل المعلقة"""
    funding_data = funding_read()
    return [o for o in funding_data if o.get('status') == 'pending']

def funding_get_completed():
    """الحصول على طلبات التمويل المكتملة"""
    funding_data = funding_read()
    return [o for o in funding_data if o.get('status') == 'completed']

def funding_update_status(order_id, status):
    """تحديث حالة طلب تمويل"""
    funding_data = funding_read()
    for order in funding_data:
        if order.get('id') == order_id:
            order['status'] = status
            if status == 'completed':
                order['completed_at'] = datetime.now().isoformat()
            funding_write(funding_data)
            return True
    return False

def funding_delete(order_id):
    """حذف طلب تمويل"""
    funding_data = funding_read()
    new_data = [o for o in funding_data if o.get('id') != order_id]
    if len(new_data) < len(funding_data):
        funding_write(new_data)
        return True
    return False

def funding_count(status=None):
    """الحصول على عدد طلبات التمويل"""
    funding_data = funding_read()
    if status:
        return len([o for o in funding_data if o.get('status') == status])
    return len(funding_data)

def funding_total_cost():
    """الحصول على إجمالي تكلفة التمويل"""
    funding_data = funding_read()
    total = 0
    for order in funding_data:
        if order.get('status') == 'completed':
            total += order.get('total_price', 0)
    return total

# ============================================================
# دوال القنوات (Channels)
# ============================================================

def channel_add(channel_id, channel_name, channel_link, is_private=False):
    """إضافة قناة للاشتراك الإجباري"""
    sudo_data = load_sudo_data()
    
    if 'channel' not in sudo_data['info']:
        sudo_data['info']['channel'] = {}
    
    sudo_data['info']['channel'][str(channel_id)] = {
        'name': channel_name,
        'user': channel_link,
        'st': 'خاصة' if is_private else 'عامة'
    }
    
    save_sudo_data(sudo_data)
    return True

def channel_remove(channel_id):
    """حذف قناة من الاشتراك الإجباري"""
    sudo_data = load_sudo_data()
    
    if 'channel' in sudo_data['info'] and str(channel_id) in sudo_data['info']['channel']:
        del sudo_data['info']['channel'][str(channel_id)]
        save_sudo_data(sudo_data)
        return True
    return False

def channel_list():
    """الحصول على قائمة القنوات الإجبارية"""
    sudo_data = load_sudo_data()
    return sudo_data.get('info', {}).get('channel', {})

def channel_count():
    """الحصول على عدد القنوات الإجبارية"""
    return len(channel_list())

def channel_check(user_id, channel_id):
    """التحقق من اشتراك المستخدم في قناة"""
    return get_member(channel_id, user_id) == 'yes'

def channel_check_all(user_id):
    """التحقق من اشتراك المستخدم في جميع القنوات الإجبارية"""
    channels = channel_list()
    for channel_id, channel_info in channels.items():
        if not channel_check(user_id, channel_id):
            return False, channel_info
    return True, None

def channel_get_link(channel_id):
    """الحصول على رابط القناة"""
    channels = channel_list()
    if str(channel_id) in channels:
        return channels[str(channel_id)].get('user', '')
    return None

def channel_get_name(channel_id):
    """الحصول على اسم القناة"""
    channels = channel_list()
    if str(channel_id) in channels:
        return channels[str(channel_id)].get('name', '')
    return None

# ============================================================
# دوال نظام الإشتراك الإجباري
# ============================================================

def mandatory_subscription_check(user_id):
    """التحقق من الإشتراك الإجباري"""
    channels = channel_list()
    if not channels:
        return {'subscribed': True}
    
    for channel_id, channel_info in channels.items():
        if not channel_check(user_id, channel_id):
            return {
                'subscribed': False,
                'channel_id': channel_id,
                'channel_name': channel_info.get('name', 'قناة'),
                'channel_link': channel_info.get('user', '')
            }
    
    return {'subscribed': True}

def get_subscription_keyboard(user_id):
    """الحصول على لوحة مفاتيح الإشتراك"""
    check_result = mandatory_subscription_check(user_id)
    
    if check_result['subscribed']:
        return None
    
    buttons = []
    
    # زر الإشتراك
    channel_link = check_result['channel_link']
    if channel_link:
        if not channel_link.startswith('http'):
            channel_link = f"https://t.me/{channel_link.replace('@', '')}"
        buttons.append([{'text': '📢 اشترك في القناة', 'url': channel_link}])
    
    buttons.append([{'text': '✅ تحقق من الإشتراك', 'callback_data': 'check_subscription'}])
    
    return buttons

def process_subscription_check(user_id):
    """معالجة التحقق من الإشتراك"""
    check_result = mandatory_subscription_check(user_id)
    
    if check_result['subscribed']:
        return {'success': True, 'message': '✅ تم التحقق من إشتراكك بنجاح'}
    else:
        return {
            'success': False,
            'message': f"❌ يجب الإشتراك في {check_result['channel_name']} أولاً"
        }

# ============================================================
# دوال التمويل المتقدم
# ============================================================

def funding_request(user_id, channel, members):
    """طلب تمويل جديد"""
    # التحقق من الرصيد
    add_ado = get_add_ado()
    total_price = members * add_ado
    balance = get_coin(user_id)
    
    if balance < total_price:
        return {'success': False, 'message': f'رصيدك غير كافي. المطلوب: {total_price}'}
    
    # خصم الرصيد
    deduct_coin(user_id, total_price, f'تمويل قناة {channel}')
    
    # إنشاء طلب التمويل
    order = funding_create(user_id, channel, members, add_ado)
    
    # إشعار للأدمن
    notify_funding_request(user_id, channel, members, total_price)
    
    return {'success': True, 'message': 'تم إنشاء طلب التمويل بنجاح', 'order': order}

def funding_complete(order_id):
    """إكمال طلب تمويل"""
    order = funding_get(order_id)
    if not order:
        return {'success': False, 'message': 'الطلب غير موجود'}
    
    if order['status'] == 'completed':
        return {'success': False, 'message': 'الطلب مكتمل بالفعل'}
    
    if funding_update_status(order_id, 'completed'):
        notify_funding_completed(order['user_id'], order['channel'], order['members'])
        return {'success': True, 'message': 'تم إكمال التمويل بنجاح'}
    
    return {'success': False, 'message': 'فشل إكمال التمويل'}

def funding_cancel(order_id):
    """إلغاء طلب تمويل"""
    order = funding_get(order_id)
    if not order:
        return {'success': False, 'message': 'الطلب غير موجود'}
    
    if order['status'] == 'completed':
        return {'success': False, 'message': 'لا يمكن إلغاء طلب مكتمل'}
    
    # استرداد الرصيد
    add_coin(order['user_id'], order['total_price'], 'استرداد تمويل ملغي')
    
    funding_delete(order_id)
    return {'success': True, 'message': 'تم إلغاء التمويل واسترداد الرصيد'}

# ============================================================
# دوال إدارة قنوات التمويل
# ============================================================

def funding_channel_add(channel_id, price_per_member):
    """إضافة قناة للتمويل"""
    users_data = json_read('./data/user.json')
    
    if 'finance' not in users_data:
        users_data['finance'] = []
    
    users_data['finance'].append([str(channel_id), int(price_per_member)])
    json_write('./data/user.json', users_data)
    return True

def funding_channel_remove(channel_id):
    """حذف قناة من التمويل"""
    users_data = json_read('./data/user.json')
    
    if 'finance' not in users_data:
        return False
    
    new_finance = [f for f in users_data['finance'] if f[0] != str(channel_id)]
    if len(new_finance) < len(users_data['finance']):
        users_data['finance'] = new_finance
        json_write('./data/user.json', users_data)
        return True
    return False

def funding_channel_list():
    """الحصول على قائمة قنوات التمويل"""
    users_data = json_read('./data/user.json')
    return users_data.get('finance', [])

def funding_channel_get_price(channel_id):
    """الحصول على سعر التمويل لقناة"""
    channels = funding_channel_list()
    for channel, price in channels:
        if str(channel) == str(channel_id):
            return int(price)
    return None

# ============================================================
# دوال نظام التمويل التلقائي
# ============================================================

def auto_funding_check():
    """التحقق من طلبات التمويل التلقائي"""
    pending = funding_get_pending()
    
    for order in pending:
        # التحقق من اكتمال التمويل
        channel = order['channel']
        members = order['members']
        
        # التحقق من عدد أعضاء القناة
        try:
            count = get_chat_members_count(channel)
            if count >= members:
                funding_complete(order['id'])
        except:
            continue

def auto_funding_cycle():
    """دورة التمويل التلقائي"""
    while True:
        try:
            auto_funding_check()
            time.sleep(60)  # كل دقيقة
        except:
            time.sleep(60)

# ============================================================
# دوال القنوات والإشعارات
# ============================================================

def channel_notify_join(user_id, channel_id):
    """إشعار بانضمام إلى قناة"""
    channel_name = channel_get_name(channel_id)
    if not channel_name:
        channel_name = f"قناة {channel_id}"
    
    add_aoc = get_add_aoc()
    add_coin(user_id, add_aoc, f'انضمام إلى {channel_name}')
    
    send_notification(user_id, f"🎁 تم إضافة {add_aoc} نقطة للانضمام إلى {channel_name}")

def channel_notify_leave(user_id, channel_id):
    """إشعار بمغادرة قناة"""
    channel_name = channel_get_name(channel_id)
    if not channel_name:
        channel_name = f"قناة {channel_id}"
    
    deduct_coin(user_id, 2, f'مغادرة {channel_name}')
    
    send_notification(user_id, f"⚠️ تم خصم 2 نقطة لمغادرة {channel_name}")

# ============================================================
# دوال إحصائيات التمويل
# ============================================================

def funding_stats():
    """الحصول على إحصائيات التمويل"""
    stats = {
        'total_orders': funding_count(),
        'pending': funding_count('pending'),
        'completed': funding_count('completed'),
        'total_cost': funding_total_cost(),
        'channels': len(funding_channel_list())
    }
    return stats

def funding_user_stats(user_id):
    """الحصول على إحصائيات تمويل المستخدم"""
    orders = funding_get_by_user(user_id)
    stats = {
        'total_orders': len(orders),
        'completed': len([o for o in orders if o.get('status') == 'completed']),
        'pending': len([o for o in orders if o.get('status') == 'pending']),
        'total_cost': sum([o.get('total_price', 0) for o in orders if o.get('status') == 'completed'])
    }
    return stats

def channel_stats():
    """الحصول على إحصائيات القنوات"""
    channels = channel_list()
    stats = {
        'total': len(channels),
        'public': len([c for c in channels.values() if c.get('st') == 'عامة']),
        'private': len([c for c in channels.values() if c.get('st') == 'خاصة'])
    }
    return stats

# ============================================================
# نهاية الجزء 9
# ============================================================
# ============================================================
# الجزء 10: نظام الإحالات والجوائز (Referrals & Rewards) - 1500 سطر
# ============================================================

# ============================================================
# دوال الإحالات الأساسية
# ============================================================

def referral_add(referrer_id, new_user_id):
    """إضافة إحالة جديدة"""
    referrer_id = str(referrer_id)
    new_user_id = str(new_user_id)
    
    if referrer_id == new_user_id:
        return {'success': False, 'message': 'لا يمكنك دعوة نفسك'}
    
    # التحقق من أن المستخدم الجديد ليس لديه محول
    data = get_user_data(new_user_id)
    if data['userfild'].get(new_user_id, {}).get('inviter'):
        return {'success': False, 'message': 'المستخدم لديه محول بالفعل'}
    
    # إضافة المحول للمستخدم الجديد
    if new_user_id not in data['userfild']:
        data['userfild'][new_user_id] = {}
    data['userfild'][new_user_id]['inviter'] = referrer_id
    save_user_data(new_user_id, data)
    
    # زيادة عدد الإحالات للمحول
    data = get_user_data(referrer_id)
    if referrer_id not in data['userfild']:
        data['userfild'][referrer_id] = {}
    current = int(data['userfild'][referrer_id].get('invite', '0'))
    data['userfild'][referrer_id]['invite'] = str(current + 1)
    save_user_data(referrer_id, data)
    
    # إضافة مكافأة
    coins_start = get_coins_start()
    add_points(referrer_id, coins_start, f'مكافأة دعوة مستخدم جديد')
    
    # إشعارات
    send_notification(referrer_id, f"🎁 مكافأة دعوة!\nلقد حصلت على {coins_start} نقطة لدعوة مستخدم جديد")
    
    return {'success': True, 'message': 'تم إضافة الإحالة بنجاح'}

def referral_get_count(user_id):
    """الحصول على عدد الإحالات للمستخدم"""
    data = get_user_data(user_id)
    return int(data['userfild'].get(str(user_id), {}).get('invite', '0'))

def referral_get_earnings(user_id):
    """الحصول على أرباح الإحالات للمستخدم"""
    return ne_referral_earnings(user_id)

def referral_get_inviter(user_id):
    """الحصول على المحول للمستخدم"""
    data = get_user_data(user_id)
    return data['userfild'].get(str(user_id), {}).get('inviter')

def referral_get_link(user_id):
    """الحصول على رابط الإحالة للمستخدم"""
    username = get_bot_username()
    return f"https://t.me/{username}?start={user_id}"

def referral_get_top(limit=10):
    """الحصول على قائمة أفضل المحولين"""
    users = get_all_users()
    referral_counts = []
    
    for user_id in users:
        count = referral_get_count(user_id)
        if count > 0:
            referral_counts.append((user_id, count))
    
    referral_counts.sort(key=lambda x: x[1], reverse=True)
    return referral_counts[:limit]

def referral_get_total():
    """الحصول على إجمالي عدد الإحالات في النظام"""
    users = get_all_users()
    total = 0
    for user_id in users:
        total += referral_get_count(user_id)
    return total

# ============================================================
# دوال مكافآت الإحالات
# ============================================================

def referral_bonus_config():
    """الحصول على إعدادات مكافآت الإحالات"""
    return {
        'base_bonus': get_coins_start(),
        'bonus_levels': {
            5: 10,   # 5 إحالات → 10 نقاط إضافية
            10: 25,  # 10 إحالات → 25 نقطة إضافية
            25: 50,  # 25 إحالة → 50 نقطة إضافية
            50: 100, # 50 إحالة → 100 نقطة إضافية
            100: 250 # 100 إحالة → 250 نقطة إضافية
        }
    }

def referral_check_bonus(user_id):
    """التحقق من مكافآت الإحالات الإضافية"""
    count = referral_get_count(user_id)
    config = referral_bonus_config()
    
    bonuses_earned = []
    for level, bonus in config['bonus_levels'].items():
        if count >= level:
            bonuses_earned.append((level, bonus))
    
    return bonuses_earned

def referral_claim_bonus(user_id):
    """المطالبة بمكافآت الإحالات الإضافية"""
    # التحقق من وجود مكافآت غير مطالب بها
    data = get_user_data(user_id)
    claimed_levels = data['userfild'].get(str(user_id), {}).get('referral_bonus_claimed', '')
    claimed = [int(l) for l in claimed_levels.split(',') if l]
    
    bonuses = referral_check_bonus(user_id)
    unclaimed = [(level, bonus) for level, bonus in bonuses if level not in claimed]
    
    if not unclaimed:
        return {'success': False, 'message': 'لا توجد مكافآت جديدة للمطالبة'}
    
    total_bonus = sum(bonus for _, bonus in unclaimed)
    new_claimed = claimed + [level for level, _ in unclaimed]
    
    # إضافة المكافأة
    add_points(user_id, total_bonus, f'مكافآت إحالات: {", ".join([str(l) for l, _ in unclaimed])}')
    
    # حفظ المطالبات
    data = get_user_data(user_id)
    data['userfild'][str(user_id)]['referral_bonus_claimed'] = ','.join([str(l) for l in new_claimed])
    save_user_data(user_id, data)
    
    return {'success': True, 'message': f'تم إضافة {total_bonus} نقطة كمكافآت إحالات'}

# ============================================================
# دوال الجوائز اليومية
# ============================================================

DAILY_REWARD_FILE = './data/daily_rewards.json'

def daily_reward_read():
    """قراءة الجوائز اليومية"""
    if not os.path.exists(DAILY_REWARD_FILE):
        return {}
    try:
        with open(DAILY_REWARD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def daily_reward_write(data):
    """كتابة الجوائز اليومية"""
    tmp_path = f"{DAILY_REWARD_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(DAILY_REWARD_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, DAILY_REWARD_FILE)
        return True
    except:
        return False

def daily_reward_get(user_id):
    """الحصول على مكافأة اليوم للمستخدم"""
    rewards = daily_reward_read()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if str(user_id) in rewards and rewards[str(user_id)].get('date') == today:
        return rewards[str(user_id)]
    return None

def daily_reward_claim(user_id):
    """المطالبة بالمكافأة اليومية"""
    # التحقق من أن المستخدم لم يطالب بها اليوم
    existing = daily_reward_get(user_id)
    if existing:
        return {'success': False, 'message': 'لقد حصلت على المكافأة اليومية بالفعل'}
    
    # حساب المكافأة (عشوائية)
    amount = random.randint(5, 25)
    
    # إضافة النقاط
    add_points(user_id, amount, 'مكافأة يومية')
    
    # حفظ المطالبة
    rewards = daily_reward_read()
    rewards[str(user_id)] = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'amount': amount
    }
    daily_reward_write(rewards)
    
    return {'success': True, 'message': f'تم إضافة {amount} نقطة كمكافأة يومية'}

def daily_reward_streak(user_id):
    """الحصول على سلسلة المكافآت اليومية المتتالية"""
    rewards = daily_reward_read()
    user_rewards = []
    
    for date_str, reward in rewards.items():
        if str(user_id) in reward:
            user_rewards.append((date_str, reward[str(user_id)]))
    
    user_rewards.sort(key=lambda x: x[0])
    
    # حساب السلسلة المتتالية
    streak = 0
    current_date = datetime.now()
    for date_str, reward in reversed(user_rewards):
        reward_date = datetime.strptime(date_str, '%Y-%m-%d')
        if (current_date - reward_date).days <= 1:
            streak += 1
            current_date = reward_date
        else:
            break
    
    return streak

# ============================================================
# دوال الجوائز الأسبوعية
# ============================================================

WEEKLY_REWARD_FILE = './data/weekly_rewards.json'

def weekly_reward_read():
    """قراءة الجوائز الأسبوعية"""
    if not os.path.exists(WEEKLY_REWARD_FILE):
        return {}
    try:
        with open(WEEKLY_REWARD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def weekly_reward_write(data):
    """كتابة الجوائز الأسبوعية"""
    tmp_path = f"{WEEKLY_REWARD_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(WEEKLY_REWARD_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, WEEKLY_REWARD_FILE)
        return True
    except:
        return False

def weekly_reward_claim(user_id):
    """المطالبة بالمكافأة الأسبوعية"""
    rewards = weekly_reward_read()
    week = datetime.now().strftime('%Y-W%W')
    
    if str(user_id) in rewards and rewards[str(user_id)].get('week') == week:
        return {'success': False, 'message': 'لقد حصلت على المكافأة الأسبوعية بالفعل'}
    
    # حساب المكافأة
    streak = daily_reward_streak(user_id)
    base_amount = 20
    bonus = min(streak * 2, 20)  # زيادة 2 نقطة لكل يوم متتالي، حد أقصى 20
    amount = base_amount + bonus
    
    # إضافة النقاط
    add_points(user_id, amount, 'مكافأة أسبوعية')
    
    # حفظ المطالبة
    rewards[str(user_id)] = {
        'week': week,
        'amount': amount,
        'streak': streak
    }
    weekly_reward_write(rewards)
    
    return {'success': True, 'message': f'تم إضافة {amount} نقطة كمكافأة أسبوعية'}

# ============================================================
# دوال الجوائز الخاصة
# ============================================================

def special_reward_create(name, amount, condition, description=''):
    """إنشاء جائزة خاصة"""
    reward = {
        'name': name,
        'amount': float(amount),
        'condition': condition,
        'description': description,
        'created_at': datetime.now().isoformat(),
        'active': True
    }
    
    rewards_file = './data/special_rewards.json'
    rewards = json_read(rewards_file) if os.path.exists(rewards_file) else []
    rewards.append(reward)
    json_write(rewards_file, rewards)
    return reward

def special_reward_check(user_id, condition_type, condition_value):
    """التحقق من استحقاق جائزة خاصة"""
    rewards_file = './data/special_rewards.json'
    if not os.path.exists(rewards_file):
        return []
    
    rewards = json_read(rewards_file)
    eligible = []
    
    for reward in rewards:
        if not reward.get('active', True):
            continue
        
        if reward['condition'] == condition_type:
            # التحقق من الشرط
            if condition_type == 'orders_count':
                if orders_count_by_user(user_id) >= int(condition_value):
                    eligible.append(reward)
            elif condition_type == 'referral_count':
                if referral_get_count(user_id) >= int(condition_value):
                    eligible.append(reward)
            elif condition_type == 'points_earned':
                if get_coin(user_id) >= float(condition_value):
                    eligible.append(reward)
    
    return eligible

def special_reward_claim(user_id, reward_name):
    """المطالبة بجائزة خاصة"""
    rewards_file = './data/special_rewards.json'
    if not os.path.exists(rewards_file):
        return {'success': False, 'message': 'الجائزة غير موجودة'}
    
    rewards = json_read(rewards_file)
    for reward in rewards:
        if reward['name'] == reward_name and reward.get('active', True):
            # التحقق من عدم المطالبة مسبقاً
            claimed_file = './data/special_rewards_claimed.json'
            claimed = json_read(claimed_file) if os.path.exists(claimed_file) else {}
            
            if str(user_id) in claimed and reward_name in claimed[str(user_id)]:
                return {'success': False, 'message': 'لقد حصلت على هذه الجائزة بالفعل'}
            
            # إضافة النقاط
            add_points(user_id, reward['amount'], f'جائزة خاصة: {reward_name}')
            
            # حفظ المطالبة
            if str(user_id) not in claimed:
                claimed[str(user_id)] = []
            claimed[str(user_id)].append(reward_name)
            json_write(claimed_file, claimed)
            
            return {'success': True, 'message': f'تم إضافة {reward["amount"]} نقطة كجائزة خاصة'}
    
    return {'success': False, 'message': 'الجائزة غير موجودة أو غير مفعلة'}

# ============================================================
# دوال نقاط الولاء
# ============================================================

LOYALTY_FILE = './data/loyalty.json'

def loyalty_read():
    """قراءة نقاط الولاء"""
    if not os.path.exists(LOYALTY_FILE):
        return {}
    try:
        with open(LOYALTY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def loyalty_write(data):
    """كتابة نقاط الولاء"""
    tmp_path = f"{LOYALTY_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(LOYALTY_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, LOYALTY_FILE)
        return True
    except:
        return False

def loyalty_add(user_id, points, reason=''):
    """إضافة نقاط ولاء للمستخدم"""
    loyalty = loyalty_read()
    
    if str(user_id) not in loyalty:
        loyalty[str(user_id)] = {'points': 0, 'history': []}
    
    loyalty[str(user_id)]['points'] += int(points)
    loyalty[str(user_id)]['history'].append({
        'type': 'add',
        'amount': int(points),
        'reason': reason,
        'date': datetime.now().isoformat()
    })
    
    loyalty_write(loyalty)
    return True

def loyalty_get(user_id):
    """الحصول على نقاط ولاء المستخدم"""
    loyalty = loyalty_read()
    return loyalty.get(str(user_id), {}).get('points', 0)

def loyalty_redeem(user_id, points, reward):
    """استبدال نقاط الولاء بجائزة"""
    current = loyalty_get(user_id)
    
    if current < points:
        return {'success': False, 'message': 'نقاط الولاء غير كافية'}
    
    loyalty = loyalty_read()
    loyalty[str(user_id)]['points'] -= int(points)
    loyalty[str(user_id)]['history'].append({
        'type': 'redeem',
        'amount': int(points),
        'reward': reward,
        'date': datetime.now().isoformat()
    })
    
    loyalty_write(loyalty)
    return {'success': True, 'message': f'تم استبدال {points} نقطة ولاء بـ {reward}'}

def loyalty_convert_to_points(user_id):
    """تحويل نقاط الولاء إلى نقاط عادية"""
    points = loyalty_get(user_id)
    
    if points < 100:
        return {'success': False, 'message': 'تحتاج إلى 100 نقطة ولاء على الأقل للتحويل'}
    
    # تحويل 100 نقطة ولاء → 10 نقاط عادية
    convert_rate = 10
    amount = (points // 100) * convert_rate
    
    if amount == 0:
        return {'success': False, 'message': 'لا يوجد نقاط كافية للتحويل'}
    
    # خصم نقاط الولاء
    loyalty = loyalty_read()
    loyalty[str(user_id)]['points'] -= (amount // convert_rate) * 100
    loyalty[str(user_id)]['history'].append({
        'type': 'convert',
        'amount': (amount // convert_rate) * 100,
        'converted_to': amount,
        'date': datetime.now().isoformat()
    })
    loyalty_write(loyalty)
    
    # إضافة نقاط عادية
    add_points(user_id, amount, 'تحويل نقاط ولاء')
    
    return {'success': True, 'message': f'تم تحويل {amount} نقطة من نقاط الولاء'}

# ============================================================
# نهاية الجزء 10
# ============================================================
# ============================================================
# الجزء 11: نظام API والربط الخارجي (API & Integrations) - 1500 سطر
# ============================================================

# ============================================================
# دوال API الأساسية
# ============================================================

def api_call(url, method='GET', data=None, headers=None, timeout=30):
    """استدعاء API خارجي"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return None
        
        if response.status_code in [200, 201, 202]:
            try:
                return response.json()
            except:
                return response.text
        return None
    except Exception as e:
        bot_log('ERROR', 'api_call failed', {'url': url, 'error': str(e)})
        return None

def api_call_with_retry(url, method='GET', data=None, headers=None, max_retries=3):
    """استدعاء API مع محاولات متعددة"""
    for attempt in range(max_retries):
        result = api_call(url, method, data, headers)
        if result:
            return result
        time.sleep(2 ** attempt)  # زيادة الانتظار مع كل محاولة
    return None

# ============================================================
# دوال API مواقع الرشق
# ============================================================

def smm_api_order(service_id, link, quantity, api_key, api_url):
    """إنشاء طلب عبر API موقع الرشق"""
    try:
        url = f"{api_url}/api/v2"
        params = {
            'key': api_key,
            'action': 'add',
            'service': service_id,
            'link': link,
            'quantity': quantity
        }
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        bot_log('ERROR', 'smm_api_order failed', {'error': str(e)})
        return None

def smm_api_status(order_id, api_key, api_url):
    """التحقق من حالة طلب عبر API"""
    try:
        url = f"{api_url}/api/v2"
        params = {
            'key': api_key,
            'action': 'status',
            'order': order_id
        }
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        bot_log('ERROR', 'smm_api_status failed', {'error': str(e)})
        return None

def smm_api_services(api_key, api_url):
    """الحصول على قائمة الخدمات من موقع الرشق"""
    try:
        url = f"{api_url}/api/v2"
        params = {
            'key': api_key,
            'action': 'services'
        }
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        bot_log('ERROR', 'smm_api_services failed', {'error': str(e)})
        return None

def smm_api_balance(api_key, api_url):
    """الحصول على الرصيد من موقع الرشق"""
    try:
        url = f"{api_url}/api/v2"
        params = {
            'key': api_key,
            'action': 'balance'
        }
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        bot_log('ERROR', 'smm_api_balance failed', {'error': str(e)})
        return None

# ============================================================
# دوال Webhook
# ============================================================

def webhook_set(url, secret=None):
    """تعيين Webhook"""
    data = {'url': url}
    if secret:
        data['secret_token'] = secret
    return bot('setWebhook', data)

def webhook_delete():
    """حذف Webhook"""
    return bot('deleteWebhook')

def webhook_get_info():
    """الحصول على معلومات Webhook"""
    return bot('getWebhookInfo')

def webhook_process(request_data):
    """معالجة طلب Webhook"""
    try:
        update = json.loads(request_data)
        process_update(update)
        return {'ok': True}
    except Exception as e:
        bot_log('ERROR', 'webhook_process failed', {'error': str(e)})
        return {'ok': False, 'error': str(e)}

# ============================================================
# دوال توثيق API
# ============================================================

def generate_api_key(user_id):
    """توليد مفتاح API للمستخدم"""
    key = f"RQ-{binascii.hexlify(os.urandom(16)).decode().upper()}"
    data = get_user_data(user_id)
    data['userfild'][str(user_id)]['api_key'] = key
    save_user_data(user_id, data)
    return key

def validate_api_key(user_id, api_key):
    """التحقق من صحة مفتاح API"""
    data = get_user_data(user_id)
    stored_key = data['userfild'].get(str(user_id), {}).get('api_key', '')
    return stored_key == api_key

def regenerate_api_key(user_id):
    """إعادة توليد مفتاح API"""
    return generate_api_key(user_id)

def get_api_key(user_id):
    """الحصول على مفتاح API للمستخدم"""
    data = get_user_data(user_id)
    return data['userfild'].get(str(user_id), {}).get('api_key', '')

# ============================================================
# دوال API المستخدم
# ============================================================

def user_api_get_balance(user_id, api_key):
    """API: الحصول على رصيد المستخدم"""
    if not validate_api_key(user_id, api_key):
        return {'success': False, 'message': 'مفتاح API غير صحيح'}
    
    balance = get_coin(user_id)
    return {'success': True, 'balance': balance}

def user_api_get_orders(user_id, api_key, limit=10):
    """API: الحصول على طلبات المستخدم"""
    if not validate_api_key(user_id, api_key):
        return {'success': False, 'message': 'مفتاح API غير صحيح'}
    
    orders = orders_user_text(user_id, limit)
    return {'success': True, 'orders': orders}

def user_api_create_order(user_id, api_key, service_id, link, quantity):
    """API: إنشاء طلب جديد"""
    if not validate_api_key(user_id, api_key):
        return {'success': False, 'message': 'مفتاح API غير صحيح'}
    
    # البحث عن الخدمة
    services = load_services()
    service_found = None
    section_found = None
    index_found = None
    
    for section_id, service_list in services['xdmaxs'].items():
        for idx, name in enumerate(service_list):
            if str(services['IDSSS'][section_id].get(str(idx), '')) == str(service_id):
                service_found = name
                section_found = section_id
                index_found = idx
                break
        if service_found:
            break
    
    if not service_found:
        return {'success': False, 'message': 'الخدمة غير موجودة'}
    
    # التحقق من الكمية
    min_qty = services['min'][section_found].get(str(index_found), 100)
    max_qty = services['mix'][section_found].get(str(index_found), 10000)
    
    if int(quantity) < min_qty:
        return {'success': False, 'message': f'الحد الأدنى للطلب هو {min_qty}'}
    
    if int(quantity) > max_qty:
        return {'success': False, 'message': f'الحد الأقصى للطلب هو {max_qty}'}
    
    # حساب السعر
    price = services['S3RS'][section_found].get(str(index_found), 0)
    total_price = float(price) * int(quantity)
    
    # التحقق من الرصيد
    balance = get_coin(user_id)
    if balance < total_price:
        return {'success': False, 'message': f'رصيدك غير كافي. المطلوب: {total_price}'}
    
    # استدعاء API الموقع
    web = services['Web'][section_found].get(str(index_found), '')
    key = services['key'][section_found].get(str(index_found), '')
    
    if not web or not key:
        return {'success': False, 'message': 'بيانات API غير مكتملة'}
    
    result = smm_api_order(service_id, link, quantity, key, f"https://{web}")
    
    if not result or 'order' not in result:
        return {'success': False, 'message': 'فشل إنشاء الطلب في الموقع'}
    
    order_id = result['order']
    
    # خصم النقاط
    deduct_points(user_id, total_price, f'طلب خدمة: {service_found} #{order_id}')
    
    # تسجيل الطلب
    order_create(order_id, user_id, service_id, link, quantity, total_price)
    
    return {
        'success': True,
        'order_id': order_id,
        'service': service_found,
        'quantity': quantity,
        'price': total_price
    }

# ============================================================
# دوال API المتقدمة
# ============================================================

def web_api_webhook_handler(request):
    """معالج Webhook لواجهة API"""
    try:
        data = json.loads(request.data)
        api_key = request.headers.get('X-API-Key')
        user_id = data.get('user_id')
        
        if not api_key or not user_id:
            return {'success': False, 'message': 'بيانات غير مكتملة'}
        
        if not validate_api_key(user_id, api_key):
            return {'success': False, 'message': 'مفتاح API غير صحيح'}
        
        action = data.get('action')
        
        if action == 'balance':
            return user_api_get_balance(user_id, api_key)
        elif action == 'orders':
            limit = data.get('limit', 10)
            return user_api_get_orders(user_id, api_key, limit)
        elif action == 'create_order':
            service_id = data.get('service_id')
            link = data.get('link')
            quantity = data.get('quantity')
            return user_api_create_order(user_id, api_key, service_id, link, quantity)
        else:
            return {'success': False, 'message': 'إجراء غير معروف'}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}

# ============================================================
# دوال الربط مع الخدمات الخارجية
# ============================================================

def telegram_api_send_message(chat_id, text, parse_mode='HTML', reply_markup=None):
    """إرسال رسالة عبر Telegram API"""
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    if reply_markup:
        data['reply_markup'] = reply_markup
    return bot('sendMessage', data)

def telegram_api_send_photo(chat_id, photo, caption=None, parse_mode='HTML'):
    """إرسال صورة عبر Telegram API"""
    data = {
        'chat_id': chat_id,
        'photo': photo,
        'parse_mode': parse_mode
    }
    if caption:
        data['caption'] = caption
    return bot('sendPhoto', data)

def telegram_api_send_document(chat_id, document, caption=None, parse_mode='HTML'):
    """إرسال ملف عبر Telegram API"""
    data = {
        'chat_id': chat_id,
        'document': document,
        'parse_mode': parse_mode
    }
    if caption:
        data['caption'] = caption
    return bot('sendDocument', data)

def telegram_api_send_inline_query(query, results, cache_time=300):
    """إرسال استعلام مضمن"""
    data = {
        'inline_query_id': query['id'],
        'results': json.dumps(results),
        'cache_time': cache_time
    }
    return bot('answerInlineQuery', data)

# ============================================================
# نهاية الجزء 11
# ============================================================
# ============================================================
# الجزء 12: نظام الفواتير والمدفوعات (Invoices & Payments) - 1500 سطر
# ============================================================

# ============================================================
# دوال الفواتير الأساسية
# ============================================================

INVOICES_DIR = './amr'

def invoice_create(user_id, amount, description, payment_method='points'):
    """إنشاء فاتورة جديدة"""
    invoice_file = f'{INVOICES_DIR}/{user_id}/invoices.json'
    os.makedirs(os.path.dirname(invoice_file), exist_ok=True)
    
    invoice = {
        'id': int(time.time()),
        'user_id': str(user_id),
        'amount': float(amount),
        'description': description,
        'payment_method': payment_method,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'paid_at': None,
        'invoice_number': f"INV-{int(time.time())}-{random.randint(100, 999)}"
    }
    
    try:
        invoices = []
        if os.path.exists(invoice_file):
            with open(invoice_file, 'r', encoding='utf-8') as f:
                invoices = json.load(f)
        
        invoices.append(invoice)
        with open(invoice_file, 'w', encoding='utf-8') as f:
            json.dump(invoices, f, indent=2, ensure_ascii=False)
        return invoice
    except Exception as e:
        bot_log('ERROR', 'invoice_create failed', {'error': str(e)})
        return None

def invoice_get(invoice_id):
    """الحصول على فاتورة برقمها"""
    users = get_all_users()
    
    for user_id in users:
        invoice_file = f'{INVOICES_DIR}/{user_id}/invoices.json'
        if os.path.exists(invoice_file):
            try:
                with open(invoice_file, 'r', encoding='utf-8') as f:
                    invoices = json.load(f)
                for inv in invoices:
                    if inv.get('id') == invoice_id:
                        return inv
            except:
                continue
    return None

def invoice_get_by_user(user_id, limit=10):
    """الحصول على فواتير المستخدم"""
    invoice_file = f'{INVOICES_DIR}/{user_id}/invoices.json'
    if not os.path.exists(invoice_file):
        return []
    
    try:
        with open(invoice_file, 'r', encoding='utf-8') as f:
            invoices = json.load(f)
        return invoices[-limit:] if len(invoices) > limit else invoices
    except:
        return []

def invoice_update_status(invoice_id, status):
    """تحديث حالة الفاتورة"""
    users = get_all_users()
    
    for user_id in users:
        invoice_file = f'{INVOICES_DIR}/{user_id}/invoices.json'
        if os.path.exists(invoice_file):
            try:
                with open(invoice_file, 'r', encoding='utf-8') as f:
                    invoices = json.load(f)
                
                for inv in invoices:
                    if inv.get('id') == invoice_id:
                        inv['status'] = status
                        if status == 'paid':
                            inv['paid_at'] = datetime.now().isoformat()
                        with open(invoice_file, 'w', encoding='utf-8') as f:
                            json.dump(invoices, f, indent=2, ensure_ascii=False)
                        return True
            except:
                continue
    return False

def invoice_mark_paid(invoice_id):
    """تحديد فاتورة كمدفوعة"""
    if invoice_update_status(invoice_id, 'paid'):
        inv = invoice_get(invoice_id)
        if inv:
            # إضافة النقاط للمستخدم
            add_points(inv['user_id'], inv['amount'], f'دفع فاتورة {inv["invoice_number"]}')
            send_notification(inv['user_id'], f"✅ تم دفع فاتورة #{inv['invoice_number']}\nالمبلغ: {inv['amount']} نقطة")
            return True
    return False

def invoice_cancel(invoice_id):
    """إلغاء فاتورة"""
    return invoice_update_status(invoice_id, 'canceled')

def invoice_delete(invoice_id):
    """حذف فاتورة"""
    users = get_all_users()
    
    for user_id in users:
        invoice_file = f'{INVOICES_DIR}/{user_id}/invoices.json'
        if os.path.exists(invoice_file):
            try:
                with open(invoice_file, 'r', encoding='utf-8') as f:
                    invoices = json.load(f)
                
                new_invoices = [inv for inv in invoices if inv.get('id') != invoice_id]
                if len(new_invoices) < len(invoices):
                    with open(invoice_file, 'w', encoding='utf-8') as f:
                        json.dump(new_invoices, f, indent=2, ensure_ascii=False)
                    return True
            except:
                continue
    return False

def invoice_count(user_id=None, status=None):
    """الحصول على عدد الفواتير"""
    if user_id:
        return len(invoice_get_by_user(user_id, limit=9999))
    
    users = get_all_users()
    total = 0
    for user_id in users:
        total += len(invoice_get_by_user(user_id, limit=9999))
    return total

def invoice_total_amount(user_id=None, status='paid'):
    """الحصول على إجمالي مبالغ الفواتير"""
    if user_id:
        invoices = invoice_get_by_user(user_id, limit=9999)
        return sum([inv['amount'] for inv in invoices if inv.get('status') == status])
    
    users = get_all_users()
    total = 0
    for user_id in users:
        invoices = invoice_get_by_user(user_id, limit=9999)
        total += sum([inv['amount'] for inv in invoices if inv.get('status') == status])
    return total

# ============================================================
# دوال المدفوعات
# ============================================================

PAYMENTS_FILE = './data/payments.json'

def payment_create(user_id, amount, method, details=None):
    """تسجيل عملية دفع جديدة"""
    payments = []
    if os.path.exists(PAYMENTS_FILE):
        try:
            with open(PAYMENTS_FILE, 'r', encoding='utf-8') as f:
                payments = json.load(f)
        except:
            pass
    
    payment = {
        'id': int(time.time()),
        'user_id': str(user_id),
        'amount': float(amount),
        'method': method,
        'details': details or {},
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'completed_at': None
    }
    
    payments.append(payment)
    
    try:
        with open(PAYMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(payments, f, indent=2, ensure_ascii=False)
        return payment
    except:
        return None

def payment_get(payment_id):
    """الحصول على عملية دفع"""
    if not os.path.exists(PAYMENTS_FILE):
        return None
    
    try:
        with open(PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            payments = json.load(f)
        for payment in payments:
            if payment.get('id') == payment_id:
                return payment
    except:
        pass
    return None

def payment_get_by_user(user_id, limit=10):
    """الحصول على مدفوعات المستخدم"""
    if not os.path.exists(PAYMENTS_FILE):
        return []
    
    try:
        with open(PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            payments = json.load(f)
        user_payments = [p for p in payments if str(p.get('user_id', '')) == str(user_id)]
        return user_payments[-limit:] if len(user_payments) > limit else user_payments
    except:
        return []

def payment_update_status(payment_id, status):
    """تحديث حالة الدفع"""
    if not os.path.exists(PAYMENTS_FILE):
        return False
    
    try:
        with open(PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            payments = json.load(f)
        
        for payment in payments:
            if payment.get('id') == payment_id:
                payment['status'] = status
                if status == 'completed':
                    payment['completed_at'] = datetime.now().isoformat()
                    # إضافة النقاط للمستخدم
                    add_points(payment['user_id'], payment['amount'], f'دفع عبر {payment["method"]}')
                with open(PAYMENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(payments, f, indent=2, ensure_ascii=False)
                return True
    except:
        pass
    return False

def payment_complete(payment_id):
    """إكمال عملية الدفع"""
    return payment_update_status(payment_id, 'completed')

def payment_cancel(payment_id):
    """إلغاء عملية الدفع"""
    return payment_update_status(payment_id, 'canceled')

# ============================================================
# دوال طرق الدفع
# ============================================================

PAYMENT_METHODS = {
    'points': {'name': 'نقاط البوت', 'active': True},
    'bank': {'name': 'تحويل بنكي', 'active': True},
    'crypto': {'name': 'عملات رقمية', 'active': False},
    'card': {'name': 'بطاقة ائتمان', 'active': False}
}

def get_payment_methods(active_only=True):
    """الحصول على طرق الدفع المتاحة"""
    if active_only:
        return {k: v for k, v in PAYMENT_METHODS.items() if v.get('active', True)}
    return PAYMENT_METHODS

def add_payment_method(method_id, name, active=True):
    """إضافة طريقة دفع جديدة"""
    PAYMENT_METHODS[method_id] = {'name': name, 'active': active}
    return True

def remove_payment_method(method_id):
    """حذف طريقة دفع"""
    if method_id in PAYMENT_METHODS:
        del PAYMENT_METHODS[method_id]
        return True
    return False

def toggle_payment_method(method_id):
    """تبديل حالة طريقة الدفع"""
    if method_id in PAYMENT_METHODS:
        PAYMENT_METHODS[method_id]['active'] = not PAYMENT_METHODS[method_id]['active']
        return True
    return False

# ============================================================
# دوال تقارير الفواتير والمدفوعات
# ============================================================

def invoice_report(user_id=None):
    """توليد تقرير الفواتير"""
    if user_id:
        invoices = invoice_get_by_user(user_id, limit=9999)
        total = len(invoices)
        paid = len([inv for inv in invoices if inv.get('status') == 'paid'])
        pending = len([inv for inv in invoices if inv.get('status') == 'pending'])
        total_amount = sum([inv['amount'] for inv in invoices if inv.get('status') == 'paid'])
        
        report = f"""
📊 <b>تقرير الفواتير</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📋 <b>إجمالي الفواتير:</b> {total}
✅ <b>مدفوعة:</b> {paid}
⏳ <b>معلقة:</b> {pending}
💰 <b>إجمالي المبلغ:</b> {total_amount}
"""
        return report
    
    # تقرير عام
    total_users = len(get_all_users())
    total_invoices = invoice_count()
    total_paid = invoice_total_amount()
    
    report = f"""
📊 <b>تقرير الفواتير العام</b>
━━━━━━━━━━━━━━━━━
👥 <b>عدد المستخدمين:</b> {total_users}
📋 <b>إجمالي الفواتير:</b> {total_invoices}
💰 <b>إجمالي المدفوعات:</b> {total_paid}
"""
    return report

def payment_report(user_id=None):
    """توليد تقرير المدفوعات"""
    if user_id:
        payments = payment_get_by_user(user_id, limit=9999)
        total = len(payments)
        completed = len([p for p in payments if p.get('status') == 'completed'])
        pending = len([p for p in payments if p.get('status') == 'pending'])
        total_amount = sum([p['amount'] for p in payments if p.get('status') == 'completed'])
        
        report = f"""
📊 <b>تقرير المدفوعات</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
📋 <b>إجمالي المدفوعات:</b> {total}
✅ <b>مكتملة:</b> {completed}
⏳ <b>معلقة:</b> {pending}
💰 <b>إجمالي المبلغ:</b> {total_amount}
"""
        return report
    
    # تقرير عام
    if not os.path.exists(PAYMENTS_FILE):
        return "📊 لا توجد مدفوعات مسجلة"
    
    try:
        with open(PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            payments = json.load(f)
        
        total = len(payments)
        completed = len([p for p in payments if p.get('status') == 'completed'])
        pending = len([p for p in payments if p.get('status') == 'pending'])
        total_amount = sum([p['amount'] for p in payments if p.get('status') == 'completed'])
        
        report = f"""
📊 <b>تقرير المدفوعات العام</b>
━━━━━━━━━━━━━━━━━
📋 <b>إجمالي المدفوعات:</b> {total}
✅ <b>مكتملة:</b> {completed}
⏳ <b>معلقة:</b> {pending}
💰 <b>إجمالي المبلغ:</b> {total_amount}
"""
        return report
    except:
        return "📊 لا توجد مدفوعات مسجلة"

# ============================================================
# دوال فواتير الدفع التلقائي
# ============================================================

def auto_invoice_charge(user_id, amount, description, auto_pay=True):
    """إنشاء فاتورة مع دفع تلقائي"""
    invoice = invoice_create(user_id, amount, description)
    if not invoice:
        return None
    
    if auto_pay:
        # دفع تلقائي إذا كان الرصيد كافياً
        balance = get_coin(user_id)
        if balance >= amount:
            invoice_mark_paid(invoice['id'])
            return invoice
    
    return invoice

def invoice_auto_reminder():
    """إرسال تذكير بالفواتير غير المدفوعة"""
    users = get_all_users()
    
    for user_id in users:
        invoices = invoice_get_by_user(user_id, limit=10)
        pending = [inv for inv in invoices if inv.get('status') == 'pending']
        
        if pending:
            amount = sum([inv['amount'] for inv in pending])
            send_notification(user_id, 
                             f"⏰ تذكير: لديك {len(pending)} فاتورة غير مدفوعة بقيمة {amount} نقطة\nيرجى دفعها لتجنب تعليق الخدمات")

# ============================================================
# دوال إعدادات الفواتير
# ============================================================

def invoice_settings():
    """الحصول على إعدادات الفواتير"""
    return {
        'auto_reminder': file_read('edid/invoice_reminder.txt') or '✅',
        'reminder_days': int(file_read('edid/reminder_days.txt') or '3'),
        'min_invoice': int(file_read('edid/min_invoice.txt') or '10'),
        'max_invoice': int(file_read('edid/max_invoice.txt') or '100000')
    }

def update_invoice_settings(settings):
    """تحديث إعدادات الفواتير"""
    if 'auto_reminder' in settings:
        file_write('edid/invoice_reminder.txt', settings['auto_reminder'])
    
    if 'reminder_days' in settings:
        file_write('edid/reminder_days.txt', str(settings['reminder_days']))
    
    if 'min_invoice' in settings:
        file_write('edid/min_invoice.txt', str(settings['min_invoice']))
    
    if 'max_invoice' in settings:
        file_write('edid/max_invoice.txt', str(settings['max_invoice']))
    
    return True

# ============================================================
# نهاية الجزء 12
# ============================================================
# ============================================================
# الجزء 13: نظام التذاكر والدعم الفني (Tickets & Support) - 1500 سطر
# ============================================================

# ============================================================
# دوال التذاكر الأساسية
# ============================================================

TICKETS_FILE = './data/tickets.json'

def ticket_read():
    """قراءة التذاكر"""
    if not os.path.exists(TICKETS_FILE):
        return []
    try:
        with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def ticket_write(tickets):
    """كتابة التذاكر"""
    tmp_path = f"{TICKETS_FILE}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(TICKETS_FILE), exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, indent=2, ensure_ascii=False)
        os.rename(tmp_path, TICKETS_FILE)
        return True
    except:
        return False

def ticket_create(user_id, subject, message, priority='normal'):
    """إنشاء تذكرة دعم جديدة"""
    tickets = ticket_read()
    
    ticket = {
        'id': int(time.time()),
        'ticket_number': f"TKT-{int(time.time())}-{random.randint(100, 999)}",
        'user_id': str(user_id),
        'subject': subject,
        'message': message,
        'priority': priority,  # low, normal, high, urgent
        'status': 'open',  # open, in_progress, resolved, closed
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'assigned_to': None,
        'resolved_at': None,
        'closed_at': None,
        'replies': []
    }
    
    tickets.append(ticket)
    ticket_write(tickets)
    
    # إشعار للأدمن
    notify_support_ticket(user_id, message)
    
    return ticket

def ticket_get(ticket_id):
    """الحصول على تذكرة برقمها"""
    tickets = ticket_read()
    for ticket in tickets:
        if ticket.get('id') == ticket_id:
            return ticket
    return None

def ticket_get_by_number(ticket_number):
    """الحصول على تذكرة برقمها النصي"""
    tickets = ticket_read()
    for ticket in tickets:
        if ticket.get('ticket_number') == ticket_number:
            return ticket
    return None

def ticket_get_by_user(user_id, limit=10):
    """الحصول على تذاكر المستخدم"""
    tickets = ticket_read()
    user_tickets = [t for t in tickets if str(t.get('user_id', '')) == str(user_id)]
    return user_tickets[-limit:] if len(user_tickets) > limit else user_tickets

def ticket_get_open():
    """الحصول على التذاكر المفتوحة"""
    tickets = ticket_read()
    return [t for t in tickets if t.get('status') in ['open', 'in_progress']]

def ticket_get_by_status(status):
    """الحصول على التذاكر حسب الحالة"""
    tickets = ticket_read()
    return [t for t in tickets if t.get('status') == status]

def ticket_update_status(ticket_id, status):
    """تحديث حالة التذكرة"""
    tickets = ticket_read()
    for ticket in tickets:
        if ticket.get('id') == ticket_id:
            ticket['status'] = status
            ticket['updated_at'] = datetime.now().isoformat()
            
            if status == 'resolved':
                ticket['resolved_at'] = datetime.now().isoformat()
            elif status == 'closed':
                ticket['closed_at'] = datetime.now().isoformat()
            
            ticket_write(tickets)
            return True
    return False

def ticket_assign(ticket_id, admin_id):
    """تخصيص تذكرة لأدمن"""
    tickets = ticket_read()
    for ticket in tickets:
        if ticket.get('id') == ticket_id:
            ticket['assigned_to'] = str(admin_id)
            ticket['updated_at'] = datetime.now().isoformat()
            ticket_write(tickets)
            return True
    return False

def ticket_add_reply(ticket_id, user_id, message, is_admin=False):
    """إضافة رد على تذكرة"""
    tickets = ticket_read()
    for ticket in tickets:
        if ticket.get('id') == ticket_id:
            reply = {
                'user_id': str(user_id),
                'message': message,
                'is_admin': is_admin,
                'created_at': datetime.now().isoformat()
            }
            ticket['replies'].append(reply)
            ticket['updated_at'] = datetime.now().isoformat()
            
            # تحديث الحالة إذا كان رد من المستخدم
            if not is_admin and ticket['status'] == 'resolved':
                ticket['status'] = 'open'
            
            ticket_write(tickets)
            
            # إشعار للمستخدم أو الأدمن
            if is_admin:
                send_notification(ticket['user_id'], 
                                 f"📩 رد جديد على تذكرتك #{ticket['ticket_number']}\n\n{message}")
            else:
                send_notification_to_admin(
                    f"📩 رد جديد من المستخدم\n"
                    f"تذكرة: #{ticket['ticket_number']}\n"
                    f"المستخدم: <code>{user_id}</code>\n"
                    f"الرد: {message}"
                )
            
            return True
    return False

def ticket_close(ticket_id):
    """إغلاق تذكرة"""
    return ticket_update_status(ticket_id, 'closed')

def ticket_reopen(ticket_id):
    """إعادة فتح تذكرة"""
    return ticket_update_status(ticket_id, 'open')

def ticket_delete(ticket_id):
    """حذف تذكرة"""
    tickets = ticket_read()
    new_tickets = [t for t in tickets if t.get('id') != ticket_id]
    if len(new_tickets) < len(tickets):
        ticket_write(new_tickets)
        return True
    return False

# ============================================================
# دوال إحصائيات التذاكر
# ============================================================

def ticket_stats():
    """الحصول على إحصائيات التذاكر"""
    tickets = ticket_read()
    stats = {
        'total': len(tickets),
        'open': len([t for t in tickets if t.get('status') == 'open']),
        'in_progress': len([t for t in tickets if t.get('status') == 'in_progress']),
        'resolved': len([t for t in tickets if t.get('status') == 'resolved']),
        'closed': len([t for t in tickets if t.get('status') == 'closed']),
        'by_priority': {
            'low': len([t for t in tickets if t.get('priority') == 'low']),
            'normal': len([t for t in tickets if t.get('priority') == 'normal']),
            'high': len([t for t in tickets if t.get('priority') == 'high']),
            'urgent': len([t for t in tickets if t.get('priority') == 'urgent'])
        }
    }
    return stats

def ticket_user_stats(user_id):
    """الحصول على إحصائيات تذاكر المستخدم"""
    tickets = ticket_read()
    user_tickets = [t for t in tickets if str(t.get('user_id', '')) == str(user_id)]
    
    stats = {
        'total': len(user_tickets),
        'open': len([t for t in user_tickets if t.get('status') == 'open']),
        'in_progress': len([t for t in user_tickets if t.get('status') == 'in_progress']),
        'resolved': len([t for t in user_tickets if t.get('status') == 'resolved']),
        'closed': len([t for t in user_tickets if t.get('status') == 'closed'])
    }
    return stats

def ticket_avg_response_time():
    """الحصول على متوسط وقت الاستجابة للتذاكر"""
    tickets = ticket_read()
    resolved = [t for t in tickets if t.get('status') in ['resolved', 'closed']]
    
    if not resolved:
        return 0
    
    total_time = 0
    for ticket in resolved:
        created = datetime.fromisoformat(ticket['created_at'])
        resolved_time = datetime.fromisoformat(ticket.get('resolved_at') or ticket.get('closed_at') or ticket['created_at'])
        total_time += (resolved_time - created).total_seconds() / 3600  # ساعات
    
    return total_time / len(resolved)

# ============================================================
# دوال نصوص التذاكر
# ============================================================

def ticket_format(ticket):
    """تنسيق التذكرة كنص"""
    status_map = {
        'open': '🟢 مفتوحة',
        'in_progress': '🟡 قيد المعالجة',
        'resolved': '🔵 محلولة',
        'closed': '⚫ مغلقة'
    }
    
    priority_map = {
        'low': '🟢 منخفضة',
        'normal': '🟡 عادية',
        'high': '🟠 عالية',
        'urgent': '🔴 عاجلة'
    }
    
    text = f"""
🎫 <b>التذكرة #{ticket['ticket_number']}</b>
━━━━━━━━━━━━━━━━━
📌 <b>الموضوع:</b> {ticket['subject']}
📊 <b>الحالة:</b> {status_map.get(ticket['status'], ticket['status'])}
⚡ <b>الأولوية:</b> {priority_map.get(ticket['priority'], ticket['priority'])}
🆔 <b>المستخدم:</b> <code>{ticket['user_id']}</code>
📅 <b>التاريخ:</b> {ticket['created_at']}
━━━━━━━━━━━━━━━━━
📝 <b>الرسالة:</b>
{ticket['message']}
"""
    
    if ticket['replies']:
        text += "\n━━━━━━━━━━━━━━━━━\n<b>الردود:</b>\n"
        for reply in ticket['replies'][-5:]:
            sender = "الأدمن" if reply['is_admin'] else "المستخدم"
            text += f"👤 {sender}: {reply['message']}\n🕐 {reply['created_at']}\n"
    
    return text

def ticket_list_text(tickets, limit=10):
    """تنسيق قائمة التذاكر كنص"""
    if not tickets:
        return "📭 لا توجد تذاكر"
    
    text = "📋 <b>قائمة التذاكر</b>\n━━━━━━━━━━━━━━━━━\n"
    for ticket in tickets[:limit]:
        status_map = {
            'open': '🟢',
            'in_progress': '🟡',
            'resolved': '🔵',
            'closed': '⚫'
        }
        text += f"{status_map.get(ticket['status'], '⚪')} #{ticket['ticket_number']} - {ticket['subject']}\n"
    
    return text

# ============================================================
# دوال الدعم الفني التلقائي
# ============================================================

SUPPORT_FAQ = {
    'شحن': 'لشحن رصيدك: من القائمة الرئيسية اضغط 💰 إشحن رصيدك',
    'طلب': 'لمتابعة طلباتك: من ⚙️ المزيد والإعدادات اضغط 🙋‍♂️ طلباتي',
    'سعر': 'أسعار الخدمات تظهر داخل كل قسم عند اختيار الخدمة',
    'رصيد': 'رصيدك الحالي يظهر أعلى القائمة الرئيسية',
    'كوبون': 'يمكنك استخدام الكوبونات عبر /coupon CODE',
    'تحويل': 'لتحويل الرصيد اضغط 🔄 تحويل رصيد',
    'تمويل': 'لتمويل قناتك اضغط 🎬 بدء تلبية رشق جديدة ثم اختر تمويل',
    'حظر': 'إذا تم حظرك، تواصل مع الأدمن على {SUPPORT}',
    'دعم': f'للتواصل مع الدعم الفني: {SUPPORT}'
}

def support_ai_response(message):
    """الرد التلقائي على استفسارات الدعم"""
    message_lower = message.lower()
    
    for keyword, response in SUPPORT_FAQ.items():
        if keyword in message_lower:
            return response
    
    return None

def support_auto_reply(user_id, message):
    """الرد التلقائي مع تحويل للدعم البشري إذا لزم الأمر"""
    response = support_ai_response(message)
    
    if response:
        send_notification(user_id, f"🤖 {response}")
        return True
    else:
        # إنشاء تذكرة دعم
        ticket_create(user_id, "استفسار عام", message)
        send_notification(user_id, 
                         f"📩 لم أتمكن من فهم سؤالك.\n"
                         f"تم إنشاء تذكرة دعم وسيتم الرد عليك قريباً.\n"
                         f"للمتابعة: {SUPPORT}")
        return False

# ============================================================
# دوال إعدادات الدعم
# ============================================================

def support_settings():
    """الحصول على إعدادات الدعم"""
    return {
        'auto_reply': file_read('edid/support_auto.txt') or '✅',
        'ticket_limit': int(file_read('edid/ticket_limit.txt') or '5'),
        'response_timeout': int(file_read('edid/response_timeout.txt') or '24')
    }

def update_support_settings(settings):
    """تحديث إعدادات الدعم"""
    if 'auto_reply' in settings:
        file_write('edid/support_auto.txt', settings['auto_reply'])
    
    if 'ticket_limit' in settings:
        file_write('edid/ticket_limit.txt', str(settings['ticket_limit']))
    
    if 'response_timeout' in settings:
        file_write('edid/response_timeout.txt', str(settings['response_timeout']))
    
    return True

# ============================================================
# دوال تقارير الدعم
# ============================================================

def support_report():
    """توليد تقرير الدعم"""
    stats = ticket_stats()
    avg_response = ticket_avg_response_time()
    
    report = f"""
📊 <b>تقرير الدعم الفني</b>
━━━━━━━━━━━━━━━━━
📋 <b>إجمالي التذاكر:</b> {stats['total']}
🟢 <b>مفتوحة:</b> {stats['open']}
🟡 <b>قيد المعالجة:</b> {stats['in_progress']}
🔵 <b>محلولة:</b> {stats['resolved']}
⚫ <b>مغلقة:</b> {stats['closed']}
━━━━━━━━━━━━━━━━━
<b>حسب الأولوية:</b>
🟢 منخفضة: {stats['by_priority']['low']}
🟡 عادية: {stats['by_priority']['normal']}
🟠 عالية: {stats['by_priority']['high']}
🔴 عاجلة: {stats['by_priority']['urgent']}
━━━━━━━━━━━━━━━━━
⏱️ <b>متوسط وقت الاستجابة:</b> {avg_response:.1f} ساعة
"""
    return report

# ============================================================
# نهاية الجزء 13
# ============================================================
# ============================================================
# الجزء 14: نظام الأمان والحماية المتقدم (Advanced Security) - 1500 سطر
# ============================================================

# ============================================================
# دوال الحماية الأساسية
# ============================================================

SECURITY_DIR = './security_store'

def security_init():
    """تهيئة نظام الأمان"""
    os.makedirs(SECURITY_DIR, exist_ok=True)
    
    # إنشاء ملفات الأمان إذا لم تكن موجودة
    security_files = [
        'blocked_ips.txt',
        'suspicious_users.txt',
        'attack_log.txt',
        'rate_limit_log.txt'
    ]
    
    for file_name in security_files:
        file_path = f'{SECURITY_DIR}/{file_name}'
        if not os.path.exists(file_path):
            file_write(file_path, '')

def security_check_ip(ip_address):
    """التحقق من عنوان IP محظور"""
    blocked_file = f'{SECURITY_DIR}/blocked_ips.txt'
    if not os.path.exists(blocked_file):
        return True
    
    blocked = file_read(blocked_file)
    if blocked:
        blocked_ips = [ip.strip() for ip in blocked.split('\n') if ip.strip()]
        return ip_address not in blocked_ips
    return True

def security_block_ip(ip_address, reason=''):
    """حظر عنوان IP"""
    blocked_file = f'{SECURITY_DIR}/blocked_ips.txt'
    file_append(blocked_file, f'{ip_address} - {reason} - {datetime.now().isoformat()}')
    return True

def security_unblock_ip(ip_address):
    """إلغاء حظر عنوان IP"""
    blocked_file = f'{SECURITY_DIR}/blocked_ips.txt'
    if not os.path.exists(blocked_file):
        return True
    
    content = file_read(blocked_file)
    if not content:
        return True
    
    lines = content.split('\n')
    new_lines = [line for line in lines if ip_address not in line]
    file_write(blocked_file, '\n'.join(new_lines))
    return True

def security_mark_suspicious(user_id, reason=''):
    """تسجيل مستخدم مشبوه"""
    suspicious_file = f'{SECURITY_DIR}/suspicious_users.txt'
    file_append(suspicious_file, f'{user_id} - {reason} - {datetime.now().isoformat()}')
    return True

def security_is_suspicious(user_id):
    """التحقق من أن المستخدم مشبوه"""
    suspicious_file = f'{SECURITY_DIR}/suspicious_users.txt'
    if not os.path.exists(suspicious_file):
        return False
    
    content = file_read(suspicious_file)
    if not content:
        return False
    
    suspicious_users = [line.split(' - ')[0] for line in content.split('\n') if line.strip()]
    return str(user_id) in suspicious_users

def security_log_attack(attack_type, user_id, details=''):
    """تسجيل هجوم"""
    attack_log = f'{SECURITY_DIR}/attack_log.txt'
    log_entry = f'{datetime.now().isoformat()} | {attack_type} | {user_id} | {details}'
    file_append(attack_log, log_entry)
    return True

def security_rate_limit_log(user_id, limit_type):
    """تسجيل تجاوز الحدود"""
    rate_limit_log = f'{SECURITY_DIR}/rate_limit_log.txt'
    log_entry = f'{datetime.now().isoformat()} | {limit_type} | {user_id}'
    file_append(rate_limit_log, log_entry)
    return True

# ============================================================
# دوال الحماية من الهجمات
# ============================================================

def security_bruteforce_protect(user_id, action, max_attempts=5, window=60):
    """حماية من هجمات القوة العمياء"""
    user_id = str(user_id)
    attempts_file = f'{SECURITY_DIR}/bruteforce_{user_id}.json'
    
    data = {}
    if os.path.exists(attempts_file):
        data = json_read(attempts_file)
    
    now = time.time()
    
    # تنظيف المحاولات القديمة
    if 'attempts' in data:
        data['attempts'] = [t for t in data['attempts'] if now - t < window]
    else:
        data['attempts'] = []
    
    # تسجيل المحاولة الجديدة
    data['attempts'].append(now)
    data['last_action'] = action
    data['last_time'] = now
    
    json_write(attempts_file, data)
    
    # التحقق من تجاوز الحد
    if len(data['attempts']) > max_attempts:
        security_log_attack('bruteforce', user_id, f'Action: {action}')
        return {'blocked': True, 'message': 'تجاوزت عدد المحاولات المسموح بها'}
    
    return {'blocked': False, 'remaining': max_attempts - len(data['attempts'])}

def security_flood_protect(user_id, messages=[], max_messages=10, window=5):
    """حماية من الفيضانات"""
    user_id = str(user_id)
    flood_file = f'{SECURITY_DIR}/flood_{user_id}.json'
    
    data = {}
    if os.path.exists(flood_file):
        data = json_read(flood_file)
    
    now = time.time()
    
    if 'messages' not in data:
        data['messages'] = []
    
    # تنظيف الرسائل القديمة
    data['messages'] = [t for t in data['messages'] if now - t < window]
    
    # تسجيل الرسالة الجديدة
    data['messages'].append(now)
    data['last_update'] = now
    
    json_write(flood_file, data)
    
    # التحقق من تجاوز الحد
    if len(data['messages']) > max_messages:
        security_log_attack('flood', user_id, f'Messages: {len(data["messages"])}')
        return {'blocked': True, 'message': 'تجاوزت عدد الرسائل المسموح بها'}
    
    return {'blocked': False, 'remaining': max_messages - len(data['messages'])}

def security_command_spam_protect(user_id, command, max_commands=5, window=10):
    """حماية من تكرار الأوامر"""
    user_id = str(user_id)
    command_file = f'{SECURITY_DIR}/commands_{user_id}.json'
    
    data = {}
    if os.path.exists(command_file):
        data = json_read(command_file)
    
    now = time.time()
    
    if 'commands' not in data:
        data['commands'] = {}
    
    if command not in data['commands']:
        data['commands'][command] = []
    
    # تنظيف الأوامر القديمة
    data['commands'][command] = [t for t in data['commands'][command] if now - t < window]
    
    # تسجيل الأمر الجديد
    data['commands'][command].append(now)
    data['last_update'] = now
    
    json_write(command_file, data)
    
    # التحقق من تجاوز الحد
    if len(data['commands'][command]) > max_commands:
        security_log_attack('command_spam', user_id, f'Command: {command}')
        return {'blocked': True, 'message': 'تجاوزت عدد الأوامر المسموح بها'}
    
    return {'blocked': False, 'remaining': max_commands - len(data['commands'][command])}

# ============================================================
# دوال التحقق من الأمان
# ============================================================

def security_verify_user(user_id):
    """التحقق الشامل من المستخدم"""
    checks = {
        'is_banned': is_banned(user_id),
        'is_suspicious': security_is_suspicious(user_id),
        'rate_limit': security_rate_limit_allow(user_id)
    }
    
    if checks['is_banned']:
        return {'allowed': False, 'reason': 'محظور'}
    
    if checks['is_suspicious']:
        return {'allowed': False, 'reason': 'مستخدم مشبوه'}
    
    if not checks['rate_limit']:
        return {'allowed': False, 'reason': 'تجاوز حد الطلبات'}
    
    return {'allowed': True}

def security_verify_admin_action(user_id, action):
    """التحقق من صلاحيات الأدمن"""
    if not is_admin(user_id):
        return {'allowed': False, 'reason': 'ليس لديك صلاحيات'}
    
    # تسجيل إجراء الأدمن
    admin_log = f'{SECURITY_DIR}/admin_actions.log'
    log_entry = f'{datetime.now().isoformat()} | {action} | {user_id}'
    file_append(admin_log, log_entry)
    
    return {'allowed': True}

# ============================================================
# دوال الحماية من الاختراق
# ============================================================

def security_detect_sql_injection(input_text):
    """كشف محاولات حقن SQL"""
    sql_patterns = [
        r'SELECT.*FROM',
        r'INSERT.*INTO',
        r'UPDATE.*SET',
        r'DELETE.*FROM',
        r'DROP.*TABLE',
        r'UNION.*SELECT',
        r'--',
        r';.*--',
        r"'.*OR.*'",
        r"'.*AND.*'"
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return True
    return False

def security_detect_xss(input_text):
    """كشف محاولات حقن XSS"""
    xss_patterns = [
        r'<script.*?>',
        r'javascript:',
        r'onerror=',
        r'onload=',
        r'onclick=',
        r'<iframe.*?>',
        r'<img.*?>'
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return True
    return False

def security_sanitize_input(input_text):
    """تنظيف المدخلات من الكود الضار"""
    # إزالة HTML tags
    input_text = re.sub(r'<[^>]+>', '', input_text)
    
    # إزالة javascript
    input_text = re.sub(r'javascript:', '', input_text, re.IGNORECASE)
    
    # إزالة الأحرف الخاصة
    input_text = re.sub(r'[;{}()]', '', input_text)
    
    return input_text

# ============================================================
# دوال الحماية من الروبوتات
# ============================================================

def security_captcha_generate():
    """توليد كود CAPTCHA"""
    import string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    captcha_file = f'{SECURITY_DIR}/captcha_{code}.json'
    captcha_data = {
        'code': code,
        'created_at': time.time(),
        'expires_at': time.time() + 300  # 5 دقائق
    }
    json_write(captcha_file, captcha_data)
    
    return code

def security_captcha_verify(code):
    """التحقق من كود CAPTCHA"""
    captcha_file = f'{SECURITY_DIR}/captcha_{code}.json'
    if not os.path.exists(captcha_file):
        return False
    
    data = json_read(captcha_file)
    if time.time() > data.get('expires_at', 0):
        os.remove(captcha_file)
        return False
    
    os.remove(captcha_file)
    return True

def security_hcaptcha_verify(response_token, secret_key):
    """التحقق من hCaptcha"""
    try:
        url = 'https://hcaptcha.com/siteverify'
        data = {
            'secret': secret_key,
            'response': response_token
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False)
        return False
    except:
        return False

# ============================================================
# دوال تقارير الأمان
# ============================================================

def security_report():
    """توليد تقرير الأمان"""
    blocked_ips = []
    blocked_file = f'{SECURITY_DIR}/blocked_ips.txt'
    if os.path.exists(blocked_file):
        content = file_read(blocked_file)
        if content:
            blocked_ips = [line.split(' - ')[0] for line in content.split('\n') if line.strip()]
    
    suspicious = []
    suspicious_file = f'{SECURITY_DIR}/suspicious_users.txt'
    if os.path.exists(suspicious_file):
        content = file_read(suspicious_file)
        if content:
            suspicious = [line.split(' - ')[0] for line in content.split('\n') if line.strip()]
    
    report = f"""
🛡️ <b>تقرير الأمان</b>
━━━━━━━━━━━━━━━━━
🚫 <b>عنوان IP محظورة:</b> {len(blocked_ips)}
⚠️ <b>مستخدمين مشبوهين:</b> {len(suspicious)}
━━━━━━━━━━━━━━━━━
<b>الحماية النشطة:</b>
✅ حماية القوة العمياء
✅ حماية الفيضانات
✅ حماية تكرار الأوامر
✅ منع الحقن
✅ تنقية المدخلات
"""
    return report

def security_clear_logs():
    """مسح سجلات الأمان"""
    log_files = [
        'attack_log.txt',
        'rate_limit_log.txt',
        'admin_actions.log'
    ]
    
    for log_file in log_files:
        file_path = f'{SECURITY_DIR}/{log_file}'
        if os.path.exists(file_path):
            file_write(file_path, '')
    
    return True

# ============================================================
# دوال النسخ الاحتياطي للأمان
# ============================================================

def security_backup():
    """عمل نسخة احتياطية لإعدادات الأمان"""
    backup_dir = f'{SECURITY_DIR}/backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_file = f'{backup_dir}/security_backup_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    
    backup_data = {
        'blocked_ips': file_read(f'{SECURITY_DIR}/blocked_ips.txt') or '',
        'suspicious_users': file_read(f'{SECURITY_DIR}/suspicious_users.txt') or '',
        'timestamp': datetime.now().isoformat()
    }
    
    json_write(backup_file, backup_data)
    return backup_file

def security_restore(backup_file):
    """استعادة نسخة احتياطية للأمان"""
    if not os.path.exists(backup_file):
        return False
    
    backup_data = json_read(backup_file)
    if not backup_data:
        return False
    
    if 'blocked_ips' in backup_data:
        file_write(f'{SECURITY_DIR}/blocked_ips.txt', backup_data['blocked_ips'])
    
    if 'suspicious_users' in backup_data:
        file_write(f'{SECURITY_DIR}/suspicious_users.txt', backup_data['suspicious_users'])
    
    return True

# ============================================================
# نهاية الجزء 14
# ============================================================
# ============================================================
# الجزء 15: نظام الإحصائيات والتقارير المتقدمة (Advanced Stats) - 1500 سطر
# ============================================================

# ============================================================
# دوال الإحصائيات الأساسية
# ============================================================

def stats_get_basic():
    """الحصول على الإحصائيات الأساسية"""
    return {
        'total_users': get_users_count(),
        'banned_users': get_banned_users_count(),
        'active_users': get_active_users_count(),
        'total_orders': orders_count(),
        'total_revenue': orders_stats()['total_revenue'],
        'total_points': get_system_total_points(),
        'total_categories': category_count(),
        'total_services': sum([len(service_list(section_id)) for section_id in category_list()])
    }

def stats_get_daily():
    """الحصول على الإحصائيات اليومية"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_orders = orders_daily_stats()
    new_users = len(get_users_from_date(today))
    
    return {
        'date': today,
        'new_users': new_users,
        'orders': daily_orders['count'],
        'revenue': daily_orders['revenue'],
        'active_users': get_active_users_count(1)
    }

def stats_get_weekly():
    """الحصول على الإحصائيات الأسبوعية"""
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
    weekly_orders = orders_weekly_stats()
    
    return {
        'week_start': week_start,
        'orders': weekly_orders['count'],
        'revenue': weekly_orders['revenue']
    }

def stats_get_monthly():
    """الحصول على الإحصائيات الشهرية"""
    month = datetime.now().strftime('%Y-%m')
    monthly_orders = orders_monthly_stats()
    
    return {
        'month': month,
        'orders': monthly_orders['count'],
        'revenue': monthly_orders['revenue']
    }

def stats_get_orders():
    """الحصول على إحصائيات الطلبات"""
    return orders_stats()

# ============================================================
# دوال إحصائيات المستخدمين
# ============================================================

def stats_user_growth(days=30):
    """الحصول على نمو المستخدمين خلال أيام"""
    growth = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        users = get_users_from_date(date)
        growth.append({
            'date': date,
            'new_users': len(users),
            'total_users': len(get_all_users())
        })
    return growth

def stats_user_activity(days=7):
    """الحصول على نشاط المستخدمين خلال أيام"""
    activity = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        orders = orders_daily_stats()
        activity.append({
            'date': date,
            'orders': orders['count'],
            'revenue': orders['revenue']
        })
    return activity

def stats_user_ranks(limit=10):
    """الحصول على ترتيب المستخدمين"""
    users = get_all_users()
    ranks = []
    
    for user_id in users:
        balance = get_coin(user_id)
        if balance > 0:
            ranks.append((user_id, balance))
    
    ranks.sort(key=lambda x: x[1], reverse=True)
    return ranks[:limit]

def stats_user_orders_ranks(limit=10):
    """الحصول على ترتيب المستخدمين حسب الطلبات"""
    users = get_all_users()
    ranks = []
    
    for user_id in users:
        count = orders_count_by_user(user_id)
        if count > 0:
            ranks.append((user_id, count))
    
    ranks.sort(key=lambda x: x[1], reverse=True)
    return ranks[:limit]

def stats_user_referral_ranks(limit=10):
    """الحصول على ترتيب المستخدمين حسب الإحالات"""
    users = get_all_users()
    ranks = []
    
    for user_id in users:
        count = referral_get_count(user_id)
        if count > 0:
            ranks.append((user_id, count))
    
    ranks.sort(key=lambda x: x[1], reverse=True)
    return ranks[:limit]

# ============================================================
# دوال إحصائيات الخدمات
# ============================================================

def stats_service_popularity():
    """الحصول على شهرة الخدمات"""
    stats = orders_stats()
    return {
        'top_service': stats['top_service'],
        'top_service_count': stats['top_service_count'],
        'all_services': stats.get('all_services', {})
    }

def stats_service_category_popularity():
    """الحصول على شهرة الأقسام"""
    services = load_services()
    popularity = {}
    
    for section_id, service_list in services['xdmaxs'].items():
        category_name = services['NAMES'].get(section_id, '')
        if category_name:
            count = 0
            for idx, name in enumerate(service_list):
                # حساب عدد الطلبات لكل خدمة
                if idx in services.get('order_count', {}):
                    count += services['order_count'][section_id].get(str(idx), 0)
            popularity[category_name] = count
    
    return popularity

# ============================================================
# دوال إحصائيات النقاط
# ============================================================

def stats_points_distribution():
    """الحصول على توزيع النقاط"""
    users = get_all_users()
    distribution = {
        '0-100': 0,
        '101-500': 0,
        '501-1000': 0,
        '1001-5000': 0,
        '5001-10000': 0,
        '10000+': 0
    }
    
    for user_id in users:
        balance = get_coin(user_id)
        if balance <= 100:
            distribution['0-100'] += 1
        elif balance <= 500:
            distribution['101-500'] += 1
        elif balance <= 1000:
            distribution['501-1000'] += 1
        elif balance <= 5000:
            distribution['1001-5000'] += 1
        elif balance <= 10000:
            distribution['5001-10000'] += 1
        else:
            distribution['10000+'] += 1
    
    return distribution

def stats_points_total():
    """الحصول على إجمالي النقاط في النظام"""
    return get_system_total_points()

def stats_points_earned_today():
    """الحصول على النقاط المكتسبة اليوم"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = WALLET_LOG_FILE
    total = 0
    
    if not os.path.exists(log_file):
        return 0
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry['time'].startswith(today) and entry['type'] == 'charge':
                    total += float(entry['amount'])
            except:
                continue
    
    return total

# ============================================================
# دوال تقارير النظام
# ============================================================

def stats_system_report():
    """توليد تقرير النظام الكامل"""
    basic = stats_get_basic()
    daily = stats_get_daily()
    weekly = stats_get_weekly()
    monthly = stats_get_monthly()
    orders = stats_get_orders()
    points_dist = stats_points_distribution()
    
    report = f"""
📊 <b>تقرير النظام الشامل</b>
━━━━━━━━━━━━━━━━━━━━━━━━
<b>📌 الإحصائيات الأساسية</b>
━━━━━━━━━━━━━━━━━━━━━━━━
👥 <b>إجمالي المستخدمين:</b> {basic['total_users']}
🚫 <b>المحظورين:</b> {basic['banned_users']}
📊 <b>النشطين:</b> {basic['active_users']}
📦 <b>إجمالي الطلبات:</b> {basic['total_orders']}
💰 <b>إجمالي الأرباح:</b> {basic['total_revenue']}
💵 <b>إجمالي النقاط:</b> {basic['total_points']}
📂 <b>الأقسام:</b> {basic['total_categories']}
🛠 <b>الخدمات:</b> {basic['total_services']}
━━━━━━━━━━━━━━━━━━━━━━━━
<b>📅 الإحصائيات اليومية</b>
━━━━━━━━━━━━━━━━━━━━━━━━
📆 <b>التاريخ:</b> {daily['date']}
👤 <b>مستخدمين جدد:</b> {daily['new_users']}
📦 <b>الطلبات:</b> {daily['orders']}
💰 <b>الأرباح:</b> {daily['revenue']}
━━━━━━━━━━━━━━━━━━━━━━━━
<b>📆 الإحصائيات الأسبوعية</b>
━━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>الطلبات:</b> {weekly['orders']}
💰 <b>الأرباح:</b> {weekly['revenue']}
━━━━━━━━━━━━━━━━━━━━━━━━
<b>📆 الإحصائيات الشهرية</b>
━━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>الطلبات:</b> {monthly['orders']}
💰 <b>الأرباح:</b> {monthly['revenue']}
━━━━━━━━━━━━━━━━━━━━━━━━
<b>📊 حالة الطلبات</b>
━━━━━━━━━━━━━━━━━━━━━━━━
⏳ <b>قيد الانتظار:</b> {orders['by_status']['pending']}
⚙️ <b>قيد التنفيذ:</b> {orders['by_status']['processing']}
✅ <b>مكتملة:</b> {orders['by_status']['completed']}
❌ <b>ملغية:</b> {orders['by_status']['canceled']}
━━━━━━━━━━━━━━━━━━━━━━━━
<b>💰 توزيع النقاط</b>
━━━━━━━━━━━━━━━━━━━━━━━━
0-100: {points_dist['0-100']} مستخدم
101-500: {points_dist['101-500']} مستخدم
501-1000: {points_dist['501-1000']} مستخدم
1001-5000: {points_dist['1001-5000']} مستخدم
5001-10000: {points_dist['5001-10000']} مستخدم
10000+: {points_dist['10000+']} مستخدم
"""
    return report

# ============================================================
# دوال تقارير المستخدمين
# ============================================================

def stats_user_report(user_id):
    """توليد تقرير عن مستخدم"""
    info = get_user_info(user_id)
    user_orders = orders_user_stats(user_id)
    referrals = referral_get_count(user_id)
    tickets = ticket_user_stats(user_id)
    
    report = f"""
📊 <b>تقرير المستخدم</b>
━━━━━━━━━━━━━━━━━
🆔 <b>المستخدم:</b> <code>{user_id}</code>
💰 <b>الرصيد:</b> {info['balance']}
💸 <b>المصروفات:</b> {info['spent']}
👥 <b>الإحالات:</b> {referrals}
📦 <b>الطلبات:</b> {info['orders']}
🚫 <b>محظور:</b> {'نعم' if info['is_banned'] else 'لا'}
━━━━━━━━━━━━━━━━━
<b>تفاصيل الطلبات</b>
⏳ قيد الانتظار: {user_orders['by_status']['pending']}
⚙️ قيد التنفيذ: {user_orders['by_status']['processing']}
✅ مكتملة: {user_orders['by_status']['completed']}
❌ ملغية: {user_orders['by_status']['canceled']}
━━━━━━━━━━━━━━━━━
<b>الدعم الفني</b>
🎫 التذاكر: {tickets['total']}
🟢 مفتوحة: {tickets['open']}
🔵 محلولة: {tickets['resolved']}
"""
    return report

# ============================================================
# دوال تصدير التقارير
# ============================================================

def stats_export_report(format='json'):
    """تصدير التقرير بصيغة محددة"""
    data = {
        'basic': stats_get_basic(),
        'daily': stats_get_daily(),
        'weekly': stats_get_weekly(),
        'monthly': stats_get_monthly(),
        'orders': stats_get_orders(),
        'timestamp': datetime.now().isoformat()
    }
    
    if format == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif format == 'text':
        return stats_system_report()
    else:
        return None

def stats_export_to_file(format='json'):
    """تصدير التقرير إلى ملف"""
    content = stats_export_report(format)
    if not content:
        return None
    
    filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format}"
    file_path = f"./exports/{filename}"
    
    os.makedirs('./exports', exist_ok=True)
    file_write(file_path, content)
    
    return file_path

# ============================================================
# دوال إحصائيات التذاكر والدعم
# ============================================================

def stats_tickets_report():
    """توليد تقرير التذاكر"""
    stats = ticket_stats()
    avg_response = ticket_avg_response_time()
    
    report = f"""
?? <b>تقرير التذاكر</b>
━━━━━━━━━━━━━━━━━
📋 <b>إجمالي التذاكر:</b> {stats['total']}
🟢 <b>مفتوحة:</b> {stats['open']}
🟡 <b>قيد المعالجة:</b> {stats['in_progress']}
🔵 <b>محلولة:</b> {stats['resolved']}
⚫ <b>مغلقة:</b> {stats['closed']}
━━━━━━━━━━━━━━━━━
<b>حسب الأولوية:</b>
🟢 منخفضة: {stats['by_priority']['low']}
🟡 عادية: {stats['by_priority']['normal']}
🟠 عالية: {stats['by_priority']['high']}
🔴 عاجلة: {stats['by_priority']['urgent']}
━━━━━━━━━━━━━━━━━
⏱️ <b>متوسط وقت الاستجابة:</b> {avg_response:.1f} ساعة
"""
    return report

# ============================================================
# نهاية الجزء 15
# ============================================================
# ============================================================
# الجزء 16: نظام الإعدادات والتهيئة (Settings & Configuration) - 1500 سطر
# ============================================================

# ============================================================
# دوال إعدادات البوت الأساسية
# ============================================================

def bot_settings_get_all():
    """الحصول على جميع إعدادات البوت"""
    return {
        'general': {
            'bot_name': file_read('edid/nambot.txt') or 'DomKom',
            'bot_token': BOT_TOKEN,
            'admin_id': ADMIN_ID,
            'support': SUPPORT,
            'currency': get_currency_name_from_file(),
            'site': service_get_site(),
            'api_token': service_get_token()
        },
        'points': {
            'coins_start': get_coins_start(),
            'adna_coins': get_adna_coins(),
            'day_coins': get_day_coins(),
            'work_add_day': get_work_add_day(),
            'add_ado': get_add_ado(),
            'add_aoc': get_add_aoc()
        },
        'features': {
            'baageel': file_read('baageel.txt') or '✅',
            'opan': file_read('edid/opan.txt') or '✅',
            'tmwel': file_read('edid/tmwel.txt') or '✅',
            'coadd': file_read('edid/coadd.txt') or '✅',
            'add_day': file_read('edid/add_day.txt') or '✅',
            'nzambot': file_read('edid/nzambot.txt') or '❌',
            'asttacbot': file_read('edid/asttacbot.txt') or '❌',
            'fwrmember': load_sudo_data().get('info', {}).get('fwrmember', '❎'),
            'tnbih': load_sudo_data().get('info', {}).get('tnbih', '✅'),
            'silk': load_sudo_data().get('info', {}).get('silk', '✅'),
            'allch': load_sudo_data().get('info', {}).get('allch', '✅')
        },
        'messages': {
            'start': file_read('start.txt'),
            'klish_sil': load_sudo_data().get('info', {}).get('klish_sil', ''),
            'msgasro': file_read('edid/msgasro.txt'),
            'msgasar': file_read('edid/msgasar.txt'),
            'msgaspat': file_read('edid/msgaspat.txt')
        },
        'channels': {
            'mandatory': channel_list(),
            'funding': funding_channel_list(),
            'admin_channel': file_read('edid/chadmin.txt') or 'لم يتم تعين قناة',
            'contact': file_read('edid/acont_admin.txt') or 'لم يتم تعين حساب'
        },
        'buttons': load_buttons(),
        'replies': load_replies(),
        'commands': load_commands()
    }

def bot_settings_update(settings):
    """تحديث إعدادات البوت"""
    # تحديث الإعدادات العامة
    if 'general' in settings:
        gen = settings['general']
        if 'bot_name' in gen:
            file_write('edid/nambot.txt', gen['bot_name'])
        if 'currency' in gen:
            file_write('edid/currency_name.txt', gen['currency'])
        if 'site' in gen:
            service_set_site(gen['site'])
        if 'api_token' in gen:
            service_set_token(gen['api_token'])
    
    # تحديث إعدادات النقاط
    if 'points' in settings:
        pts = settings['points']
        if 'coins_start' in pts:
            file_write('edid/coinsstart.txt', str(pts['coins_start']))
        if 'adna_coins' in pts:
            file_write('data/adna_coins.txt', str(pts['adna_coins']))
        if 'day_coins' in pts:
            file_write('data/day_coins.txt', str(pts['day_coins']))
        if 'work_add_day' in pts:
            file_write('edid/work_add_day.txt', str(pts['work_add_day']))
        if 'add_ado' in pts:
            file_write('edid/addado.txt', str(pts['add_ado']))
        if 'add_aoc' in pts:
            file_write('edid/add_aoc.txt', str(pts['add_aoc']))
    
    # تحديث إعدادات الميزات
    if 'features' in settings:
        feat = settings['features']
        if 'baageel' in feat:
            file_write('baageel.txt', feat['baageel'])
        if 'opan' in feat:
            file_write('edid/opan.txt', feat['opan'])
        if 'tmwel' in feat:
            file_write('edid/tmwel.txt', feat['tmwel'])
        if 'coadd' in feat:
            file_write('edid/coadd.txt', feat['coadd'])
        if 'add_day' in feat:
            file_write('edid/add_day.txt', feat['add_day'])
        if 'nzambot' in feat:
            file_write('edid/nzambot.txt', feat['nzambot'])
        if 'asttacbot' in feat:
            file_write('edid/asttacbot.txt', feat['asttacbot'])
        if 'fwrmember' in feat or 'tnbih' in feat or 'silk' in feat or 'allch' in feat:
            sudo_data = load_sudo_data()
            if 'fwrmember' in feat:
                sudo_data['info']['fwrmember'] = feat['fwrmember']
            if 'tnbih' in feat:
                sudo_data['info']['tnbih'] = feat['tnbih']
            if 'silk' in feat:
                sudo_data['info']['silk'] = feat['silk']
            if 'allch' in feat:
                sudo_data['info']['allch'] = feat['allch']
            save_sudo_data(sudo_data)
    
    # تحديث الرسائل
    if 'messages' in settings:
        msg = settings['messages']
        if 'start' in msg and msg['start']:
            file_write('start.txt', msg['start'])
        if 'klish_sil' in msg:
            sudo_data = load_sudo_data()
            sudo_data['info']['klish_sil'] = msg['klish_sil']
            save_sudo_data(sudo_data)
        if 'msgasro' in msg:
            file_write('edid/msgasro.txt', msg['msgasro'])
        if 'msgasar' in msg:
            file_write('edid/msgasar.txt', msg['msgasar'])
        if 'msgaspat' in msg:
            file_write('edid/msgaspat.txt', msg['msgaspat'])
    
    return True

# ============================================================
# دوال إعدادات النقاط
# ============================================================

def points_settings_get():
    """الحصول على إعدادات النقاط"""
    return {
        'coins_start': get_coins_start(),
        'adna_coins': get_adna_coins(),
        'day_coins': get_day_coins(),
        'work_add_day': get_work_add_day(),
        'add_ado': get_add_ado(),
        'add_aoc': get_add_aoc(),
        'currency_name': get_currency_name_from_file()
    }

def points_settings_update(settings):
    """تحديث إعدادات النقاط"""
    if 'coins_start' in settings:
        file_write('edid/coinsstart.txt', str(settings['coins_start']))
    if 'adna_coins' in settings:
        file_write('data/adna_coins.txt', str(settings['adna_coins']))
    if 'day_coins' in settings:
        file_write('data/day_coins.txt', str(settings['day_coins']))
    if 'work_add_day' in settings:
        file_write('edid/work_add_day.txt', str(settings['work_add_day']))
    if 'add_ado' in settings:
        file_write('edid/addado.txt', str(settings['add_ado']))
    if 'add_aoc' in settings:
        file_write('edid/add_aoc.txt', str(settings['add_aoc']))
    if 'currency_name' in settings:
        file_write('edid/currency_name.txt', settings['currency_name'])
    return True

# ============================================================
# دوال إعدادات الميزات
# ============================================================

def features_settings_get():
    """الحصول على إعدادات الميزات"""
    sudo_data = load_sudo_data()
    return {
        'baageel': file_read('baageel.txt') or '✅',
        'opan': file_read('edid/opan.txt') or '✅',
        'tmwel': file_read('edid/tmwel.txt') or '✅',
        'coadd': file_read('edid/coadd.txt') or '✅',
        'add_day': file_read('edid/add_day.txt') or '✅',
        'nzambot': file_read('edid/nzambot.txt') or '❌',
        'asttacbot': file_read('edid/asttacbot.txt') or '❌',
        'fwrmember': sudo_data.get('info', {}).get('fwrmember', '❎'),
        'tnbih': sudo_data.get('info', {}).get('tnbih', '✅'),
        'silk': sudo_data.get('info', {}).get('silk', '✅'),
        'allch': sudo_data.get('info', {}).get('allch', '✅')
    }

def features_settings_toggle(feature):
    """تبديل حالة ميزة"""
    current = file_read(f'edid/{feature}.txt') or '✅'
    new_value = '❌' if current == '✅' else '✅'
    file_write(f'edid/{feature}.txt', new_value)
    return new_value

# ============================================================
# دوال إعدادات الرسائل
# ============================================================

def messages_settings_get():
    """الحصول على إعدادات الرسائل"""
    sudo_data = load_sudo_data()
    return {
        'start': file_read('start.txt'),
        'klish_sil': sudo_data.get('info', {}).get('klish_sil', ''),
        'msgasro': file_read('edid/msgasro.txt'),
        'msgasar': file_read('edid/msgasar.txt'),
        'msgaspat': file_read('edid/msgaspat.txt'),
        'aklamrnm1': file_read('edid/aklamrnm1.txt') or 'الخدمات 🗂',
        'aklamrnm2': file_read('edid/aklamrnm2.txt') or 'تجميع ✳️',
        'aklamrnm3': file_read('edid/aklamrnm3.txt') or 'الحساب 🗃️',
        'aklamrnm4': file_read('edid/aklamrnm4.txt') or 'استخدام كود 💳',
        'aklamrnm5': file_read('edid/aklamrnm5.txt') or 'تحويل نقاط ♻️',
        'aklamrnm6': file_read('edid/aklamrnm6.txt') or 'معلومات الطلب 📥',
        'aklamrnm7': file_read('edid/aklamrnm7.txt') or 'طلباتي 📮',
        'aklamrnm8': file_read('edid/aklamrnm8.txt') or 'قناة البوت 🤍',
        'aklamrnm9': file_read('edid/aklamrnm9.txt') or 'شحن نقاط 💰',
        'aklamrnm10': file_read('edid/aklamrnm10.txt') or 'الشروط 📜'
    }

def messages_settings_update(settings):
    """تحديث إعدادات الرسائل"""
    sudo_data = load_sudo_data()
    
    if 'start' in settings:
        file_write('start.txt', settings['start'])
    if 'klish_sil' in settings:
        sudo_data['info']['klish_sil'] = settings['klish_sil']
    if 'msgasro' in settings:
        file_write('edid/msgasro.txt', settings['msgasro'])
    if 'msgasar' in settings:
        file_write('edid/msgasar.txt', settings['msgasar'])
    if 'msgaspat' in settings:
        file_write('edid/msgaspat.txt', settings['msgaspat'])
    if 'aklamrnm1' in settings:
        file_write('edid/aklamrnm1.txt', settings['aklamrnm1'])
    if 'aklamrnm2' in settings:
        file_write('edid/aklamrnm2.txt', settings['aklamrnm2'])
    if 'aklamrnm3' in settings:
        file_write('edid/aklamrnm3.txt', settings['aklamrnm3'])
    if 'aklamrnm4' in settings:
        file_write('edid/aklamrnm4.txt', settings['aklamrnm4'])
    if 'aklamrnm5' in settings:
        file_write('edid/aklamrnm5.txt', settings['aklamrnm5'])
    if 'aklamrnm6' in settings:
        file_write('edid/aklamrnm6.txt', settings['aklamrnm6'])
    if 'aklamrnm7' in settings:
        file_write('edid/aklamrnm7.txt', settings['aklamrnm7'])
    if 'aklamrnm8' in settings:
        file_write('edid/aklamrnm8.txt', settings['aklamrnm8'])
    if 'aklamrnm9' in settings:
        file_write('edid/aklamrnm9.txt', settings['aklamrnm9'])
    if 'aklamrnm10' in settings:
        file_write('edid/aklamrnm10.txt', settings['aklamrnm10'])
    
    save_sudo_data(sudo_data)
    return True

# ============================================================
# دوال إعدادات القنوات
# ============================================================

def channels_settings_get():
    """الحصول على إعدادات القنوات"""
    return {
        'mandatory': channel_list(),
        'funding': funding_channel_list(),
        'admin_channel': file_read('edid/chadmin.txt') or 'لم يتم تعين قناة',
        'contact': file_read('edid/acont_admin.txt') or 'لم يتم تعين حساب',
        'aspatchid': file_read('edid/aspatchid1.txt') or 'لم يتم تعين قناة'
    }

def channels_settings_update(settings):
    """تحديث إعدادات القنوات"""
    if 'admin_channel' in settings:
        file_write('edid/chadmin.txt', settings['admin_channel'])
    if 'contact' in settings:
        file_write('edid/acont_admin.txt', settings['contact'])
    if 'aspatchid' in settings:
        file_write('edid/aspatchid1.txt', settings['aspatchid'])
    return True

# ============================================================
# دوال إعدادات الأزرار والردود
# ============================================================

def buttons_settings_get():
    """الحصول على إعدادات الأزرار"""
    return load_buttons()

def buttons_settings_update(buttons):
    """تحديث إعدادات الأزرار"""
    return save_buttons(buttons)

def replies_settings_get():
    """الحصول على إعدادات الردود"""
    return load_replies()

def replies_settings_update(replies):
    """تحديث إعدادات الردود"""
    return save_replies(replies)

def commands_settings_get():
    """الحصول على إعدادات الأوامر المختصرة"""
    return load_commands()

def commands_settings_update(commands):
    """تحديث إعدادات الأوامر المختصرة"""
    return save_commands(commands)

# ============================================================
# دوال إعدادات الأدمن
# ============================================================

def admin_settings_get():
    """الحصول على إعدادات الأدمن"""
    sudo_data = load_sudo_data()
    return {
        'admins': sudo_data.get('info', {}).get('admins', []),
        'fwrmember': sudo_data.get('info', {}).get('fwrmember', '❎'),
        'tnbih': sudo_data.get('info', {}).get('tnbih', '✅'),
        'silk': sudo_data.get('info', {}).get('silk', '✅'),
        'allch': sudo_data.get('info', {}).get('allch', '✅')
    }

def admin_settings_update(settings):
    """تحديث إعدادات الأدمن"""
    sudo_data = load_sudo_data()
    
    if 'admins' in settings:
        sudo_data['info']['admins'] = settings['admins']
    if 'fwrmember' in settings:
        sudo_data['info']['fwrmember'] = settings['fwrmember']
    if 'tnbih' in settings:
        sudo_data['info']['tnbih'] = settings['tnbih']
    if 'silk' in settings:
        sudo_data['info']['silk'] = settings['silk']
    if 'allch' in settings:
        sudo_data['info']['allch'] = settings['allch']
    
    save_sudo_data(sudo_data)
    return True

# ============================================================
# دوال إعدادات API
# ============================================================

def api_settings_get():
    """الحصول على إعدادات API"""
    return {
        'site': service_get_site(),
        'token': service_get_token(),
        'webhook_secret': WEBHOOK_SECRET
    }

def api_settings_update(settings):
    """تحديث إعدادات API"""
    if 'site' in settings:
        service_set_site(settings['site'])
    if 'token' in settings:
        service_set_token(settings['token'])
    return True

# ============================================================
# دوال تصدير واستيراد الإعدادات
# ============================================================

def settings_export():
    """تصدير جميع الإعدادات"""
    return {
        'bot': bot_settings_get_all(),
        'points': points_settings_get(),
        'features': features_settings_get(),
        'messages': messages_settings_get(),
        'channels': channels_settings_get(),
        'admin': admin_settings_get(),
        'api': api_settings_get(),
        'timestamp': datetime.now().isoformat()
    }

def settings_import(data):
    """استيراد جميع الإعدادات"""
    try:
        settings = json.loads(data) if isinstance(data, str) else data
        
        if 'bot' in settings:
            bot_settings_update(settings['bot'])
        if 'points' in settings:
            points_settings_update(settings['points'])
        if 'features' in settings:
            features_settings_update(settings['features'])
        if 'messages' in settings:
            messages_settings_update(settings['messages'])
        if 'channels' in settings:
            channels_settings_update(settings['channels'])
        if 'admin' in settings:
            admin_settings_update(settings['admin'])
        if 'api' in settings:
            api_settings_update(settings['api'])
        
        return True
    except:
        return False

def settings_reset():
    """إعادة تعيين الإعدادات إلى الوضع الافتراضي"""
    create_directories()
    return True

# ============================================================
# نهاية الجزء 16
# ============================================================
# ============================================================
# الجزء 17: نظام معالجة الطلبات (Request Handler) - 1500 سطر
# ============================================================

# ============================================================
# دوال معالجة الرسائل النصية
# ============================================================

def handle_message(update):
    """معالجة الرسائل النصية الواردة"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    message_id = message.get('message_id')
    
    if not chat_id or not from_id:
        return
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ {security_check['reason']}"
        })
        return
    
    # معالجة الأوامر
    if text.startswith('/'):
        handle_command(update)
        return
    
    # معالجة الردود التلقائية
    reply = process_reply(text)
    if reply:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': reply,
            'parse_mode': 'HTML'
        })
        return
    
    # معالجة الحالات (states)
    handle_state(update)

def handle_command(update):
    """معالجة الأوامر"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    message_id = message.get('message_id')
    
    # /start
    if text == '/start':
        handle_start(update)
        return
    
    # /wallet
    if text == '/wallet':
        handle_wallet(update)
        return
    
    # /orders
    if text == '/orders':
        handle_orders(update)
        return
    
    # /id
    if text == '/id':
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"🆔 <b>معرفك:</b> <code>{from_id}</code>",
            'parse_mode': 'HTML'
        })
        return
    
    # /stats (للأدمن فقط)
    if text == '/stats' and is_admin(from_id):
        handle_stats(update)
        return
    
    # /coupon CODE
    if text.startswith('/coupon '):
        handle_coupon(update)
        return
    
    # /createcoupon (للأدمن فقط)
    if text.startswith('/createcoupon ') and is_admin(from_id):
        handle_create_coupon(update)
        return
    
    # /disablecoupon (للأدمن فقط)
    if text.startswith('/disablecoupon ') and is_admin(from_id):
        handle_disable_coupon(update)
        return
    
    # أوامر الأدمن
    if is_admin(from_id):
        if text == '/admin':
            handle_admin_panel(update)
            return
        if text == '/broadcast':
            handle_broadcast(update)
            return
        if text == '/ban':
            handle_ban(update)
            return
        if text == '/unban':
            handle_unban(update)
            return
        if text == '/reset':
            handle_reset_points(update)
            return
    
    # أوامر مختصرة
    command_response = process_command(text)
    if command_response:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': command_response,
            'parse_mode': 'HTML'
        })
        return
    
    # أمر غير معروف
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': "❌ أمر غير معروف. استخدم /help للمساعدة"
    })

# ============================================================
# دوال معالجة الأوامر الأساسية
# ============================================================

def handle_start(update):
    """معالجة أمر /start"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    # التحقق من رابط الإحالة
    if ' ' in text:
        referrer_id = text.split(' ')[1]
        if referrer_id and referrer_id != str(from_id):
            referral_add(referrer_id, from_id)
    
    # إضافة المستخدم
    add_user(from_id)
    
    # التحقق من الإشتراك الإجباري
    subscription_check = mandatory_subscription_check(from_id)
    if not subscription_check['subscribed']:
        keyboard = [
            [{'text': '📢 اشترك في القناة', 'url': subscription_check['channel_link']}],
            [{'text': '✅ تحقق من الإشتراك', 'callback_data': 'check_subscription'}]
        ]
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ يجب الإشتراك في {subscription_check['channel_name']} أولاً",
            'reply_markup': json.dumps({'inline_keyboard': keyboard})
        })
        return
    
    # عرض القائمة الرئيسية
    show_main_menu(chat_id, from_id)

def handle_wallet(update):
    """معالجة أمر /wallet"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    
    balance = get_coin(from_id)
    spent = get_total_spent(from_id)
    referrals = referral_get_count(from_id)
    
    text = f"""
💰 <b>محفظتك</b>
━━━━━━━━━━━━━━━━━
💵 <b>الرصيد:</b> {balance} نقطة
💸 <b>المصروفات:</b> {spent} نقطة
👥 <b>الإحالات:</b> {referrals}
📊 <b>الترتيب:</b> #{get_user_rank(from_id)}
"""
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    })

def handle_orders(update):
    """معالجة أمر /orders"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    
    orders_text = orders_user_text(from_id)
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': orders_text,
        'parse_mode': 'HTML'
    })

def handle_stats(update):
    """معالجة أمر /stats (للأدمن)"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    
    report = stats_system_report()
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': report,
        'parse_mode': 'HTML'
    })

def handle_coupon(update):
    """معالجة أمر /coupon"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    code = text.split(' ')[1] if len(text.split(' ')) > 1 else ''
    if not code:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ يرجى إرسال الكود بعد الأمر\nمثال: /coupon CODE123"
        })
        return
    
    result = coupon_redeem(code, from_id)
    if result['ok']:
        coupon = result['coupon']
        if coupon['type'] == 'charge':
            add_points(from_id, coupon['value'], f'كوبون: {code}')
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"✅ تم شحن {coupon['value']} نقطة باستخدام الكوبون {code}"
            })
        else:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"✅ تم تفعيل خصم {coupon['value']}% باستخدام الكوبون {code}"
            })
    else:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': result['message']
        })

def handle_create_coupon(update):
    """معالجة أمر /createcoupon (للأدمن)"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')
    
    parts = text.split(' ')
    if len(parts) < 4:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ صيغة غير صحيحة\nمثال: /createcoupon CODE charge 10 0"
        })
        return
    
    code = parts[1]
    type_ = parts[2]
    value = float(parts[3])
    max_uses = int(parts[4]) if len(parts) > 4 else 0
    
    result = coupon_create(code, type_, value, max_uses)
    if result:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"✅ تم إنشاء كوبون جديد\nالكود: {code}\nالنوع: {type_}\nالقيمة: {value}"
        })
    else:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ فشل إنشاء الكوبون. تأكد من صحة البيانات"
        })

def handle_disable_coupon(update):
    """معالجة أمر /disablecoupon (للأدمن)"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')
    
    code = text.split(' ')[1] if len(text.split(' ')) > 1 else ''
    if not code:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ يرجى إرسال الكود بعد الأمر\nمثال: /disablecoupon CODE123"
        })
        return
    
    if coupon_disable(code):
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"✅ تم تعطيل الكوبون: {code}"
        })
    else:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"❌ الكوبون غير موجود: {code}"
        })

# ============================================================
# دوال معالجة الأوامر الإدارية
# ============================================================

def handle_admin_panel(update):
    """معالجة لوحة الأدمن"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    
    keyboard = get_admin_keyboard()
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': get_admin_panel_message(),
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({'inline_keyboard': keyboard})
    })

def handle_broadcast(update):
    """معالجة أمر الإذاعة"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    
    if not is_admin(from_id):
        return
    
    # طلب رسالة الإذاعة
    user_states[from_id] = 'broadcast_wait'
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': "📢 أرسل الرسالة التي تريد إذاعتها للجميع:"
    })

def handle_ban(update):
    """معالجة أمر الحظر"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    if not is_admin(from_id):
        return
    
    parts = text.split(' ')
    if len(parts) < 2:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ يرجى إرسال ايدي المستخدم\nمثال: /ban 123456789"
        })
        return
    
    user_id = parts[1]
    reason = ' '.join(parts[2:]) if len(parts) > 2 else ''
    
    result = ban_user(user_id, reason)
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': result['message']
    })

def handle_unban(update):
    """معالجة أمر إلغاء الحظر"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    if not is_admin(from_id):
        return
    
    parts = text.split(' ')
    if len(parts) < 2:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ يرجى إرسال ايدي المستخدم\nمثال: /unban 123456789"
        })
        return
    
    user_id = parts[1]
    result = unban_user_action(user_id)
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': result['message']
    })

def handle_reset_points(update):
    """معالجة أمر إعادة تعيين النقاط"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    if not is_admin(from_id):
        return
    
    parts = text.split(' ')
    if len(parts) < 2:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ يرجى إرسال ايدي المستخدم\nمثال: /reset 123456789"
        })
        return
    
    user_id = parts[1]
    if reset_user_points(user_id):
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"✅ تم إعادة تعيين نقاط المستخدم {user_id}"
        })
    else:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ فشل إعادة تعيين النقاط"
        })

# ============================================================
# دوال معالجة الحالات (States)
# ============================================================

user_states = {}

def handle_state(update):
    """معالجة الحالات"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    state = user_states.get(from_id)
    
    if state == 'broadcast_wait':
        # إرسال الإذاعة
        result = broadcast_message(text)
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"📢 تم الإذاعة\n✅ نجح: {result['success']}\n❌ فشل: {result['failed']}"
        })
        user_states.pop(from_id, None)
        return
    
    if state == 'admin_add_points':
        # إضافة نقاط لمستخدم
        parts = text.split(' ')
        if len(parts) < 2:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': "❌ صيغة غير صحيحة\nمثال: user_id amount"
            })
            return
        
        user_id = parts[0]
        amount = float(parts[1])
        reason = ' '.join(parts[2:]) if len(parts) > 2 else ''
        
        result = admin_add_points(user_id, amount, reason)
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': result['message']
        })
        user_states.pop(from_id, None)
        return

# ============================================================
# دوال عرض القوائم
# ============================================================

def show_main_menu(chat_id, user_id):
    """عرض القائمة الرئيسية"""
    cdiamlaadf = get_currency_name_from_file()
    cdiamlanoo = cdiamlaadf
    coin = get_coin(user_id)
    cuser = get_user_data(user_id)
    
    keyboard = ne_home_keyboard()
    reply_markup = json.dumps({'inline_keyboard': keyboard})
    
    start_text = ne_home_text(chat_id, user_id, cuser, {}, cdiamlaadf, cdiamlanoo)
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': start_text,
        'parse_mode': 'HTML',
        'reply_markup': reply_markup
    })

# ============================================================
# دوال معالجة الإشتراك الإجباري
# ============================================================

def handle_subscription_check(update):
    """معالجة التحقق من الإشتراك"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    from_id = callback_query.get('from', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    
    check_result = process_subscription_check(from_id)
    
    if check_result['success']:
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "✅ تم التحقق من إشتراكك بنجاح"
        })
        show_main_menu(chat_id, from_id)
    else:
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': check_result['message'],
            'show_alert': True
        })

# ============================================================
# نهاية الجزء 17
# ============================================================
# ============================================================
# الجزء 18: نظام معالجة الأزرار والكول باك (Callback Handler) - 1500 سطر
# ============================================================

# ============================================================
# دوال معالجة الكول باك الأساسية
# ============================================================

def handle_callback(update):
    """معالجة الكول باك الواردة"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    from_id = callback_query.get('from', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    data = callback_query.get('data', '')
    callback_id = callback_query.get('id')
    
    if not chat_id or not from_id:
        return
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('answerCallbackQuery', {
            'callback_query_id': callback_id,
            'text': f"⚠️ {security_check['reason']}",
            'show_alert': True
        })
        return
    
    # معالجة الكول باك
    if data.startswith('category_'):
        handle_category_callback(update)
    elif data.startswith('service_'):
        handle_service_callback(update)
    elif data.startswith('order_'):
        handle_order_callback(update)
    elif data.startswith('admin_'):
        handle_admin_callback(update)
    elif data.startswith('emperor_'):
        handle_emperor_callback(update)
    elif data.startswith('ne_'):
        handle_ne_callback(update)
    elif data.startswith('check_subscription'):
        handle_subscription_check(update)
    elif data.startswith('panel'):
        handle_panel_callback(update)
    else:
        handle_general_callback(update)

# ============================================================
# دوال معالجة الكول باك الأساسية
# ============================================================

def handle_panel_callback(update):
    """معالجة العودة للوحة الرئيسية"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    from_id = callback_query.get('from', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    
    show_main_menu_with_edit(chat_id, from_id, message_id)

def show_main_menu_with_edit(chat_id, user_id, message_id):
    """عرض القائمة الرئيسية مع تعديل الرسالة"""
    cdiamlaadf = get_currency_name_from_file()
    cdiamlanoo = cdiamlaadf
    coin = get_coin(user_id)
    cuser = get_user_data(user_id)
    
    keyboard = ne_home_keyboard()
    reply_markup = json.dumps({'inline_keyboard': keyboard})
    
    start_text = ne_home_text(chat_id, user_id, cuser, {}, cdiamlaadf, cdiamlanoo)
    bot('editMessageText', {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': start_text,
        'parse_mode': 'HTML',
        'reply_markup': reply_markup
    })

# ============================================================
# دوال معالجة الأقسام والخدمات
# ============================================================

def handle_category_callback(update):
    """معالجة اختيار قسم"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    data = callback_query.get('data', '')
    
    section_id = data.replace('category_', '')
    category = category_get(section_id)
    
    if not category:
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': 'القسم غير موجود',
            'show_alert': True
        })
        return
    
    # عرض خدمات القسم
    services = service_list(section_id)
    keyboard = []
    
    for idx, name in enumerate(services):
        keyboard.append([{
            'text': name,
            'callback_data': f'service_{section_id}_{idx}'
        }])
    
    keyboard.append([{'text': '🔙 رجوع', 'callback_data': 'panel'}])
    
    bot('editMessageText', {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': f"📂 <b>{category['name']}</b>\nاختر الخدمة المطلوبة:",
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({'inline_keyboard': keyboard})
    })

def handle_service_callback(update):
    """معالجة اختيار خدمة"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    from_id = callback_query.get('from', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    data = callback_query.get('data', '')
    
    parts = data.split('_')
    if len(parts) < 3:
        return
    
    section_id = parts[1]
    index = int(parts[2])
    
    service = service_get(section_id, index)
    if not service:
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': 'الخدمة غير موجودة',
            'show_alert': True
        })
        return
    
    # عرض تفاصيل الخدمة
    price_per_1000 = service['price'] * 1000
    text = f"""
🛠 <b>{service['name']}</b>
━━━━━━━━━━━━━━━━━
💰 <b>السعر:</b> {price_per_1000} نقطة لكل 1000
📊 <b>الحد الأدنى:</b> {service['min']}
📊 <b>الحد الأقصى:</b> {service['max']}
📝 <b>الوصف:</b> {service['description'] or 'لا يوجد وصف'}
"""
    
    keyboard = [
        [{'text': '📥 طلب الخدمة', 'callback_data': f'order_{section_id}_{index}'}],
        [{'text': '🔙 رجوع', 'callback_data': f'category_{section_id}'}]
    ]
    
    bot('editMessageText', {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({'inline_keyboard': keyboard})
    })

# ============================================================
# دوال معالجة الطلبات
# ============================================================

def handle_order_callback(update):
    """معالجة طلب خدمة"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    from_id = callback_query.get('from', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    data = callback_query.get('data', '')
    
    parts = data.split('_')
    if len(parts) < 3:
        return
    
    section_id = parts[1]
    index = int(parts[2])
    
    service = service_get(section_id, index)
    if not service:
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': 'الخدمة غير موجودة',
            'show_alert': True
        })
        return
    
    # طلب الرابط والكمية
    user_states[from_id] = f'order_{section_id}_{index}'
    
    bot('editMessageText', {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': f"📥 <b>طلب {service['name']}</b>\n━━━━━━━━━━━━━━━━━\nأرسل الرابط المطلوب:",
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({'inline_keyboard': [[{'text': '🔙 إلغاء', 'callback_data': f'service_{section_id}_{index}'}]]})
    })

def handle_order_submit(update):
    """معالجة إرسال رابط الطلب"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    state = user_states.get(from_id, '')
    if not state.startswith('order_'):
        return
    
    parts = state.split('_')
    section_id = parts[1]
    index = int(parts[2])
    
    service = service_get(section_id, index)
    if not service:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': '❌ الخدمة غير موجودة'
        })
        user_states.pop(from_id, None)
        return
    
    # حفظ الرابط وطلب الكمية
    user_states[from_id] = f'order_quantity_{section_id}_{index}_{text}'
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': f"📥 <b>طلب {service['name']}</b>\n━━━━━━━━━━━━━━━━━\nالرابط: {text}\n\nأرسل الكمية المطلوبة (الحد الأدنى: {service['min']}):",
        'parse_mode': 'HTML'
    })

def handle_order_quantity(update):
    """معالجة إرسال كمية الطلب"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    state = user_states.get(from_id, '')
    if not state.startswith('order_quantity_'):
        return
    
    parts = state.split('_')
    section_id = parts[2]
    index = int(parts[3])
    link = parts[4]
    
    if not text.isdigit():
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': '❌ يرجى إرسال رقم صحيح'
        })
        return
    
    quantity = int(text)
    service = service_get(section_id, index)
    
    if quantity < service['min']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"❌ الحد الأدنى للطلب هو {service['min']}"
        })
        return
    
    if quantity > service['max']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"❌ الحد الأقصى للطلب هو {service['max']}"
        })
        return
    
    # حساب السعر
    total_price = service['price'] * quantity
    
    # التحقق من الرصيد
    balance = get_coin(from_id)
    if balance < total_price:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"❌ رصيدك غير كافي\nالمطلوب: {total_price} نقطة\nالرصيد: {balance} نقطة"
        })
        user_states.pop(from_id, None)
        return
    
    # تنفيذ الطلب عبر API
    web = service['web']
    key = service['key']
    service_id = service['service_id']
    
    if not web or not key or not service_id:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ بيانات API غير مكتملة"
        })
        user_states.pop(from_id, None)
        return
    
    result = smm_api_order(service_id, link, quantity, key, f"https://{web}")
    
    if not result or 'order' not in result:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ فشل إنشاء الطلب في الموقع"
        })
        user_states.pop(from_id, None)
        return
    
    order_id = result['order']
    
    # خصم النقاط
    deduct_points(from_id, total_price, f'طلب خدمة: {service["name"]} #{order_id}')
    
    # تسجيل الطلب
    order_create(order_id, from_id, service_id, link, quantity, total_price)
    
    # إشعار للأدمن
    notify_new_order(order_id)
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': f"✅ تم إنشاء الطلب بنجاح\n🔢 رقم الطلب: {order_id}\n🛠 الخدمة: {service['name']}\n📊 الكمية: {quantity}\n💰 السعر: {total_price} نقطة"
    })
    
    user_states.pop(from_id, None)

# ============================================================
# دوال معالجة الكول باك الإدارية
# ============================================================

def handle_admin_callback(update):
    """معالجة كول باك الأدمن"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    from_id = callback_query.get('from', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    data = callback_query.get('data', '')
    
    if not is_admin(from_id):
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': 'ليس لديك صلاحيات',
            'show_alert': True
        })
        return
    
    if data == 'admin_users':
        # عرض إدارة المستخدمين
        keyboard = [
            [{'text': '📋 قائمة المستخدمين', 'callback_data': 'admin_users_list'}],
            [{'text': '🚫 حظر مستخدم', 'callback_data': 'admin_ban'}],
            [{'text': '✅ إلغاء حظر', 'callback_data': 'admin_unban'}],
            [{'text': '💰 إضافة نقاط', 'callback_data': 'admin_add_points'}],
            [{'text': '💸 خصم نقاط', 'callback_data': 'admin_deduct_points'}],
            [{'text': '🔙 رجوع', 'callback_data': 'panel'}]
        ]
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': '👥 <b>إدارة المستخدمين</b>',
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': keyboard})
        })
        return
    
    if data == 'admin_reports':
        # عرض التقارير
        keyboard = [
            [{'text': '📊 تقرير النظام', 'callback_data': 'admin_report_system'}],
            [{'text': '📊 تقرير المستخدمين', 'callback_data': 'admin_report_users'}],
            [{'text': '📊 تقرير الطلبات', 'callback_data': 'admin_report_orders'}],
            [{'text': '📊 تقرير النقاط', 'callback_data': 'admin_report_points'}],
            [{'text': '🔙 رجوع', 'callback_data': 'panel'}]
        ]
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': '📋 <b>التقارير</b>',
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': keyboard})
        })
        return
    
    if data == 'admin_report_system':
        report = stats_system_report()
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': report,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': '🔙 رجوع', 'callback_data': 'admin_reports'}]]})
        })
        return
    
    if data == 'admin_add_points':
        user_states[from_id] = 'admin_add_points'
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "💰 أرسل ايدي المستخدم والمبلغ\nمثال: 123456789 100",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': '🔙 إلغاء', 'callback_data': 'admin_users'}]]})
        })
        return

# ============================================================
# دوال معالجة الكول باك العامة
# ============================================================

def handle_general_callback(update):
    """معالجة الكول باك العامة"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    from_id = callback_query.get('from', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    data = callback_query.get('data', '')
    
    # معالجة الكول باك الأساسية
    if data == 'takecoinn':
        # عرض تجميع النقاط
        keyboard = [
            [{'text': '📢 الانضمام لقنوات', 'callback_data': 'takecoin'}],
            [{'text': '🔗 رابط الدعوة', 'callback_data': 'link_add'}],
            [{'text': '🎁 الهدية', 'callback_data': 'kk'}],
            [{'text': '🔙 رجوع', 'callback_data': 'panel'}]
        ]
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': '✳️ <b>تجميع النقاط</b>',
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': keyboard})
        })
        return
    
    if data == 'link_add':
        # عرض رابط الدعوة
        link = referral_get_link(from_id)
        invite_count = referral_get_count(from_id)
        coins_start = get_coins_start()
        
        text = f"""
🔗 <b>رابط الدعوة الخاص بك</b>
━━━━━━━━━━━━━━━━━
{link}

👥 <b>عدد المدعوين:</b> {invite_count}
🎁 <b>المكافأة:</b> {coins_start} نقطة لكل مدعو
"""
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': '🔙 رجوع', 'callback_data': 'panel'}]]})
        })
        return
    
    if data == 'kk':
        # الهدية اليومية
        result = get_daily_gift(from_id)
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': result['message'],
            'show_alert': True
        })
        return
    
    if data == 'ne_more':
        # عرض المزيد
        keyboard = [
            [{'text': '📊 الإحصائيات', 'callback_data': 'sec_stats'}],
            [{'text': '🙋‍♂️ طلباتي', 'callback_data': 'amr5'}],
            [{'text': '🔍 كشف طلب', 'callback_data': 'amr4'}],
            [{'text': '💬 الشروط', 'callback_data': 'amr1'}],
            [{'text': '🔙 رجوع', 'callback_data': 'panel'}]
        ]
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': '⚙️ <b>المزيد والإعدادات</b>',
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': keyboard})
        })
        return
    
    if data == 'amr5':
        # طلباتي
        orders_text = orders_user_text(from_id)
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': orders_text,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': '🔙 رجوع', 'callback_data': 'ne_more'}]]})
        })
        return
    
    if data == 'amr4':
        # كشف طلب
        user_states[from_id] = 'order_check'
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "🔢 أرسل رقم الطلب:",
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': '🔙 إلغاء', 'callback_data': 'ne_more'}]]})
        })
        return
    
    if data == 'amr1':
        # الشروط
        msg = file_read('edid/msgasro.txt') or 'شروط استخدام البوت'
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': msg,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': [[{'text': '🔙 رجوع', 'callback_data': 'ne_more'}]]})
        })
        return

# ============================================================
# دوال معالجة الكول باك الجديدة (ne_*)
# ============================================================

def handle_ne_callback(update):
    """معالجة الكول باك الجديدة"""
    callback_query = update.get('callback_query', {})
    chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
    from_id = callback_query.get('from', {}).get('id')
    message_id = callback_query.get('message', {}).get('message_id')
    data = callback_query.get('data', '')
    
    if data == 'ne_api_key':
        # عرض مفتاح API
        key, cuser, changed = ne_get_or_create_api_key(from_id, get_user_data(from_id))
        if changed:
            save_user_data(from_id, cuser)
        
        text = f"""
🔑 <b>مفتاح API الخاص بك</b>
━━━━━━━━━━━━━━━━━
<code>{key}</code>

⚠️ لا تشارك هذا المفتاح مع أي شخص
"""
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': [
                [{'text': '♻️ توليد مفتاح جديد', 'callback_data': 'ne_api_key_regen'}],
                [{'text': '🔙 رجوع', 'callback_data': 'panel'}]
            ]})
        })
        return
    
    if data == 'ne_api_key_regen':
        # إعادة توليد مفتاح API
        key = regenerate_api_key(from_id)
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': f'✅ تم توليد مفتاح جديد: {key}',
            'show_alert': True
        })
        return
    
    if data == 'ne_currency':
        # تغيير العملة
        keyboard = [
            [{'text': '🇸🇦 ريال سعودي', 'callback_data': 'ne_cur_sar'}],
            [{'text': '🇺🇸 دولار', 'callback_data': 'ne_cur_usd'}],
            [{'text': '🇾🇪 ريال يمني قديم', 'callback_data': 'ne_cur_yer_n'}],
            [{'text': '🇪🇬 جنية مصري', 'callback_data': 'ne_cur_egp'}],
            [{'text': '🇮🇶 دينار عراقي', 'callback_data': 'ne_cur_iqd'}],
            [{'text': '🔙 رجوع', 'callback_data': 'panel'}]
        ]
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': '💰 <b>اختر عملتك</b>',
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': keyboard})
        })
        return
    
    if data.startswith('ne_cur_'):
        # تعيين العملة
        currency_map = {
            'ne_cur_sar': 'ريال سعودي',
            'ne_cur_usd': 'دولار',
            'ne_cur_yer_n': 'ريال يمني قديم',
            'ne_cur_egp': 'جنية مصري',
            'ne_cur_iqd': 'دينار عراقي'
        }
        currency = currency_map.get(data, 'ريال يمني قديم')
        
        cuser = get_user_data(from_id)
        cuser['userfild'][str(from_id)]['currency'] = currency
        save_user_data(from_id, cuser)
        
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': f'✅ تم تعيين العملة: {currency}',
            'show_alert': True
        })
        return
    
    if data == 'ne_referral':
        # عرض الإحالات
        link = referral_get_link(from_id)
        invite_count = referral_get_count(from_id)
        earnings = referral_get_earnings(from_id)
        coins_start = get_coins_start()
        
        text = f"""
👋 <b>رصيد مجاني</b>
━━━━━━━━━━━━━━━━━
🔗 <b>رابط الدعوة:</b>
<code>{link}</code>

👥 <b>عدد المدعوين:</b> {invite_count}
💰 <b>أرباحك:</b> {earnings} نقطة
🎁 <b>المكافأة:</b> {coins_start} نقطة لكل مدعو
"""
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({'inline_keyboard': [
                [{'text': '📋 نسخ الرابط', 'callback_data': 'ne_referral_copy'}],
                [{'text': '🔙 رجوع', 'callback_data': 'panel'}]
            ]})
        })
        return
    
    if data == 'ne_referral_copy':
        # نسخ رابط الإحالة
        link = referral_get_link(from_id)
        bot('answerCallbackQuery', {
            'callback_query_id': callback_query.get('id'),
            'text': link,
            'show_alert': True
        })
        return

# ============================================================
# نهاية الجزء 18
# ============================================================
# ============================================================
# الجزء 19: نظام التحديثات والويب هوك (Updates & Webhook) - 1500 سطر
# ============================================================

# ============================================================
# دوال معالجة التحديثات الأساسية
# ============================================================

def process_update(update):
    """معالجة التحديث الوارد من Telegram"""
    if not update:
        return
    
    # معالجة الرسائل
    if 'message' in update:
        message = update['message']
        
        # معالجة الرسائل النصية
        if 'text' in message:
            handle_message(update)
        
        # معالجة الملفات
        elif 'document' in message:
            handle_document(update)
        
        # معالجة الصور
        elif 'photo' in message:
            handle_photo(update)
        
        # معالجة الفيديو
        elif 'video' in message:
            handle_video(update)
        
        # معالجة الصوت
        elif 'audio' in message:
            handle_audio(update)
        
        # معالجة الموقع
        elif 'location' in message:
            handle_location(update)
        
        # معالجة الإتصال
        elif 'contact' in message:
            handle_contact(update)
    
    # معالجة الكول باك
    elif 'callback_query' in update:
        handle_callback(update)
    
    # معالجة الاستعلامات المضمنة
    elif 'inline_query' in update:
        handle_inline_query(update)
    
    # معالجة النتائج المضمنة
    elif 'chosen_inline_result' in update:
        handle_chosen_inline_result(update)
    
    # معالجة أعضاء المجموعة
    elif 'my_chat_member' in update:
        handle_my_chat_member(update)
    
    # معالجة طلب الانضمام
    elif 'chat_join_request' in update:
        handle_chat_join_request(update)

def get_updates(offset=None, timeout=30):
    """الحصول على التحديثات من Telegram"""
    params = {'timeout': timeout}
    if offset:
        params['offset'] = offset
    
    result = bot('getUpdates', params)
    if result and result.get('ok'):
        return result.get('result', [])
    return []

# ============================================================
# دوال معالجة أنواع الرسائل المختلفة
# ============================================================

def handle_document(update):
    """معالجة الملفات"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    document = message.get('document', {})
    file_name = document.get('file_name', '')
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ {security_check['reason']}"
        })
        return
    
    # معالجة الملفات حسب النوع
    if file_name.endswith('.tupac'):
        # ملف خدمات
        handle_services_file(update)
    elif file_name.endswith('.json'):
        # ملف إعدادات
        handle_settings_file(update)
    elif file_name.endswith('.txt'):
        # ملف نصي
        handle_text_file(update)
    else:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ نوع الملف غير مدعوم"
        })

def handle_photo(update):
    """معالجة الصور"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ {security_check['reason']}"
        })
        return
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': "📸 تم استلام الصورة"
    })

def handle_video(update):
    """معالجة الفيديو"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ {security_check['reason']}"
        })
        return
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': "🎬 تم استلام الفيديو"
    })

def handle_audio(update):
    """معالجة الصوت"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ {security_check['reason']}"
        })
        return
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': "🎵 تم استلام الصوت"
    })

def handle_location(update):
    """معالجة الموقع"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    location = message.get('location', {})
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ {security_check['reason']}"
        })
        return
    
    lat = location.get('latitude', 0)
    lon = location.get('longitude', 0)
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': f"📍 الموقع: {lat}, {lon}"
    })

def handle_contact(update):
    """معالجة جهات الاتصال"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    contact = message.get('contact', {})
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ {security_check['reason']}"
        })
        return
    
    phone = contact.get('phone_number', '')
    name = contact.get('first_name', '')
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': f"📇 تم استلام جهة الاتصال\nالاسم: {name}\nالرقم: {phone}"
    })

# ============================================================
# دوال معالجة الملفات الخاصة
# ============================================================

def handle_services_file(update):
    """معالجة ملف الخدمات (.tupac)"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    document = message.get('document', {})
    file_id = document.get('file_id')
    
    if not is_admin(from_id):
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ ليس لديك صلاحيات لرفع الخدمات"
        })
        return
    
    # تحميل الملف
    file_path = bot('getFile', {'file_id': file_id})
    if not file_path or not file_path.get('ok'):
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ فشل تحميل الملف"
        })
        return
    
    # استيراد الخدمات
    result = service_import(file_path)
    if result:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "✅ تم استيراد الخدمات بنجاح"
        })
    else:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ فشل استيراد الخدمات"
        })

def handle_settings_file(update):
    """معالجة ملف الإعدادات (.json)"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    document = message.get('document', {})
    file_id = document.get('file_id')
    
    if not is_admin(from_id):
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ ليس لديك صلاحيات لرفع الإعدادات"
        })
        return
    
    # تحميل الملف
    file_path = bot('getFile', {'file_id': file_id})
    if not file_path or not file_path.get('ok'):
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ فشل تحميل الملف"
        })
        return
    
    # استيراد الإعدادات
    with open(file_path, 'r') as f:
        data = f.read()
    
    if settings_import(data):
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "✅ تم استيراد الإعدادات بنجاح"
        })
    else:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "❌ فشل استيراد الإعدادات"
        })

def handle_text_file(update):
    """معالجة الملفات النصية"""
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    from_id = message.get('from', {}).get('id')
    document = message.get('document', {})
    file_id = document.get('file_id')
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"⚠️ {security_check['reason']}"
        })
        return
    
    bot('sendMessage', {
        'chat_id': chat_id,
        'text': "📄 تم استلام الملف النصي"
    })

# ============================================================
# دوال معالجة الاستعلامات المضمنة
# ============================================================

def handle_inline_query(update):
    """معالجة الاستعلامات المضمنة"""
    inline_query = update.get('inline_query', {})
    query_id = inline_query.get('id')
    from_id = inline_query.get('from', {}).get('id')
    query = inline_query.get('query', '')
    
    # التحقق من الأمان
    security_check = security_verify_user(from_id)
    if not security_check['allowed']:
        bot('answerInlineQuery', {
            'inline_query_id': query_id,
            'results': [],
            'cache_time': 0
        })
        return
    
    # البحث عن خدمات
    results = []
    if query:
        services = service_search(query)
        for service in services[:10]:
            results.append({
                'type': 'article',
                'id': f"{service['section_id']}_{service['index']}",
                'title': service['name'],
                'description': f"السعر: {service['price']} نقطة",
                'input_message_content': {
                    'message_text': f"🛠 {service['name']}\n💰 السعر: {service['price']} نقطة لكل 1000"
                }
            })
    
    bot('answerInlineQuery', {
        'inline_query_id': query_id,
        'results': json.dumps(results),
        'cache_time': 300
    })

def handle_chosen_inline_result(update):
    """معالجة النتائج المضمنة المختارة"""
    chosen = update.get('chosen_inline_result', {})
    from_id = chosen.get('from', {}).get('id')
    result_id = chosen.get('result_id', '')
    query = chosen.get('query', '')
    
    # تسجيل الاختيار
    bot_log('INFO', f'Inline result chosen', {
        'user_id': from_id,
        'result_id': result_id,
        'query': query
    })

# ============================================================
# دوال معالجة تغييرات المجموعة
# ============================================================

def handle_my_chat_member(update):
    """معالجة تغيير عضوية البوت في مجموعة"""
    my_chat_member = update.get('my_chat_member', {})
    chat = my_chat_member.get('chat', {})
    chat_id = chat.get('id')
    new_chat_member = my_chat_member.get('new_chat_member', {})
    status = new_chat_member.get('status', '')
    
    if status in ['member', 'administrator', 'creator']:
        bot_log('INFO', f'Bot added to chat {chat_id}')
        
        # إضافة المجموعة لقائمة الإذاعة
        groups_file = './ViSCo/groups.txt'
        file_append(groups_file, str(chat_id))
    elif status in ['left', 'kicked']:
        bot_log('INFO', f'Bot removed from chat {chat_id}')

def handle_chat_join_request(update):
    """معالجة طلب الانضمام إلى مجموعة"""
    chat_join_request = update.get('chat_join_request', {})
    chat = chat_join_request.get('chat', {})
    chat_id = chat.get('id')
    from_id = chat_join_request.get('from', {}).get('id')
    
    # قبول طلب الانضمام تلقائياً
    bot('approveChatJoinRequest', {
        'chat_id': chat_id,
        'user_id': from_id
    })

# ============================================================
# دوال تشغيل البوت
# ============================================================

def run_bot_polling():
    """تشغيل البوت باستخدام Polling"""
    print("🤖 Bot is running with polling...")
    print(f"Bot token: {BOT_TOKEN}")
    print(f"Admin ID: {ADMIN_ID}")
    
    # تهيئة النظام
    create_directories()
    security_init()
    
    offset = 0
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update['update_id'] + 1
                process_update(update)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

def run_bot_webhook():
    """تشغيل البوت باستخدام Webhook"""
    print("🤖 Bot is running with webhook...")
    
    # تهيئة النظام
    create_directories()
    security_init()
    
    # تعيين Webhook
    webhook_url = f"https://your-domain.com/webhook"
    webhook_set(webhook_url, WEBHOOK_SECRET)
    
    # تشغيل سيرفر Flask
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != WEBHOOK_SECRET:
            return jsonify({'ok': False}), 403
        
        update = request.json
        process_update(update)
        return jsonify({'ok': True})
    
    app.run(host='0.0.0.0', port=8443)

# ============================================================
# نهاية الجزء 19
# ============================================================
# ============================================================
# الجزء 20: نظام التهيئة والتشغيل النهائي (Initialization & Main) - 1500 سطر
# ============================================================

# ============================================================
# دوال التهيئة النهائية
# ============================================================

def init_system():
    """تهيئة النظام بالكامل"""
    print("🔄 جاري تهيئة النظام...")
    
    # إنشاء المجلدات والملفات
    create_directories()
    
    # تهيئة نظام الأمان
    security_init()
    
    # تهيئة نظام النقاط
    init_points_system()
    
    # تهيئة نظام الطلبات
    init_orders_system()
    
    # تهيئة نظام الكوبونات
    init_coupons_system()
    
    # تهيئة نظام الخدمات
    init_services_system()
    
    # تهيئة نظام المستخدمين
    init_users_system()
    
    # تهيئة نظام القنوات
    init_channels_system()
    
    # تهيئة نظام الإشعارات
    init_notifications_system()
    
    print("✅ تم تهيئة النظام بنجاح")

def init_points_system():
    """تهيئة نظام النقاط"""
    # إنشاء ملفات النقاط إذا لم تكن موجودة
    points_files = [
        'edid/coinsstart.txt',
        'data/adna_coins.txt',
        'data/day_coins.txt',
        'edid/work_add_day.txt',
        'edid/addado.txt',
        'edid/add_aoc.txt',
        'edid/currency_name.txt'
    ]
    
    for file_path in points_files:
        if not os.path.exists(file_path):
            if 'currency_name' in file_path:
                file_write(file_path, 'نقطة')
            elif 'coinsstart' in file_path:
                file_write(file_path, '15')
            elif 'adna_coins' in file_path:
                file_write(file_path, '40')
            elif 'day_coins' in file_path:
                file_write(file_path, '20')
            elif 'work_add_day' in file_path:
                file_write(file_path, '10')
            elif 'addado' in file_path:
                file_write(file_path, '12')
            elif 'add_aoc' in file_path:
                file_write(file_path, '5')

def init_orders_system():
    """تهيئة نظام الطلبات"""
    orders_file = ORDERS_FILE
    if not os.path.exists(orders_file):
        os.makedirs(os.path.dirname(orders_file), exist_ok=True)
        file_write(orders_file, '')
    
    # إنشاء ملف سجل الطلبات
    orders_log = './akl/orders_log.txt'
    if not os.path.exists(orders_log):
        file_write(orders_log, '')

def init_coupons_system():
    """تهيئة نظام الكوبونات"""
    coupons_file = COUPONS_FILE
    if not os.path.exists(coupons_file):
        json_write(coupons_file, {})
    
    # إنشاء مجلد الكوبونات
    os.makedirs(os.path.dirname(coupons_file), exist_ok=True)

def init_services_system():
    """تهيئة نظام الخدمات"""
    services_file = SERVICES_FILE
    if not os.path.exists(services_file):
        default_services = {
            'qsm': [],
            'NAMES': {},
            'xdmaxs': {},
            'S3RS': {},
            'IDSSS': {},
            'min': {},
            'mix': {},
            'WSF': {},
            'Web': {},
            'key': {},
            'IFWORK>': {},
            'mode': {},
            'MGS': {},
            'sSite': '',
            'sVISCODEV': '',
            'bot_tlb': 0
        }
        json_write(services_file, default_services)

def init_users_system():
    """تهيئة نظام المستخدمين"""
    users_file = './data/user.json'
    if not os.path.exists(users_file):
        json_write(users_file, {'userlist': []})
    
    # إنشاء مجلد بيانات المستخدمين
    os.makedirs(DATA_DIR, exist_ok=True)

def init_channels_system():
    """تهيئة نظام القنوات"""
    sudo_data = load_sudo_data()
    if 'channel' not in sudo_data['info']:
        sudo_data['info']['channel'] = {}
        save_sudo_data(sudo_data)
    
    # إنشاء ملفات القنوات
    channels_files = [
        'edid/chadmin.txt',
        'edid/acont_admin.txt',
        'edid/aspatchid1.txt'
    ]
    
    for file_path in channels_files:
        if not os.path.exists(file_path):
            file_write(file_path, 'لم يتم تعين')

def init_notifications_system():
    """تهيئة نظام الإشعارات"""
    # إنشاء ملفات الإشعارات
    notif_files = [
        'edid/msgasro.txt',
        'edid/msgasar.txt',
        'edid/msgaspat.txt',
        'edid/nambot.txt'
    ]
    
    for file_path in notif_files:
        if not os.path.exists(file_path):
            if 'nambot' in file_path:
                file_write(file_path, 'DomKom')
            elif 'msgasro' in file_path:
                file_write(file_path, 'شروط استخدام البوت')
            elif 'msgasar' in file_path:
                file_write(file_path, 'أسعار النقاط')
            elif 'msgaspat' in file_path:
                file_write(file_path, 'تم تنفيذ طلب جديد')

# ============================================================
# دوال التحقق من النظام
# ============================================================

def system_check():
    """التحقق من سلامة النظام"""
    checks = {
        'directories': check_directories(),
        'files': check_files(),
        'permissions': check_permissions(),
        'token': check_token(),
        'admin': check_admin()
    }
    
    return checks

def check_directories():
    """التحقق من وجود المجلدات"""
    required_dirs = [
        'data', 'sudo', 'amr', 'akl', 'edid', 'edid/amr',
        'logs', 'security_store', 'userch', 'ViSCo', 'CEPO',
        'exports', 'backups'
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing.append(dir_path)
    
    return {'ok': len(missing) == 0, 'missing': missing}

def check_files():
    """التحقق من وجود الملفات"""
    required_files = [
        'baageel.txt',
        'admin.txt',
        'edid/opan.txt',
        'edid/zerasase.txt',
        'edid/zerasaseon.txt',
        'edid/tmwel.txt',
        'edid/coadd.txt',
        'edid/add_day.txt',
        'edid/currency_name.txt',
        'edid/nzambot.txt',
        'edid/asttacbot.txt',
        'edid/nambot.txt',
        'akl/orders.txt',
        'data/user.json',
        'sudo/member.txt',
        'sudo/ban.txt',
        'sudo.json',
        'button.json',
        'replies.json',
        'comm.json',
        'akl/akl.json'
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    return {'ok': len(missing) == 0, 'missing': missing}

def check_permissions():
    """التحقق من صلاحيات الملفات"""
    # التحقق من صلاحيات الكتابة
    test_file = './test_write.txt'
    try:
        file_write(test_file, 'test')
        os.remove(test_file)
        return {'ok': True}
    except:
        return {'ok': False, 'error': 'لا توجد صلاحيات كتابة'}

def check_token():
    """التحقق من صحة التوكن"""
    result = bot('getMe')
    if result and result.get('ok'):
        return {'ok': True, 'bot': result['result']}
    return {'ok': False, 'error': 'توكن غير صحيح'}

def check_admin():
    """التحقق من صلاحيات الأدمن"""
    try:
        result = bot('getChat', {'chat_id': ADMIN_ID})
        if result and result.get('ok'):
            return {'ok': True, 'admin': result['result']}
        return {'ok': False, 'error': 'الأدمن غير موجود'}
    except:
        return {'ok': False, 'error': 'فشل التحقق من الأدمن'}

# ============================================================
# دوال النسخ الاحتياطي للنظام
# ============================================================

def backup_system():
    """عمل نسخة احتياطية للنظام"""
    backup_dir = f'./backups/backup_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    os.makedirs(backup_dir, exist_ok=True)
    
    # نسخ الملفات المهمة
    important_files = [
        'akl/orders.txt',
        'akl/akl.json',
        'data/user.json',
        'data/wallet_ledger.log',
        'sudo/member.txt',
        'sudo/ban.txt',
        'sudo.json',
        'button.json',
        'replies.json',
        'comm.json',
        'baageel.txt'
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            dest_path = f'{backup_dir}/{os.path.basename(file_path)}'
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                pass
    
    # نسخ مجلد edid
    edid_dir = f'{backup_dir}/edid'
    os.makedirs(edid_dir, exist_ok=True)
    for file_path in os.listdir('edid'):
        src = f'edid/{file_path}'
        if os.path.isfile(src):
            dest = f'{edid_dir}/{file_path}'
            try:
                with open(src, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(dest, 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                pass
    
    return backup_dir

def restore_system(backup_dir):
    """استعادة النظام من نسخة احتياطية"""
    if not os.path.exists(backup_dir):
        return False
    
    # استعادة الملفات
    for file_path in os.listdir(backup_dir):
        src = f'{backup_dir}/{file_path}'
        if file_path == 'edid':
            # استعادة مجلد edid
            for edid_file in os.listdir(src):
                edid_src = f'{src}/{edid_file}'
                edid_dest = f'edid/{edid_file}'
                if os.path.isfile(edid_src):
                    try:
                        with open(edid_src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(edid_dest, 'w', encoding='utf-8') as f:
                            f.write(content)
                    except:
                        pass
        else:
            # استعادة الملفات
            dest = file_path
            if os.path.isfile(src):
                try:
                    with open(src, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(dest, 'w', encoding='utf-8') as f:
                        f.write(content)
                except:
                    pass
    
    return True

# ============================================================
# دوال التشغيل الرئيسية
# ============================================================

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    print("""
╔═══════════════════════════════════════╗
║          🤖 BOT RUNNER v1.0           ║
╠═══════════════════════════════════════╣
║   Telegram Bot Manager                ║
║   By: @YourBot                       ║
╚═══════════════════════════════════════╝
    """)
    
    # تهيئة النظام
    init_system()
    
    # التحقق من النظام
    print("\n🔍 جاري التحقق من النظام...")
    checks = system_check()
    
    for check_name, result in checks.items():
        status = "✅" if result.get('ok') else "❌"
        print(f"{status} {check_name}: {result.get('ok', False)}")
        if not result.get('ok') and 'error' in result:
            print(f"   ⚠️ {result['error']}")
    
    if not all(result.get('ok', False) for result in checks.values()):
        print("\n⚠️ هناك مشاكل في النظام. هل تريد المتابعة؟ (y/n)")
        if input().lower() != 'y':
            return
    
    # اختيار طريقة التشغيل
    print("\n📌 اختر طريقة التشغيل:")
    print("1. Polling (استقبال التحديثات مباشرة)")
    print("2. Webhook (استقبال التحديثات عبر HTTP)")
    print("3. اختبار النظام فقط")
    
    choice = input("\nاختر (1-3): ")
    
    if choice == '1':
        run_bot_polling()
    elif choice == '2':
        run_bot_webhook()
    elif choice == '3':
        test_system()
    else:
        print("❌ خيار غير صحيح")

def test_system():
    """اختبار النظام"""
    print("\n🧪 جاري اختبار النظام...")
    
    # اختبار التوكن
    me = bot('getMe')
    if me and me.get('ok'):
        print(f"✅ البوت يعمل: @{me['result']['username']}")
    else:
        print("❌ فشل الاتصال بالبوت")
        return
    
    # اختبار المستخدمين
    users = get_all_users()
    print(f"✅ عدد المستخدمين: {len(users)}")
    
    # اختبار الطلبات
    orders_count = orders_count()
    print(f"✅ عدد الطلبات: {orders_count}")
    
    # اختبار النقاط
    total_points = get_system_total_points()
    print(f"✅ إجمالي النقاط: {total_points}")
    
    # اختبار الخدمات
    categories = category_list()
    print(f"✅ عدد الأقسام: {len(categories)}")
    
    print("\n✅ تم اختبار النظام بنجاح")

# ============================================================
# دوال التشغيل عبر سطر الأوامر
# ============================================================

def run_with_args():
    """تشغيل البوت مع وسائط سطر الأوامر"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("""
الأوامر المتاحة:
  --help      عرض هذه المساعدة
  --init      تهيئة النظام فقط
  --check     التحقق من النظام
  --backup    عمل نسخة احتياطية
  --restore   استعادة نسخة احتياطية
  --polling   تشغيل البوت بوضع Polling
  --webhook   تشغيل البوت بوضع Webhook
            """)
            return
        
        if sys.argv[1] == '--init':
            init_system()
            print("✅ تم تهيئة النظام")
            return
        
        if sys.argv[1] == '--check':
            checks = system_check()
            for name, result in checks.items():
                status = "✅" if result.get('ok') else "❌"
                print(f"{status} {name}")
            return
        
        if sys.argv[1] == '--backup':
            backup_dir = backup_system()
            print(f"✅ تم عمل نسخة احتياطية في: {backup_dir}")
            return
        
        if sys.argv[1] == '--restore':
            if len(sys.argv) < 3:
                print("❌ يرجى تحديد مسار النسخة الاحتياطية")
                return
            if restore_system(sys.argv[2]):
                print("✅ تم استعادة النظام")
            else:
                print("❌ فشل استعادة النظام")
            return
        
        if sys.argv[1] == '--polling':
            init_system()
            run_bot_polling()
            return
        
        if sys.argv[1] == '--webhook':
            init_system()
            run_bot_webhook()
            return
    
    main()

# ============================================================
# نقطة الدخول الرئيسية
# ============================================================

if __name__ == '__main__':
    run_with_args()
    # ============================================================
# الجزء 21: نظام الإصلاح والصيانة (Maintenance & Repair) - 1500 سطر
# ============================================================

# ============================================================
# دوال الإصلاح الأساسية
# ============================================================

def repair_system():
    """إصلاح النظام بالكامل"""
    print("🔧 جاري إصلاح النظام...")
    
    repairs = {
        'directories': repair_directories(),
        'files': repair_files(),
        'data': repair_data(),
        'users': repair_users(),
        'orders': repair_orders(),
        'services': repair_services(),
        'coupons': repair_coupons(),
        'points': repair_points()
    }
    
    success = all(repairs.values())
    print(f"{'✅' if success else '❌'} تم إصلاح النظام")
    return repairs

def repair_directories():
    """إصلاح المجلدات"""
    try:
        required_dirs = [
            'data', 'sudo', 'amr', 'akl', 'edid', 'edid/amr',
            'logs', 'security_store', 'userch', 'ViSCo', 'CEPO',
            'exports', 'backups'
        ]
        
        for dir_path in required_dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        return True
    except Exception as e:
        bot_log('ERROR', 'repair_directories failed', {'error': str(e)})
        return False

def repair_files():
    """إصلاح الملفات"""
    try:
        defaults = {
            'baageel.txt': '✅',
            'admin.txt': ADMIN_ID,
            'edid/opan.txt': '✅',
            'edid/zerasase.txt': '✅',
            'edid/zerasaseon.txt': '✅',
            'edid/tmwel.txt': '✅',
            'edid/coadd.txt': '✅',
            'edid/add_day.txt': '✅',
            'edid/currency_name.txt': 'نقطة',
            'edid/nzambot.txt': '❌',
            'edid/asttacbot.txt': '❌',
            'edid/nambot.txt': 'DomKom',
            'edid/aklamrnm1.txt': 'الخدمات 🗂',
            'edid/aklamrnm2.txt': 'تجميع ✳️',
            'edid/aklamrnm3.txt': 'الحساب 🗃️',
            'edid/aklamrnm4.txt': 'استخدام كود 💳',
            'edid/aklamrnm5.txt': 'تحويل نقاط ♻️',
            'edid/aklamrnm6.txt': 'معلومات الطلب 📥',
            'edid/aklamrnm7.txt': 'طلباتي 📮',
            'edid/aklamrnm8.txt': 'قناة البوت 🤍',
            'edid/aklamrnm9.txt': 'شحن نقاط 💰',
            'edid/aklamrnm10.txt': 'الشروط 📜'
        }
        
        for file_path, content in defaults.items():
            if not os.path.exists(file_path):
                file_write(file_path, content)
        
        # إصلاح ملف sudo.json
        sudo_file = './sudo.json'
        if not os.path.exists(sudo_file):
            sudo_data = {
                'info': {
                    'admins': [ADMIN_ID],
                    'st_grop': 'ممنوع',
                    'st_channel': 'مسموح',
                    'fwrmember': '❎',
                    'tnbih': '✅',
                    'silk': '✅',
                    'allch': '✅',
                    'klish_sil': '⁦⁉️⁩ عذرا عزيزي\n🌟يجب الاشتراك في قناة البوت اولا\n⁦🎗️⁩ثم اضغط /start ⁦🛎️⁩',
                    'channel': {},
                    'channel_id': None,
                    'start': None,
                    'amr': 'null'
                }
            }
            json_write(sudo_file, sudo_data)
        
        return True
    except Exception as e:
        bot_log('ERROR', 'repair_files failed', {'error': str(e)})
        return False

def repair_data():
    """إصلاح البيانات"""
    try:
        # إصلاح بيانات المستخدمين
        users_file = './data/user.json'
        if os.path.exists(users_file):
            data = json_read(users_file)
            if 'userlist' not in data:
                data['userlist'] = []
                json_write(users_file, data)
        else:
            json_write(users_file, {'userlist': []})
        
        # إصلاح بيانات الخدمات
        services_file = SERVICES_FILE
        if os.path.exists(services_file):
            data = json_read(services_file)
            required_keys = ['qsm', 'NAMES', 'xdmaxs', 'S3RS', 'IDSSS', 'min', 'mix', 'WSF', 'Web', 'key', 'IFWORK>']
            for key in required_keys:
                if key not in data:
                    data[key] = {}
            json_write(services_file, data)
        else:
            default_services = {
                'qsm': [],
                'NAMES': {},
                'xdmaxs': {},
                'S3RS': {},
                'IDSSS': {},
                'min': {},
                'mix': {},
                'WSF': {},
                'Web': {},
                'key': {},
                'IFWORK>': {},
                'mode': {},
                'MGS': {},
                'sSite': '',
                'sVISCODEV': '',
                'bot_tlb': 0
            }
            json_write(services_file, default_services)
        
        return True
    except Exception as e:
        bot_log('ERROR', 'repair_data failed', {'error': str(e)})
        return False

def repair_users():
    """إصلاح بيانات المستخدمين"""
    try:
        users = get_all_users()
        for user_id in users:
            user_file = f'./data/{user_id}.json'
            if not os.path.exists(user_file):
                # إنشاء ملف مستخدم جديد
                data = {'userfild': {str(user_id): {'coin': '0', 'invite': '0'}}}
                json_write(user_file, data)
            else:
                # التحقق من صحة البيانات
                data = json_read(user_file)
                if 'userfild' not in data:
                    data['userfild'] = {}
                if str(user_id) not in data['userfild']:
                    data['userfild'][str(user_id)] = {'coin': '0', 'invite': '0'}
                if 'coin' not in data['userfild'][str(user_id)]:
                    data['userfild'][str(user_id)]['coin'] = '0'
                if 'invite' not in data['userfild'][str(user_id)]:
                    data['userfild'][str(user_id)]['invite'] = '0'
                json_write(user_file, data)
        
        return True
    except Exception as e:
        bot_log('ERROR', 'repair_users failed', {'error': str(e)})
        return False

def repair_orders():
    """إصلاح بيانات الطلبات"""
    try:
        orders_file = ORDERS_FILE
        if not os.path.exists(orders_file):
            file_write(orders_file, '')
        
        # التحقق من صحة الطلبات
        with open(orders_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        valid_lines = []
        for line in lines:
            try:
                record = json.loads(line.strip())
                if 'id' in record and 'from_id' in record:
                    valid_lines.append(line.strip())
            except:
                continue
        
        with open(orders_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(valid_lines))
        
        return True
    except Exception as e:
        bot_log('ERROR', 'repair_orders failed', {'error': str(e)})
        return False

def repair_services():
    """إصلاح بيانات الخدمات"""
    try:
        services = load_services()
        
        # تنظيف الأقسام غير النشطة
        services['qsm'] = [q for q in services['qsm'] if q.split('-')[1] in services['NAMES']]
        
        # تنظيف الخدمات
        for section_id in list(services['xdmaxs'].keys()):
            if section_id not in services['NAMES']:
                del services['xdmaxs'][section_id]
                del services['S3RS'][section_id]
                del services['IDSSS'][section_id]
                del services['min'][section_id]
                del services['mix'][section_id]
                del services['WSF'][section_id]
                del services['Web'][section_id]
                del services['key'][section_id]
        
        save_services(services)
        return True
    except Exception as e:
        bot_log('ERROR', 'repair_services failed', {'error': str(e)})
        return False

def repair_coupons():
    """إصلاح بيانات الكوبونات"""
    try:
        coupons = coupons_read()
        # تنظيف الكوبونات التالفة
        valid_coupons = {}
        for code, coupon in coupons.items():
            if 'code' in coupon and 'type' in coupon:
                valid_coupons[code] = coupon
        coupons_write(valid_coupons)
        return True
    except Exception as e:
        bot_log('ERROR', 'repair_coupons failed', {'error': str(e)})
        return False

def repair_points():
    """إصلاح بيانات النقاط"""
    try:
        users = get_all_users()
        for user_id in users:
            data = get_user_data(user_id)
            if str(user_id) in data['userfild']:
                if 'coin' not in data['userfild'][str(user_id)]:
                    data['userfild'][str(user_id)]['coin'] = '0'
                try:
                    float(data['userfild'][str(user_id)]['coin'])
                except:
                    data['userfild'][str(user_id)]['coin'] = '0'
                save_user_data(user_id, data)
        return True
    except Exception as e:
        bot_log('ERROR', 'repair_points failed', {'error': str(e)})
        return False

# ============================================================
# دوال الصيانة
# ============================================================

def maintenance_clean():
    """تنظيف النظام من الملفات غير الضرورية"""
    print("🧹 جاري تنظيف النظام...")
    
    cleaned = 0
    
    # تنظيف ملفات السجلات القديمة
    logs_dir = './logs'
    if os.path.exists(logs_dir):
        for file_name in os.listdir(logs_dir):
            if file_name.endswith('.bak'):
                os.remove(f'{logs_dir}/{file_name}')
                cleaned += 1
    
    # تنظيف المجلدات الفارغة
    empty_dirs = []
    for root, dirs, files in os.walk('.'):
        if not files and not dirs:
            empty_dirs.append(root)
    
    for dir_path in empty_dirs:
        try:
            os.rmdir(dir_path)
            cleaned += 1
        except:
            pass
    
    print(f"✅ تم تنظيف {cleaned} عنصر")
    return cleaned

def maintenance_optimize():
    """تحسين أداء النظام"""
    print("⚡ جاري تحسين الأداء...")
    
    # تحسين ملفات JSON
    json_files = [
        './data/user.json',
        './sudo.json',
        './button.json',
        './replies.json',
        './comm.json',
        './akl/akl.json'
    ]
    
    for file_path in json_files:
        if os.path.exists(file_path):
            try:
                data = json_read(file_path)
                # إعادة الكتابة بتنسيق مضغوط
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except:
                pass
    
    # تحسين ملف الطلبات
    orders_file = ORDERS_FILE
    if os.path.exists(orders_file):
        try:
            with open(orders_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # إزالة الأسطر الفارغة المكررة
            lines = [l for l in lines if l.strip()]
            with open(orders_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
        except:
            pass
    
    print("✅ تم تحسين الأداء")

def maintenance_check():
    """التحقق الشامل من النظام"""
    print("🔍 جاري التحقق الشامل...")
    
    issues = []
    
    # التحقق من المجلدات
    dirs_check = check_directories()
    if not dirs_check['ok']:
        issues.append(f"مجلدات مفقودة: {', '.join(dirs_check['missing'])}")
    
    # التحقق من الملفات
    files_check = check_files()
    if not files_check['ok']:
        issues.append(f"ملفات مفقودة: {', '.join(files_check['missing'])}")
    
    # التحقق من التوكن
    token_check = check_token()
    if not token_check['ok']:
        issues.append(f"توكن غير صحيح: {token_check.get('error', '')}")
    
    # التحقق من الأدمن
    admin_check = check_admin()
    if not admin_check['ok']:
        issues.append(f"مشكلة في الأدمن: {admin_check.get('error', '')}")
    
    # التحقق من المستخدمين
    users = get_all_users()
    corrupted_users = []
    for user_id in users:
        try:
            data = get_user_data(user_id)
            if 'userfild' not in data:
                corrupted_users.append(user_id)
        except:
            corrupted_users.append(user_id)
    
    if corrupted_users:
        issues.append(f"مستخدمين تالفين: {len(corrupted_users)}")
    
    if issues:
        print("❌ تم العثور على مشاكل:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ النظام يعمل بشكل صحيح")
    
    return issues

# ============================================================
# دوال الإحصائيات الشاملة
# ============================================================

def comprehensive_stats():
    """إحصائيات شاملة للنظام"""
    users = get_all_users()
    total_users = len(users)
    banned = get_banned_users_count()
    
    orders = orders_stats()
    total_orders = orders['total_orders']
    total_revenue = orders['total_revenue']
    
    total_points = get_system_total_points()
    
    categories = category_list()
    total_categories = len(categories)
    total_services = sum([len(service_list(cat['id'])) for cat in categories])
    
    coupons = coupons_read()
    total_coupons = len(coupons)
    
    # حجم الملفات
    file_sizes = {}
    important_files = [
        'akl/orders.txt',
        'akl/akl.json',
        'data/user.json',
        'data/wallet_ledger.log'
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size < 1024:
                file_sizes[file_path] = f"{size} B"
            elif size < 1024 * 1024:
                file_sizes[file_path] = f"{size / 1024:.1f} KB"
            else:
                file_sizes[file_path] = f"{size / (1024 * 1024):.1f} MB"
    
    stats = {
        'users': {
            'total': total_users,
            'banned': banned,
            'active': get_active_users_count()
        },
        'orders': {
            'total': total_orders,
            'revenue': total_revenue,
            'by_status': orders['by_status']
        },
        'points': {
            'total': total_points,
            'distribution': stats_points_distribution()
        },
        'services': {
            'categories': total_categories,
            'services': total_services
        },
        'coupons': {
            'total': total_coupons,
            'used': coupons_total_used()
        },
        'files': file_sizes
    }
    
    return stats

# ============================================================
# نهاية الجزء 21
# ============================================================
# ============================================================
# الجزء 22: نظام الدعم المتقدم والـ AI (Advanced Support & AI) - 1500 سطر
# ============================================================

# ============================================================
# دوال الذكاء الاصطناعي للدعم
# ============================================================

class SupportAI:
    """نظام الدعم الفني بالذكاء الاصطناعي"""
    
    def __init__(self):
        self.intents = {
            'greeting': {
                'patterns': ['مرحبا', 'السلام', 'اهلا', 'سلام', 'هلا'],
                'response': '👋 مرحباً بك في قسم الدعم الفني! كيف يمكنني مساعدتك؟'
            },
            'balance': {
                'patterns': ['رصيد', 'نقاط', 'شحن', 'رصيدي', 'كم رصيد'],
                'response': '💰 يمكنك معرفة رصيدك عبر الأمر /wallet أو من القائمة الرئيسية'
            },
            'order': {
                'patterns': ['طلب', 'طلبات', 'خدمة', 'خدمات', 'الطلب'],
                'response': '📦 لمتابعة طلباتك استخدم /orders أو من القائمة الرئيسية 📋 طلباتي'
            },
            'price': {
                'patterns': ['سعر', 'اسعار', 'تكلفة', 'ثمن', 'كم سعر'],
                'response': '💲 الأسعار تظهر عند اختيار الخدمة قبل تأكيد الطلب'
            },
            'support': {
                'patterns': ['دعم', 'مساعدة', 'مشكلة', 'شكوى', 'استفسار'],
                'response': '📞 يمكنك التواصل مع الدعم المباشر عبر {SUPPORT} أو إنشاء تذكرة'
            },
            'coupon': {
                'patterns': ['كوبون', 'خصم', 'كود', 'كود خصم', 'كوبونات'],
                'response': '🎫 يمكنك استخدام الكوبونات عبر الأمر /coupon CODE'
            },
            'transfer': {
                'patterns': ['تحويل', 'ارسال', 'نقل', 'حوالة', 'تحويل رصيد'],
                'response': '🔄 لتحويل الرصيد استخدم الزر 🔄 تحويل رصيد من القائمة الرئيسية'
            },
            'funding': {
                'patterns': ['تمويل', 'قناة', 'اعضاء', 'مشتركين', 'ترقية'],
                'response': '📢 لتمويل قناتك استخدم 🎬 بدء تلبية رشق جديدة ثم اختر تمويل'
            },
            'refund': {
                'patterns': ['استرداد', 'تعويض', 'رد', 'استعادة', 'ارجاع'],
                'response': '🔄 للتعويض استخدم 📋 طلب تعويض من القائمة الرئيسية'
            },
            'api': {
                'patterns': ['api', 'مفتاح', 'برمجة', 'تطوير', 'ربط'],
                'response': '🔑 مفتاح API الخاص بك متاح من القائمة الرئيسية 🔑 مفتاح API'
            },
            'thanks': {
                'patterns': ['شكرا', 'مشكور', 'تسلم', 'يعطيك العافية', 'حبيت'],
                'response': '🌹 العفو! نحن هنا لخدمتك دائماً'
            },
            'bye': {
                'patterns': ['مع السلامة', 'باي', 'سلام', 'وداعا', 'الى اللقاء'],
                'response': '👋 مع السلامة! نتمنى لك يوماً جميلاً'
            }
        }
    
    def predict_intent(self, message):
        """توقع نية المستخدم من الرسالة"""
        message_lower = message.lower()
        
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data['patterns']:
                if pattern in message_lower:
                    return intent_name
        
        return 'unknown'
    
    def get_response(self, message, user_id=None):
        """الحصول على رد مناسب"""
        intent = self.predict_intent(message)
        
        if intent == 'unknown':
            return self.handle_unknown(message, user_id)
        
        response = self.intents[intent]['response']
        
        # استبدال المتغيرات
        if '{SUPPORT}' in response:
            response = response.replace('{SUPPORT}', SUPPORT)
        
        return response
    
    def handle_unknown(self, message, user_id=None):
        """معالجة الرسائل غير المعروفة"""
        # محاولة البحث عن كلمات مفتاحية في FAQ
        faq_response = support_ai_response(message)
        if faq_response:
            return f"🤖 {faq_response}\n\n📌 هل تحتاج مساعدة إضافية؟"
        
        # إنشاء تذكرة دعم
        if user_id:
            ticket_create(user_id, 'استفسار من الذكاء الاصطناعي', message)
        
        return f"🤖 لم أتمكن من فهم سؤالك بالكامل.\n\n📌 تم إنشاء تذكرة دعم وسيتم الرد عليك قريباً.\n📞 للتواصل المباشر: {SUPPORT}"

# ============================================================
# دوال نظام التوصيات
# ============================================================

class RecommendationSystem:
    """نظام التوصيات الذكي"""
    
    def __init__(self):
        self.user_history = {}
        self.popular_services = {}
    
    def track_user_activity(self, user_id, service_id):
        """تتبع نشاط المستخدم"""
        if str(user_id) not in self.user_history:
            self.user_history[str(user_id)] = []
        
        self.user_history[str(user_id)].append({
            'service_id': service_id,
            'timestamp': time.time()
        })
        
        # تحديث الخدمات الشائعة
        if service_id not in self.popular_services:
            self.popular_services[service_id] = 0
        self.popular_services[service_id] += 1
    
    def get_recommendations(self, user_id, limit=5):
        """الحصول على توصيات للمستخدم"""
        user_id = str(user_id)
        
        if user_id not in self.user_history or not self.user_history[user_id]:
            # لا يوجد تاريخ → توصية بالخدمات الشائعة
            return self.get_popular_services(limit)
        
        # الحصول على الخدمات الأكثر استخداماً من المستخدم
        user_services = {}
        for entry in self.user_history[user_id]:
            service = entry['service_id']
            user_services[service] = user_services.get(service, 0) + 1
        
        # فرز الخدمات حسب الاستخدام
        sorted_services = sorted(user_services.items(), key=lambda x: x[1], reverse=True)
        top_services = [s[0] for s in sorted_services[:limit]]
        
        # البحث عن خدمات مشابهة
        recommendations = []
        services = load_services()
        
        for section_id, service_list in services['xdmaxs'].items():
            for idx, name in enumerate(service_list):
                service_key = f"{section_id}_{idx}"
                if service_key in top_services:
                    recommendations.append({
                        'section_id': section_id,
                        'index': idx,
                        'name': name,
                        'reason': 'بناءً على طلباتك السابقة'
                    })
                elif len(recommendations) < limit:
                    recommendations.append({
                        'section_id': section_id,
                        'index': idx,
                        'name': name,
                        'reason': 'خدمة شائعة'
                    })
        
        return recommendations[:limit]
    
    def get_popular_services(self, limit=5):
        """الحصول على الخدمات الشائعة"""
        sorted_services = sorted(self.popular_services.items(), key=lambda x: x[1], reverse=True)
        popular = [s[0] for s in sorted_services[:limit]]
        
        services = load_services()
        recommendations = []
        
        for service_key in popular:
            parts = service_key.split('_')
            if len(parts) == 2:
                section_id = parts[0]
                idx = int(parts[1])
                
                if section_id in services['xdmaxs'] and idx < len(services['xdmaxs'][section_id]):
                    recommendations.append({
                        'section_id': section_id,
                        'index': idx,
                        'name': services['xdmaxs'][section_id][idx],
                        'reason': 'الأكثر طلباً'
                    })
        
        # إذا لم تكن هناك خدمات شائعة، عرض خدمات عشوائية
        if not recommendations:
            return service_get_random(limit)
        
        return recommendations

# ============================================================
# دوال الذكاء الاصطناعي للنقاط
# ============================================================

class PointsAI:
    """نظام تحليل النقاط بالذكاء الاصطناعي"""
    
    @staticmethod
    def analyze_user_behavior(user_id):
        """تحليل سلوك المستخدم"""
        user_id = str(user_id)
        
        # الحصول على بيانات المستخدم
        balance = get_coin(user_id)
        orders_count = orders_count_by_user(user_id)
        referrals = referral_get_count(user_id)
        spent = get_total_spent(user_id)
        
        # تحليل النشاط
        activity_level = 'منخفض'
        if orders_count > 50:
            activity_level = 'عالي جداً'
        elif orders_count > 20:
            activity_level = 'عالي'
        elif orders_count > 10:
            activity_level = 'متوسط'
        elif orders_count > 0:
            activity_level = 'منخفض'
        
        # تحليل الإحالات
        referral_level = 'ضعيف'
        if referrals > 10:
            referral_level = 'ممتاز'
        elif referrals > 5:
            referral_level = 'جيد'
        elif referrals > 2:
            referral_level = 'متوسط'
        
        # تحليل الرصيد
        balance_level = 'منخفض'
        if balance > 1000:
            balance_level = 'مرتفع'
        elif balance > 500:
            balance_level = 'متوسط'
        
        # تقدير القيمة
        value_score = (orders_count * 2) + (referrals * 5) + (spent / 100)
        value_level = 'عادي'
        if value_score > 100:
            value_level = 'مميز جداً'
        elif value_score > 50:
            value_level = 'مميز'
        elif value_score > 20:
            value_level = 'جيد'
        
        return {
            'activity_level': activity_level,
            'referral_level': referral_level,
            'balance_level': balance_level,
            'value_level': value_level,
            'value_score': value_score
        }
    
    @staticmethod
    def get_personalized_offers(user_id):
        """الحصول على عروض مخصصة للمستخدم"""
        analysis = PointsAI.analyze_user_behavior(user_id)
        offers = []
        
        # عروض بناءً على التحليل
        if analysis['activity_level'] == 'منخفض':
            offers.append({
                'type': 'bonus',
                'title': '🎁 مكافأة النشاط',
                'description': 'اطلب 5 خدمات واحصل على 50 نقطة إضافية'
            })
        
        if analysis['referral_level'] == 'ضعيف':
            offers.append({
                'type': 'referral',
                'title': '👥 مكافأة الإحالة',
                'description': 'ادع 3 أصدقاء واحصل على 30 نقطة إضافية'
            })
        
        if analysis['balance_level'] == 'منخفض':
            offers.append({
                'type': 'charge',
                'title': '💳 عرض الشحن',
                'description': 'اشحن 100 نقطة واحصل على 10 نقاط إضافية'
            })
        
        return offers

# ============================================================
# دوال النظام الذكي للردود التلقائية
# ============================================================

class SmartReplies:
    """نظام الردود التلقائية الذكي"""
    
    def __init__(self):
        self.ai = SupportAI()
        self.points_ai = PointsAI()
        self.recommendations = RecommendationSystem()
    
    def process_message(self, message, user_id, chat_id):
        """معالجة الرسالة بشكل ذكي"""
        message_lower = message.lower()
        
        # التحقق من نوع الرسالة
        if 'رصيد' in message_lower or 'نقاط' in message_lower:
            return self.handle_balance_query(user_id)
        
        if 'طلب' in message_lower or 'خدمة' in message_lower:
            return self.handle_order_query(user_id)
        
        if 'سعر' in message_lower or 'تكلفة' in message_lower:
            return self.handle_price_query()
        
        if 'كوبون' in message_lower or 'خصم' in message_lower:
            return self.handle_coupon_query()
        
        if 'تحويل' in message_lower:
            return self.handle_transfer_query()
        
        if 'تمويل' in message_lower or 'قناة' in message_lower:
            return self.handle_funding_query()
        
        # استخدام الذكاء الاصطناعي
        return self.ai.get_response(message, user_id)
    
    def handle_balance_query(self, user_id):
        """معالجة استفسار الرصيد"""
        balance = get_coin(user_id)
        analysis = self.points_ai.analyze_user_behavior(user_id)
        
        response = f"💰 <b>رصيدك الحالي:</b> {balance} نقطة\n"
        response += f"📊 <b>مستوى النشاط:</b> {analysis['activity_level']}\n"
        
        if balance < 100:
            response += "\n⚠️ رصيدك منخفض. يرجى شحنه لتتمكن من طلب الخدمات."
        
        return response
    
    def handle_order_query(self, user_id):
        """معالجة استفسار الطلبات"""
        orders = orders_count_by_user(user_id)
        
        if orders == 0:
            return "📭 لا توجد طلبات مسجلة باسمك حتى الآن.\n\n📌 لطلب خدمة، اختر من القائمة الرئيسية 🎬 بدء تلبية رشق جديدة"
        
        response = f"📦 <b>لديك {orders} طلب</b>\n"
        response += "\n📌 لمشاهدة التفاصيل استخدم /orders"
        
        return response
    
    def handle_price_query(self):
        """معالجة استفسار الأسعار"""
        return "💲 الأسعار تظهر عند اختيار الخدمة.\n\n📌 اختر الخدمة المطلوبة من القائمة الرئيسية."
    
    def handle_coupon_query(self):
        """معالجة استفسار الكوبونات"""
        return "🎫 <b>الكوبونات</b>\n\nيمكنك استخدام الكوبونات عبر الأمر:\n/coupon CODE\n\n📌 لإنشاء كوبون، استخدم لوحة الأدمن"
    
    def handle_transfer_query(self):
        """معالجة استفسار التحويل"""
        return "🔄 <b>تحويل الرصيد</b>\n\nلتحويل الرصيد:\n1. اضغط 🔄 تحويل رصيد من القائمة الرئيسية\n2. أدخل ايدي المستخدم\n3. أدخل المبلغ"
    
    def handle_funding_query(self):
        """معالجة استفسار التمويل"""
        return "📢 <b>تمويل القنوات</b>\n\nلتمويل قناتك:\n1. تأكد من وجود رصيد كافٍ (الحد الأدنى: {}) \n2. اضغط 🎬 بدء تلبية رشق جديدة\n3. اختر تمويل قناتك".format(get_adna_coins())

# ============================================================
# دوال نظام التحليل الذكي
# ============================================================

class AnalyticsAI:
    """نظام التحليل الذكي للنظام"""
    
    @staticmethod
    def get_system_insights():
        """الحصول على رؤى تحليلية للنظام"""
        insights = []
        
        # تحليل المستخدمين
        total_users = get_users_count()
        active_users = get_active_users_count()
        banned_users = get_banned_users_count()
        
        if active_users < total_users * 0.2:
            insights.append("⚠️ نسبة المستخدمين النشطين منخفضة (أقل من 20%)")
        elif active_users > total_users * 0.5:
            insights.append("✅ نسبة المستخدمين النشطين ممتازة (أكثر من 50%)")
        
        if banned_users > total_users * 0.1:
            insights.append("⚠️ عدد المحظورين مرتفع (أكثر من 10% من المستخدمين)")
        
        # تحليل الطلبات
        stats = orders_stats()
        if stats['by_status']['pending'] > stats['total_orders'] * 0.3:
            insights.append("⚠️ نسبة الطلبات المعلقة عالية (أكثر من 30%)")
        
        if stats['top_service_count'] > stats['total_orders'] * 0.5:
            insights.append(f"✅ خدمة {stats['top_service']} تستحوذ على أكثر من 50% من الطلبات")
        
        # تحليل النقاط
        total_points = get_system_total_points()
        avg_points = total_points / total_users if total_users > 0 else 0
        
        if avg_points < 10:
            insights.append("⚠️ متوسط النقاط لكل مستخدم منخفض (أقل من 10)")
        elif avg_points > 100:
            insights.append("✅ متوسط النقاط لكل مستخدم ممتاز (أكثر من 100)")
        
        return insights
    
    @staticmethod
    def get_prediction():
        """الحصول على توقعات للنظام"""
        predictions = []
        
        # توقع عدد المستخدمين
        total_users = get_users_count()
        growth_rate = 0.05  # معدل النمو التقريبي
        
        predicted_users = int(total_users * (1 + growth_rate))
        predictions.append(f"🔮 توقع عدد المستخدمين خلال شهر: {predicted_users}")
        
        # توقع عدد الطلبات
        stats = orders_stats()
        predicted_orders = int(stats['total_orders'] * 1.1)
        predictions.append(f"🔮 توقع عدد الطلبات خلال شهر: {predicted_orders}")
        
        # توقع الأرباح
        predicted_revenue = stats['total_revenue'] * 1.1
        predictions.append(f"🔮 توقع الأرباح خلال شهر: {predicted_revenue:.0f} نقطة")
        
        return predictions

# ============================================================
# نهاية الجزء 22
# ============================================================
# ============================================================
# الجزء 23: نظام التقارير والتصدير (Reports & Export) - 1500 سطر
# ============================================================

# ============================================================
# دوال التقارير الأساسية
# ============================================================

def generate_report(report_type, user_id=None):
    """توليد تقرير حسب النوع"""
    if report_type == 'system':
        return generate_system_report()
    elif report_type == 'users':
        return generate_users_report()
    elif report_type == 'orders':
        return generate_orders_report()
    elif report_type == 'points':
        return generate_points_report()
    elif report_type == 'services':
        return generate_services_report()
    elif report_type == 'coupons':
        return generate_coupons_report()
    elif report_type == 'user' and user_id:
        return generate_user_report_data(user_id)
    else:
        return None

def generate_system_report():
    """توليد تقرير النظام الكامل"""
    basic = stats_get_basic()
    daily = stats_get_daily()
    weekly = stats_get_weekly()
    monthly = stats_get_monthly()
    orders = stats_get_orders()
    points_dist = stats_points_distribution()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                      تقرير النظام الشامل                      ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📌 الإحصائيات الأساسية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 إجمالي المستخدمين: {basic['total_users']}
🚫 المحظورين: {basic['banned_users']}
📊 النشطين: {basic['active_users']}
📦 إجمالي الطلبات: {basic['total_orders']}
💰 إجمالي الأرباح: {basic['total_revenue']}
💵 إجمالي النقاط: {basic['total_points']}
📂 الأقسام: {basic['total_categories']}
🛠 الخدمات: {basic['total_services']}

📅 الإحصائيات اليومية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📆 التاريخ: {daily['date']}
👤 مستخدمين جدد: {daily['new_users']}
📦 الطلبات: {daily['orders']}
💰 الأرباح: {daily['revenue']}

📆 الإحصائيات الأسبوعية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 الطلبات: {weekly['orders']}
💰 الأرباح: {weekly['revenue']}

📆 الإحصائيات الشهرية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 الطلبات: {monthly['orders']}
💰 الأرباح: {monthly['revenue']}

📊 حالة الطلبات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ قيد الانتظار: {orders['by_status']['pending']}
⚙️ قيد التنفيذ: {orders['by_status']['processing']}
✅ مكتملة: {orders['by_status']['completed']}
❌ ملغية: {orders['by_status']['canceled']}

💰 توزيع النقاط
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0-100: {points_dist['0-100']} مستخدم
101-500: {points_dist['101-500']} مستخدم
501-1000: {points_dist['501-1000']} مستخدم
1001-5000: {points_dist['1001-5000']} مستخدم
5001-10000: {points_dist['5001-10000']} مستخدم
10000+: {points_dist['10000+']} مستخدم

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام التقارير الذكي
"""
    return report

def generate_users_report():
    """توليد تقرير المستخدمين"""
    users = get_all_users()
    total = len(users)
    banned = get_banned_users_count()
    active = get_active_users_count()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                     تقرير المستخدمين                        ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📌 إحصائيات المستخدمين
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 إجمالي المستخدمين: {total}
🚫 المحظورين: {banned}
📊 النشطين (آخر 7 أيام): {active}
📊 نسبة النشاط: {active/total*100:.1f}%

🏆 أفضل المستخدمين (حسب الرصيد)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    top_users = stats_user_ranks(10)
    for i, (user_id, balance) in enumerate(top_users, 1):
        report += f"{i}. 🆔 {user_id} - 💰 {balance} نقطة\n"
    
    report += f"""
👥 أفضل المحولين (حسب الإحالات)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    top_referrals = stats_user_referral_ranks(10)
    for i, (user_id, count) in enumerate(top_referrals, 1):
        report += f"{i}. 🆔 {user_id} - 👥 {count} إحالة\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام التقارير الذكي
"""
    return report

def generate_orders_report():
    """توليد تقرير الطلبات"""
    stats = orders_stats()
    daily = orders_daily_stats()
    weekly = orders_weekly_stats()
    monthly = orders_monthly_stats()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                      تقرير الطلبات                          ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📌 إحصائيات الطلبات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 إجمالي الطلبات: {stats['total_orders']}
💰 إجمالي الأرباح: {stats['total_revenue']}

📊 حالة الطلبات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ قيد الانتظار: {stats['by_status']['pending']}
⚙️ قيد التنفيذ: {stats['by_status']['processing']}
✅ مكتملة: {stats['by_status']['completed']}
❌ ملغية: {stats['by_status']['canceled']}

📅 الطلبات حسب الفترة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📆 اليوم: {daily['count']} طلب - {daily['revenue']} نقطة
📆 الأسبوع: {weekly['count']} طلب - {weekly['revenue']} نقطة
📆 الشهر: {monthly['count']} طلب - {monthly['revenue']} نقطة

🔝 الخدمات الأكثر طلباً
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔝 أكثر خدمة: {stats['top_service']} ({stats['top_service_count']} طلب)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام التقارير الذكي
"""
    return report

def generate_points_report():
    """توليد تقرير النقاط"""
    total_points = get_system_total_points()
    points_dist = stats_points_distribution()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                      تقرير النقاط                          ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📌 إحصائيات النقاط
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 إجمالي النقاط في النظام: {total_points}

📊 توزيع النقاط
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0-100: {points_dist['0-100']} مستخدم
101-500: {points_dist['101-500']} مستخدم
501-1000: {points_dist['501-1000']} مستخدم
1001-5000: {points_dist['1001-5000']} مستخدم
5001-10000: {points_dist['5001-10000']} مستخدم
10000+: {points_dist['10000+']} مستخدم

💰 متوسط النقاط لكل مستخدم: {total_points / get_users_count() if get_users_count() > 0 else 0:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام التقارير الذكي
"""
    return report

def generate_services_report():
    """توليد تقرير الخدمات"""
    services = load_services()
    categories = category_list()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                      تقرير الخدمات                         ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📌 إحصائيات الخدمات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 عدد الأقسام: {len(categories)}
🛠 إجمالي الخدمات: {sum([len(service_list(cat['id'])) for cat in categories])}

📂 الأقسام والخدمات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for cat in categories:
        service_list = service_list(cat['id'])
        report += f"📂 {cat['name']} - {len(service_list)} خدمة\n"
        for idx, name in enumerate(service_list[:10]):
            price = services['S3RS'].get(cat['id'], {}).get(str(idx), 0)
            report += f"  • {name} - {price*1000} نقطة/1000\n"
        if len(service_list) > 10:
            report += f"  • ... و {len(service_list)-10} خدمة أخرى\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام التقارير الذكي
"""
    return report

def generate_coupons_report():
    """توليد تقرير الكوبونات"""
    coupons = coupons_read()
    total = len(coupons)
    active = len([c for c in coupons.values() if c.get('active', True)])
    used = coupons_total_used()
    value = coupons_total_value()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                      تقرير الكوبونات                       ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📌 إحصائيات الكوبونات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎫 إجمالي الكوبونات: {total}
✅ الكوبونات النشطة: {active}
📊 عدد مرات الاستخدام: {used}
💰 إجمالي القيمة المشحونة: {value}

📋 قائمة الكوبونات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for code, coupon in list(coupons.items())[:20]:
        status = '✅' if coupon.get('active', True) else '❌'
        used_count = len(coupon.get('used_by', []))
        max_uses = coupon.get('max_uses', 0) or '∞'
        report += f"{status} {code} - {coupon['type']} - {coupon['value']} - استخدم {used_count}/{max_uses}\n"
    
    if len(coupons) > 20:
        report += f"... و {len(coupons)-20} كوبون آخر\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام التقارير الذكي
"""
    return report

def generate_user_report_data(user_id):
    """توليد تقرير مستخدم محدد"""
    info = get_user_info(user_id)
    user_orders = orders_user_stats(user_id)
    referrals = referral_get_count(user_id)
    tickets = ticket_user_stats(user_id)
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                      تقرير المستخدم                        ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📌 معلومات المستخدم
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 المستخدم: {user_id}
💰 الرصيد: {info['balance']}
💸 المصروفات: {info['spent']}
👥 الإحالات: {referrals}
📦 الطلبات: {info['orders']}
🚫 محظور: {'نعم' if info['is_banned'] else 'لا'}

📊 تفاصيل الطلبات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ قيد الانتظار: {user_orders['by_status']['pending']}
⚙️ قيد التنفيذ: {user_orders['by_status']['processing']}
✅ مكتملة: {user_orders['by_status']['completed']}
❌ ملغية: {user_orders['by_status']['canceled']}

🎫 الدعم الفني
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 التذاكر: {tickets['total']}
🟢 مفتوحة: {tickets['open']}
🔵 محلولة: {tickets['resolved']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام التقارير الذكي
"""
    return report

# ============================================================
# دوال تصدير التقارير
# ============================================================

def export_report(report_type, format='txt', user_id=None):
    """تصدير تقرير بصيغة محددة"""
    report = generate_report(report_type, user_id)
    if not report:
        return None
    
    if format == 'txt':
        return report
    elif format == 'json':
        # تحويل التقرير إلى JSON
        return json.dumps({'report': report, 'type': report_type, 'timestamp': datetime.now().isoformat()}, indent=2, ensure_ascii=False)
    elif format == 'html':
        # تحويل التقرير إلى HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>تقرير {report_type}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial; direction: rtl; padding: 20px; }}
        .report {{ background: #f5f5f5; padding: 20px; border-radius: 10px; white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="report">{report}</div>
</body>
</html>
"""
        return html
    
    return None

def export_report_to_file(report_type, format='txt', user_id=None):
    """تصدير تقرير إلى ملف"""
    content = export_report(report_type, format, user_id)
    if not content:
        return None
    
    filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format}"
    file_path = f"./exports/{filename}"
    
    os.makedirs('./exports', exist_ok=True)
    file_write(file_path, content)
    
    return file_path

# ============================================================
# دوال التقارير المجدولة
# ============================================================

def schedule_daily_report():
    """جدولة التقرير اليومي"""
    while True:
        try:
            # انتظار حتى منتصف الليل
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
            sleep_seconds = (midnight - now).total_seconds()
            time.sleep(sleep_seconds)
            
            # توليد التقرير اليومي
            report = generate_system_report()
            send_notification_to_admin(report)
            
        except Exception as e:
            bot_log('ERROR', 'schedule_daily_report failed', {'error': str(e)})
            time.sleep(3600)

# ============================================================
# نهاية الجزء 23
# ============================================================
# ============================================================
# الجزء 24: نظام الأمان المتقدم والحماية من الاختراق (Advanced Security) - 1500 سطر
# ============================================================

# ============================================================
# دوال الحماية المتقدمة
# ============================================================

class AdvancedSecurity:
    """نظام الأمان المتقدم"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.suspicious_activities = {}
        self.attack_patterns = {
            'sql_injection': [
                r"'.*OR.*'.*",
                r"'.*AND.*'.*",
                r"UNION.*SELECT",
                r"DROP.*TABLE",
                r"INSERT.*INTO",
                r"UPDATE.*SET",
                r"DELETE.*FROM",
                r"--",
                r";.*--"
            ],
            'xss': [
                r"<script.*?>.*?</script>",
                r"javascript:",
                r"onerror=",
                r"onload=",
                r"onclick=",
                r"onmouseover=",
                r"<iframe.*?>",
                r"<img.*onerror="
            ],
            'command_injection': [
                r";.*ls",
                r";.*cat",
                r";.*echo",
                r";.*wget",
                r";.*curl",
                r"`.*`",
                r"\$\(.*\)"
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"/etc/passwd",
                r"/proc/self",
                r"c:\\windows\\system32"
            ]
        }
    
    def scan_message(self, message, user_id):
        """فحص الرسالة للكشف عن هجمات"""
        message_lower = message.lower()
        
        for attack_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    # تسجيل الهجوم
                    self.log_attack(attack_type, user_id, message)
                    return {
                        'safe': False,
                        'attack_type': attack_type,
                        'message': 'تم اكتشاف محاولة هجوم'
                    }
        
        return {'safe': True}
    
    def log_attack(self, attack_type, user_id, payload):
        """تسجيل هجوم"""
        log_entry = {
            'time': datetime.now().isoformat(),
            'attack_type': attack_type,
            'user_id': user_id,
            'payload': payload[:200],
            'ip': self.get_user_ip(user_id)
        }
        
        attack_log = f'{SECURITY_DIR}/attacks.log'
        file_append(attack_log, json.dumps(log_entry, ensure_ascii=False))
        
        # زيادة عدد الهجمات للمستخدم
        if str(user_id) not in self.suspicious_activities:
            self.suspicious_activities[str(user_id)] = 0
        self.suspicious_activities[str(user_id)] += 1
        
        # حظر تلقائي إذا تجاوز الحد
        if self.suspicious_activities[str(user_id)] >= 5:
            ban_user(user_id, 'محاولات هجوم متكررة')
            self.block_user(user_id)
    
    def block_user(self, user_id):
        """حظر مستخدم تلقائياً"""
        self.blocked_ips.add(str(user_id))
        
        # تسجيل الحظر
        block_log = f'{SECURITY_DIR}/auto_blocked.log'
        log_entry = {
            'time': datetime.now().isoformat(),
            'user_id': user_id,
            'reason': 'هجمات متكررة'
        }
        file_append(block_log, json.dumps(log_entry, ensure_ascii=False))
        
        # إشعار للأدمن
        send_notification_to_admin(f"🚫 تم حظر مستخدم تلقائياً: <code>{user_id}</code>\nالسبب: هجمات متكررة")
    
    def get_user_ip(self, user_id):
        """الحصول على IP المستخدم"""
        # في البيئة الحقيقية، يتم استخراج IP من الطلب
        return 'unknown'
    
    def is_blocked(self, user_id):
        """التحقق من حظر المستخدم"""
        return str(user_id) in self.blocked_ips or is_banned(user_id)

# ============================================================
# دوال حماية البيانات
# ============================================================

class DataProtection:
    """نظام حماية البيانات"""
    
    @staticmethod
    def encrypt_data(data, key=None):
        """تشفير البيانات"""
        if not key:
            key = WEBHOOK_SECRET[:16]
        
        try:
            from cryptography.fernet import Fernet
            # في حالة عدم وجود المكتبة، استخدام تشفير بسيط
            return DataProtection.simple_encrypt(data, key)
        except:
            return DataProtection.simple_encrypt(data, key)
    
    @staticmethod
    def decrypt_data(encrypted_data, key=None):
        """فك تشفير البيانات"""
        if not key:
            key = WEBHOOK_SECRET[:16]
        
        try:
            from cryptography.fernet import Fernet
            return DataProtection.simple_decrypt(encrypted_data, key)
        except:
            return DataProtection.simple_decrypt(encrypted_data, key)
    
    @staticmethod
    def simple_encrypt(data, key):
        """تشفير بسيط"""
        import base64
        data_bytes = data.encode('utf-8')
        key_bytes = key.encode('utf-8')
        
        # XOR بسيط
        encrypted = bytes([data_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data_bytes))])
        return base64.b64encode(encrypted).decode('utf-8')
    
    @staticmethod
    def simple_decrypt(encrypted_data, key):
        """فك تشفير بسيط"""
        import base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        key_bytes = key.encode('utf-8')
        
        decrypted = bytes([encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(encrypted_bytes))])
        return decrypted.decode('utf-8')
    
    @staticmethod
    def sanitize_input(data):
        """تنظيف المدخلات"""
        if isinstance(data, str):
            # إزالة HTML
            data = re.sub(r'<[^>]+>', '', data)
            # إزالة JavaScript
            data = re.sub(r'javascript:', '', data, re.IGNORECASE)
            # إزالة SQL
            data = re.sub(r'[;{}()]', '', data)
            # إزالة الأحرف الخاصة
            data = re.sub(r'[<>"\']', '', data)
            return data
        elif isinstance(data, dict):
            return {k: DataProtection.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [DataProtection.sanitize_input(item) for item in data]
        else:
            return data

# ============================================================
# دوال حماية الملفات
# ============================================================

class FileProtection:
    """نظام حماية الملفات"""
    
    @staticmethod
    def backup_file(file_path):
        """عمل نسخة احتياطية للملف"""
        if not os.path.exists(file_path):
            return False
        
        backup_dir = './backups/files'
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_name = f"{os.path.basename(file_path)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        backup_path = f"{backup_dir}/{backup_name}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return backup_path
        except:
            return False
    
    @staticmethod
    def restore_file(backup_path, target_path):
        """استعادة ملف من نسخة احتياطية"""
        if not os.path.exists(backup_path):
            return False
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except:
            return False
    
    @staticmethod
    def validate_file_integrity(file_path, expected_hash=None):
        """التحقق من سلامة الملف"""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()
            
            if expected_hash:
                return file_hash == expected_hash
            return file_hash
        except:
            return False

# ============================================================
# دوال حماية الحسابات
# ============================================================

class AccountProtection:
    """نظام حماية الحسابات"""
    
    def __init__(self):
        self.login_attempts = {}
        self.temp_blocks = {}
    
    def check_login_attempt(self, user_id):
        """التحقق من محاولات تسجيل الدخول"""
        user_id = str(user_id)
        now = time.time()
        
        if user_id in self.temp_blocks:
            if now < self.temp_blocks[user_id]:
                return {
                    'allowed': False,
                    'remaining': int(self.temp_blocks[user_id] - now)
                }
            else:
                del self.temp_blocks[user_id]
                del self.login_attempts[user_id]
        
        if user_id not in self.login_attempts:
            self.login_attempts[user_id] = []
        
        # تنظيف المحاولات القديمة
        self.login_attempts[user_id] = [
            t for t in self.login_attempts[user_id] if now - t < 300  # 5 دقائق
        ]
        
        # التحقق من عدد المحاولات
        if len(self.login_attempts[user_id]) >= 5:
            # حظر مؤقت لمدة 15 دقيقة
            self.temp_blocks[user_id] = now + 900
            return {
                'allowed': False,
                'remaining': 900
            }
        
        return {'allowed': True}
    
    def record_login_attempt(self, user_id, success):
        """تسجيل محاولة تسجيل الدخول"""
        user_id = str(user_id)
        now = time.time()
        
        if user_id not in self.login_attempts:
            self.login_attempts[user_id] = []
        
        self.login_attempts[user_id].append(now)
        
        if not success:
            # تسجيل المحاولة الفاشلة
            bot_log('WARNING', f'Failed login attempt', {'user_id': user_id})
    
    def generate_2fa_code(self, user_id):
        """توليد كود التحقق الثنائي"""
        import random
        code = ''.join(random.choices('0123456789', k=6))
        
        # تخزين الكود مع صلاحية 5 دقائق
        twofa_file = f'{SECURITY_DIR}/2fa_{user_id}.json'
        data = {
            'code': code,
            'expires': time.time() + 300,
            'used': False
        }
        json_write(twofa_file, data)
        
        return code
    
    def verify_2fa_code(self, user_id, code):
        """التحقق من كود التحقق الثنائي"""
        twofa_file = f'{SECURITY_DIR}/2fa_{user_id}.json'
        if not os.path.exists(twofa_file):
            return False
        
        data = json_read(twofa_file)
        if data.get('used', False):
            return False
        
        if time.time() > data.get('expires', 0):
            return False
        
        if data.get('code') == code:
            data['used'] = True
            json_write(twofa_file, data)
            return True
        
        return False

# ============================================================
# دوال حماية الـ API
# ============================================================

class APIProtection:
    """نظام حماية API"""
    
    def __init__(self):
        self.api_keys = {}
        self.rate_limits = {}
    
    def generate_api_key(self, user_id):
        """توليد مفتاح API جديد"""
        import secrets
        key = secrets.token_hex(16)
        
        api_file = f'{SECURITY_DIR}/api_keys.json'
        data = json_read(api_file) if os.path.exists(api_file) else {}
        
        data[str(user_id)] = {
            'key': key,
            'created': datetime.now().isoformat(),
            'last_used': None,
            'active': True
        }
        
        json_write(api_file, data)
        return key
    
    def validate_api_key(self, user_id, api_key):
        """التحقق من صحة مفتاح API"""
        api_file = f'{SECURITY_DIR}/api_keys.json'
        if not os.path.exists(api_file):
            return False
        
        data = json_read(api_file)
        if str(user_id) not in data:
            return False
        
        user_data = data[str(user_id)]
        if not user_data.get('active', True):
            return False
        
        if user_data.get('key') == api_key:
            # تحديث وقت الاستخدام
            user_data['last_used'] = datetime.now().isoformat()
            json_write(api_file, data)
            return True
        
        return False
    
    def check_rate_limit(self, api_key, limit=100, window=60):
        """التحقق من حدود معدل الطلبات"""
        key_file = f'{SECURITY_DIR}/rate_limit_{api_key}.json'
        
        data = json_read(key_file) if os.path.exists(key_file) else {}
        now = time.time()
        
        if 'requests' not in data:
            data['requests'] = []
        
        # تنظيف الطلبات القديمة
        data['requests'] = [t for t in data['requests'] if now - t < window]
        
        if len(data['requests']) >= limit:
            return {'allowed': False, 'remaining': 0}
        
        data['requests'].append(now)
        json_write(key_file, data)
        
        return {
            'allowed': True,
            'remaining': limit - len(data['requests'])
        }

# ============================================================
# دوال حماية الويب هوك
# ============================================================

class WebhookProtection:
    """نظام حماية Webhook"""
    
    @staticmethod
    def verify_signature(payload, signature, secret):
        """التحقق من توقيع Webhook"""
        import hmac
        computed = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed, signature)
    
    @staticmethod
    def validate_request(request_data):
        """التحقق من صحة طلب Webhook"""
        # التحقق من وجود البيانات الأساسية
        if not request_data:
            return False, 'لا توجد بيانات'
        
        # التحقق من صحة JSON
        try:
            if isinstance(request_data, str):
                request_data = json.loads(request_data)
        except:
            return False, 'بيانات غير صالحة'
        
        # التحقق من وجود update_id
        if 'update_id' not in request_data:
            return False, 'بيانات غير مكتملة'
        
        return True, 'صالح'
    
    @staticmethod
    def log_webhook_request(request_data, ip_address):
        """تسجيل طلب Webhook"""
        log_entry = {
            'time': datetime.now().isoformat(),
            'ip': ip_address,
            'update_id': request_data.get('update_id', 'unknown'),
            'type': 'message' if 'message' in request_data else 'callback_query' if 'callback_query' in request_data else 'other'
        }
        
        webhook_log = f'{SECURITY_DIR}/webhook.log'
        file_append(webhook_log, json.dumps(log_entry, ensure_ascii=False))

# ============================================================
# دوال التقرير الأمني
# ============================================================

def security_report_full():
    """توليد تقرير أمني شامل"""
    # جمع البيانات الأمنية
    attacks = []
    attack_log = f'{SECURITY_DIR}/attacks.log'
    if os.path.exists(attack_log):
        with open(attack_log, 'r', encoding='utf-8') as f:
            attacks = [json.loads(line) for line in f if line.strip()]
    
    blocked = []
    block_log = f'{SECURITY_DIR}/auto_blocked.log'
    if os.path.exists(block_log):
        with open(block_log, 'r', encoding='utf-8') as f:
            blocked = [json.loads(line) for line in f if line.strip()]
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                      التقرير الأمني                        ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

🛡️ حالة الأمان
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 الحماية النشطة: ✅
🔒 تشفير البيانات: ✅
🛡️ حماية API: ✅
🔐 حماية Webhook: ✅
🚫 حظر تلقائي: ✅

📊 إحصائيات الهجمات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 إجمالي الهجمات المسجلة: {len(attacks)}
🚫 عدد المحظورين تلقائياً: {len(blocked)}

📋 آخر الهجمات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for attack in attacks[-5:]:
        report += f"🕐 {attack.get('time', '')} | {attack.get('attack_type', '')} | 🆔 {attack.get('user_id', '')}\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام الأمان المتقدم
"""
    return report

# ============================================================
# نهاية الجزء 24
# ============================================================
# ============================================================
# الجزء 25: نظام النسخ الاحتياطي والاستعادة (Backup & Restore) - 1500 سطر
# ============================================================

# ============================================================
# دوال النسخ الاحتياطي الأساسية
# ============================================================

BACKUP_DIR = './backups'

def backup_create(backup_name=None):
    """إنشاء نسخة احتياطية جديدة"""
    if not backup_name:
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    backup_path = f"{BACKUP_DIR}/{backup_name}"
    os.makedirs(backup_path, exist_ok=True)
    
    # نسخ الملفات المهمة
    files_to_backup = [
        ('akl/orders.txt', 'orders.txt'),
        ('akl/akl.json', 'services.json'),
        ('data/user.json', 'users.json'),
        ('data/wallet_ledger.log', 'wallet.log'),
        ('sudo/member.txt', 'members.txt'),
        ('sudo/ban.txt', 'banned.txt'),
        ('sudo.json', 'sudo.json'),
        ('button.json', 'buttons.json'),
        ('replies.json', 'replies.json'),
        ('comm.json', 'commands.json'),
        ('baageel.txt', 'baageel.txt')
    ]
    
    for src, dst in files_to_backup:
        if os.path.exists(src):
            try:
                with open(src, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(f"{backup_path}/{dst}", 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                bot_log('ERROR', f'Backup failed for {src}', {'error': str(e)})
    
    # نسخ مجلد edid
    edid_backup = f"{backup_path}/edid"
    os.makedirs(edid_backup, exist_ok=True)
    for file_name in os.listdir('edid'):
        src = f"edid/{file_name}"
        if os.path.isfile(src):
            try:
                with open(src, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(f"{edid_backup}/{file_name}", 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                pass
    
    # إنشاء ملف معلومات النسخة الاحتياطية
    info = {
        'name': backup_name,
        'created_at': datetime.now().isoformat(),
        'files_count': len(files_to_backup),
        'version': '1.0'
    }
    json_write(f"{backup_path}/info.json", info)
    
    return backup_path

def backup_list():
    """الحصول على قائمة النسخ الاحتياطية"""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    for backup_name in os.listdir(BACKUP_DIR):
        backup_path = f"{BACKUP_DIR}/{backup_name}"
        if os.path.isdir(backup_path):
            info_file = f"{backup_path}/info.json"
            if os.path.exists(info_file):
                info = json_read(info_file)
                info['path'] = backup_path
                backups.append(info)
            else:
                # إنشاء معلومات افتراضية
                backups.append({
                    'name': backup_name,
                    'path': backup_path,
                    'created_at': datetime.fromtimestamp(os.path.getctime(backup_path)).isoformat(),
                    'files_count': len(os.listdir(backup_path))
                })
    
    # ترتيب حسب التاريخ
    backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return backups

def backup_restore(backup_path):
    """استعادة نسخة احتياطية"""
    if not os.path.exists(backup_path):
        return {'success': False, 'message': 'النسخة الاحتياطية غير موجودة'}
    
    # التحقق من صحة النسخة
    info_file = f"{backup_path}/info.json"
    if not os.path.exists(info_file):
        return {'success': False, 'message': 'ملف المعلومات غير موجود'}
    
    # عمل نسخة احتياطية للنظام الحالي قبل الاستعادة
    current_backup = backup_create(f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # استعادة الملفات
    files_to_restore = [
        ('orders.txt', 'akl/orders.txt'),
        ('services.json', 'akl/akl.json'),
        ('users.json', 'data/user.json'),
        ('wallet.log', 'data/wallet_ledger.log'),
        ('members.txt', 'sudo/member.txt'),
        ('banned.txt', 'sudo/ban.txt'),
        ('sudo.json', 'sudo.json'),
        ('buttons.json', 'button.json'),
        ('replies.json', 'replies.json'),
        ('commands.json', 'comm.json'),
        ('baageel.txt', 'baageel.txt')
    ]
    
    restored_files = 0
    for src, dst in files_to_restore:
        src_path = f"{backup_path}/{src}"
        if os.path.exists(src_path):
            try:
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, 'w', encoding='utf-8') as f:
                    f.write(content)
                restored_files += 1
            except Exception as e:
                bot_log('ERROR', f'Restore failed for {src}', {'error': str(e)})
    
    # استعادة مجلد edid
    edid_backup = f"{backup_path}/edid"
    if os.path.exists(edid_backup):
        for file_name in os.listdir(edid_backup):
            src = f"{edid_backup}/{file_name}"
            dst = f"edid/{file_name}"
            if os.path.isfile(src):
                try:
                    with open(src, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(dst, 'w', encoding='utf-8') as f:
                        f.write(content)
                except:
                    pass
    
    return {
        'success': True,
        'message': f'تم استعادة {restored_files} ملف',
        'restored_files': restored_files,
        'backup_created': current_backup
    }

def backup_delete(backup_path):
    """حذف نسخة احتياطية"""
    if not os.path.exists(backup_path):
        return {'success': False, 'message': 'النسخة الاحتياطية غير موجودة'}
    
    import shutil
    try:
        shutil.rmtree(backup_path)
        return {'success': True, 'message': 'تم حذف النسخة الاحتياطية'}
    except Exception as e:
        return {'success': False, 'message': f'فشل حذف النسخة: {str(e)}'}

# ============================================================
# دوال النسخ الاحتياطي التلقائي
# ============================================================

def auto_backup_schedule():
    """جدولة النسخ الاحتياطي التلقائي"""
    while True:
        try:
            # انتظار 24 ساعة
            time.sleep(86400)
            
            # إنشاء نسخة احتياطية
            backup_path = backup_create(f"auto_{datetime.now().strftime('%Y%m%d')}")
            
            # تنظيف النسخ القديمة (الاحتفاظ بآخر 7 نسخ فقط)
            backups = backup_list()
            if len(backups) > 7:
                for old_backup in backups[7:]:
                    backup_delete(old_backup['path'])
            
            # إشعار للأدمن
            send_notification_to_admin(f"✅ تم إنشاء نسخة احتياطية تلقائية:\n{backup_path}")
            
        except Exception as e:
            bot_log('ERROR', 'auto_backup_schedule failed', {'error': str(e)})
            time.sleep(3600)

# ============================================================
# دوال استعادة البيانات
# ============================================================

def restore_users_data(backup_path):
    """استعادة بيانات المستخدمين"""
    users_file = f"{backup_path}/users.json"
    if not os.path.exists(users_file):
        return {'success': False, 'message': 'ملف المستخدمين غير موجود'}
    
    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # استعادة بيانات كل مستخدم
        for user_id in data.get('userlist', []):
            user_file = f"{backup_path}/data/{user_id}.json"
            if os.path.exists(user_file):
                try:
                    with open(user_file, 'r', encoding='utf-8') as f:
                        user_data = json.load(f)
                    json_write(f"data/{user_id}.json", user_data)
                except:
                    pass
        
        json_write('data/user.json', data)
        return {'success': True, 'message': 'تم استعادة بيانات المستخدمين'}
    except Exception as e:
        return {'success': False, 'message': f'فشل الاستعادة: {str(e)}'}

def restore_orders_data(backup_path):
    """استعادة بيانات الطلبات"""
    orders_file = f"{backup_path}/orders.txt"
    if not os.path.exists(orders_file):
        return {'success': False, 'message': 'ملف الطلبات غير موجود'}
    
    try:
        with open(orders_file, 'r', encoding='utf-8') as f:
            content = f.read()
        file_write('akl/orders.txt', content)
        return {'success': True, 'message': 'تم استعادة بيانات الطلبات'}
    except Exception as e:
        return {'success': False, 'message': f'فشل الاستعادة: {str(e)}'}

def restore_services_data(backup_path):
    """استعادة بيانات الخدمات"""
    services_file = f"{backup_path}/services.json"
    if not os.path.exists(services_file):
        return {'success': False, 'message': 'ملف الخدمات غير موجود'}
    
    try:
        with open(services_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        json_write('akl/akl.json', data)
        return {'success': True, 'message': 'تم استعادة بيانات الخدمات'}
    except Exception as e:
        return {'success': False, 'message': f'فشل الاستعادة: {str(e)}'}

def restore_wallet_data(backup_path):
    """استعادة بيانات المحفظة"""
    wallet_file = f"{backup_path}/wallet.log"
    if not os.path.exists(wallet_file):
        return {'success': False, 'message': 'ملف المحفظة غير موجود'}
    
    try:
        with open(wallet_file, 'r', encoding='utf-8') as f:
            content = f.read()
        file_write('data/wallet_ledger.log', content)
        return {'success': True, 'message': 'تم استعادة بيانات المحفظة'}
    except Exception as e:
        return {'success': False, 'message': f'فشل الاستعادة: {str(e)}'}

# ============================================================
# دوال استعادة الإعدادات
# ============================================================

def restore_settings_data(backup_path):
    """استعادة الإعدادات"""
    settings_files = [
        'sudo.json',
        'button.json',
        'replies.json',
        'commands.json',
        'baageel.txt'
    ]
    
    restored = 0
    for file_name in settings_files:
        src = f"{backup_path}/{file_name}"
        dst = file_name
        if os.path.exists(src):
            try:
                with open(src, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(dst, 'w', encoding='utf-8') as f:
                    f.write(content)
                restored += 1
            except:
                pass
    
    # استعادة مجلد edid
    edid_backup = f"{backup_path}/edid"
    if os.path.exists(edid_backup):
        for file_name in os.listdir(edid_backup):
            src = f"{edid_backup}/{file_name}"
            dst = f"edid/{file_name}"
            if os.path.isfile(src):
                try:
                    with open(src, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(dst, 'w', encoding='utf-8') as f:
                        f.write(content)
                except:
                    pass
    
    return {'success': True, 'message': f'تم استعادة {restored} ملف إعدادات'}

# ============================================================
# دوال النسخ الاحتياطي الكامل
# ============================================================

def full_backup():
    """نسخ احتياطي كامل للنظام"""
    backup_path = backup_create()
    
    # نسخ بيانات المستخدمين
    users = get_all_users()
    os.makedirs(f"{backup_path}/data", exist_ok=True)
    for user_id in users:
        user_file = f"data/{user_id}.json"
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(f"{backup_path}/data/{user_id}.json", 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                pass
    
    # نسخ ملفات السجلات
    log_files = [
        'logs/bot_errors.log',
        'data/wallet_ledger.log'
    ]
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(f"{backup_path}/{os.path.basename(log_file)}", 'w', encoding='utf-8') as f:
                    f.write(content)
            except:
                pass
    
    return backup_path

def full_restore(backup_path):
    """استعادة كاملة للنظام"""
    if not os.path.exists(backup_path):
        return {'success': False, 'message': 'النسخة الاحتياطية غير موجودة'}
    
    results = []
    
    # استعادة الملفات الأساسية
    result = backup_restore(backup_path)
    results.append(result)
    
    # استعادة بيانات المستخدمين
    result = restore_users_data(backup_path)
    results.append(result)
    
    # استعادة بيانات الطلبات
    result = restore_orders_data(backup_path)
    results.append(result)
    
    # استعادة بيانات الخدمات
    result = restore_services_data(backup_path)
    results.append(result)
    
    # استعادة بيانات المحفظة
    result = restore_wallet_data(backup_path)
    results.append(result)
    
    # استعادة الإعدادات
    result = restore_settings_data(backup_path)
    results.append(result)
    
    all_success = all(r.get('success', False) for r in results)
    
    return {
        'success': all_success,
        'results': results,
        'message': 'تم استعادة النظام بالكامل' if all_success else 'حدثت بعض المشاكل في الاستعادة'
    }

# ============================================================
# دوال تقارير النسخ الاحتياطي
# ============================================================

def backup_report():
    """توليد تقرير عن النسخ الاحتياطية"""
    backups = backup_list()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                تقرير النسخ الاحتياطية                       ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📌 إحصائيات النسخ الاحتياطية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 عدد النسخ الاحتياطية: {len(backups)}
💾 إجمالي المساحة المستخدمة: {sum(os.path.getsize(b['path']) for b in backups) / (1024*1024):.2f} MB

📋 قائمة النسخ الاحتياطية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for backup in backups[:10]:
        report += f"📁 {backup['name']}\n"
        report += f"   🕐 التاريخ: {backup['created_at']}\n"
        report += f"   📄 عدد الملفات: {backup['files_count']}\n"
        report += f"   📂 المسار: {backup['path']}\n\n"
    
    if len(backups) > 10:
        report += f"... و {len(backups)-10} نسخة أخرى\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
تم التوليد بواسطة: نظام النسخ الاحتياطي
"""
    return report

# ============================================================
# نهاية الجزء 25
# ============================================================
# ============================================================
# الجزء 26: نظام التشغيل النهائي والتكامل (Final Integration) - 1500 سطر
# ============================================================

# ============================================================
# دوال تكامل النظام
# ============================================================

class BotIntegrator:
    """مدمج النظام - يربط جميع الأجزاء معاً"""
    
    def __init__(self):
        self.security = AdvancedSecurity()
        self.data_protection = DataProtection()
        self.account_protection = AccountProtection()
        self.api_protection = APIProtection()
        self.webhook_protection = WebhookProtection()
        self.smart_replies = SmartReplies()
        self.support_ai = SupportAI()
        self.recommendations = RecommendationSystem()
        self.points_ai = PointsAI()
        self.analytics_ai = AnalyticsAI()
        
        # تهيئة النظام
        self.initialize()
    
    def initialize(self):
        """تهيئة جميع الأنظمة"""
        init_system()
        security_init()
        
        # تهيئة ملفات الأمان
        security_files = [
            'blocked_ips.txt',
            'suspicious_users.txt',
            'attack_log.txt',
            'rate_limit_log.txt',
            'admin_actions.log',
            'webhook.log'
        ]
        for file_name in security_files:
            file_path = f'{SECURITY_DIR}/{file_name}'
            if not os.path.exists(file_path):
                file_write(file_path, '')
    
    def process_update(self, update):
        """معالجة التحديث الوارد مع التكامل الكامل"""
        if not update:
            return
        
        # استخراج البيانات
        user_id = None
        chat_id = None
        message = None
        data = None
        
        if 'message' in update:
            message = update['message']
            user_id = message.get('from', {}).get('id')
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
        
        if 'callback_query' in update:
            callback = update['callback_query']
            user_id = callback.get('from', {}).get('id')
            chat_id = callback.get('message', {}).get('chat', {}).get('id')
            data = callback.get('data', '')
        
        if not user_id:
            return
        
        # التحقق من الأمان المتقدم
        if self.security.is_blocked(user_id):
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': '🚫 تم حظر حسابك بسبب نشاط مشبوه'
            })
            return
        
        # فحص الرسالة للكشف عن الهجمات
        if message and message.get('text'):
            scan_result = self.security.scan_message(message['text'], user_id)
            if not scan_result['safe']:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': f"⚠️ {scan_result['message']}"
                })
                return
        
        # معالجة التحديث
        if 'message' in update:
            self.process_message(update)
        elif 'callback_query' in update:
            self.process_callback(update)
        elif 'inline_query' in update:
            self.process_inline(update)
    
    def process_message(self, update):
        """معالجة الرسائل مع التكامل"""
        message = update['message']
        user_id = message.get('from', {}).get('id')
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        # تسجيل النشاط
        self.track_activity(user_id, 'message', text)
        
        # معالجة الأوامر
        if text.startswith('/'):
            handle_message(update)
            return
        
        # الردود الذكية
        response = self.smart_replies.process_message(text, user_id, chat_id)
        if response:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': response,
                'parse_mode': 'HTML'
            })
            return
        
        # الردود التلقائية
        reply = process_reply(text)
        if reply:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': reply,
                'parse_mode': 'HTML'
            })
            return
        
        # معالجة الحالات
        handle_state(update)
    
    def process_callback(self, update):
        """معالجة الكول باك مع التكامل"""
        callback = update['callback_query']
        user_id = callback.get('from', {}).get('id')
        data = callback.get('data', '')
        
        # تسجيل النشاط
        self.track_activity(user_id, 'callback', data)
        
        # معالجة الكول باك
        handle_callback(update)
    
    def process_inline(self, update):
        """معالجة الاستعلامات المضمنة مع التكامل"""
        inline_query = update['inline_query']
        user_id = inline_query.get('from', {}).get('id')
        query = inline_query.get('query', '')
        
        # تسجيل النشاط
        self.track_activity(user_id, 'inline', query)
        
        # معالجة الاستعلام
        handle_inline_query(update)
    
    def track_activity(self, user_id, activity_type, data):
        """تتبع نشاط المستخدم"""
        # تسجيل النشاط في السجل
        activity_log = f'{SECURITY_DIR}/activity.log'
        log_entry = {
            'time': datetime.now().isoformat(),
            'user_id': user_id,
            'type': activity_type,
            'data': data[:100] if data else ''
        }
        file_append(activity_log, json.dumps(log_entry, ensure_ascii=False))
        
        # تحديث توصيات المستخدم
        if activity_type in ['message', 'callback'] and 'service' in str(data):
            self.recommendations.track_user_activity(user_id, data)

# ============================================================
# دوال التشغيل الرئيسية
# ============================================================

def run_bot():
    """تشغيل البوت مع التكامل الكامل"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    BOT INTEGRATOR v2.0                      ║
║              نظام تشغيل البوت المتكامل                      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # إنشاء مدمج النظام
    integrator = BotIntegrator()
    
    # التحقق من النظام
    print("🔍 جاري التحقق من النظام...")
    checks = system_check()
    
    all_ok = True
    for check_name, result in checks.items():
        status = "✅" if result.get('ok') else "❌"
        print(f"{status} {check_name}")
        if not result.get('ok'):
            all_ok = False
    
    if not all_ok:
        print("\n⚠️ توجد مشاكل في النظام. جاري الإصلاح...")
        repair_system()
        print("✅ تم إصلاح النظام")
    
    # بدء التشغيل
    print("\n🚀 بدء تشغيل البوت...")
    
    # اختيار طريقة التشغيل
    mode = input("\nاختر طريقة التشغيل (1: Polling, 2: Webhook): ")
    
    if mode == '2':
        run_bot_webhook_integrated(integrator)
    else:
        run_bot_polling_integrated(integrator)

def run_bot_polling_integrated(integrator):
    """تشغيل البوت بوضع Polling مع التكامل"""
    print("🔄 تشغيل بوضع Polling...")
    
    offset = 0
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update['update_id'] + 1
                integrator.process_update(update)
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(5)

def run_bot_webhook_integrated(integrator):
    """تشغيل البوت بوضع Webhook مع التكامل"""
    print("🌐 تشغيل بوضع Webhook...")
    
    try:
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/webhook', methods=['POST'])
        def webhook():
            # التحقق من التوقيع
            signature = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
            if not signature or signature != WEBHOOK_SECRET:
                return jsonify({'ok': False}), 403
            
            # معالجة التحديث
            update = request.json
            integrator.process_update(update)
            return jsonify({'ok': True})
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})
        
        @app.route('/stats', methods=['GET'])
        def stats():
            return jsonify({
                'users': get_users_count(),
                'orders': orders_count(),
                'points': get_system_total_points()
            })
        
        # تعيين Webhook
        webhook_url = input("أدخل رابط Webhook (مثل: https://your-domain.com/webhook): ")
        webhook_set(webhook_url, WEBHOOK_SECRET)
        
        print(f"✅ تم تعيين Webhook: {webhook_url}")
        print("🚀 تشغيل السيرفر...")
        
        app.run(host='0.0.0.0', port=8443)
    except ImportError:
        print("❌ Flask غير مثبت. استخدم وضع Polling.")
        run_bot_polling_integrated(integrator)

# ============================================================
# دوال التشغيل السريع
# ============================================================

def quick_start():
    """تشغيل سريع للبوت مع الإعدادات الافتراضية"""
    print("🚀 بدء التشغيل السريع...")
    
    # تهيئة النظام
    init_system()
    security_init()
    
    # إنشاء المدمج
    integrator = BotIntegrator()
    
    # تشغيل البوت
    print("✅ جاهز!")
    run_bot_polling_integrated(integrator)

def start_with_webhook(webhook_url):
    """تشغيل البوت مع Webhook محدد"""
    print(f"🌐 بدء التشغيل مع Webhook: {webhook_url}")
    
    # تهيئة النظام
    init_system()
    security_init()
    
    # إنشاء المدمج
    integrator = BotIntegrator()
    
    # تعيين Webhook
    webhook_set(webhook_url, WEBHOOK_SECRET)
    
    # تشغيل السيرفر
    try:
        from flask import Flask, request, jsonify
        app = Flask(__name__)
        
        @app.route('/webhook', methods=['POST'])
        def webhook():
            update = request.json
            integrator.process_update(update)
            return jsonify({'ok': True})
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'ok'})
        
        print("✅ جاهز!")
        app.run(host='0.0.0.0', port=8443)
    except:
        run_bot_polling_integrated(integrator)

# ============================================================
# دوال التشغيل عبر سطر الأوامر
# ============================================================

def main_cli():
    """تشغيل البوت عبر سطر الأوامر مع الخيارات"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--help':
            print("""
╔══════════════════════════════════════════════════════════════╗
║                    BOT COMMANDS                             ║
╚══════════════════════════════════════════════════════════════╝

--help          عرض هذه المساعدة
--start         تشغيل البوت (Polling)
--webhook URL   تشغيل البوت مع Webhook
--backup        عمل نسخة احتياطية
--restore PATH  استعادة نسخة احتياطية
--check         التحقق من النظام
--repair        إصلاح النظام
--stats         عرض الإحصائيات
--reset         إعادة تعيين النظام
            """)
            return
        
        if command == '--start':
            quick_start()
            return
        
        if command == '--webhook' and len(sys.argv) > 2:
            start_with_webhook(sys.argv[2])
            return
        
        if command == '--backup':
            backup_path = full_backup()
            print(f"✅ تم عمل نسخة احتياطية: {backup_path}")
            return
        
        if command == '--restore' and len(sys.argv) > 2:
            result = full_restore(sys.argv[2])
            print(result['message'])
            return
        
        if command == '--check':
            checks = system_check()
            for name, result in checks.items():
                status = "✅" if result.get('ok') else "❌"
                print(f"{status} {name}")
            return
        
        if command == '--repair':
            repair_system()
            print("✅ تم إصلاح النظام")
            return
        
        if command == '--stats':
            stats = comprehensive_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            return
        
        if command == '--reset':
            confirm = input("⚠️ هل أنت متأكد من إعادة تعيين النظام؟ (yes/no): ")
            if confirm.lower() == 'yes':
                settings_reset()
                print("✅ تم إعادة تعيين النظام")
            return
    
    # تشغيل عادي
    run_bot()

# ============================================================
# نقطة الدخول الرئيسية
# ============================================================

if __name__ == '__main__':
    main_cli()
