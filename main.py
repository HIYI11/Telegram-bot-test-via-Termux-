import telebot
from telebot import types
import time
import json
import os
import re
from threading import Timer
import random
import datetime

# --- إعدادات البوت ---
bot = telebot.TeleBot('7139851198:AAGB_MpuZn6AqdH8nHK0DNX-Fnp8kjGlMJ8')

# ملفات حفظ البيانات
DB_FILE = 'verification_data.json'
ADMINS_FILE = 'admins.json'
GROUP_SETTINGS_FILE = 'group_settings.json'
USER_STATS_FILE = 'user_stats.json'

# معلومات المطور
DEVELOPER_ID = 5931329955
DEVELOPER_USERNAME = "@H_IYI"
DEVELOPER_NAME = "القرصان اليماني"

# --- تحميل وحفظ البيانات ---
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تحميل البيانات عند بدء البوت
verification_status = load_data(DB_FILE)
admins_data = load_data(ADMINS_FILE)
group_settings = load_data(GROUP_SETTINGS_FILE)
user_stats = load_data(USER_STATS_FILE)

# --- الإيموجيز ---
emojis = {
    'clock': '⏳',
    'welcome': '👋',
    'goodbye': '👋',
    'verify': '✅',
    'success': '🎉',
    'ban': '🚫',
    'unban': '🟢',
    'kick': '👞',
    'mute': '🔇',
    'unmute': '🔊',
    'warn': '⚠️',
    'admin': '🛡️',
    'dev': '👨‍💻',
    'game': '🎮',
    'broadcast': '📣',
    'member': '👤',
    'search': '🔍',
    'group': '🏘️',
    'error': '❌',
    'info': 'ℹ️',
    'settings': '⚙️',
    'stats': '📊',
    'fun': '🎭',
    'music': '🎵',
    'video': '🎬',
    'lock': '🔒',
    'unlock': '🔓',
    'filter': '🔎',
    'clean': '🧹'
}

# --- دوال مساعدة ---
def parse_time(time_str):
    if not time_str:
        return 0
    
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800
    }
    
    match = re.match(r'(\d+)([smhdw]?)', time_str)
    if match:
        value = int(match.group(1))
        unit = match.group(2) or 'm'
        return value * units[unit]
    return 0

def format_time(seconds):
    if seconds == 0:
        return "دائم"
    periods = [
        ('أسبوع', 604800),
        ('يوم', 86400),
        ('ساعة', 3600),
        ('دقيقة', 60),
        ('ثانية', 1)
    ]
    
    result = []
    remaining_seconds = int(seconds)
    for period_name, period_seconds in periods:
        if remaining_seconds >= period_seconds:
            period_value, remaining_seconds = divmod(remaining_seconds, period_seconds)
            result.append(f"{period_value} {period_name}")
    
    return " ".join(result[:2]) if result else "0 ثواني"

def is_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in admins)
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

def get_user_info(message, command_parts):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    
    if len(command_parts) < 2:
        return None
    
    identifier = command_parts[1]
    try:
        if identifier.isdigit():
            user_id = int(identifier)
            return bot.get_chat_member(message.chat.id, user_id).user
        elif identifier.startswith('@'):
            pass
    except Exception as e:
        print(f"Error getting user info: {e}")
    
    return None

def extract_duration_and_reason(command_parts):
    duration_str = None
    reason = "بدون سبب"
    
    if len(command_parts) > 2:
        potential_duration = command_parts[2]
        if re.match(r'^\d+[smhdw]?$', potential_duration):
            duration_str = potential_duration
            if len(command_parts) > 3:
                reason = " ".join(command_parts[3:])
        else:
            reason = " ".join(command_parts[2:])
            
    return duration_str, reason

def update_user_stats(user_id, command):
    if str(user_id) not in user_stats:
        user_stats[str(user_id)] = {
            'commands_used': {},
            'join_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'warnings': 0
        }
    
    if command not in user_stats[str(user_id)]['commands_used']:
        user_stats[str(user_id)]['commands_used'][command] = 0
    
    user_stats[str(user_id)]['commands_used'][command] += 1
    save_data(USER_STATS_FILE, user_stats)

