import json
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
# CREDS_JSON = os.getenv("CREDS_JSON")

# creds_dict = json.loads(CREDS_JSON)
creds_dict = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY"),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN")
}

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# الآن نقرأ كل القيم كقائمة قوائم
all_values = sheet.get_all_values()
headers = all_values[0]
data_rows = all_values[1:]

user_states = {}
TOKEN = "8020773258:AAHY88ZtYg816ktYkx-DWPPT8cImzivfWEg"

def strip_international_prefix(phone):
    phone = phone.strip()
    if phone.startswith('+'):
        return phone[1:]
    elif phone.startswith('00'):
        return phone[2:]
    else:
        return phone

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_username = update.effective_user.username
    if not tg_username:
        await update.message.reply_text("يرجى ضبط اسم المستخدم في تيليجرام الخاص بك ثم إعادة المحاولة.")
        return

    matched = next(
        (row for row in data_rows if row[3].replace('@', '').strip().lower() == tg_username.lower()),
        None
    )

    if matched:
        name = matched[0]  # العمود A
        academic_id = matched[4]  # العمود E

        message = (
            f"🌸 *حياكِ الله يا طيبة*\n\n"
            f"👩‍🔬 *مهندسة الأجيال:* `{name}`\n"
            f"🎓 *الرقم الأكاديمي:* `{academic_id}`\n\n"
            f"📝 يرجى *الاحتفاظ برقمك الأكاديمي* ونسخه مباشرة عند الحاجة بدلاً من كتابته يدويًا لضمان الدقة وتفادي الأخطاء.\n"
            f"📋 يمكنك النسخ بسهولة عبر الضغط المطوّل على الرقم.\n\n"
            f"🔁 *ملاحظة:* إذا كنتِ طالبة سابقة، تأكدي من *مطابقة الرقم الأكاديمي* لرقمك السابق.\n\n"
            f"📩 في حال وجود مشكلة بالبيانات يمكنكِ التواصل عبر: [اضغطي هنا للتواصل](https://t.me/AJYACADST_BOT)\n\n"
            f"🤍 *نتمنى لكِ رحلة موفقة ومباركة*"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        user_states[update.effective_user.id] = 'awaiting_contact'
        await update.message.reply_text(
            "مهندستنا الغالية،\n\n"
            "لم نتمكّن من العثور على اسم المستخدم (معرّف تيليجرام) الخاص بك.\n\n"
            "للمساعدة في العثور على رقمك الأكاديمي، يُرجى إرسال أحد الخيارين التاليين بشكل صحيح:\n\n"
            "1. البريد الإلكتروني الذي تم استخدامه عند تعبئة استمارة التسجيل.\n"
            "أو\n"
            "2. رقم الهاتف المرتبط بتطبيق واتساب، مكتوبًا مع رمز الدولة (من دون كتابة \"+\" أو \"00\") في بداية الرقم، تمامًا كما تم إدخاله في استمارة التسجيل.\n\n"
            "📌 أمثلة على الشكل الصحيح لكتابة الرقم:\n"
            "المغرب: 21276132676\n"
            "الأردن: 962780144811\n"
            "السعودية: 966576064723\n\n"
            "🔹 ملاحظة مهمة:\n"
            "إذا لم تقومي بكتابة رمز الدولة في الاستمارة، يُرجى إدخال الرقم تمامًا كما كتبتيه أثناء التسجيل، أو تجربة البريد الإلكتروني بدلًا من ذلك.\n\n"
            "🔁 يُرجى المحاولة أكثر من مرة، وفي حال لم يتم العثور على البيانات، يُرجى الرجوع إلى تعليمات الإدارة المرفقة مع منشور الرقم الأكاديمي على قناة الطالبات.\n"
            "📌 هذا البوت ردّه آلي ولا يستقبل الاستفسارات.\n\n"
            "مع أطيب الأمنيات بالتوفيق 🌷"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_states.get(user_id) != 'awaiting_contact':
        await update.message.reply_text("اضغطي على /start لبدء التحقق.")
        return

    input_text = update.message.text.strip().lower()

    matched = None
    for row in data_rows:
        email = row[1].strip().lower()
        phone = strip_international_prefix(row[2].strip()).lower()
        if input_text == email or input_text == phone:
            matched = row
            break

    if matched:
        name = matched[0]
        academic_id = matched[4]
        row_index = data_rows.index(matched) + 2

        tg_username = update.effective_user.username
        if tg_username:
            sheet.update_cell(row_index, 6, f"@{tg_username}")  # عمود F

        message = (
            f"🌸 *حياكِ الله يا طيبة*\n\n"
            f"👩‍🔬 *مهندسة الأجيال:* `{name}`\n"
            f"🎓 *الرقم الأكاديمي:* `{academic_id}`\n\n"
            f"📝 يرجى *الاحتفاظ برقمك الأكاديمي* ونسخه مباشرة عند الحاجة بدلاً من كتابته يدويًا لضمان الدقة وتفادي الأخطاء.\n"
            f"📋 يمكنك النسخ بسهولة عبر الضغط المطوّل على الرقم.\n\n"
            f"🔁 *ملاحظة:* إذا كنتِ طالبة سابقة، تأكدي من *مطابقة الرقم الأكاديمي* لرقمك السابق.\n\n"
            f"📩 في حال وجود مشكلة بالبيانات يمكنكِ التواصل عبر: [اضغطي هنا للتواصل](https://t.me/AJYACADST_BOT)\n\n"
            f"🤍 *نتمنى لكِ رحلة موفقة ومباركة*"
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        user_states.pop(user_id)
    else:
        await update.message.reply_text(
            "📌 لم يتم العثور على بيانات مطابقة لما أرسلتيه.\n\n"
            "يرجى التأكد مما يلي:\n"
            "1. أنكِ أرسلتي *البريد الإلكتروني* أو *رقم الهاتف المرتبط بالواتساب* والذي أدخلتيه أثناء تعبئة استمارة التسجيل.\n"
            "2. في حالة إرسال رقم الهاتف، تأكدي من كتابته *مع رمز الدولة*، ولكن *دون كتابة \"+\" أو \"00\"* في بدايته.\n\n"
            "📞 أمثلة صحيحة:\n"
            "- الأردن: 962780144811\n"
            "- السعودية: 966512345678\n"
            "- المغرب: 212611223344\n\n"
            "✉️ أو أرسلي بريدك الإلكتروني بدلاً من الرقم إن وُجد.\n\n"
            "📌 هذا البوت ردّه آلي ولا يستقبل الاستفسارات.\n\n"
            "🔁 بإمكانكِ المحاولة مرة أخرى، وإذا تعذّر الوصول، يُرجى مراجعة التعليمات في منشور الرقم الأكاديمي أو التواصل عبر المجموعة التفاعلية في حال استمرار المشكلة.",
            parse_mode='Markdown'
        )

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
