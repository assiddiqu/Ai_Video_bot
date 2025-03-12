import openai
import requests
import os
import random
import logging
import dropbox
from moviepy.editor import *
from elevenlabs import generate, save
from pexels_api import API
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import pysrt

# API Keys
BOT_TOKEN = "7851673153:AAFJwac1sejUqy4GdpI2iEjt3VgHWXjq3PE"
OPENAI_API_KEY = "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"
PEXELS_API_KEY = "TcQSFWhZgOZA1Dusqw4ykYfCpg7y4D6LysJOH2fUPENc6lA9tELK86kH"
ELEVENLABS_API_KEY = "sk_66ca479ce0017918780d712163a598cd46a86bf1222ac8e8"
DROPBOX_ACCESS_TOKEN = "sl.u.AFl8RXpsVakKUeK955_UpfNtgxdQCEl85SzsOX_WroR-NfK7_JFMiGrwW0_kowspnq6F4kgRvvOvmOue_DUv32A7UngpdYlIlq3xsDPG46pqdbvsyWMhNRWC0fdT69mY7ZP0yBXGmbycAZL5K3eqstzd2ksZaQo91WGA9U5dh4F4p6r1Ol4IkBFkD4THAcoY7UlmyZ4jF1hC1nRmudimta65dcZ8lUiF61zCYKwiJQKeMZNK1mPfPENlm8i1PfqISIKvx38UCjOAuJzGfOPQqp_WR7Y8BS2sl4RV5GdpclmO1PAEEMei2nwRSP05AS4NkfB_Jl23wkuo8zILKQX7kAsLC1QjtWAyJqdn_r1BrH8NCTcL5Ixuu3myiK8BPf21zdVdgZ9PqUY94wEDjz2yZ6ZpCSfamPQQFWP3zv9Pd7MEuMRYzG9jusm9tz648yDvXKDdWnTNqAuBM2KzX1nx5wdEL8oHtztk9hol7PG1GFm0RtC3trHaVi8HW7OWOvtUzVY906EDAw8DzL7_hPmDpKdjhMQxza1Sd1jGRQWPfuqV5mYo-3xyNRuTexqvAtrrSwHOr0HU2YnvjXthDFObftB99uQAC1Q4eGOK4yuubDE7L15jrgizHq9Dp1J4vEi-nRDIQWIHHWBnELi5etvwKeebvssfkyeBGc4428iKMrZLkHjbLJkHKztXIOgC3lFdgWXtE_ohIzOr2UKmNeakOBwYbPImVZWc6tmFm02lgxEUqqVycEhS06Ri20ySp88u46ZeiHpJKWccg3r6mwT6IZI1g9RCmn0ROmaCY1WmO4lhS3dYdQ_WxWJnnnmyZs-H1eSLIaslMk7q0uGZQjjiqfAUhAtvKNT84Q3unyEwYcQoU0ePQ6stvO8SOR_XzStFNZ44UDAannb5fi3jdy7TRI9Wqk9WvotV5RuyKq-h7Q6grY1ngWoY4CjpGyjr06dRyDzYpv_3HMiFwsAvHiHa6ObAXpMik499lJXScA-zaB4clmbmxeeKIwo48pKSBdmuT7juMEgHjwVapSY3yusDLgbgatfmUIqyiX_Q2lDfUirbHrJLS9e6xbrRLPLI-JZMl61T65oIiycmUyBCahAyr6A-A_wNnZ6TA85uqwAP2FG3yiWkkTx_XBlcS5YUYmUEm1jXTNh8kBIXDtxMVWma-zXzEEFT-wt7p6cNgkYmmGTw4iFfpybOy0wcg0c0tKG37m-FW-x9W4XDHNbd8Iq3WeKoAscD2z6pME4pv5JP11gXW1WkcriJa-zEIxkI2B_MQcZNtaUWXpKRELX6CmfYHLhDMx5RdO3pTjfpDiG2Iv_2ln4Z_2_DtWYco0jZ3qZPG9qTe-zj1SJQ_blytjpNVCjz-4ZLuXrQ-WTQylzY2XEWzC6TQZD237jp416d-F1kWFLgcR_nIQWOkvW8d5pm5e8I-bFU4AtkUR5D3WibBtlgqas92GqMa0nCcBwsqFGCuck"
BACKGROUND_MUSIC = "background.mp3"
LOGO_IMAGE = "logo.png"