# --- واجهة الأوامر الرئيسية ---
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton(f"{emojis['admin']} أوامر الإدارة"),
        types.KeyboardButton(f"{emojis['group']} أوامر المجموعة"),
        types.KeyboardButton(f"{emojis['member']} أوامر الأعضاء"),
        types.KeyboardButton(f"{emojis['game']} أوامر الألعاب"),
        types.KeyboardButton(f"{emojis['search']} أوامر البحث"),
        types.KeyboardButton(f"{emojis['settings']} الإعدادات")
    )
    return markup

# --- رسائل الترحيب والوداع ---
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    chat_id = message.chat.id
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            bot.send_message(chat_id,
                f"{emojis['welcome']} شكراً لإضافتي إلى مجموعتك! أنا هنا لمساعدتك في الإدارة. يمكنك البدء بإرسال `اوامر` أو `start` لعرض قائمة الأوامر.",
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
            continue
        
        member_name = new_member.first_name
        if new_member.last_name:
            member_name += f" {new_member.last_name}"
        if new_member.username:
            member_name += f" (@{new_member.username})"

        welcome_message = group_settings.get(str(chat_id), {}).get('welcome_message',
            f"{emojis['welcome']} أهلاً بك يا {member_name} في مجموعتنا! نورت الجروب."
        )
        bot.send_message(chat_id, welcome_message)

@bot.message_handler(content_types=['left_chat_member'])
def handle_left_member(message):
    chat_id = message.chat.id
    left_member = message.left_chat_member
    
    if left_member.id == bot.get_me().id:
        return

    member_name = left_member.first_name
    if left_member.last_name:
        member_name += f" {left_member.last_name}"
    if left_member.username:
        member_name += f" (@{left_member.username})"

    goodbye_message = group_settings.get(str(chat_id), {}).get('goodbye_message',
        f"{emojis['goodbye']} وداعاً يا {member_name}. نتمنى لك التوفيق في مكان آخر."
    )
    bot.send_message(chat_id, goodbye_message)

# --- قائمة الأوامر الرئيسية ---
@bot.message_handler(func=lambda message: message.text and (message.text.lower() in ['اوامر', 'start', 'help', 'الاوامر', 'commands']))
def show_main_commands(message):
    update_user_stats(message.from_user.id, 'commands')
    
    commands_text = f"""
{emojis['info']} *أهلاً بك في بوت الإدارة المتطور!* {emojis['info']}

📌 *الأوامر الرئيسية:*
▫️ `اوامر` - عرض هذه القائمة
▫️ `ايدي` - عرض معلومات حسابك
▫️ `بينج` - اختبار سرعة البوت

🎯 *اختر أحد الخيارات من الأزرار أدناه لعرض الأوامر المتخصصة:*

{emojis['admin']} *أوامر الإدارة* (للمشرفين)
{emojis['group']} *أوامر المجموعة*
{emojis['member']} *أوامر الأعضاء*
{emojis['game']} *أوامر الألعاب*
{emojis['search']} *أوامر البحث*
{emojis['settings']} *الإعدادات*
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown', reply_markup=get_main_keyboard())

# --- معالجة الأزرار الرئيسية ---
@bot.message_handler(func=lambda message: message.text == f"{emojis['admin']} أوامر الإدارة")
def show_admin_commands(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, f"{emojis['error']} أنت لست مشرفاً في هذه المجموعة!")
        return
    
    commands_text = f"""
{emojis['admin']} *أوامر الإدارة (للمشرفين فقط):*

▫️ `حظر [مدة] [سبب]` - حظر عضو
▫️ `الغاء_حظر [آيدي]` - إلغاء حظر عضو
▫️ `طرد [سبب]` - طرد عضو
▫️ `كتم [مدة] [سبب]` - تقييد عضو
▫️ `الغاء_كتم [آيدي]` - إلغاء تقييد عضو
▫️ `تحذير [سبب]` - تحذير عضو
▫️ `قائمة_المشرفين` - عرض المشرفين
▫️ `تثبيت` - تثبيت الرسالة
▫️ `الغاء_تثبيت` - إلغاء تثبيت الرسالة
▫️ `حذف` - حذف رسالة (بالرد)
▫️ `تنظيف [عدد]` - حذف عدد من الرسائل
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == f"{emojis['group']} أوامر المجموعة")
def show_group_commands(message):
    commands_text = f"""
{emojis['group']} *أوامر المجموعة:*

▫️ `معلومات_المجموعة` - معلومات المجموعة
▫️ `الروابط` - إعدادات الروابط
▫️ `الصور` - إعدادات الصور
▫️ `الفيديو` - إعدادات الفيديو
▫️ `الملفات` - إعدادات الملفات
▫️ `تغيير_رسالة_الترحيب [نص]` - تغيير رسالة الترحيب
▫️ `تغيير_رسالة_الوداع [نص]` - تغيير رسالة الوداع
▫️ `القوانين` - عرض قوانين المجموعة
▫️ `تغيير_القوانين [نص]` - تغيير قوانين المجموعة
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == f"{emojis['member']} أوامر الأعضاء")
def show_member_commands(message):
    commands_text = f"""
{emojis['member']} *أوامر الأعضاء:*

