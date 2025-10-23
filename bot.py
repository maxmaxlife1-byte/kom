import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Your environment variables
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
RUNPOD_ENDPOINT = os.environ["RUNPOD_ENDPOINT"]
RUNPOD_KEY = os.environ["RUNPOD_KEY"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Hi! Send /generate <your prompt> to create an image.")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates an image based on the user's prompt."""
    if not context.args:
        await update.message.reply_text("Please provide a prompt after the command. \nExample: /generate a cat wearing a wizard hat")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text(f"🚀 Generating image for: \"{prompt}\". Please wait...")

    headers = {
        "Authorization": f"Bearer {RUNPOD_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"input": {"prompt": prompt, "width": 1024, "height": 1024}}

    try:
        # Use a synchronous call to wait for the result
        response = requests.post(RUNPOD_ENDPOINT, headers=headers, json=payload, timeout=300)
        response.raise_for_status()  # This will raise an error for bad status codes (4xx or 5xx)
        data = response.json()

        # Extract the image URL from the RunPod response
        output = data.get("output", data)
        image_url = output.get("image_url")

        if not image_url:
            await update.message.reply_text(f"❌ Generation failed. The API did not return an image URL. Response: {output}")
            return

        # Send the image back to the user
        await update.message.reply_photo(photo=image_url, caption=f"✨ Here is your image!")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ An error occurred while contacting the generation service: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ An unexpected error occurred: {e}")

def main():
    """Starts the bot."""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))

    # Start the Bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()