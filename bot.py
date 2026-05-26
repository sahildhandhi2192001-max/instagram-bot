from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

from instagrapi import Client
from dotenv import load_dotenv

import requests
import os

# =====================================
# LOAD ENV VARIABLES
# =====================================
load_dotenv()

# =====================================
# TELEGRAM BOT TOKEN
# =====================================
TOKEN = os.getenv("BOT_TOKEN")

# =====================================
# INSTAGRAM LOGIN
# =====================================
cl = Client()

cl.load_settings("session.json")

# =====================================
# MAIN FUNCTION
# =====================================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # REMOVE TRACKING PARAMETERS
    if "?" in text:
        text = text.split("?")[0]

    # =====================================
    # POST / REEL DOWNLOAD
    # =====================================
    if (
        "instagram.com/p/" in text
        or
        "instagram.com/reel/" in text
    ):

        msg = await update.message.reply_text(
            "Downloading media..."
        )

        try:

            media_pk = cl.media_pk_from_url(text)

            media = cl.media_info(media_pk)

            # =================================
            # VIDEO / REEL
            # =================================
            if media.media_type == 2:

                video_path = cl.video_download(
                    media_pk,
                    folder="downloads"
                )

                await update.message.reply_video(
                    video=open(video_path, "rb")
                )

            # =================================
            # IMAGE / CAROUSEL POST
            # =================================
            else:

                # CAROUSEL POST
                if media.media_type == 8:

                    resources = media.resources

                    for item in resources:

                        # IMAGE ONLY
                        if item.media_type == 1:

                            image_url = item.thumbnail_url

                            img = requests.get(image_url)

                            filename = "carousel.jpg"

                            with open(filename, "wb") as f:
                                f.write(img.content)

                            await update.message.reply_photo(
                                photo=open(filename, "rb")
                            )

                # SINGLE IMAGE POST
                else:

                    photo_path = cl.photo_download(
                        media_pk,
                        folder="downloads"
                    )

                    await update.message.reply_photo(
                        photo=open(photo_path, "rb")
                    )

            await msg.delete()

        except Exception as e:

            await update.message.reply_text(
                f"Error: {e}"
            )

    # =====================================
    # PROFILE LINK
    # =====================================
    elif "instagram.com/" in text:

        msg = await update.message.reply_text(
            "Downloading HD profile picture..."
        )

        try:

            username = text.replace(
                "https://www.instagram.com/",
                ""
            ).replace("/", "").strip()

            user_id = cl.user_id_from_username(
                username
            )

            user_info = cl.user_info(user_id)

            dp_url = str(
                user_info.profile_pic_url_hd
            )

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            img = requests.get(
                dp_url,
                headers=headers
            )

            with open("hd_dp.jpg", "wb") as f:
                f.write(img.content)

            await update.message.reply_photo(
                photo=open("hd_dp.jpg", "rb")
            )

            await msg.delete()

        except Exception as e:

            await update.message.reply_text(
                f"Error: {e}"
            )

    # =====================================
    # USERNAME ONLY
    # =====================================
    else:

        msg = await update.message.reply_text(
            "Downloading HD profile picture..."
        )

        try:

            user_id = cl.user_id_from_username(
                text
            )

            user_info = cl.user_info(user_id)

            dp_url = str(
                user_info.profile_pic_url_hd
            )

            img = requests.get(dp_url)

            with open("hd_dp.jpg", "wb") as f:
                f.write(img.content)

            await update.message.reply_photo(
                photo=open("hd_dp.jpg", "rb")
            )

            await msg.delete()

        except Exception:

            await update.message.reply_text(
                "Send valid Instagram link or username."
            )


# =====================================
# CREATE BOT
# =====================================
app = (
    ApplicationBuilder()
    .token(TOKEN)
    .read_timeout(120)
    .write_timeout(120)
    .connect_timeout(120)
    .pool_timeout(120)
    .build()
)

# =====================================
# HANDLER
# =====================================
app.add_handler(
    MessageHandler(filters.TEXT, reply)
)

print("Instagram Bot Running...")

# =====================================
# START BOT
# =====================================
app.run_polling()