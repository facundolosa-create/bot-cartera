import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from analyzer import analyze_portfolio, format_portfolio_report, format_single_report
from config import PORTFOLIO

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def authorized(update: Update) -> bool:
    if not ALLOWED_USER_ID:
        return True
    return str(update.effective_user.id) == str(ALLOWED_USER_ID)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    await update.message.reply_text(
        "🤖 Bot de Cartera — Etapa 1\n\n"
        "Comandos:\n"
        "/analizar — analiza toda la cartera\n"
        "/posiciones — muestra las posiciones configuradas\n"
        "/help — ayuda\n\n"
        "Las señales son técnicas y no ejecutan operaciones."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    await start(update, context)

async def posiciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    lines = ["📋 POSICIONES CONFIGURADAS\n"]
    for p in PORTFOLIO:
        lines.append(f"• {p['name']} ({p['ticker']}) — {p['quantity']}")
    await update.message.reply_text("\n".join(lines))

async def analizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    msg = await update.message.reply_text("⏳ Analizando mercado y calculando indicadores...")
    try:
        results = analyze_portfolio(PORTFOLIO)
        report = format_portfolio_report(results)
        # Telegram has a message limit; split conservatively.
        chunks = [report[i:i+3800] for i in range(0, len(report), 3800)]
        await msg.edit_text(chunks[0])
        for chunk in chunks[1:]:
            await update.message.reply_text(chunk)
    except Exception as e:
        logging.exception("Error analizando cartera")
        await msg.edit_text(
            "❌ No pude completar el análisis.\n"
            f"Detalle: {str(e)[:500]}"
        )

async def ticker_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return
    if not context.args:
        await update.message.reply_text("Uso: /ticker GOOGL")
        return
    symbol = context.args[0].upper()
    found = next((p for p in PORTFOLIO if p["ticker"] == symbol), None)
    if not found:
        await update.message.reply_text(
            f"{symbol} no está configurado en la cartera.\n"
            "Usá /posiciones para ver los activos."
        )
        return
    try:
        result = analyze_portfolio([found])[0]
        await update.message.reply_text(format_single_report(result))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:500]}")

def main():
    if not TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en el archivo .env")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("analizar", analizar))
    app.add_handler(CommandHandler("posiciones", posiciones))
    app.add_handler(CommandHandler("ticker", ticker_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
