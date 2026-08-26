import logging
import asyncio
import os
import random
import string
import json
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, 
    PreCheckoutQueryHandler, filters, ContextTypes
)
from telegram.error import Forbidden
from pyrogram import Client, filters as pyro_filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserNotParticipant, SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

SESSION_DIR = os.path.join(os.getcwd(), "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

DATA_FILE = "bot_data.json"

# =================================================================
# ⚙️ قسم البيانات الأساسية وتوكن البوت
# =================================================================
BOT_TOKEN = "5192231015:AAFDUpT_c_lHlU0e-ql-5mok1Q43CIOAkzc" 
OWNER_ID = 5200567520              
DEVELOPER_USER = "@b99b2"      
SOURCE_CHANNEL = "@b99bo"  

API_ID =                    
API_HASH = ""      
# =================================================================

PM_CONVERSATIONS = {}

# =================================================================
# 🖼️ الصورة الثابتة والإيموجي الجديدة
# =================================================================
IMAGE_URL = "https://f.top4top.io/p_3857rhpxe0.png"

# خريطة استبدال الإيموجي القديم بجديد (للاستخدام في النصوص)
EMOJI_MAP = {
    "«": "➡️",
    "»": "⬅️",
    "⭐️": "✨",
    "⭐": "✨",
    "🌙": "🌜",
    "✅": "✔️",
    "❌": "✖️",
    "⚠️": "❗",
    "📊": "📈",
    "👤": "🧑",
    "🗑": "🗑️",
    "ℹ️": "ℹ️",
    "🛒": "🛍️",
    "🔑": "🔐",
    "⏰": "⏳",
    "📱": "📲",
    "⚙️": "⚙️",
    "🎉": "🎉",
    "❓": "❓",
    "🔄": "🔄",
    "🔙": "🔙",
    "📨": "📨",
    "📤": "📤",
    "📥": "📥",
    "📁": "📁",
    "📂": "📂",
    "📝": "📝",
    "📌": "📌",
    "🔔": "🔔",
    "🔕": "🔕",
    "💬": "💬",
    "💭": "💭",
    "🌐": "🌐",
    "🏷️": "🏷️",
    "🔗": "🔗",
    "📎": "📎",
    "📋": "📋",
    "📖": "📖",
    "📚": "📚",
    "📢": "📢",
    "📣": "📣",
    "🔊": "🔊",
    "🔇": "🔇",
    "🎯": "🎯",
    "🏆": "🏆",
    "🥇": "🥇",
    "🥈": "🥈",
    "🥉": "🥉",
    "💎": "💎",
    "🌟": "🌟",
    "💫": "💫",
    "✨": "✨",
    "🔥": "🔥",
    "⚡": "⚡",
    "💡": "💡",
    "🧩": "🧩",
    "🛠️": "🛠️",
    "🔧": "🔧",
    "🔨": "🔨",
    "⚒️": "⚒️",
    "🖥️": "🖥️",
    "💻": "💻",
    "⌨️": "⌨️",
    "🖱️": "🖱️",
    "🖨️": "🖨️",
    "📡": "📡",
    "📶": "📶",
    "📳": "📳",
    "📴": "📴",
    "🔋": "🔋",
    "🪫": "🪫",
    "🔌": "🔌",
    "💾": "💾",
    "💿": "💿",
    "📀": "📀",
    "🧲": "🧲",
    "🧮": "🧮",
    "🧰": "🧰",
    "🧱": "🧱",
    "🧊": "🧊",
    "🧬": "🧬",
    "🧫": "🧫",
    "🧪": "🧪",
    "🧹": "🧹",
    "🧺": "🧺",
    "🧻": "🧻",
    "🧼": "🧼",
    "🧽": "🧽",
    "🧾": "🧾",
    "🧿": "🧿",
}

def replace_emojis(text: str) -> str:
    """استبدال الإيموجي القديم بالجديد في النص"""
    for old, new in EMOJI_MAP.items():
        text = text.replace(old, new)
    return text

def format_text(text: str) -> str:
    """
    تنسيق النص كاقتباس حقيقي باستخدام <blockquote> مع الحفاظ على التنسيق الداخلي.
    """
    text = replace_emojis(text)
    # استخدام blockquote حقيقي في HTML
    return f"<blockquote>{text}</blockquote>"

# =================================================================
# ⚡ دالة إرسال متقدمة مع الصورة والاقتباس
# =================================================================
async def send_photo_message(
    chat_id: int,
    text: str,
    parse_mode: str = None,
    reply_markup=None,
    context: ContextTypes.DEFAULT_TYPE = None,
    **kwargs
):
    """إرسال رسالة تحتوي على صورة ثابتة + نص منسق (اقتباس + إيموجي جديد) + أزرار"""
    if context is None:
        logging.error("context is required for send_photo_message")
        return
    try:
        formatted_text = format_text(text)
        # استخدام HTML بشكل افتراضي لعرض الاقتباس
        if parse_mode is None:
            parse_mode = 'HTML'
        # إرسال الصورة مع النص كـ caption والأزرار
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=IMAGE_URL,
            caption=formatted_text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            **kwargs
        )
    except Forbidden:
        alert_text = f"⚠️ تنبيه حظر جديد:\n\n• المستخدم: `{chat_id}`\n• الحالة: قام بحظر البوت."
        for admin_id in ADMINS:
            try: await context.bot.send_message(chat_id=admin_id, text=alert_text, parse_mode="Markdown")
            except: pass
    except Exception as e:
        logging.error(f"Error sending photo message to {chat_id}: {e}")

# =================================================================
# 🛡️ دالة safe_send_message (للرسائل النصية العادية)
# =================================================================
async def safe_send_message(context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str, parse_mode: str = None, reply_markup=None):
    """إرسال رسالة آمنة مع الصورة والاقتباس"""
    try:
        await send_photo_message(user_id, text, parse_mode, reply_markup, context=context)
        return True
    except Forbidden:
        alert_text = f"⚠️ تنبيه حظر جديد:\n\n• المستخدم: `{user_id}`\n• الحالة: قام بحظر البوت."
        for admin_id in ADMINS:
            try: await context.bot.send_message(chat_id=admin_id, text=alert_text, parse_mode="Markdown")
            except: pass
        return None
    except Exception as e:
        logging.error(f"Error sending message to {user_id}: {e}")
        return None

# =================================================================
# باقي الكود الأصلي مع التعديلات الشكلية في كل مكان
# =================================================================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for uid, udata in data.get("users", {}).items():
                    if "sub_expire" in udata and udata["sub_expire"]:
                        udata["sub_expire"] = datetime.fromisoformat(udata["sub_expire"])
                    if "texts" not in udata:
                        old_text = udata.get("text", "")
                        udata["texts"] = [old_text] if old_text else []
                    if "pm_reply_text" not in udata:
                        udata["pm_reply_text"] = "صاحب الحساب مشغول حالياً، أترك رسالتك وسيتم الرد عليك فور تفرغه."
                    if "pm_auto_reply_enabled" not in udata:
                        udata["pm_auto_reply_enabled"] = False
                    if "night_mode_enabled" not in udata:
                        udata["night_mode_enabled"] = False
                    if "night_start" not in udata:
                        udata["night_start"] = None
                    if "night_end" not in udata:
                        udata["night_end"] = None

                ready_groups = data.get("ready_groups", {"super": [], "exchange": [], "other": []})
                custom_start_msg = data.get("custom_start_msg", None)
                star_prices = data.get("star_prices", {"1m": 50, "3m": 100, "6m": 150, "1y": 300})
                buyers = data.get("buyers", [])
                
                return (
                    data.get("users", {}), data.get("codes", {}), data.get("admins", [OWNER_ID]), 
                    data.get("channels", []), ready_groups, custom_start_msg, star_prices, buyers
                )
            except Exception as e:
                logging.error(f"Error loading data: {e}")
    return {}, {}, [OWNER_ID], [], {"super": [], "exchange": [], "other": []}, None, {"1m": 50, "3m": 100, "6m": 150, "1y": 300}, []

def save_data():
    serializable_users = {}
    for uid, udata in USERS_DATA.items():
        serializable_users[str(uid)] = udata.copy()
        if isinstance(serializable_users[str(uid)].get("sub_expire"), datetime):
            serializable_users[str(uid)]["sub_expire"] = serializable_users[str(uid)]["sub_expire"].isoformat()
            
    data = {
        "users": serializable_users,
        "codes": VALID_CODES,
        "admins": ADMINS,
        "channels": REQUIRED_CHANNELS,
        "ready_groups": READY_GROUPS,
        "custom_start_msg": CUSTOM_START_MSG,
        "star_prices": STAR_PRICES,
        "buyers": CODE_BUYERS
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

(USERS_DATA, VALID_CODES, ADMINS, REQUIRED_CHANNELS, 
 READY_GROUPS, CUSTOM_START_MSG, STAR_PRICES, CODE_BUYERS) = load_data()

if OWNER_ID not in ADMINS:
    ADMINS.append(OWNER_ID)
    save_data()

PYRO_SESSIONS = {}
ACTIVE_CLIENTS = {}

def is_subscribed(user_id):
    if int(user_id) in ADMINS:
        return True
    user = USERS_DATA.get(str(user_id)) or USERS_DATA.get(int(user_id), {})
    expire_date = user.get('sub_expire')
    if expire_date:
        if isinstance(expire_date, str):
            expire_date = datetime.fromisoformat(expire_date)
        if datetime.now() < expire_date:
            return True
    return False

async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    if not REQUIRED_CHANNELS or int(user_id) in ADMINS:
        return True
    
    unsubscribed = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ['member', 'creator', 'administrator']:
                unsubscribed.append(ch)
        except Exception:
            unsubscribed.append(ch)
            
    if not unsubscribed:
        return True
        
    keyboard = []
    for idx, ch in enumerate(unsubscribed, start=1):
        clean_ch = ch.replace('https://t.me/', '').replace('t.me/', '').replace('@', '')
        keyboard.append([InlineKeyboardButton(f"📢 اشترك في القناة {idx}", url=f"https://t.me/{clean_ch}")])
    keyboard.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_join", style="success")])
    
    msg = "يجب عليك الاشتراك في قنوات البوت أولاً لاستخدامه!"
    if update.message:
        await send_photo_message(update.effective_chat.id, msg, "HTML", InlineKeyboardMarkup(keyboard), context=context)
    elif update.callback_query:
        await send_photo_message(update.effective_chat.id, msg, "HTML", InlineKeyboardMarkup(keyboard), context=context)
    return False

def get_lang_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🌐 العربية", callback_data="lang_ar", style="danger"),
        InlineKeyboardButton("🌐 English", callback_data="lang_en", style="danger")
    ]])

def get_welcome_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎫 استخدام كود لتفعيل الاشتراك", callback_data="use_code", style="success")],
        [InlineKeyboardButton("🆓 تجربة مجانية ليوم واحد", callback_data="free_trial_confirm_page", style="success")],
        [InlineKeyboardButton("🛒 شراء كود بنجوم ⭐", callback_data="buy_stars_menu", style="success")]
    ])

def get_confirm_keyboard(action_type):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأكيد العملية", callback_data=f"confirm_{action_type}", style="success")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_welcome", style="danger")]
    ])

