#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Raspberry Pi のカメラで撮影を行い，サーバーにアップロードします

import os
import paramiko
import scp
from picamera import PiCamera
from datetime import datetime

TMP_FILE_PATH = '/run/user/{}/camera.jpg'.format(os.getuid())
IMAGE_NAME_FORMAT = 'camera-%Y%m%d_%H%M.jpg'

SSH_HOST = '192.168.2.20'
SSH_USER = 'guest'
SSH_KEY  = 'guest.id_rsa'

def upload(from_file_path, to_file_path):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=SSH_HOST, port=22,
                    username=SSH_USER,
                    pkey=paramiko.RSAKey.from_private_key_file(SSH_KEY))

        scp.SCPClient(ssh.get_transport()).put(from_file_path, to_file_path)

def capture():
    image_path = TMP_FILE_PATH
    camera = PiCamera()
    camera.resolution = (3280, 2464)
    camera.iso = 100
    
    camera.capture(image_path, quality=100)

    return image_path

image_path = capture()
upload(image_path, datetime.now().strftime(IMAGE_NAME_FORMAT))