▫️ `ايدي` - عرض معلوماتك
▫️ `معلوماتي` - معلومات حسابك
▫️ `بينج` - اختبار سرعة البوت
▫️ `الرتبة` - عرض رتبتك
▫️ `النقاط` - عرض نقاطك
▫️ `التفاعل` - تفاعلك في المجموعة
▫️ `الاحصائيات` - إحصائيات استخدامك
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == f"{emojis['game']} أوامر الألعاب")
def show_game_commands(message):
    commands_text = f"""
{emojis['game']} *أوامر الألعاب:*

▫️ `لعبة حجر_ورقة_مقص` - لعبة كلاسيكية
▫️ `لعبة كرة_قدم` - لعبة كرة قدم
▫️ `لعبة سهم` - لعبة السهام
▫️ `لعبة سحب` - سحب عشوائي
▫️ `لعبة ذكاء` - اختبار ذكاء
▫️ `لعبة رياضيات` - مسائل رياضية
▫️ `لعبة كلمات` - لعبة الكلمات المتقاطعة
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == f"{emojis['search']} أوامر البحث")
def show_search_commands(message):
    commands_text = f"""
{emojis['search']} *أوامر البحث:*

▫️ `بحث يوتيوب [كلمة]` - بحث في يوتيوب
▫️ `تحميل يوتيوب [رابط]` - تحميل من يوتيوب
▫️ `بحث صور [كلمة]` - بحث عن صور
▫️ `بحث ويكيبيديا [كلمة]` - بحث في ويكيبيديا
▫️ `بحث جوجل [كلمة]` - بحث في جوجل
▫️ `الطقس [مدينة]` - حالة الطقس
▫️ `التاريخ` - التاريخ الهجري والميلادي
▫️ `الوقت` - الوقت الحالي
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == f"{emojis['settings']} الإعدادات")
def show_settings_commands(message):
    commands_text = f"""
{emojis['settings']} *أوامر الإعدادات:*

▫️ `اللغة` - تغيير لغة البوت
▫️ `الإشعارات` - إعدادات الإشعارات
▫️ `الحماية` - إعدادات الحماية
▫️ `الوضع_الليلي` - تفعيل الوضع الليلي
▫️ `الوضع_الصباحي` - تفعيل الوضع الصباحي
▫️ `المظهر` - تغيير مظهر البوت
"""
    bot.reply_to(message, commands_text, parse_mode='Markdown')

# --- أوامر الأعضاء الأساسية ---
@bot.message_handler(func=lambda message: message.text and (message.text.lower() in ['ايدي', 'id', 'معرف']))
def get_user_id(message):
    update_user_stats(message.from_user.id, 'id')
    
    user = message.from_user
    chat = message.chat
    
    info_text = f"""
{emojis['member']} *معلومات العضو:*
▫️ الاسم: {user.first_name} {user.last_name if user.last_name else ''}
▫️ المعرف: @{user.username if user.username else 'غير متوفر'}
▫️ آيدي المستخدم: `{user.id}`
▫️ آيدي الدردشة: `{chat.id}`
"""
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and (message.text.lower() in ['معلوماتي', 'myinfo']))
def get_my_info(message):
    update_user_stats(message.from_user.id, 'myinfo')
    
    user = message.from_user
    stats = user_stats.get(str(user.id), {})
    
    info_text = f"""
{emojis['info']} *معلومات حسابك:*
▫️ الاسم: {user.first_name} {user.last_name if user.last_name else ''}
▫️ المعرف: @{user.username if user.username else 'غير متوفر'}
▫️ تاريخ الانضمام: {stats.get('join_date', 'غير معروف')}
▫️ عدد التحذيرات: {stats.get('warnings', 0)}
▫️ الأوامر المستخدمة: {sum(stats.get('commands_used', {}).values())}
"""
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and (message.text.lower() in ['بينج', 'ping']))
def ping_command(message):
    update_user_stats(message.from_user.id, 'ping')
    
    start_time = time.time()
    sent_message = bot.reply_to(message, "Pong!")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 2)
    bot.edit_message_text(f"Pong! {ping_time}ms {emojis['clock']}", chat_id=sent_message.chat.id, message_id=sent_message.message_id)