def get_main_keyboard(user_id):
    user = USERS_DATA.get(str(user_id), {})
    is_running = user.get('is_running', False)
    night_active = user.get('night_mode_enabled', False)

    keyboard = [
        [InlineKeyboardButton("💬 رد الكروبات", callback_data="auto_reply_group_menu", style="primary"),
         InlineKeyboardButton("💬 رد الخاص", callback_data="auto_reply_pm_menu", style="primary")],
        [InlineKeyboardButton("⚙️ إدارة الحسابات", callback_data="manage_accs", style="success"),
         InlineKeyboardButton("📊 الإحصائيات", callback_data="stats", style="danger")],
        [InlineKeyboardButton("⏰ تعديل الوقت", callback_data="edit_time", style="success")],
        [InlineKeyboardButton("📝 إدارة الكلايش", callback_data="manage_texts_menu", style="success")],
        [InlineKeyboardButton("📁 إدارة الكروبات", callback_data="manage_groups_menu", style="success"),
         InlineKeyboardButton("📂 كروبات جاهزة", callback_data="ready_groups_menu", style="primary")],
        [InlineKeyboardButton("🚀 بدء النشر" if not is_running else "⏳ النشر يعمل حالياً", callback_data="start_post", style="success"),
         InlineKeyboardButton("⏹️ توقيف النشر", callback_data="stop_post", style="danger")],
        [InlineKeyboardButton("🔐 معلومات الاشتراك", callback_data="sub_info", style="primary")],
        [InlineKeyboardButton("🌜 وضع راحة الليلية" if not night_active else "🌜 وضع الراحة (مُفعل)", callback_data="night_sleep_mode", style="success"),
         InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEVELOPER_USER.replace('@','')}", style="danger")],
        [InlineKeyboardButton("📡 قناة السورس", url=f"https://t.me/{SOURCE_CHANNEL.replace('@','')}", style="danger")],
    ]
    if int(user_id) in ADMINS:
        keyboard.append([InlineKeyboardButton("🎛️ لوحة التحكم الإدارية", callback_data="admin_panel", style="success")])
    return InlineKeyboardMarkup(keyboard)

def get_pm_reply_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تفعيل الرد الخاص", callback_data="enable_pm_reply", style="success"),
         InlineKeyboardButton("❌ تعطيل الرد الخاص", callback_data="disable_pm_reply", style="danger")],
        [InlineKeyboardButton("✏️ تعديل كليشة رد الخاص", callback_data="edit_pm_reply_text", style="primary")],
        [InlineKeyboardButton("📣 إذاعة في الخاص", callback_data="user_pm_broadcast", style="success")],
        [InlineKeyboardButton("🔙 رجوع لقائمة الرئيسية", callback_data="back_main", style="danger")]
    ])

def get_texts_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة كليشة جديدة", callback_data="add_text", style="success")],
        [InlineKeyboardButton("📋 عرض وتصدير الكلايش", callback_data="view_texts", style="primary")],
        [InlineKeyboardButton("🗑️ مسح جميع الكلايش", callback_data="clear_all_texts", style="danger")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])

def get_groups_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة كروب يدوي", callback_data="add_group_manual", style="primary")],
        [InlineKeyboardButton("📂 جلب كروبات الحساب", callback_data="list_account_groups_0", style="primary")],
        [InlineKeyboardButton("📂 كروبات جاهزة", callback_data="ready_groups_menu")],
        [InlineKeyboardButton("📋 عرض المجموعات المضافة", callback_data="view_groups", style="primary")],
        [InlineKeyboardButton("🗑️ مسح جميع المجموعات", callback_data="clear_all_groups", style="danger")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])

def get_ready_groups_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 كروبات السوبر", callback_data="view_ready_cat_super", style="success")],
        [InlineKeyboardButton("🔄 كروبات التبادل", callback_data="view_ready_cat_exchange", style="success")],
        [InlineKeyboardButton("📁 كروبات اخرى", callback_data="view_ready_cat_other", style="success")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])

def get_admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎫 إنشاء كود اشتراك", callback_data="adm_gen_code", style="success"),
         InlineKeyboardButton("🔐 معلومات الاشتراك الكود", callback_data="adm_code_info", style="success")],
        [InlineKeyboardButton("➕ إضافة اشتراك يدوي", callback_data="adm_add_sub_manual", style="success"),
         InlineKeyboardButton("➖ مسح اشتراك يدوي", callback_data="adm_delete_sub_manual", style="danger")],
        [InlineKeyboardButton("📈 إحصائيات البوت", callback_data="adm_bot_stats", style="danger"),
         InlineKeyboardButton("⚙️ التحكم في رسالة /start", callback_data="adm_start_msg_menu", style="primary")],
        [InlineKeyboardButton("⭐ أسعار الكود بالنجوم", callback_data="adm_star_prices_menu", style="success"),
         InlineKeyboardButton("🛍️ قائمة مشترين الكود", callback_data="adm_view_buyers", style="primary")],
        [InlineKeyboardButton("📂 إدارة الكروبات الجاهزة", callback_data="adm_ready_groups_menu", style="primary"),
         InlineKeyboardButton("📢 الاشتراك الإجباري", callback_data="adm_force_sub_menu", style="primary")],
        [InlineKeyboardButton("🛡️ قسم الأدمنية", callback_data="adm_admins_menu", style="primary"),
         InlineKeyboardButton("✏️ تعديل الحقوق (يوزر/سورس)", callback_data="adm_edit_rights", style="success")],
        [InlineKeyboardButton("📣 إذاعة للمستخدمين", callback_data="broadcast", style="success")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_main", style="danger")]
    ])

def get_admin_sub_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة قناة", callback_data="ch_add", style="success")],
        [InlineKeyboardButton("➖ حذف قناة", callback_data="ch_del", style="danger")],
        [InlineKeyboardButton("📋 عرض القنوات", callback_data="ch_view", style="primary")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ])

def get_admin_manage_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة أدمن", callback_data="admin_add", style="success")],
        [InlineKeyboardButton("➖ مسح أدمن", callback_data="admin_del", style="danger")],
        [InlineKeyboardButton("📋 عرض الأدمنية", callback_data="admin_view", style="primary")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ])

def get_admin_ready_groups_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة كروب جديد", callback_data="adm_add_ready_group", style="success")],
        [InlineKeyboardButton("🗑️ عرض وحذف الكروبات", callback_data="adm_view_ready_groups", style="danger")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ])

# =================================================================
# 🔄 قسم الرد التلقائي الفوري (للمجموعات وللخاص)
# =================================================================
def register_session_reply_handler(client: Client, user_id: str):
    @client.on_message(pyro_filters.group & pyro_filters.reply)
    async def session_auto_reply_handler(bot_client: Client, message: Message):
        try:
            me = await bot_client.get_me()
            if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id:
                user_data = USERS_DATA.get(str(user_id), {})
                auto_replies = user_data.get('auto_replies', {})
                msg_text = message.text.strip() if message.text else ""
                replied_post_text = message.reply_to_message.text or ""
                
                matched = False
                for key, data in auto_replies.items():
                    if msg_text == key or key == "*":
                        target_text_idx = data.get("text_index", "all")
                        if target_text_idx != "all":
                            try:
                                target_idx = int(target_text_idx)
                                user_texts = user_data.get('texts', [])
                                if 0 <= target_idx < len(user_texts):
                                    if user_texts[target_idx] not in replied_post_text:
                                        continue
                            except ValueError:
                                pass
                        
                        reply_content = data.get("reply", "")
                        if reply_content:
                            await message.reply_text(reply_content)
                            matched = True
                            break
                
                if not matched and "*" in auto_replies:
                    default_reply = auto_replies["*"].get("reply", "")
                    if default_reply:
                        await message.reply_text(default_reply)
        except Exception as e:
            logging.error(f"Error in group auto reply: {e}")

    @client.on_message(pyro_filters.private & ~pyro_filters.me)
    async def session_pm_auto_reply_handler(bot_client: Client, message: Message):
        try:
            if not message.from_user or message.from_user.is_bot:
                return

            user_data = USERS_DATA.get(str(user_id), {})
            if not user_data.get('pm_auto_reply_enabled', False):
                return
                
            pm_text = user_data.get('pm_reply_text', 'صاحب الحساب مشغول حالياً، أترك رسالتك وسيتم الرد عليك فور تفرغه.')
            target_user_id = message.from_user.id
            key = f"{user_id}_{target_user_id}"
            now = datetime.now()

            if key not in PM_CONVERSATIONS:
                if pm_text:
                    await message.reply_text(pm_text)
                PM_CONVERSATIONS[key] = {
                    'start_time': now,
                    'first_reply_sent': True,
                    'three_min_alert_sent': False
                }
            else:
                conv = PM_CONVERSATIONS[key]
                if not conv['three_min_alert_sent']:
                    if now - conv['start_time'] >= timedelta(minutes=3):
                        await message.reply_text("شكراً لاستمرار تواصلك، أرجو الانتظار سيتم الرد عليك قريباً من صاحب الحساب.")
                        conv['three_min_alert_sent'] = True
        except Exception as e:
            logging.error(f"Error in PM auto reply handler: {e}")

async def start_user_clients(user_id: str):
    user = USERS_DATA.get(str(user_id), {})
    accounts = user.get('accounts', [])
    
    for acc in accounts:
        phone = str(acc['phone'])
        if phone not in ACTIVE_CLIENTS:
            session_path = os.path.join(SESSION_DIR, phone)
            client = Client(name=session_path, api_id=API_ID, api_hash=API_HASH)
            try:
                await client.start()
                register_session_reply_handler(client, str(user_id))
                ACTIVE_CLIENTS[phone] = client
            except Exception as e:
                logging.error(f"Error starting client for {phone}: {e}")

async def user_pm_broadcast_worker(user_id: str, broadcast_text: str, context: ContextTypes.DEFAULT_TYPE):
    user = USERS_DATA.get(str(user_id), {})
    accounts = user.get('accounts', [])
    
    if not accounts:
        await safe_send_message(context, int(user_id), "لا توجد حسابات مضافة للقيام بالإذاعة في الخاص.", parse_mode="HTML")
        return

    await safe_send_message(context, int(user_id), "جاري البدء بالإذاعة في المحادثات الخاصة للحسابات...", parse_mode="HTML")

    total_sent = 0
    total_failed = 0

    for acc in accounts:
        phone = str(acc['phone'])
        client = ACTIVE_CLIENTS.get(phone)
        
        if not client or not client.is_connected:
            session_path = os.path.join(SESSION_DIR, phone)
            client = Client(name=session_path, api_id=API_ID, api_hash=API_HASH)
            try:
                await client.start()
                register_session_reply_handler(client, str(user_id))
                ACTIVE_CLIENTS[phone] = client
            except Exception as e:
                logging.error(f"Failed to connect client {phone} for broadcast: {e}")
                continue

        try:
            async for dialog in client.get_dialogs():
                chat_type = str(dialog.chat.type).lower()
                if "private" in chat_type or "user" in chat_type:
                    if dialog.chat.is_self or dialog.chat.is_support:
                        continue
                    try:
                        await client.send_message(chat_id=dialog.chat.id, text=broadcast_text)
                        total_sent += 1
                        await asyncio.sleep(1.5)
                    except FloodWait as fw:
                        await asyncio.sleep(fw.value)
                        try:
                            await client.send_message(chat_id=dialog.chat.id, text=broadcast_text)
                            total_sent += 1
                        except:
                            total_failed += 1
                    except Exception:
                        total_failed += 1
        except Exception as e:
            logging.error(f"Broadcast error on account {phone}: {e}")

    await safe_send_message(
        context,
        int(user_id),
        f"اكتمال الإذاعة في الخاص!\n\nالرسائل الناجحة: `{total_sent}`\nالرسائل الفاشلة: `{total_failed}`",
        parse_mode="HTML"
    )

