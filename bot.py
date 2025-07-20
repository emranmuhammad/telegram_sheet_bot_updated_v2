
import gspread
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
import json
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
CREDS_JSON = os.getenv("CREDS_JSON")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds_dict = json.loads(CREDS_JSON)


creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

ASK_CONTACT = 1

def find_by_column(value: str, col: int):
    try:
        cell = sheet.find(value.strip().lower(), in_column=col, case_sensitive=False)
        return cell.row
    except gspread.exceptions.CellNotFound:
        return None

async def send_academic_number(chat_id: int, row: int, app: Application):
    name    = sheet.cell(row, 1).value
    acad_no = sheet.cell(row, 5).value
    await app.bot.send_message(
        chat_id,
        text=(
            f"حياكِ الله يا طيبة،\n"
            f"نبارك لكِ انضمامكِ إلى دفعة \"السناء\" ضمن دبلوم هندسة الأجيال - الدفعة السابعة.\n\n"
            f"🌸 مهندسة الأجيال: {name}\n"
            f"🎓 الرقم الأكاديمي: {acad_no}\n\n"
            f"يرجى الاحتفاظ برقمك الأكاديمي ونسخه مباشرة عند الحاجة بدلاً من كتابته يدوياً لضمان الدقة وتفادي الأخطاء.\n\n"
            f"🔁 ملاحظة: إذا كنتِ طالبة سابقة، تأكدي من مطابقة الرقم الأكاديمي لرقمك السابق.\n"
            f"في حال وجود مشكلة بالبيانات يمكنكِ التواصل عبر: https://t.me/AJYACADST_BOT\n\n"
            f"نتمنى لكِ رحلة موفقة ومباركة 🤍"
        )
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = (update.effective_user.username or "").lower()
    row = find_by_column(username, 4)

    if row:
        await send_academic_number(update.effective_chat.id, row, context.application)
        return ConversationHandler.END

    await update.message.reply_text(
        "مرحبًا بكِ يا مهندسة الأجيال 💛\n\n"
        "يبدو أن معرف التيليجرام الخاص بك غير مسجّل بشكل صحيح في استمارة التسجيل.\n"
        "أرسلي الإيميل أو رقم هاتف الواتس (مع وضع رمز الدولة) بالضبط كما وضعته في استمارة التسجيل، وسأتحقق من بياناتك مباشرة بإذن الله 🤍"
    )
    return ASK_CONTACT

async def ask_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    row = find_by_column(user_input, 2) or find_by_column(user_input, 3)

    if row:
        if update.effective_user.username:
            sheet.update_cell(row, 4, update.effective_user.username.lower())
        await send_academic_number(update.effective_chat.id, row, context.application)
    else:
        await update.message.reply_text(
            "عذرًا لم أستطع العثور على بياناتك. "
            "يرجى التأكد من صحة الإيميل أو رقم الهاتف، أو التواصل مع الإدارة."
        )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الإلغاء. في خدمتكِ دائمًا 🌸")
    return ConversationHandler.END

logging.basicConfig(level=logging.INFO)
app = Application.builder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contact)]},
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)

if __name__ == "__main__":
    app.run_polling()
