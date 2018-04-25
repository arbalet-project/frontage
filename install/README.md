# Installation


```
sudo apt install docker-compose avahi-daemon openssh-server
sudo adduser arbalet docker
sudo apt install python3-pip
sudo pip3 install pika numpy
sudo pip3 install --no-cache-dir git+https://github.com/arbalet-project/python-artnet.git

mkdir ~/Arbalet && cd ~/Arbalet
git clone http://github.com/arbalet-project/frontage.git

cd frontage/install

sudo ln -fs /etc/systemd/system/autologin@.service /etc/systemd/system/getty.target.wants/getty@tty1.service
sudo systemctl set-default multi-user.target
sudo cp arbalet.service /lib/systemd/system/
sudo cp artnet.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable arbalet.service
sudo systemctl enable artnet.service

sudo systemctl edit artnet  # Add a [Service] section with the 2 rabbitMQ credential strings

sudo cp interfaces /etc/network/interfaces
sudo apt install dnsmasq
sudo cp dnsmasq.conf /etc/dnsmasq.conf
sudo cp hosts /etc/hosts
sudo cp hostname /etc/hostname

sudo reboot
```

Following commands are useful to manager services:
```
sudo service arbalet stop
sudo service arbalet start
sudo systemctl status arbalet.service
sudo journalctl -u arbalet -f
```
