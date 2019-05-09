#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Raspberry Pi のカメラで撮影を行い，サーバーにアップロードします

from datetime import datetime

print('{} SCRIPT Start.'.format(datetime.now()), flush=True)

import os
import time
import subprocess

# print('{} Loading paramiko...'.format(datetime.now()), flush=True)
# import paramiko

print('{} Loading GPIO...'.format(datetime.now()), flush=True)
import RPi.GPIO as GPIO

print('{} Loading PiCamera...'.format(datetime.now()), flush=True)
from picamera import PiCamera

TMP_FILE_PATH = '/dev/shm/camera_uid_{}.jpg'.format(os.getuid())
IMAGE_NAME_FORMAT = 'camera-%Y%m%d_%H%M.jpg'

SSH_HOST = '192.168.2.20'
SSH_USER = 'guest'
SSH_KEY  = '/home/pi/.ssh/guest.id_rsa'

SSH_CMD  = 'ssh -i {key} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no {user}@{host}'
SCP_CMD  = 'scp -i {key} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -q {from_file_path} {user}@{host}:{to_file_path}'

GPIO_DONE= 23

# NOTE: paramiko は重い(Raspberry Pi Zero W だと import に 10秒近くかかる)ので使わない
# def upload(from_file_path):
#     while True:
#         try:
#             with paramiko.SSHClient() as ssh:
#                 ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#                 ssh.connect(hostname=SSH_HOST, port=22,
#                             username=SSH_USER,
#                             pkey=paramiko.RSAKey.from_private_key_file(SSH_KEY))

#                 # NOTE: この時点で時刻が NTP で同期されていない可能性
#                 # があるので，リモートで date を使ってファイル名を生成する
#                 ssh_stdout = ssh.exec_command('date "+%Y%m%d_%H%M"')[1]
#                 to_file_path = 'camera-{}.jpg'.format(ssh_stdout.read().decode().strip())

#                 ftp_client = ssh.open_sftp()
#                 ftp_client.put(from_file_path, to_file_path)
#                 ftp_client.close()
#             break
#         except:
#             pass
#         time.sleep(1)

def upload(from_file_path):
    while True:
        try:
            proc = subprocess.run(
                [ *(SSH_CMD.format(host=SSH_HOST,user=SSH_USER,key=SSH_KEY).split(' ')),
                  'date "+%Y%m%d_%H%M"' ],
                stdout = subprocess.PIPE,
                check = True
            )
            to_file_path = 'camera-{}.jpg'.format(proc.stdout.decode('utf-8').strip())

            subprocess.run(
                SCP_CMD.format(host=SSH_HOST,user=SSH_USER,key=SSH_KEY,
                               from_file_path=from_file_path,to_file_path=to_file_path).split(' '),
                check = True
            )
            break
        except:
            pass
        time.sleep(1)


def capture():
    image_path = TMP_FILE_PATH
    camera = PiCamera()
    camera.resolution = (3280, 2464)
    camera.iso = 100
    
    camera.capture(image_path, quality=100)

    return image_path

def notify_dine():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_DONE, GPIO.OUT)
    GPIO.output(GPIO_DONE, GPIO.HIGH)


print('{} START capture...'.format(datetime.now()), flush=True)
image_path = capture()
print('{} START upload...'.format(datetime.now()), flush=True)
upload(image_path)
print('{} FINISH.'.format(datetime.now()), flush=True)
notify_dine()
