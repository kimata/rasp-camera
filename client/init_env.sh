#!/usr/bin/env zsh

pkg_list=(python3-paramiko python3-picamera)

echo "Start setting..."

for pkg in ${pkg_list};
do
    echo "Install ${pkg}"
    sudo apt install -y ${pkg}
done

sudo raspi-config nonint do_camera 0

sudo ln -sf $(cd $(dirname $0); pwd)/capture.service /etc/systemd/system/capture.service
sudo systemctl enable capture.service

echo "Finish."