async def posting_worker(user_id, context: ContextTypes.DEFAULT_TYPE):
    str_user_id = str(user_id)
    
    while True:
        user = USERS_DATA.get(str_user_id)
        if not user or not user.get('is_running', False):
            break

        # فحص وضع الراحة الليلية
        if user.get('night_mode_enabled', False):
            now_hour = datetime.now().hour
            start_h = user.get('night_start')
            end_h = user.get('night_end')
            
            if start_h is not None and end_h is not None:
                is_night = False
                if start_h > end_h:
                    if now_hour >= start_h or now_hour < end_h:
                        is_night = True
                else:
                    if start_h <= now_hour < end_h:
                        is_night = True
                        
                if is_night:
                    await asyncio.sleep(60)
                    continue

        accounts = user.get('accounts', [])
        groups = user.get('groups', [])
        texts = user.get('texts', [])
        interval = user.get('interval', 30)

        if not accounts or not groups or not texts:
            user['is_running'] = False
            save_data()
            await safe_send_message(
                context,
                int(user_id),
                "تم إيقاف النشر تلقائياً بسبب نقص البيانات (الحسابات، المجموعات، أو الكلايش).",
                parse_mode="HTML"
            )
            break

        for acc in list(accounts):
            if not user.get('is_running', False):
                break

            phone = str(acc['phone'])
            client = ACTIVE_CLIENTS.get(phone)
            
            if not client or not client.is_connected:
                session_path = os.path.join(SESSION_DIR, phone)
                client = Client(name=session_path, api_id=API_ID, api_hash=API_HASH)
                try:
                    await client.start()
                    register_session_reply_handler(client, str_user_id)
                    ACTIVE_CLIENTS[phone] = client
                except Exception as e:
                    logging.error(f"Client connection error for {phone}: {e}")
                    continue

            try:
                for group in list(groups):
                    if not user.get('is_running', False):
                        break

                    target_chat = str(group).strip()
                    
                    if "t.me/+" in target_chat or "t.me/joinchat/" in target_chat:
                        try:
                            chat_obj = await client.join_chat(target_chat)
                            target_chat = chat_obj.id
                        except Exception:
                            continue
                    elif "t.me/" in target_chat:
                        target_chat = "@" + target_chat.split("t.me/")[1].replace("/", "")
                    elif target_chat.lstrip('-').isdigit():
                        target_chat = int(target_chat)

                    for text_to_send in texts:
                        if not user.get('is_running', False):
                            break
                        try:
                            await client.send_message(chat_id=target_chat, text=text_to_send)
                            await asyncio.sleep(1)
                        except FloodWait as fw:
                            await asyncio.sleep(fw.value)
                        except UserNotParticipant:
                            try:
                                await client.join_chat(target_chat)
                                await client.send_message(chat_id=target_chat, text=text_to_send)
                            except Exception:
                                pass
                        except Exception:
                            pass

            except Exception as e:
                logging.error(f"Posting error for {phone}: {e}")

        for _ in range(int(interval)):
            if not USERS_DATA.get(str_user_id, {}).get('is_running', False):
                break
            await asyncio.sleep(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name
    username = f"@{update.effective_user.username}" if update.effective_user.username else "لا يوجد"
    
    if not await check_force_join(update, context, int(user_id)): return

    if user_id not in USERS_DATA:
        USERS_DATA[user_id] = {
            'lang': None, 'sub_expire': datetime.now(),
            'accounts': [], 'groups': [], 'texts': [], 'interval': 30, 
            'is_running': False, 'auto_replies': {},
            'pm_reply_text': "صاحب الحساب مشغول حالياً، أترك رسالتك وسيتم الرد عليك فور تفرغه.",
            'pm_auto_reply_enabled': False,
            'night_mode_enabled': False,
            'night_start': None,
            'night_end': None
        }
        save_data()
        
        alert_msg = f"دخول مستخدم جديد للبوت:\n\nالاسم: {first_name}\nالآيدي: `{user_id}`\nاليوزر: {username}"
        await safe_send_message(context, OWNER_ID, alert_msg, parse_mode="HTML")
            
        await send_photo_message(update.effective_chat.id, "الرجاء اختيار اللغة / Language:", "HTML", get_lang_keyboard(), context=context)
    else:
        USERS_DATA[user_id]['is_running'] = False
        asyncio.create_task(start_user_clients(user_id))
        await show_appropriate_menu(update, context, int(user_id))

async def show_appropriate_menu(update, context, user_id):
    if not is_subscribed(user_id):
        msg = (
            "عذراً، لا يمكنك استخدام مميزات البوت، يجب تفعيل اشتراكك أولاً.\n\n"
            f"تواصل مع المطور: {DEVELOPER_USER}\n"
            "أو استخدم كود تفعيل:\n"
            f"لمعرفة اسعار اشتراكات البوت: {SOURCE_CHANNEL}"
        )
        if update.message: 
            await send_photo_message(update.effective_chat.id, msg, "HTML", get_welcome_keyboard(), context=context)
        elif update.callback_query: 
            await send_photo_message(update.effective_chat.id, msg, "HTML", get_welcome_keyboard(), context=context)
    else:
        msg = CUSTOM_START_MSG if CUSTOM_START_MSG else "قائمة التحكم الرئيسية:"
        p_mode = "HTML"  # استخدام HTML لجميع الرسائل
        if update.message: 
            await send_photo_message(update.effective_chat.id, msg, p_mode, get_main_keyboard(user_id), context=context)
        elif update.callback_query: 
            await send_photo_message(update.effective_chat.id, msg, p_mode, get_main_keyboard(user_id), context=context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DEVELOPER_USER, SOURCE_CHANNEL, CUSTOM_START_MSG
    query = update.callback_query
    
    # تأكد من وجود بيانات callback
    if not query or not query.data:
        logging.warning("Callback query with no data received")
        return

    data = query.data
    logging.info(f"Callback data received: {data}")
    
    try:
        await query.answer()
    except Exception as e:
        logging.error(f"Error answering callback query: {e}")

    user_id = str(query.from_user.id)

    if data == "check_join":
        subscribed = await check_force_join(update, context, int(user_id))
        if subscribed:
            await query.answer("✅ تم التحقق بنجاح! تم اشتراكك في القنوات.", show_alert=True)
            try: await query.message.delete()
            except Exception: pass
            await show_appropriate_menu(update, context, int(user_id))
        else:
            await query.answer("❌ لم تشترك في جميع القنوات بعد، يرجى الاشتراك ثم الضغط مجدداً.", show_alert=True)
        return

    user = USERS_DATA.setdefault(user_id, {
        'lang': 'ar', 'sub_expire': datetime.now(), 
        'accounts': [], 'groups': [], 'texts': [], 'interval': 30, 
        'is_running': False, 'auto_replies': {},
        'pm_reply_text': "صاحب الحساب مشغول حالياً، أترك رسالتك وسيتم الرد عليك فور تفرغه.", 
        'pm_auto_reply_enabled': False,
        'night_mode_enabled': False,
        'night_start': None,
        'night_end': None
    })

    # دالة مساعدة لتعديل caption الصورة مع الحفاظ على الأزرار
    async def edit_caption(text, reply_markup=None, parse_mode="HTML"):
        try:
            await query.edit_message_caption(
                caption=format_text(text),
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Error editing caption: {e}")

    if data.startswith("lang_"):
        user['lang'] = data.split("_")[1]
        save_data()
        await query.message.delete()
        await show_appropriate_menu(update, context, int(user_id))
        return

    if data == "free_trial_confirm_page":
        await edit_caption(
            "هل أنت متأكد من تفعيل التجربة المجانية لمدة يوم واحد؟",
            get_confirm_keyboard("free_trial")
        )
    elif data == "confirm_free_trial":
        user['sub_expire'] = datetime.now() + timedelta(days=1)
        save_data()
        await edit_caption(
            "تم تفعيل التجربة المجانية لمدة يوم واحد بنجاح!",
            get_main_keyboard(int(user_id))
        )
    elif data == "use_code":
        await edit_caption(
            "أرسل كود الاشتراك الخاص بك أو اضغط رجوع:",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_welcome")]])
        )
        context.user_data['action'] = 'entering_code'
    elif data in ["back_to_welcome", "back_main"]:
        context.user_data['action'] = None
        await query.message.delete()
        await show_appropriate_menu(update, context, int(user_id))

    # =================================================================
    # 🌙 قسم وضع الراحة الليلية (المطور والمنسق)
    # =================================================================
    elif data == "night_sleep_mode":
        has_acc = len(user.get('accounts', [])) > 0
        start_h = user.get('night_start')
        end_h = user.get('night_end')
        has_time = (start_h is not None) and (end_h is not None)
        
        status_txt = "معطل ❌" if not user.get('night_mode_enabled', False) else "شغال ✅"
        time_txt = f"من الساعة {start_h}:00 الى {end_h}:00" if has_time else "غير محدد"
        
        msg = (
            "🌙 وضع الراحة الليلية\n\n"
            "يمكنك اختيار وقت توقيف النشر ووقت الذي يعود فيه النشر.\n\n"
            f"حالة القسم: {status_txt}\n"
            f"وقت التوقيف واستئناف: {time_txt}"
        )
        
        kb = [
            [InlineKeyboardButton("⏰ تحديد وقت توقيف النشر", callback_data="night_set_start", style="success")],
            [InlineKeyboardButton("⏰ الوقت الذي يعود فيه النشر", callback_data="night_set_end", style="success")],
            [InlineKeyboardButton("✅ تفعيل" if not user.get('night_mode_enabled') else "❌ تعطيل", callback_data="night_toggle", style="danger")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
        ]
        await edit_caption(msg, InlineKeyboardMarkup(kb))

    elif data in ["night_set_start", "night_set_end"]:
        # قيد الأمان: اشتراط وجود حساب قبل تحديد الوقت
        if not user.get('accounts'):
            await query.answer("⚠️ لا يمكنك إعداد وضع الراحة الليلية! يجب عليك إضافة حساب أولاً.", show_alert=True)
            return
            
        target = "start" if data == "night_set_start" else "end"
        title = "تحديد وقت توقيف النشر (بالساعة 0-23):" if target == "start" else "تحديد الوقت الذي يعود فيه النشر (بالساعة 0-23):"
        
        buttons = []
        for h in range(24):
            buttons.append(InlineKeyboardButton(f"{h:02d}:00", callback_data=f"night_save_{target}_{h}"))
        
        kb_grid = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
        kb_grid.append([InlineKeyboardButton("🔙 رجوع", callback_data="night_sleep_mode")])
        
        await edit_caption(f"{title}", InlineKeyboardMarkup(kb_grid))

    elif data.startswith("night_save_"):
        parts = data.split("_")
        target = parts[2]
        hour = int(parts[3])
        
        if target == "start": user['night_start'] = hour
        else: user['night_end'] = hour
        
        save_data()
        await query.answer("تم حفظ التوقيت بنجاح!", show_alert=False)
        
        # إعادة التوجيه لقائمة الوضع الليلي
        has_time = (user.get('night_start') is not None) and (user.get('night_end') is not None)
        status_txt = "معطل ❌" if not user.get('night_mode_enabled', False) else "شغال ✅"
        time_txt = f"من الساعة {user.get('night_start')}:00 الى {user.get('night_end')}:00" if has_time else "غير محدد"
        
        msg = (
            "🌙 وضع الراحة الليلية\n\n"
            "يمكنك اختيار وقت توقيف النشر ووقت الذي يعود فيه النشر.\n\n"
            f"حالة القسم: {status_txt}\n"
            f"وقت التوقيف واستئناف: {time_txt}"
        )
        
        kb = [
            [InlineKeyboardButton("⏰ تحديد وقت توقيف النشر", callback_data="night_set_start")],
            [InlineKeyboardButton("⏰ الوقت الذي يعود فيه النشر", callback_data="night_set_end")],
            [InlineKeyboardButton("✅ تفعيل" if not user.get('night_mode_enabled') else "❌ تعطيل", callback_data="night_toggle")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
        ]
        await edit_caption(msg, InlineKeyboardMarkup(kb))

    elif data == "night_toggle":
        # قيود الأمان المشروطة: حساب + تحديد الوقت
        if not user.get('accounts'):
            await query.answer("❌ يجب عليك إضافة حساب أولاً لتفعيل وضع الراحة الليلية!", show_alert=True)
            return
            
        if user.get('night_start') is None or user.get('night_end') is None:
            await query.answer("❌ يرجى تحديد وقت توقيف النشر ووقت استئنافه أولاً!", show_alert=True)
            return

        user['night_mode_enabled'] = not user.get('night_mode_enabled', False)
        save_data()
        
        status_msg = "تم تفعيل وضع الراحة الليلية" if user['night_mode_enabled'] else "تم تعطيل وضع الراحة الليلية"
        await query.answer(status_msg, show_alert=True)
        
        has_time = (user.get('night_start') is not None) and (user.get('night_end') is not None)
        status_txt = "معطل ❌" if not user.get('night_mode_enabled', False) else "شغال ✅"
        time_txt = f"من الساعة {user.get('night_start')}:00 الى {user.get('night_end')}:00" if has_time else "غير محدد"
        
        msg = (
            "🌙 وضع الراحة الليلية\n\n"
            "يمكنك اختيار وقت توقيف النشر ووقت الذي يعود فيه النشر.\n\n"
            f"حالة القسم: {status_txt}\n"
            f"وقت التوقيف واستئناف: {time_txt}"
        )
        
        kb = [
            [InlineKeyboardButton("⏰ تحديد وقت توقيف النشر", callback_data="night_set_start")],
            [InlineKeyboardButton("⏰ الوقت الذي يعود فيه النشر", callback_data="night_set_end")],
            [InlineKeyboardButton("✅ تفعيل" if not user.get('night_mode_enabled') else "❌ تعطيل", callback_data="night_toggle")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
        ]
        await edit_caption(msg, InlineKeyboardMarkup(kb))

    # =================================================================
    # ⭐️ قسم شراء كود بالنجوم للمستخدمين
    # =================================================================
    elif data == "buy_stars_menu":
        p1 = STAR_PRICES.get("1m", 50)
        p3 = STAR_PRICES.get("3m", 100)
        p6 = STAR_PRICES.get("6m", 150)
        p12 = STAR_PRICES.get("1y", 300)
        
        msg = "⭐ اختر مدة الاشتراك لشراء الكود بالنجوم:"
        kb = [
            [InlineKeyboardButton(f"📅 شهر واحد - ⭐ {p1}", callback_data="buy_plan_1m")],
            [InlineKeyboardButton(f"📅 3 أشهر - ⭐ {p3}", callback_data="buy_plan_3m")],
            [InlineKeyboardButton(f"📅 6 أشهر - ⭐ {p6}", callback_data="buy_plan_6m")],
            [InlineKeyboardButton(f"📅 سنة كاملة - ⭐ {p12}", callback_data="buy_plan_1y")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_welcome")]
        ]
        await edit_caption(msg, InlineKeyboardMarkup(kb))

    elif data.startswith("buy_plan_"):
        plan = data.replace("buy_plan_", "")
        plans_info = {
            "1m": ("اشتراك شهر واحد", STAR_PRICES.get("1m", 50), 30),
            "3m": ("اشتراك 3 أشهر", STAR_PRICES.get("3m", 100), 90),
            "6m": ("اشتراك 6 أشهر", STAR_PRICES.get("6m", 150), 180),
            "1y": ("اشتراك سنة كاملة", STAR_PRICES.get("1y", 300), 365),
        }
        
        if plan in plans_info:
            title, price, days = plans_info[plan]
            prices = [LabeledPrice(title, price)]
            payload = f"stars_code_{plan}_{days}_{price}_{query.from_user.id}"
            
            await context.bot.send_invoice(
                chat_id=query.from_user.id,
                title=f"شراء كود {title}",
                description=f"احصل على كود تفعيل تلقائي لمدة {days} يوم بالنجوم",
                payload=payload,
                provider_token="", # فارغ لنجوم تليجرام
                currency="XTR",
                prices=prices
            )
            await query.answer("تم إرسال فاتورة الشراء بالنجوم لك!", show_alert=False)

    # =================================================================
    # 👑 لوحة تحكم الأدمن والخيارات الجديدة
    # =================================================================
    elif data == "admin_panel" and int(user_id) in ADMINS:
        await edit_caption("لوحة التحكم الإدارية والتحكم الكامل:", get_admin_keyboard())

    elif data == "adm_star_prices_menu" and int(user_id) in ADMINS:
        msg = (
            "⚙️ التحكم بأسعار النجوم:\n\n"
            f"• 1 شهر: ⭐ {STAR_PRICES.get('1m', 50)}\n"
            f"• 3 أشهر: ⭐ {STAR_PRICES.get('3m', 100)}\n"
            f"• 6 أشهر: ⭐ {STAR_PRICES.get('6m', 150)}\n"
            f"• سنة: ⭐ {STAR_PRICES.get('1y', 300)}\n\n"
            "اضغط على الباقة التي ترغب بتعديل سعرها:"
        )
        kb = [
            [InlineKeyboardButton("تعديل سعر شهر", callback_data="adm_edit_price_1m", style="primary"),
             InlineKeyboardButton("تعديل سعر 3 أشهر", callback_data="adm_edit_price_3m", style="primary")],
            [InlineKeyboardButton("تعديل سعر 6 أشهر", callback_data="adm_edit_price_6m", style="primary"),
             InlineKeyboardButton("تعديل سعر سنة", callback_data="adm_edit_price_1y", style="primary")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
        ]
        await edit_caption(msg, InlineKeyboardMarkup(kb))

    elif data.startswith("adm_edit_price_") and int(user_id) in ADMINS:
        p_key = data.replace("adm_edit_price_", "")
        context.user_data['target_price_key'] = p_key
        context.user_data['action'] = 'adm_setting_star_price'
        await edit_caption(
            f"أرسل السعر الجديد بالنجوم للباقة المختارة (`{p_key}`):",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="adm_star_prices_menu", style="danger")]])
        )

    elif data == "adm_view_buyers" and int(user_id) in ADMINS:
        if not CODE_BUYERS:
            await edit_caption(
                "لا يوجد مشترين للكود بالنجوم حتى الآن.",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]])
            )
            return

        kb = []
        for idx, b in enumerate(CODE_BUYERS):
            btn_txt = f"🧑 {b.get('user_id')} | {b.get('plan')} | ⭐ {b.get('stars')}"
            kb.append([
                InlineKeyboardButton(btn_txt, callback_data=f"adm_buyer_info_{idx}"),
                InlineKeyboardButton("🗑️ حذف", callback_data=f"adm_del_buyer_{idx}", style="danger")
            ])
        kb.append([InlineKeyboardButton("🗑️ مسح كافة السجلات", callback_data="adm_clear_all_buyers", style="danger")])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")])
        
        await edit_caption(
            f"🛍️ قائمة مشترين الكود بالنجوم ({len(CODE_BUYERS)}):",
            InlineKeyboardMarkup(kb)
        )

    elif data.startswith("adm_buyer_info_") and int(user_id) in ADMINS:
        idx = int(data.replace("adm_buyer_info_", ""))
        if 0 <= idx < len(CODE_BUYERS):
            b = CODE_BUYERS[idx]
            info = (
                "📑 تفاصيل عملية الشراء:\n\n"
                f"• المستخدم: `{b.get('user_id')}`\n"
                f"• الكود المكتسب: `{b.get('code')}`\n"
                f"• الباقة: `{b.get('plan')}`\n"
                f"• النجوم المدفوعة: ⭐ `{b.get('stars')}`\n"
                f"• التاريخ: `{b.get('date')}`"
            )
            await query.answer(format_text(info), show_alert=True)

    elif data.startswith("adm_del_buyer_") and int(user_id) in ADMINS:
        idx = int(data.replace("adm_del_buyer_", ""))
        if 0 <= idx < len(CODE_BUYERS):
            CODE_BUYERS.pop(idx)
            save_data()
            await query.answer("تم حذف السجل بنجاح", show_alert=True)
            
        if not CODE_BUYERS:
            await edit_caption(
                "لا يوجد مشترين للكود بالنجوم حتى الآن.",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]])
            )
        else:
            kb = []
            for i, b in enumerate(CODE_BUYERS):
                btn_txt = f"🧑 {b.get('user_id')} | {b.get('plan')} | ⭐ {b.get('stars')}"
                kb.append([
                    InlineKeyboardButton(btn_txt, callback_data=f"adm_buyer_info_{i}"),
                    InlineKeyboardButton("🗑️ حذف", callback_data=f"adm_del_buyer_{i}")
                ])
            kb.append([InlineKeyboardButton("🗑️ مسح كافة السجلات", callback_data="adm_clear_all_buyers")])
            kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")])
            await edit_caption(
                f"🛍️ قائمة مشترين الكود بالنجوم ({len(CODE_BUYERS)}):",
                InlineKeyboardMarkup(kb)
            )

    elif data == "adm_clear_all_buyers" and int(user_id) in ADMINS:
        CODE_BUYERS.clear()
        save_data()
        await edit_caption(
            "تم مسح كافة سجلات المشترين بنجاح.",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]])
        )

    elif data == "adm_gen_code" and int(user_id) in ADMINS:
        await edit_caption(
            "أرسل مدة الكود بالأيام (مثال: 30):",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel")]])
        )
        context.user_data['action'] = 'adm_code_days'

    elif data == "adm_code_info" and int(user_id) in ADMINS:
        await edit_caption(
            "أرسل كود الاشتراك للتحقق من معلوماته:",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel")]])
        )
        context.user_data['action'] = 'adm_check_code_info'

    elif data == "adm_add_sub_manual" and int(user_id) in ADMINS:
        await edit_caption(
            "أرسل آيدي المستخدم المراد تفعيل اشتراكه:",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel")]])
        )
        context.user_data['action'] = 'adm_manual_id'

    elif data == "adm_delete_sub_manual" and int(user_id) in ADMINS:
        await edit_caption(
            "أرسل آيدي المستخدم المراد مسح/إلغاء اشتراكه اليدوي:",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel")]])
        )
        context.user_data['action'] = 'adm_del_sub_id'

    elif data == "adm_bot_stats" and int(user_id) in ADMINS:
        total_users = len(USERS_DATA)
        active_subs = sum(1 for u in USERS_DATA.values() if is_subscribed(list(USERS_DATA.keys())[list(USERS_DATA.values()).index(u)]))
        total_accs = sum(len(u.get('accounts', [])) for u in USERS_DATA.values())
        total_codes = len(VALID_CODES)
        
        stats_msg = (
            "📈 إحصائيات البوت الإدارية:\n\n"
            f"🧑 إجمالي المستخدِمين: `{total_users}`\n"
            f"✨ الاشتراكات النشطة: `{active_subs}`\n"
            f"📲 الحسابات المربوطة الكلية: `{total_accs}`\n"
            f"🔐 الكودات الفعالة المتوفرة: `{total_codes}`\n"
            f"🛍️ إجمالي مبيعات النجوم: `{len(CODE_BUYERS)}`"
        )
        await edit_caption(
            stats_msg,
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]])
        )

    elif data == "adm_start_msg_menu" and int(user_id) in ADMINS:
        kb = [
            [InlineKeyboardButton("✏️ تعيين نص جديد لـ /start", callback_data="adm_set_start_msg", style="primary")],
            [InlineKeyboardButton("🔄 إعادة النص الافتراضي", callback_data="adm_reset_start_msg", style="success")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
        ]
        curr_msg = CUSTOM_START_MSG if CUSTOM_START_MSG else "النص الافتراضي"
        await edit_caption(
            f"إعدادات رسالة /start:\n\nالنص الحالي:\n{curr_msg}",
            InlineKeyboardMarkup(kb)
        )

    elif data == "adm_set_start_msg" and int(user_id) in ADMINS:
        info_msg = "أرسل نص رسالة /start الجديد الآن مع التنسيقات المفضلة:"
        await edit_caption(
            info_msg,
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="adm_start_msg_menu")]])
        )
        context.user_data['action'] = 'adm_waiting_start_text'

    elif data == "adm_reset_start_msg" and int(user_id) in ADMINS:
        CUSTOM_START_MSG = None
        save_data()
        await query.answer("تم إعادة رسالة /start للوضع الافتراضي", show_alert=True)
        await edit_caption(
            "تم ضبط النص الافتراضي بنجاح!",
            get_admin_keyboard()
        )

    elif data == "broadcast" and int(user_id) in ADMINS:
        await edit_caption(
            "أرسل النشرة/الرسالة المراد إرسالها لكافة المستخدمين:",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel")]])
        )
        context.user_data['action'] = 'adm_broadcast'

    elif data == "adm_force_sub_menu" and int(user_id) in ADMINS:
        await edit_caption(
            "قسم إدارة الاشتراك الإجباري:",
            get_admin_sub_menu()
        )

    elif data == "ch_add" and int(user_id) in ADMINS:
        await edit_caption(
            "أرسل معرف القناة الآن (مثال: @uut4u):",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="adm_force_sub_menu")]])
        )
        context.user_data['action'] = 'adm_add_ch'

    elif data == "ch_view" and int(user_id) in ADMINS:
        chs = "\n".join(REQUIRED_CHANNELS) if REQUIRED_CHANNELS else "لا توجد قنوات مضافة"
        await edit_caption(
            f"قنوات الاشتراك الإجباري:\n\n{chs}",
            get_admin_sub_menu()
        )

    elif data == "ch_del" and int(user_id) in ADMINS:
        if not REQUIRED_CHANNELS:
            await edit_caption(
                "لا توجد قنوات لحذفها.",
                get_admin_sub_menu()
            )
            return
        kb = [[InlineKeyboardButton(f"🗑️ حذف {ch}", callback_data=f"del_ch_{ch}")] for ch in REQUIRED_CHANNELS]
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="adm_force_sub_menu")])
        await edit_caption(
            "اختر القناة المراد حذفها:",
            InlineKeyboardMarkup(kb)
        )

    elif data.startswith("del_ch_") and int(user_id) in ADMINS:
        target_ch = data.replace("del_ch_", "")
        if target_ch in REQUIRED_CHANNELS:
            REQUIRED_CHANNELS.remove(target_ch)
            save_data()
            await query.answer("تم حذف القناة بنجاح", show_alert=True)
        await edit_caption(
            "قسم إدارة الاشتراك الإجباري:",
            get_admin_sub_menu()
        )

    elif data == "adm_admins_menu" and int(user_id) in ADMINS:
        await edit_caption(
            "قسم التحكم بالأدمنية:",
            get_admin_manage_menu()
        )

    elif data == "admin_add" and int(user_id) in ADMINS:
        await edit_caption(
            "أرسل آيدي الشخص المراد ترقيته إلى أدمن:",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="adm_admins_menu")]])
        )
        context.user_data['action'] = 'adm_add_admin_id'

    elif data == "admin_view" and int(user_id) in ADMINS:
        admins_str = "\n".join([f"• `{a}`" for a in ADMINS])
        await edit_caption(
            f"قائمة الأدمنية:\n\n{admins_str}",
            get_admin_manage_menu()
        )

    elif data == "admin_del" and int(user_id) in ADMINS:
        kb = [[InlineKeyboardButton(f"🗑️ حذف {a}", callback_data=f"del_adm_{a}")] for a in ADMINS if a != OWNER_ID]
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="adm_admins_menu")])
        await edit_caption(
            "اختر الأدمن المراد حذفه:",
            InlineKeyboardMarkup(kb)
        )

    elif data.startswith("del_adm_") and int(user_id) in ADMINS:
        target_a = int(data.replace("del_adm_", ""))
        if target_a in ADMINS and target_a != OWNER_ID:
            ADMINS.remove(target_a)
            save_data()
            await query.answer("تم حذف الأدمن بنجاح", show_alert=True)
        await edit_caption(
            "قسم التحكم بالأدمنية:",
            get_admin_manage_menu()
        )

    elif data == "adm_edit_rights" and int(user_id) in ADMINS:
        msg = f"تعديل الحقوق:\n\nيوزر المطور الحالي: {DEVELOPER_USER}\nقناة السورس الحالية: {SOURCE_CHANNEL}\n\nأرسل الحقوق الجديدة:\n`@developer @channel`"
        await edit_caption(
            msg,
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel")]])
        )
        context.user_data['action'] = 'adm_set_rights'

    elif data == "adm_ready_groups_menu" and int(user_id) in ADMINS:
        await edit_caption(
            "لوحة التحكم بالكروبات الجاهزة:",
            get_admin_ready_groups_menu()
        )

    elif data == "adm_add_ready_group" and int(user_id) in ADMINS:
        kb = [
            [InlineKeyboardButton("🔥 كروبات السوبر", callback_data="adm_sel_cat_super")],
            [InlineKeyboardButton("🔄 كروبات التبادل", callback_data="adm_sel_cat_exchange")],
            [InlineKeyboardButton("📁 كروبات اخرى", callback_data="adm_sel_cat_other")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="adm_ready_groups_menu")]
        ]
        await edit_caption(
            "اختر القسم المراد إضافة كروب إليه:",
            InlineKeyboardMarkup(kb)
        )

    elif data.startswith("adm_sel_cat_") and int(user_id) in ADMINS:
        cat = data.replace("adm_sel_cat_", "")
        context.user_data['temp_ready_cat'] = cat
        await edit_caption(
            "أرسل اسم الكروب والرابط مفصولين بشرطة (-) مثال:\n`كروب المطورين - https://t.me/example`",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="adm_ready_groups_menu")]])
        )
        context.user_data['action'] = 'adm_adding_ready_group'

    elif data == "adm_view_ready_groups" and int(user_id) in ADMINS:
        kb = []
        for cat_key, cat_name in [("super", "كروبات السوبر"), ("exchange", "كروبات التبادل"), ("other", "كروبات اخرى")]:
            for idx, g in enumerate(READY_GROUPS.get(cat_key, [])):
                kb.append([
                    InlineKeyboardButton(f"{g['title']} ({cat_name})", callback_data="none"),
                    InlineKeyboardButton("🗑️ حذف", callback_data=f"adm_del_rg_{cat_key}_{idx}")
                ])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="adm_ready_groups_menu")])
        if len(kb) == 1:
            await edit_caption(
                "لا توجد كروبات جاهزة مضافة حالياً.",
                get_admin_ready_groups_menu()
            )
        else:
            await edit_caption(
                "اختر الكروب الجاهز المراد حذفه:",
                InlineKeyboardMarkup(kb)
            )

    elif data.startswith("adm_del_rg_") and int(user_id) in ADMINS:
        parts = data.split("_")
        cat_key = parts[3]
        idx = int(parts[4])
        if cat_key in READY_GROUPS and 0 <= idx < len(READY_GROUPS[cat_key]):
            removed = READY_GROUPS[cat_key].pop(idx)
            save_data()
            await query.answer(f"تم حذف {removed['title']}", show_alert=True)
        await edit_caption(
            "لوحة التحكم بالكروبات الجاهزة:",
            get_admin_ready_groups_menu()
        )

    # =================================================================
    # 👥 قسم الكروبات الجاهزة للمستخدمين
    # =================================================================
    elif data == "ready_groups_menu":
        await edit_caption(
            "قسم الكروبات الجاهزة:\n\nاختر نوع الكروبات التي تريد الانضمام إليها:",
            get_ready_groups_main_keyboard()
        )

    elif data.startswith("view_ready_cat_"):
        cat_key = data.replace("view_ready_cat_", "")
        cat_names = {"super": "كروبات السوبر", "exchange": "كروبات التبادل", "other": "كروبات اخرى"}
        groups_list = READY_GROUPS.get(cat_key, [])

        if not groups_list:
            await edit_caption(
                f"لا توجد كروبات مضافة حالياً في قسم ({cat_names.get(cat_key, '')}).",
                get_ready_groups_main_keyboard()
            )
            return

        kb = []
        for idx, g in enumerate(groups_list):
            kb.append([InlineKeyboardButton(f"📁 {g['title']}", callback_data=f"join_rg_{cat_key}_{idx}")])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="ready_groups_menu")])

        await edit_caption(
            f"قسم {cat_names.get(cat_key, '')}:\n\nاضغط على أي كروب للانضمام إليه بحساباتك وإضافته للنشر:",
            InlineKeyboardMarkup(kb)
        )

    elif data.startswith("join_rg_"):
        parts = data.split("_")
        cat_key = parts[2]
        idx = int(parts[3])
        group_item = READY_GROUPS.get(cat_key, [])[idx] if cat_key in READY_GROUPS and idx < len(READY_GROUPS[cat_key]) else None

        if not group_item:
            await query.answer("الكروب غير موجود", show_alert=True)
            return

        link = group_item['link']

        if not user.get('accounts'):
            await query.answer("يرجى إضافة حسابات أولاً للانضمام للكروب!", show_alert=True)
            return

        await query.answer("جاري انضمام حساباتك للكروب... يرجى الانتظار", show_alert=False)

        success_accs = 0
        for acc in user.get('accounts', []):
            phone = str(acc['phone'])
            client = ACTIVE_CLIENTS.get(phone)
            if not client or not client.is_connected:
                session_path = os.path.join(SESSION_DIR, phone)
                client = Client(name=session_path, api_id=API_ID, api_hash=API_HASH)
                try:
                    await client.start()
                    register_session_reply_handler(client, user_id)
                    ACTIVE_CLIENTS[phone] = client
                except Exception:
                    continue

            try:
                chat_obj = await client.join_chat(link)
                target_val = f"@{chat_obj.username}" if chat_obj.username else str(chat_obj.id)
                if target_val not in user['groups']:
                    user['groups'].append(target_val)
                success_accs += 1
            except Exception:
                try:
                    target_val = link
                    if "t.me/" in target_val and not ("t.me/+" in target_val or "t.me/joinchat/" in target_val):
                        target_val = "@" + target_val.split("t.me/")[1].replace("/", "")
                    if target_val not in user['groups']:
                        user['groups'].append(target_val)
                    success_accs += 1
                except Exception:
                    pass

        save_data()
        await edit_caption(
            f"تم انضمام حساباتك ({success_accs}) إلى الكروب ({group_item['title']}) بنجاح وإضافته لقائمة النشر!",
            get_ready_groups_main_keyboard()
        )

    # =================================================================
    # باقي أقسام إدارة التلقائي والرسائل
    # =================================================================
    elif data == "auto_reply_pm_menu":
        asyncio.create_task(start_user_clients(user_id))
        pm_status = "مفعل" if user.get('pm_auto_reply_enabled', False) else "معطل"
        pm_text = user.get('pm_reply_text', 'صاحب الحساب مشغول حالياً، أترك رسالتك وسيتم الرد عليك فور تفرغه.')
        msg = f"📌 قسم الرد التلقائي في الخاص (للمستخدمين):\n\n📊 الحالة: {pm_status}\n📝 الكليشة الحالية للرد:\n`{pm_text}`"
        await edit_caption(msg, get_pm_reply_keyboard(user_id))

    elif data == "enable_pm_reply":
        user['pm_auto_reply_enabled'] = True
        save_data()
        asyncio.create_task(start_user_clients(user_id))
        await query.answer("تم تفعيل الرد التلقائي في الخاص", show_alert=True)
        pm_status = "مفعل"
        pm_text = user.get('pm_reply_text', 'صاحب الحساب مشغول حالياً، أترك رسالتك وسيتم الرد عليك فور تفرغه.')
        msg = f"📌 قسم الرد التلقائي في الخاص (للمستخدمين):\n\n📊 الحالة: {pm_status}\n📝 الكليشة الحالية للرد:\n`{pm_text}`"
        await edit_caption(msg, get_pm_reply_keyboard(user_id))

    elif data == "disable_pm_reply":
        user['pm_auto_reply_enabled'] = False
        save_data()
        asyncio.create_task(start_user_clients(user_id))
        await query.answer("تم تعطيل الرد التلقائي في الخاص", show_alert=True)
        pm_status = "معطل"
        pm_text = user.get('pm_reply_text', 'صاحب الحساب مشغول حالياً، أترك رسالتك وسيتم الرد عليك فور تفرغه.')
        msg = f"📌 قسم الرد التلقائي في الخاص (للمستخدمين):\n\n📊 الحالة: {pm_status}\n📝 الكليشة الحالية للرد:\n`{pm_text}`"
        await edit_caption(msg, get_pm_reply_keyboard(user_id))

    elif data == "edit_pm_reply_text":
        await edit_caption(
            "أرسل الكليشة الجديدة للرد التلقائي في الخاص:",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="auto_reply_pm_menu")]])
        )
        context.user_data['action'] = 'editing_pm_reply_text'

    elif data == "user_pm_broadcast":
        if not user.get('accounts'):
            await edit_caption(
                "يرجى إضافة حسابات أولاً للتمكن من الإذاعة في الخاص!",
                get_pm_reply_keyboard(user_id)
            )
            return
        await edit_caption(
            "أرسل نص الإذاعة التي تريد نشرها لكافة المحادثات الخاصة بحساباتك المربوطة:",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="auto_reply_pm_menu")]])
        )
        context.user_data['action'] = 'entering_user_pm_broadcast'

    elif data == "auto_reply_group_menu":
        asyncio.create_task(start_user_clients(user_id))
        replies = user.get('auto_replies', {})
        msg = f"📌 قسم الرد التلقائي في الكروبات:\n\nعدد الردود المضافة للكروبات: `{len(replies)}`"
        kb = [
            [InlineKeyboardButton("➕ إضافة رد للكروبات", callback_data="add_auto_reply", style="success")],
            [InlineKeyboardButton("📋 عرض أو حذف ردود الكروبات", callback_data="view_auto_replies", style="danger")],
            [InlineKeyboardButton("🔙 رجوع لقائمة الرئيسية", callback_data="back_main")]
        ]
        await edit_caption(msg, InlineKeyboardMarkup(kb))

    elif data == "add_auto_reply":
        await edit_caption(
            "أرسل الكلمة المفتاحية للرد التلقائي في المجموعات:",
            InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="auto_reply_group_menu")]])
        )
        context.user_data['action'] = 'adding_reply_key'

    elif data.startswith("select_reply_text_"):
        selected_target = data.replace("select_reply_text_", "")
        reply_key = context.user_data.get('temp_reply_key')
        reply_text = context.user_data.get('temp_reply_text')
        
        if reply_key and reply_text:
            if 'auto_replies' not in user: user['auto_replies'] = {}
            user['auto_replies'][reply_key] = {"reply": reply_text, "text_index": selected_target}
            save_data()
            asyncio.create_task(start_user_clients(user_id))
            
            target_str = "جميع الكلايش" if selected_target == "all" else f"الكليشة رقم [{int(selected_target)+1}]"
            await edit_caption(
                f"تم إضافة الرد بنجاح!\n\nالكلمة المفتاحية: `{reply_key}`\nالنص: {reply_text}\nمخصص لكليشة: {target_str}",
                get_main_keyboard(int(user_id))
            )
        context.user_data['action'] = None

    elif data == "view_auto_replies":
        replies = user.get('auto_replies', {})
        if not replies:
            await edit_caption(
                "لا توجد ردود تلقائية مضافة حالياً للمجموعات.",
                get_main_keyboard(int(user_id))
            )
            return
            
        kb = []
        for key, val in replies.items():
            t_idx = val.get('text_index', 'all')
            txt_info = "الكل" if t_idx == 'all' else f"كليشة {int(t_idx)+1}"
            kb.append([
                InlineKeyboardButton(f"💬 {key} ({txt_info})", callback_data="none"),
                InlineKeyboardButton("🗑️ حذف", callback_data=f"del_reply_{key}")
            ])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="auto_reply_group_menu")])
        await edit_caption("قائمة ردود الكروبات المضافة:", InlineKeyboardMarkup(kb))

    elif data.startswith("del_reply_"):
        key_to_del = data.replace("del_reply_", "")
        if key_to_del in user.get('auto_replies', {}):
            del user['auto_replies'][key_to_del]
            save_data()
            await query.answer(f"تم حذف الرد الخاص بـ ({key_to_del})", show_alert=True)
            
        replies = user.get('auto_replies', {})
        if not replies:
            await edit_caption(
                "لا توجد ردود تلقائية مضافة حالياً للمجموعات.",
                get_main_keyboard(int(user_id))
            )
        else:
            kb = []
            for key, val in replies.items():
                t_idx = val.get('text_index', 'all')
                txt_info = "الكل" if t_idx == 'all' else f"كليشة {int(t_idx)+1}"
                kb.append([
                    InlineKeyboardButton(f"💬 {key} ({txt_info})", callback_data="none"),
                    InlineKeyboardButton("🗑️ حذف", callback_data=f"del_reply_{key}")
                ])
            kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="auto_reply_group_menu")])
            await edit_caption("قائمة ردود الكروبات المضافة:", InlineKeyboardMarkup(kb))

    elif data == "manage_texts_menu":
        texts_count = len(user.get('texts', []))
        msg = f"📌 قسم إدارة الكلايش المتعددة:\n\nعدد الكلايش المضافة حالياً: `{texts_count}`"
        await edit_caption(msg, get_texts_keyboard())

    elif data == "add_text":
        await edit_caption(
            "أرسل الكليشة الجديدة الخاصة بالنشر التلقائي:",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="manage_texts_menu")]])
        )
        context.user_data['action'] = 'adding_text'

    elif data == "view_texts":
        texts = user.get('texts', [])
        if not texts:
            await edit_caption(
                "لا توجد أي كلايش مضافة حالياً.",
                get_texts_keyboard()
            )
            return
        kb = []
        for idx, txt in enumerate(texts):
            short_txt = txt[:25] + "..." if len(txt) > 25 else txt
            kb.append([
                InlineKeyboardButton(f"[{idx+1}]: {short_txt}", callback_data="none"),
                InlineKeyboardButton("🗑️ حذف", callback_data=f"del_text_{idx}")
            ])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_texts_menu")])
        await edit_caption(
            f"قائمة الكلايش المضافة بالنظام ({len(texts)}):",
            InlineKeyboardMarkup(kb)
        )

    elif data.startswith("del_text_"):
        idx = int(data.replace("del_text_", ""))
        texts = user.get('texts', [])
        if 0 <= idx < len(texts):
            texts.pop(idx)
            save_data()
            await query.answer("تم حذف الكليشة بنجاح", show_alert=True)

        if not user.get('texts', []):
            await edit_caption(
                "لا توجد أي كلايش مضافة حالياً.",
                get_texts_keyboard()
            )
        else:
            kb = []
            for i, txt in enumerate(user['texts']):
                short_txt = txt[:25] + "..." if len(txt) > 25 else txt
                kb.append([
                    InlineKeyboardButton(f"[{i+1}]: {short_txt}", callback_data="none"),
                    InlineKeyboardButton("🗑️ حذف", callback_data=f"del_text_{i}")
                ])
            kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_texts_menu")])
            await edit_caption(
                f"قائمة الكلايش المضافة بالنظام ({len(user['texts'])}):",
                InlineKeyboardMarkup(kb)
            )

    elif data == "clear_all_texts":
        user['texts'] = []
        save_data()
        await edit_caption(
            "تم مسح جميع الكلايش بنجاح.",
            get_texts_keyboard()
        )

    elif data == "manage_groups_menu":
        groups_count = len(user.get('groups', []))
        msg = f"📌 قسم إدارة الكروبات:\n\nعدد الكروبات المضافة للنشر: `{groups_count}`"
        await edit_caption(msg, get_groups_keyboard())

    elif data == "view_groups":
        groups = user.get('groups', [])
        if not groups:
            await edit_caption(
                "لا توجد أي كروبات مضافة.",
                get_groups_keyboard()
            )
            return

        kb = []
        for idx, grp in enumerate(groups):
            kb.append([
                InlineKeyboardButton(f"{grp}", callback_data="none"),
                InlineKeyboardButton("🗑️ حذف", callback_data=f"del_single_grp_{idx}")
            ])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_groups_menu")])
        await edit_caption(
            f"الكروبات المضافة حالياً للنشر ({len(groups)}):",
            InlineKeyboardMarkup(kb)
        )

    elif data.startswith("del_single_grp_"):
        idx = int(data.replace("del_single_grp_", ""))
        groups = user.get('groups', [])
        if 0 <= idx < len(groups):
            groups.pop(idx)
            save_data()
            await query.answer("تم حذف الكروب من قائمة النشر", show_alert=True)

        if not user.get('groups', []):
            await edit_caption(
                "لا توجد أي كروبات مضافة.",
                get_groups_keyboard()
            )
        else:
            kb = []
            for i, grp in enumerate(user['groups']):
                kb.append([
                    InlineKeyboardButton(f"{grp}", callback_data="none"),
                    InlineKeyboardButton("🗑️ حذف", callback_data=f"del_single_grp_{i}")
                ])
            kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_groups_menu")])
            await edit_caption(
                f"الكروبات المضافة حالياً للنشر ({len(user['groups'])}):",
                InlineKeyboardMarkup(kb)
            )

    elif data == "clear_all_groups":
        user['groups'] = []
        save_data()
        await edit_caption(
            "تم مسح جميع الكروبات بنجاح.",
            get_groups_keyboard()
        )

    elif data == "manage_accs":
        kb = [
            [InlineKeyboardButton("➕ إضافة حساب جديد", callback_data="acc_add", style="success")],
            [InlineKeyboardButton("📋 عرض الحسابات المضافة", callback_data="acc_view", style="primary")],
            [InlineKeyboardButton("🗑️ حذف كافة الحسابات", callback_data="acc_del", style="danger")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
        ]
        status = "لا توجد حسابات مضافة." if not user['accounts'] else f"لديك ({len(user['accounts'])}) حسابات مضافة."
        await edit_caption(
            f"{status}\n\nاختر إجراءً:",
            InlineKeyboardMarkup(kb)
        )
    
    elif data == "acc_view":
        if not user['accounts']:
            msg = "لا توجد حسابات مضافة حالياً."
        else:
            acc_list = "\n".join([f"• `{acc['phone']}`" for acc in user['accounts']])
            msg = f"قائمة الحسابات المضافة ({len(user['accounts'])}):\n\n{acc_list}"
        kb = [[InlineKeyboardButton("🔙 رجوع", callback_data="manage_accs")]]
        await edit_caption(msg, InlineKeyboardMarkup(kb))

    elif data == "acc_add":
        await edit_caption(
            "الخطوة [1/3]: يرجى إرسال رقم الهاتف مع رمز الدولة (مثال: +9647xxxxxxx) أو اضغط رجوع:",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="manage_accs")]])
        )
        context.user_data['action'] = 'pyro_phone'
    
    elif data == "acc_del":
        for acc in user.get('accounts', []):
            p = str(acc['phone'])
            if p in ACTIVE_CLIENTS:
                try: asyncio.create_task(ACTIVE_CLIENTS[p].stop())
                except: pass
                ACTIVE_CLIENTS.pop(p, None)
        user['accounts'] = []
        save_data()
        await edit_caption(
            "تم مسح كافة حساباتك بنجاح.",
            get_main_keyboard(int(user_id))
        )

    elif data == "start_post":
        if not user['accounts']:
            await edit_caption(
                "لا يمكنك بدء النشر. يرجى إضافة حساب أولاً.",
                get_main_keyboard(int(user_id))
            )
            return
        if not user.get('interval') or user['interval'] <= 0:
            await edit_caption(
                "لا يمكنك بدء النشر. يرجى تحديد وقت النشر أولاً.",
                get_main_keyboard(int(user_id))
            )
            return
        if not user['groups']:
            await edit_caption(
                "لا يمكنك بدء النشر. يرجى إضافة/اختيار كروب واحد على الأقل أولاً.",
                get_main_keyboard(int(user_id))
            )
            return
        if not user.get('texts'):
            await edit_caption(
                "لا يمكنك بدء النشر. يرجى إضافة كليشة واحدة على الأقل.",
                get_main_keyboard(int(user_id))
            )
            return
            
        if not user.get('is_running', False):
            user['is_running'] = True
            save_data()
            asyncio.create_task(posting_worker(user_id, context))
            await edit_caption(
                f"تم بدء النشر التلقائي بنجاح!\nالوقت المحدد بين النشر: {user['interval']} ثانية\nعدد الكروبات المضافة: {len(user['groups'])}\nعدد الكلايش المستخدمة: {len(user['texts'])}",
                get_main_keyboard(int(user_id))
            )
    
    elif data == "stop_post":
        user['is_running'] = False
        save_data()
        await edit_caption(
            "تم إيقاف النشر التلقائي.",
            get_main_keyboard(int(user_id))
        )

    elif data == "edit_time":
        await edit_caption(
            f"الوقت الحالي للنشر: ({user.get('interval', 30)}) ثانية.\n\nأرسل الوقت الجديد بالثواني بين كل منشور:",
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]])
        )
        context.user_data['action'] = 'editing_time'

    elif data == "add_group_manual":
        msg_text = "إضافة كروب يدوي للنشر:\n\n• أرسل يوزر الكروب أو رابط الكروب العام أو رابط الدعوة الخاص (`https://t.me/+...`)."
        await edit_caption(
            msg_text,
            InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="manage_groups_menu")]])
        )
        context.user_data['action'] = 'adding_group'

    elif data.startswith("list_account_groups_"):
        page = int(data.split("_")[-1])
        if not user['accounts']:
            await edit_caption(
                "لا توجد حسابات مضافة لاستخراج الكروبات منها!",
                get_main_keyboard(int(user_id))
            )
            return

        if 'all_fetched_groups' not in context.user_data or page == 0:
            await edit_caption(
                "جاري جلب كافة الكروبات الحقيقية الحالية للحساب... يرجى الانتظار قليلاً",
                get_main_keyboard(int(user_id))
            )

            acc = user['accounts'][0]
            phone = str(acc['phone'])
            client = ACTIVE_CLIENTS.get(phone)
            
            close_after = False
            if not client or not client.is_connected:
                session_path = os.path.join(SESSION_DIR, phone)
                client = Client(name=session_path, api_id=API_ID, api_hash=API_HASH)
                await client.start()
                close_after = True

            fetched_groups = []
            try:
                async for dialog in client.get_dialogs():
                    chat_type = str(dialog.chat.type).lower()
                    if "group" in chat_type or "supergroup" in chat_type:
                        target_val = f"@{dialog.chat.username}" if dialog.chat.username else str(dialog.chat.id)
                        fetched_groups.append({"id": target_val, "title": dialog.chat.title})
                if close_after:
                    register_session_reply_handler(client, str(user_id))
                    ACTIVE_CLIENTS[phone] = client
            except Exception as e:
                await edit_caption(
                    f"حدث خطأ أثناء جلب الكروبات: `{e}`",
                    get_main_keyboard(int(user_id))
                )
                return

            context.user_data['all_fetched_groups'] = fetched_groups

        all_fetched = context.user_data.get('all_fetched_groups', [])
        if not all_fetched:
            await edit_caption(
                "لم يتم العثور على أي كروبات ينضم إليها هذا الحساب.",
                get_main_keyboard(int(user_id))
            )
            return

        per_page = 5
        start_idx = page * per_page
        end_idx = start_idx + per_page
        current_page_groups = all_fetched[start_idx:end_idx]

        kb = []
        for grp in current_page_groups:
            is_added = "محدد: " if grp['id'] in user['groups'] else ""
            btn_text = f"📂 {is_added}{grp['title']}"
            kb.append([InlineKeyboardButton(btn_text, callback_data=f"toggle_grp_{grp['id']}_{page}")])

        nav_buttons = []
        if page > 0: nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"list_account_groups_{page-1}", style="danger"))
        if end_idx < len(all_fetched): nav_buttons.append(InlineKeyboardButton("➡️ التالي", callback_data=f"list_account_groups_{page+1}", style="success"))

        if nav_buttons: kb.append(nav_buttons)
        kb.append([InlineKeyboardButton("📥 إدراج الكل", callback_data="add_all_fetched_groups", style="primary")])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_groups_menu")])

        await edit_caption(
            f"اختر الكروبات المراد تحديدها للنشر ({len(all_fetched)} كروب):",
            InlineKeyboardMarkup(kb)
        )

    elif data.startswith("toggle_grp_"):
        parts = data.split("_")
        page = parts[-1]
        target_gid = "_".join(parts[2:-1])
        
        if target_gid in user['groups']:
            user['groups'].remove(target_gid)
            await query.answer("تم حذف الكروب من قائمة النشر", show_alert=False)
        else:
            user['groups'].append(target_gid)
            await query.answer("تم إضافة الكروب إلى قائمة النشر", show_alert=False)
        save_data()

        all_fetched = context.user_data.get('all_fetched_groups', [])
        page = int(page)
        per_page = 5
        start_idx = page * per_page
        end_idx = start_idx + per_page
        current_page_groups = all_fetched[start_idx:end_idx]

        kb = []
        for grp in current_page_groups:
            is_added = "محدد: " if grp['id'] in user['groups'] else ""
            btn_text = f"📂 {is_added}{grp['title']}"
            kb.append([InlineKeyboardButton(btn_text, callback_data=f"toggle_grp_{grp['id']}_{page}")])

        nav_buttons = []
        if page > 0: nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"list_account_groups_{page-1}"))
        if end_idx < len(all_fetched): nav_buttons.append(InlineKeyboardButton("➡️ التالي", callback_data=f"list_account_groups_{page+1}"))

        if nav_buttons: kb.append(nav_buttons)
        kb.append([InlineKeyboardButton("📥 إدراج الكل", callback_data="add_all_fetched_groups")])
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_groups_menu")])

        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(kb))

    elif data == "add_all_fetched_groups":
        all_fetched = context.user_data.get('all_fetched_groups', [])
        added_count = 0
        for grp in all_fetched:
            if grp['id'] not in user['groups']:
                user['groups'].append(grp['id'])
                added_count += 1
        save_data()
        await edit_caption(
            f"تم إضافة كافة الكروبات ({added_count}) بنجاح لقائمة النشر!",
            get_main_keyboard(int(user_id))
        )

    elif data == "sub_info":
        exp = user['sub_expire']
        if isinstance(exp, str): exp = datetime.fromisoformat(exp)
        await edit_caption(
            f"ينتهي اشتراكك بتاريخ: `{exp.strftime('%Y-%m-%d %H:%M:%S')}`",
            get_main_keyboard(int(user_id))
        )

    elif data == "stats":
        groups_count = len(user['groups'])
        acc_count = len(user['accounts'])
        texts_count = len(user.get('texts', []))
        time_sec = user.get('interval', 30)
        status = "شغال" if user.get('is_running', False) else "متوقف"
        await edit_caption(
            f"📊 إحصائيات حسابك الحالية:\n\n• حالة النشر: {status}\n• الحسابات المربوطة: {acc_count}\n• الكروبات المضافة: {groups_count}\n• الكلايش المفعلة: {texts_count}\n• توقيت النشر: {time_sec} ثانية",
            get_main_keyboard(int(user_id))
        )

