from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

import yt_dlp
import os
import glob
import traceback

TOKEN = "8475164533:AAEf2A6J_uueZ5QCPOaK9_joq0T4d1dlt-g"

# CREATE DOWNLOADS FOLDER
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# MAIN FUNCTION
progress_message = None

def progress_hook(d):

    if d['status'] == 'downloading':

        percent = d.get('_percent_str', '0%')

        print(f"Downloading {percent}")

    elif d['status'] == 'finished':

        print("Download finished")
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        text = update.message.text.strip()

        print("MESSAGE RECEIVED:")
        print(text)

        # REMOVE EXTRA PARAMETERS
        if "?" in text:
            text = text.split("?")[0]

        await update.message.reply_text(
            "Downloading..."
        )

        # DELETE OLD FILES
        old_files = glob.glob("downloads/*")

        for file in old_files:
            os.remove(file)

        # yt-dlp settings
        ydl_opts = {
            "progress_hooks": [progress_hook],
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": False,
            "noplaylist": False,
            "extract_flat": False,
        }

        # DOWNLOAD
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            try:

                info = ydl.extract_info(
                    text,
                    download=True
                )

                print(info)

            except Exception as e:

                print("DOWNLOAD ERROR:")
                print(e)

                await update.message.reply_text(
                    "Photo posts are currently unsupported."
                )

                return

        # FIND FILES
        files = glob.glob("downloads/*")

        print("DOWNLOADED FILES:")
        print(files)

        # NO FILES FOUND
        if not files:

            await update.message.reply_text(
                "Could not download media."
            )

            return

        # SEND FILES
        for file_path in files:

            print("SENDING:")
            print(file_path)

            # VIDEO
            if file_path.lower().endswith(
                (
                    ".mp4",
                    ".mov",
                    ".mkv"
                )
            ):

                with open(file_path, "rb") as video:

                    await update.message.reply_video(
                        video=video
                    )

            # IMAGE
            elif file_path.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                    ".bmp"
                )
            ):

                with open(file_path, "rb") as photo:

                    await update.message.reply_photo(
                        photo=photo
                    )

        await update.message.reply_text(
            "Done."
        )

    except Exception as e:

        print("ERROR:")
        print(e)

        traceback.print_exc()

        await update.message.reply_text(
            f"ERROR:\n{e}"
        )

# CREATE BOT
app = ApplicationBuilder().token(TOKEN).build()

# HANDLER
app.add_handler(
    MessageHandler(filters.TEXT, reply)
)

print("Bot Running...")
print("Waiting for messages...")

# START BOT
app.run_polling()