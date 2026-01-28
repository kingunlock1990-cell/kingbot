from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 8429077668   # <-- apni Telegram ID yahan dalo

approved_users = set()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 You are ADMIN")
        return

    if user_id not in approved_users:
        await update.message.reply_text(
            "⏳ Your access is pending approval.\nPlease wait for admin approval."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 New approval request\n\n👤 User ID: `{user_id}`\n\nApprove using:\n/approve {user_id}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("✅ You are approved. Send serial number.")

# Admin approve command
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])
        approved_users.add(user_id)

        await update.message.reply_text(f"✅ User {user_id} approved")

        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 You are approved!\nNow you can send serial numbers."
        )
    except:
        await update.message.reply_text("❌ Usage: /approve USER_ID")

# Serial handler
async def handle_serial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    serial = update.message.text.strip()

    if user_id != ADMIN_ID and user_id not in approved_users:
        await update.message.reply_text("⛔ You are not approved yet.")
        return

    url = f"https://dnuativador.com/api/registerA12.php?dnu=UTO&serial={serial}"

    try:
        r = requests.get(url, timeout=10)
        text = r.text.lower()

        if "already" in text:
            await update.message.reply_text(
                f"⚠️ Already Registered\n🔑 Serial: {serial}"
            )
        elif r.status_code == 200:
            await update.message.reply_text(
                f"✅ Successfully Registered\n🔑 Serial: {serial}"
            )
        else:
            await update.message.reply_text("❌ Registration Failed")

    except:
        await update.message.reply_text("⚠️ Server Error")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_serial))

app.run_polling()