# Logging
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# AI Script Generator
def generate_script(topic, language="en"):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": f"Generate a {language} video script about {topic}"}]
    )
    return response["choices"][0]["message"]["content"]

# AI Voiceover Generator
def generate_voiceover(script_text, voice="Bella", output_file="voice.mp3"):
    audio = generate(text=script_text, voice=voice, api_key=ELEVENLABS_API_KEY)
    save(audio, output_file)
    return output_file

# Fetch Images
def fetch_images(query, count=3):
    api = API(PEXELS_API_KEY)
    api.search(query)
    photos = api.get_entries()[:count]
    image_files = []

    for i, photo in enumerate(photos):
        img_data = requests.get(photo.original).content
        img_path = f"image_{i}.jpg"
        with open(img_path, "wb") as f:
            f.write(img_data)
        image_files.append(img_path)

    return image_files

# Generate Subtitles
def generate_subtitles(script_text, output_srt="subtitles.srt"):
    lines = script_text.split(". ")
    subs = []
    start_time = 0

    for i, line in enumerate(lines):
        end_time = start_time + 3
        subs.append(pysrt.SubRipItem(i + 1, start=start_time, end=end_time, text=line))
        start_time = end_time

    subs_obj = pysrt.SubRipFile(subs)
    subs_obj.save(output_srt)
    return output_srt

# Create AI Video with Effects
def create_video(image_files, voice_file, subtitles, output_video="output.mp4"):
    clips = []
    for img_path in image_files:
        img_clip = ImageClip(img_path).set_duration(3).fx(vfx.fadein, 1).fx(vfx.fadeout, 1).resize(width=1280)
        clips.append(img_clip)

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(voice_file)
    music = AudioFileClip(BACKGROUND_MUSIC).set_duration(audio.duration).volumex(0.3)

    # Add Subtitles
    txt_clips = []
    sub_file = pysrt.open(subtitles)
    for sub in sub_file:
        txt = TextClip(sub.text, fontsize=40, color='white', bg_color='black')
        txt = txt.set_position(('center', 'bottom')).set_duration(sub.duration.seconds).set_start(sub.start.ordinal / 1000)
        txt_clips.append(txt)

    final_video = CompositeVideoClip([video] + txt_clips)
    final_audio = CompositeAudioClip([audio, music])

    # Add Watermark (Logo)
    if os.path.exists(LOGO_IMAGE):
        logo = ImageClip(LOGO_IMAGE).set_duration(final_video.duration).resize(height=100).set_position(("right", "top"))
        final_video = CompositeVideoClip([final_video, logo])

    final_video = final_video.set_audio(final_audio)
    final_video.write_videofile(output_video, fps=30, codec="libx264")

# Upload to Dropbox
def upload_to_dropbox(file_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(file_path, "rb") as f:
        dbx.files_upload(f.read(), f"/{os.path.basename(file_path)}", mode=dropbox.files.WriteMode("overwrite"))
    shared_link = dbx.sharing_create_shared_link_with_settings(f"/{os.path.basename(file_path)}").url
    return shared_link.replace("?dl=0", "?dl=1")

# Telegram Bot Commands
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("👋 Welcome! Send me a topic, and I'll generate an AI video for you.")

def generate_video(update: Update, context: CallbackContext):
    topic = update.message.text
    update.message.reply_text(f"🎬 Generating video on: {topic}")

    # AI Processing
    script = generate_script(topic)
    voice_file = generate_voiceover(script)
    images = fetch_images(topic)
    subtitles = generate_subtitles(script)

    # Video Generation
    update.message.reply_text("🎥 Creating video, please wait...")
    create_video(images, voice_file, subtitles)

    # Upload to Dropbox
    dropbox_link = upload_to_dropbox("output.mp4")
    
    update.message.reply_text(f"✅ Video Created!\n[Download Video]({dropbox_link})", parse_mode="Markdown")

# Telegram Bot Setup
def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, generate_video))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
