from telebot import TeleBot
from dotenv import load_dotenv
import os
from pdf2docx import Converter
import subprocess

load_dotenv(override=True)
TOKEN = os.environ.get("BOT_TOKEN")

allowed_users_str = os.getenv("ALLOWED_USERS", "")
allowed_users = [int(u.strip())
                 for u in allowed_users_str.split(",") if u.strip()]
bot = TeleBot(TOKEN, parse_mode=None)

os.makedirs("./converted", exist_ok=True)
os.makedirs("./downloaded", exist_ok=True)


def convert_document(input_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    output_file = None

    if ext in [".doc", ".docx", ".odt"]:
        output_file = os.path.join(output_dir, f"{name}.pdf")
        subprocess.run(["libreoffice", "--headless", "--convert-to",
                       "pdf", "--outdir", output_dir, input_path], check=True)

    elif ext == ".pdf":
        try:
            output_file = os.path.join(output_dir, f"{name}.docx")
            cv = Converter(input_path)
            cv.convert(output_file, start=0, end=None)
            cv.close()
        except Exception:
            subprocess.run(["libreoffice", "--headless", "--convert-to",
                           "odt", "--outdir", output_dir, input_path], check=True)
            odt_file = os.path.join(output_dir, f"{name}.odt")
            subprocess.run(["libreoffice", "--headless", "--convert-to",
                           "docx", "--outdir", output_dir, odt_file], check=True)
            output_file = os.path.join(output_dir, f"{name}.docx")

    elif ext in [".ppt", ".pptx", ".odp"]:
        output_file = os.path.join(output_dir, f"{name}.pdf")
        subprocess.run(["libreoffice", "--headless", "--convert-to",
                       "pdf", "--outdir", output_dir, input_path], check=True)

    elif ext in [".jpg", ".jpeg", ".png"]:
        output_file = convert_image(input_path, output_dir)
        return output_file

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    for f in os.listdir(output_dir):
        if f.startswith(name):
            return os.path.join(output_dir, f)

    raise FileNotFoundError(f"Conversion failed for {input_path}")


def convert_image(input_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path)
    name, _ = os.path.splitext(filename)
    output_file = os.path.join(output_dir, f"{name}.pdf")

    subprocess.run(["libreoffice", "--headless", "--convert-to",
                   "pdf", "--outdir", output_dir, input_path], check=True)

    for f in os.listdir(output_dir):
        if f.startswith(name):
            return os.path.join(output_dir, f)

    raise FileNotFoundError(f"Image conversion failed for {input_path}")


def check_user(message):
    if len(allowed_users) == 0:
        return True
    elif message.from_user.id not in allowed_users:
        bot.send_message(message.from_user.id,
                         "Sorry, you don't have access to this bot.")
        return False
    return True


@bot.message_handler(content_types=["document"])
def handle_document(message):
    if not check_user(message):
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    input_path = os.path.join("downloaded", file_name)

    with open(input_path, "wb") as new_file:
        new_file.write(downloaded_file)

    ext = os.path.splitext(file_name)[1].lower()

    if ext in [".doc", ".docx", ".odt"]:
        bot.send_message(
            message.chat.id, "Word document received. Converting to PDF...")
    elif ext in [".pdf"]:
        bot.send_message(
            message.chat.id, "PDF document received. Converting to Word...")
    elif ext in [".ppt", ".pptx", ".odp"]:
        bot.send_message(
            message.chat.id, "PowerPoint document received. Converting to PDF...")
    elif ext in [".jpg", ".jpeg", ".png"]:
        bot.send_message(
            message.chat.id, "Image document received. Converting to PDF...")
    else:
        bot.send_message(message.chat.id, "Unsupported file type.")
        return

    try:
        output_path = convert_document(input_path, "converted")
        with open(output_path, "rb") as f:
            bot.send_document(message.chat.id, f)
    except Exception as e:
        bot.send_message(message.chat.id, f"Conversion failed: {e}")

    try:
        os.remove(input_path)
        os.remove(output_path)
    except Exception:
        pass


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    if not check_user(message):
        return

    bot.send_message(message.chat.id, "Image received. Converting to PDF...")

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = f"photo_{message.photo[-1].file_id}.jpg"
    input_path = os.path.join("downloaded", file_name)

    with open(input_path, "wb") as new_file:
        new_file.write(downloaded_file)

    try:
        output_path = convert_image(input_path, "converted")
        with open(output_path, "rb") as f:
            bot.send_document(message.chat.id, f)
    except Exception as e:
        bot.send_message(message.chat.id, f"Image conversion failed: {e}")

    try:
        os.remove(input_path)
        os.remove(output_path)
    except Exception:
        pass


bot.infinity_polling()