# =================================================================
# ⭐️ معالجة الشراء بالنجوم والتأكيد الدفع التلقائي
# =================================================================
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    payload_parts = payment.invoice_payload.split("_")
    
    plan = payload_parts[2]
    days = int(payload_parts[3])
    stars_paid = int(payload_parts[4])
    buyer_user_id = str(update.effective_user.id)
    
    generated_code = "STAR-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    VALID_CODES[generated_code] = days
    
    buyer_record = {
        "user_id": buyer_user_id,
        "code": generated_code,
        "plan": plan,
        "stars": stars_paid,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    CODE_BUYERS.append(buyer_record)
    save_data()

    success_msg = (
        "🎉 تمت عملية الشراء بنجاح بالنجوم!\n\n"
        f"• الكود الخاص بك: `{generated_code}`\n"
        f"• المدة: `{days}` يوم\n\n"
        "إضغط على الكود للنسخ، ثم اضغط على 📋 استخدام كود لتفعيل الاشتراك وقم بإرساله لتفعيل البوت فوراً!"
    )
    await send_photo_message(update.effective_chat.id, success_msg, "HTML", get_welcome_keyboard(), context=context)
    
    # إشعار الأدمن
    admin_alert = f"⭐️ عملية شراء جديدة بالنجوم:\n\n👤 المستخدم: `{buyer_user_id}`\n🔑 الكود: `{generated_code}`\n💰 النجوم: {stars_paid}"
    for adm in ADMINS:
        try: await context.bot.send_message(chat_id=adm, text=admin_alert, parse_mode="HTML")
        except: pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DEVELOPER_USER, SOURCE_CHANNEL, CUSTOM_START_MSG
    user_id = str(update.effective_user.id)
    text = update.message.text.strip() if update.message.text else ""
    action = context.user_data.get('action')
    
    if user_id not in USERS_DATA: return
    user = USERS_DATA[user_id]

    if action == 'adm_setting_star_price' and int(user_id) in ADMINS:
        p_key = context.user_data.get('target_price_key')
        try:
            val = int(text)
            STAR_PRICES[p_key] = val
            save_data()
            await send_photo_message(update.effective_chat.id, f"✅ تم تعديل سعر الباقة (`{p_key}`) إلى ⭐ {val} نجوم بنجاح.", "HTML", get_admin_keyboard(), context=context)
        except:
            await send_photo_message(update.effective_chat.id, "❌ يرجى إدخال رقم صحيح.", "HTML", reply_markup=None, context=context)
        context.user_data['action'] = None
        return

    if action == 'entering_code':
        if text in VALID_CODES:
            days = VALID_CODES.pop(text)
            user['sub_expire'] = datetime.now() + timedelta(days=days)
            save_data()
            await send_photo_message(update.effective_chat.id, f"تم تفعيل الاشتراك بنجاح لمدة {days} يوم!", "HTML", get_main_keyboard(int(user_id)), context=context)
        else:
            await send_photo_message(update.effective_chat.id, "الكود غير صحيح أو مستخدم سابقاً!", "HTML", reply_markup=None, context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_check_code_info' and int(user_id) in ADMINS:
        if text in VALID_CODES:
            days = VALID_CODES[text]
            await send_photo_message(update.effective_chat.id, f"ℹ️ تفاصيل الكود:\n\n• الكود: `{text}`\n• الصلوحية: `{days}` يوم\n• الحالة: فعّال وغير مستخدم.", "HTML", get_admin_keyboard(), context=context)
        else:
            await send_photo_message(update.effective_chat.id, "❌ هذا الكود غير موجود أو تم استخدامه سابقاً.", "HTML", get_admin_keyboard(), context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_del_sub_id' and int(user_id) in ADMINS:
        target_id = text
        if target_id in USERS_DATA:
            USERS_DATA[target_id]['sub_expire'] = datetime.now() - timedelta(days=1)
            save_data()
            await send_photo_message(update.effective_chat.id, f"✅ تم مسح اشتراك المستخدم `{target_id}` بنجاح.", "HTML", get_admin_keyboard(), context=context)
        else:
            await send_photo_message(update.effective_chat.id, "❌ المستخدم غير موجود في قاعدة البيانات.", "HTML", get_admin_keyboard(), context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_waiting_start_text' and int(user_id) in ADMINS:
        CUSTOM_START_MSG = update.message.text_html
        save_data()
        await send_photo_message(update.effective_chat.id, "✅ تم تحديث رسالة /start بنجاح!", "HTML", get_admin_keyboard(), context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_adding_ready_group' and int(user_id) in ADMINS:
        cat = context.user_data.get('temp_ready_cat')
        if "-" in text and cat in READY_GROUPS:
            parts = text.split("-", 1)
            title = parts[0].strip()
            link = parts[1].strip()
            READY_GROUPS[cat].append({"title": title, "link": link})
            save_data()
            await send_photo_message(update.effective_chat.id, f"تم إضافة الكروب بنجاح إلى قسم ({cat})!", "HTML", get_admin_ready_groups_menu(), context=context)
        else:
            await send_photo_message(update.effective_chat.id, "صيغة إدخال غير صحيحة، يرجى الفصل بشرطة (-):\n`الاسم - الرابط`", "HTML", reply_markup=None, context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_code_days' and int(user_id) in ADMINS:
        try:
            days = int(text)
            code = "SUB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            VALID_CODES[code] = days
            save_data()
            await send_photo_message(update.effective_chat.id, f"تم إنشاء الكود بنجاح:\n\n`{code}`\n\nالمدة: {days} يوم.", "HTML", get_admin_keyboard(), context=context)
        except:
            await send_photo_message(update.effective_chat.id, "يرجى إدخال عدد أيام صحيح.", "HTML", reply_markup=None, context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_manual_id' and int(user_id) in ADMINS:
        context.user_data['target_sub_id'] = text
        context.user_data['action'] = 'adm_manual_days'
        await send_photo_message(update.effective_chat.id, "أرسل عدد أيام الاشتراك:", "HTML", reply_markup=None, context=context)
        return

    elif action == 'adm_manual_days' and int(user_id) in ADMINS:
        target_id = context.user_data.get('target_sub_id')
        try:
            days = int(text)
            if target_id not in USERS_DATA:
                USERS_DATA[target_id] = {
                    'lang': 'ar', 'sub_expire': datetime.now(),
                    'accounts': [], 'groups': [], 'texts': [], 'interval': 30,
                    'is_running': False, 'auto_replies': {},
                    'pm_reply_text': "صاحب الحساب مشغول حالياً، أترك رسالتك وسيتم الرد عليك فور تفرغه.",
                    'pm_auto_reply_enabled': False,
                    'night_mode_enabled': False,
                    'night_start': None,
                    'night_end': None
                }
            USERS_DATA[target_id]['sub_expire'] = datetime.now() + timedelta(days=days)
            save_data()
            await send_photo_message(update.effective_chat.id, f"تم تفعيل الاشتراك للمستخدم `{target_id}` لمدة {days} يوم.", "HTML", get_admin_keyboard(), context=context)
        except:
            await send_photo_message(update.effective_chat.id, "حدث خطأ في البيانات المدخلة.", "HTML", reply_markup=None, context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_broadcast' and int(user_id) in ADMINS:
        success, failed = 0, 0
        for uid in list(USERS_DATA.keys()):
            res = await safe_send_message(context, int(uid), text)
            if res: success += 1
            else: failed += 1
        await send_photo_message(update.effective_chat.id, f"تمت الإذاعة بنجاح!\n\nالناجحة: {success}\nالفاشلة: {failed}", "HTML", get_admin_keyboard(), context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_add_ch' and int(user_id) in ADMINS:
        ch = text.strip()
        if not ch.startswith("@"): ch = "@" + ch
        if ch not in REQUIRED_CHANNELS:
            REQUIRED_CHANNELS.append(ch)
            save_data()
            await send_photo_message(update.effective_chat.id, f"تم إضافة القناة {ch} بنجاح!", "HTML", get_admin_sub_menu(), context=context)
        else:
            await send_photo_message(update.effective_chat.id, "القناة مضافة بالفعل.", "HTML", get_admin_sub_menu(), context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_add_admin_id' and int(user_id) in ADMINS:
        try:
            new_a = int(text)
            if new_a not in ADMINS:
                ADMINS.append(new_a)
                save_data()
                await send_photo_message(update.effective_chat.id, f"تم إضافة الأدمن `{new_a}` بنجاح.", "HTML", get_admin_manage_menu(), context=context)
            else:
                await send_photo_message(update.effective_chat.id, "الأدمن مضاف بالفعل.", "HTML", reply_markup=None, context=context)
        except:
            await send_photo_message(update.effective_chat.id, "يرجى إدخال آيدي أرقام فقط.", "HTML", reply_markup=None, context=context)
        context.user_data['action'] = None
        return

    elif action == 'adm_set_rights' and int(user_id) in ADMINS:
        parts = text.split()
        if len(parts) >= 2:
            DEVELOPER_USER = parts[0]
            SOURCE_CHANNEL = parts[1]
            await send_photo_message(update.effective_chat.id, f"تم تحديث الحقوق بنجاح!\n\nالمطور: {DEVELOPER_USER}\nالسورس: {SOURCE_CHANNEL}", "HTML", get_admin_keyboard(), context=context)
        else:
            await send_photo_message(update.effective_chat.id, "يرجى إرسال المعرفين بشكل صحيح مسبوقين بـ @", "HTML", reply_markup=None, context=context)
        context.user_data['action'] = None
        return

    if action == 'editing_pm_reply_text':
        user['pm_reply_text'] = text
        save_data()
        asyncio.create_task(start_user_clients(user_id))
        await send_photo_message(update.effective_chat.id, f"تم تحديث كليشة الرد التلقائي للخاص بنجاح!\n\nالكليشة الحالية:\n`{text}`", "HTML", get_pm_reply_keyboard(user_id), context=context)
        context.user_data['action'] = None
        return

    elif action == 'entering_user_pm_broadcast':
        context.user_data['action'] = None
        asyncio.create_task(user_pm_broadcast_worker(user_id, text, context))
        await send_photo_message(update.effective_chat.id, "بدأت عملية الإذاعة في المحادثات الخاصة بحساباتك!", "HTML", get_pm_reply_keyboard(user_id), context=context)
        return

    elif action == 'adding_reply_key':
        context.user_data['temp_reply_key'] = text
        context.user_data['action'] = 'adding_reply_text'
        await send_photo_message(update.effective_chat.id, f"الكلمة المفتاحية (كروبات): `{text}`\n\nالآن أرسل النص الذي تريد أن ترد به الجلسة فورياً:", "HTML", reply_markup=None, context=context)
        return

    elif action == 'adding_reply_text':
        context.user_data['temp_reply_text'] = text
        texts = user.get('texts', [])
        kb = [[InlineKeyboardButton("📋 تطبيق على جميع الكلايش", callback_data="select_reply_text_all", style="primary")]]
        
        for idx, txt in enumerate(texts):
            short_txt = txt[:25] + "..." if len(txt) > 25 else txt
            kb.append([InlineKeyboardButton(f"📝 كليشة [{idx+1}]: {short_txt}", callback_data=f"select_reply_text_{idx}")])
            
        await send_photo_message(update.effective_chat.id, "اختر الكليشة التي تريد تخصيص هذا الرد التلقائي لها عند الرد عليها:", "HTML", InlineKeyboardMarkup(kb), context=context)
        context.user_data['action'] = None
        return

    elif action == 'adding_text':
        if 'texts' not in user: user['texts'] = []
        user['texts'].append(text)
        save_data()
        await send_photo_message(update.effective_chat.id, f"تم إضافة الكليشة بنجاح!\n\nعدد الكلايش الحالية: {len(user['texts'])}", "HTML", get_texts_keyboard(), context=context)
        context.user_data['action'] = None
        return

    if action == 'pyro_phone':
        phone = text.replace(" ", "")
        session_path = os.path.join(SESSION_DIR, str(phone))
        client = Client(name=session_path, api_id=API_ID, api_hash=API_HASH)
        await client.connect()
        try:
            code_hash = await client.send_code(phone)
            PYRO_SESSIONS[user_id] = {"client": client, "phone": phone, "code_hash": code_hash.phone_code_hash}
            context.user_data['action'] = 'pyro_code'
            await send_photo_message(update.effective_chat.id, "الخطوة [2/3]: تم إرسال الرمز بنجاح. يرجى كتابة الرمز هنا مباشرة:", "HTML", reply_markup=None, context=context)
        except Exception:
            try: await client.disconnect()
            except: pass
            await send_photo_message(update.effective_chat.id, "حدث خطأ أثناء إرسال الرمز. تأكد من صحة الرقم وجرب مجدداً.", "HTML", get_main_keyboard(int(user_id)), context=context)
            context.user_data['action'] = None

    elif action == 'pyro_code':
        session_data = PYRO_SESSIONS.get(user_id)
        if not session_data:
            context.user_data['action'] = None
            return
            
        pure_code = text.replace(" ", "")
        client = session_data["client"]
        
        try:
            await client.sign_in(phone_number=session_data["phone"], phone_code_hash=session_data["code_hash"], phone_code=pure_code)
            user['accounts'].append({"phone": session_data["phone"]})
            save_data()
            register_session_reply_handler(client, str(user_id))
            ACTIVE_CLIENTS[str(session_data["phone"])] = client
            PYRO_SESSIONS.pop(user_id, None)
            context.user_data['action'] = None
            await send_photo_message(update.effective_chat.id, "تم ربط وتسجيل دخول الحساب بنجاح تام وبأمان!", "HTML", get_main_keyboard(int(user_id)), context=context)
        except SessionPasswordNeeded:
            context.user_data['action'] = 'pyro_2fa'
            await send_photo_message(update.effective_chat.id, "الخطوة [3/3]: حسابك محمي بالتحقق بخطوتين. يرجى إرسال كلمة السر الخاصة بحسابك الآن:", "HTML", reply_markup=None, context=context)
        except (PhoneCodeInvalid, PhoneCodeExpired):
            await send_photo_message(update.effective_chat.id, "الكود الذي أرسلته خاطئ أو منتهي الصلاحية. يرجى إعادة المحاولة.", "HTML", reply_markup=None, context=context)

    elif action == 'pyro_2fa':
        session_data = PYRO_SESSIONS.get(user_id)
        if not session_data: return
        client = session_data["client"]
        
        try:
            await client.check_password(password=text)
            user['accounts'].append({"phone": session_data["phone"]})
            save_data()
            register_session_reply_handler(client, str(user_id))
            ACTIVE_CLIENTS[str(session_data["phone"])] = client
            PYRO_SESSIONS.pop(user_id, None)
            context.user_data['action'] = None
            await send_photo_message(update.effective_chat.id, "تم التحقق من كلمة السر وربط الحساب بنجاح!", "HTML", get_main_keyboard(int(user_id)), context=context)
        except Exception:
            await send_photo_message(update.effective_chat.id, "كلمة السر غير صحيحة. أعد المحاولة:", "HTML", reply_markup=None, context=context)

    elif action == 'editing_time':
        try:
            user['interval'] = int(text)
            save_data()
            await send_photo_message(update.effective_chat.id, f"تم حفظ تعديل وقت النشر إلى ({user['interval']}) ثانية بنجاح.", "HTML", get_main_keyboard(int(user_id)), context=context)
        except: 
            await send_photo_message(update.effective_chat.id, "يرجى إدخال وقت صحيح بالثواني (أرقام فقط).", "HTML", reply_markup=None, context=context)
        context.user_data['action'] = None
        
    elif action == 'adding_group':
        grp_input = text
        if grp_input not in user['groups']:
            user['groups'].append(grp_input)
            save_data()
            await send_photo_message(update.effective_chat.id, "تم إضافة الكروب بنجاح إلى قائمة النشر.", "HTML", get_groups_keyboard(), context=context)
        else:
            await send_photo_message(update.effective_chat.id, "الكروب مضاف مسبقاً.", "HTML", get_groups_keyboard(), context=context)
        context.user_data['action'] = None

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    
    # معالجات الدفع بالنجوم
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()