# Installation


```
sudo apt install docker-compose avahi-daemon openssh-server
sudo adduser arbalet docker

mkdir ~/Arbalet && cd ~/Arbalet
git clone http://github.com/arbalet-project/frontage.git
cd frontage/install

sudo ln -fs /etc/systemd/system/autologin@.service /etc/systemd/system/getty.target.wants/getty@tty1.service
sudo systemctl set-default multi-user.target
sudo cp arbalet.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable arbalet.service

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