# --- أوامر الإدارة ---
@bot.message_handler(func=lambda message: message.text and (message.text.lower().startswith('حظر') or message.text.lower().startswith('ban')))
def ban_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, f"{emojis['error']} أنت لست مشرفاً لتنفيذ هذا الأمر!")
        return
    
    update_user_stats(message.from_user.id, 'ban')
    
    command_parts = message.text.split()
    target_user = get_user_info(message, command_parts)
    if not target_user:
        bot.reply_to(message, f"{emojis['warn']} يرجى الرد على رسالة المستخدم أو كتابة آيديه بعد الأمر.")
        return
    
    if is_admin(message.chat.id, target_user.id):
        bot.reply_to(message, f"{emojis['error']} لا يمكنك حظر مشرف!")
        return
    
    duration_str, reason = extract_duration_and_reason(command_parts)
    duration = parse_time(duration_str)
    
    until_date = int(time.time()) + duration if duration > 0 else 0
    try:
        bot.ban_chat_member(message.chat.id, target_user.id, until_date=until_date)
        duration_text = format_time(duration)
        bot.reply_to(message, f"{emojis['ban']} تم حظر {target_user.first_name}\n⏰ المدة: {duration_text}\n📝 السبب: {reason}")
    except Exception as e:
        bot.reply_to(message, f"{emojis['error']} حدث خطأ أثناء الحظر: {e}")

# ... (أوامر الإدارة الأخرى بنفس النمط)

# --- أوامر الألعاب ---
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('لعبة حجر_ورقة_مقص'))
def rock_paper_scissors_game(message):
    update_user_stats(message.from_user.id, 'game_rps')
    
    choices = ["حجر", "ورقة", "مقص"]
    bot_choice = random.choice(choices)
    
    user_choice_raw = message.text.lower().replace('لعبة حجر_ورقة_مقص', '').strip()
    
    if user_choice_raw not in choices:
        bot.reply_to(message, f"{emojis['game']} يرجى اختيار إحدى هذه الخيارات: حجر، ورقة، مقص.")
        return

    result = ""
    if user_choice_raw == bot_choice:
        result = "تعادل!"
    elif (user_choice_raw == "حجر" and bot_choice == "مقص") or \
         (user_choice_raw == "ورقة" and bot_choice == "حجر") or \
         (user_choice_raw == "مقص" and bot_choice == "ورقة"):
        result = f"أنت فزت! {emojis['success']}"
    else:
        result = f"أنا فزت! {emojis['error']}"
    
    bot.reply_to(message, f"{emojis['game']} اخترت: **{user_choice_raw}**\nأنا اخترت: **{bot_choice}**\nالنتيجة: **{result}**", parse_mode='Markdown')

# --- أوامر البحث ---
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('بحث يوتيوب'))
def search_youtube(message):
    update_user_stats(message.from_user.id, 'search_yt')
    
    query = message.text[len('بحث يوتيوب'):].strip()
    if not query:
        bot.reply_to(message, f"{emojis['warn']} يرجى إدخال كلمة للبحث بعد الأمر.")
        return
    
    bot.reply_to(message, f"{emojis['search']} جاري البحث عن `{query}` في يوتيوب...")

# --- أوامر المطور ---
@bot.message_handler(func=lambda message: message.text and message.text.lower() == 'المطور')
def show_developer_info(message):
    update_user_stats(message.from_user.id, 'developer')
    
    developer_info = f"""
{emojis['dev']} *معلومات المطور:*
▫️ الاسم: {DEVELOPER_NAME}
▫️ يوزر التليجرام: {DEVELOPER_USERNAME}
▫️ آيدي المطور: `{DEVELOPER_ID}`
"""
    bot.reply_to(message, developer_info, parse_mode='Markdown')

# --- تشغيل البوت ---
if __name__ == "__main__":
    print("البوت يعمل...")
    bot.polling(none_stop=True)
