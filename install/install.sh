#!/bin/bash
# script to install easily arbalet server
# has to be execute as root

# GLOBAL VARIABLES
username=`whoami`
logname=`logname`
directory=`pwd`

##   Package Manager variables
distrib=`cat /etc/*-release | grep ^NAME | sed 's/NAME=\"\(.*\)\"/\1/'`
package_manager=pkgmanager
install_cmd=install
list_cmd=list
end_chr=""
pip=pip

##   Package Requirements
pkg_list="git \
          docker \
          docker-compose \
          python \
          python-pip \
          python-pika \
          python-numpy \
          makepasswd \
          net-tools \
          netplan.io \
          openssh-server \
          "
          #ufw \
pkg_to_install=""

# FUNCTIONS

# find the package manager corresponding to the linux distribution
# and adjust the parameter corresponding to it
function get_pkgmanager {
  case $1 in
    "Arch Linux" )
    package_manager=pacman
    install_cmd="-S"
    list_cmd="-Q"
    end_chr="\ "
    pip=pip
    ;;
    "Ubuntu" )
    package_manager="apt"
    install_cmd="install -y "
    list_cmd="list --installed"
    end_chr="/"
    pip=pip3
    for var in $pkg_list; do
      tmp+=`echo $var | sed 's/python/python3/'`
      tmp+=" "
    done
    pkg_list=$tmp
    ;;
  esac
}

# configure the firewall ufw
# if the first argument is not "yes" ufw will be stopped
# and disabled. Otherwise, the range of ipv4 from
# 192.168.0.32 to 192.168.0.127 will be granted acces on
# 22 (ssh), 53 (dns), 67 (dhcp), 80 (http) and 443 (https) ports
function ufw_config {
  if [[ "$1" != "y" ]]; then
    systemctl stop ufw
    systemctl disable ufw
  else
    # Configuration of firewall
    # Range allow to pass : 192.168.0.32 to 192.168.0.127
    ufw allow proto tcp from 192.168.0.32/27 to any port 22
    ufw allow proto tcp from 192.168.0.32/27 to any port 53
    ufw allow proto tcp from 192.168.0.32/27 to any port 67
    ufw allow proto tcp from 192.168.0.32/27 to any port 80
    ufw allow proto tcp from 192.168.0.32/27 to any port 443
    ufw allow proto tcp from 192.168.0.64/27 to any port 22
    ufw allow proto tcp from 192.168.0.64/27 to any port 53
    ufw allow proto tcp from 192.168.0.64/27 to any port 67
    ufw allow proto tcp from 192.168.0.64/27 to any port 80
    ufw allow proto tcp from 192.168.0.64/27 to any port 443
    ufw allow proto tcp from 192.168.0.96/27 to any port 22
    ufw allow proto tcp from 192.168.0.96/27 to any port 53
    ufw allow proto tcp from 192.168.0.96/27 to any port 67
    ufw allow proto tcp from 192.168.0.96/27 to any port 80
    ufw allow proto tcp from 192.168.0.96/27 to any port 443

    ufw allow proto udp from 192.168.0.32/27 to any port 22
    ufw allow proto udp from 192.168.0.32/27 to any port 53
    ufw allow proto udp from 192.168.0.32/27 to any port 67
    ufw allow proto udp from 192.168.0.32/27 to any port 80
    ufw allow proto udp from 192.168.0.32/27 to any port 443
    ufw allow proto udp from 192.168.0.64/27 to any port 22
    ufw allow proto udp from 192.168.0.64/27 to any port 53
    ufw allow proto udp from 192.168.0.64/27 to any port 67
    ufw allow proto udp from 192.168.0.64/27 to any port 80
    ufw allow proto udp from 192.168.0.64/27 to any port 443

    ufw allow proto udp from 192.168.0.96/27 to any port 22
    ufw allow proto udp from 192.168.0.96/27 to any port 53
    ufw allow proto udp from 192.168.0.96/27 to any port 67
    ufw allow proto udp from 192.168.0.96/27 to any port 80
    ufw allow proto udp from 192.168.0.96/27 to any port 443
    systemctl restart ufw
  fi
}

# configure the ethernet interfaces required by the system
# if the number of available ethernet interfaces is lesser than
# the amount required, the install procedure will abort end exit with
# error code 1. Elsewise netplan will be used to configure their ipv4
# fixed address.
# Ntd: this function has to be invoked in install directory.
function netplan_config {
  if [[ $# -lt 2 ]]; then
    echo "There is not enough ethernets interfaces : Abort"
    exit 1
  fi
  artnet_interface=$1
  lan_interface=$2
  cp 10-arbalet.yaml 10-arbalet.yaml.base
  sed -i "s/artnet_interface/$artnet_interface/" 10-arbalet.yaml
  sed -i "s/lan_interface/$lan_interface/" 10-arbalet.yaml
  mv 10-arbalet.yaml /etc/netplan/10-arbalet.yaml
  mv 10-arbalet.yaml.base 10-arbalet.yaml
  ifconfig $artnet_interface up
  ifconfig $lan_interface up
  netplan apply
}

# put in pkg_to_install list all the package in pkg_list
# that are not installed on the host device.
function to_install {
  while [[ $# -gt 0 ]]; do
    var=`$package_manager $list_cmd | grep "^$1$end_chr"`
    if [[ "$var" == "" ]]; then
      pkg_to_install="$pkg_to_install $1"
    fi
    shift
  done
}

# manage the passwords generation a password can be generated
# either manually or automatically. It will always be consultable
# in .env file.
# gen_password take 2 arguments which are :
#  1) the password TOKEN to replace
#  2) Y/n to know if the password is auto-gen
function gen_password {
  TOKEN=$1
  passwd=""
  confirm="unconfirm"
  if [[ "$2" != "n" ]]; then
    passwd=`makepasswd --chars 16`
  else
    while [[ "$passwd" != "$confirm" || "$passwd" == "" ]]; do
      read -p "Enter password :" passwd
      read -p "Re-enter password:" confirm
      if [[ "$passwd" != "$confirm" ]]; then
        echo "Password does not match"
      fi
    done
  fi
  sed -i "s/$TOKEN/$passwd/" ../prod/.env
}

# MAIN

# Requirements installation
if [[ "$username" == "root" ]]; then
  echo "Script started as sudoer"
else
  echo "Start this script as sudoer"
  exit 1
fi

get_pkgmanager "$distrib"

echo "You are running this script on $distrib distribution, $package_manager will be used"

to_install $pkg_list

# Installation of required package
if [[ "$pkg_to_install" != "" ]]; then
  echo "Packages$pkg_to_install need to be installed"
  $package_manager $install_cmd $pkg_to_install
  # Check installation
  pkg_to_install=""
  to_install $pkg_list

  if [[ "$pkg_to_install" != "" ]]; then
    echo "ERROR :$pkg_to_install packages are missing ==> Abort"
    exit 1
  fi
else
  echo "All required packages are installed ==> skipping installation"
fi


# Arbalet installation

# check if git respository is here if not download it
exist=`[ -f ../.git/config ] && echo true || echo false`
if [[ "$exist" == "true" && `grep "url = https://github.com/arbalet-project/frontage.git" ../.git/config` != "" ]]; then
  directory=`echo $directory | sed 's/\/install//'`
  echo $directory
  echo "Repository already downloaded : Skipp downloading"
else
  echo "Downloading Repository"
  cd ~
  directory=`pwd`
  directory+=/frontage
  git clone http://github.com/arbalet-project/frontage.git
  cd ~/frontage/install
fi

# docker
adduser arbalet docker

#set passwords
gen_password CKK_RBB yes
read -p "generate automatically rabbitmq password ? (Y/n)" reply
gen_password PWD_RBB $reply
read -p "generate automatically postgres password ? (Y/n)" reply
gen_password PWD_PG $reply
read -p "generate automatically mysql root password ? (Y/n)" reply
gen_password PWD_RMQL $reply
read -p "generate automatically mysql password ? (Y/n)" reply
gen_password PWD_MQL $reply

# build arbalet service
sed -i "s#WDIRECTORY#$directory/prod/#" arbalet.service
sed -i "s#CURRENTUSER#$logname#" arbalet.service
cp arbalet.service /lib/systemd/system/

# set up services
ln -fs /etc/systemd/system/autologin@.service /etc/systemd/system/getty.target.wants/getty@tty1.service
systemctl set-default multi-user.target
systemctl daemon-reload
systemctl enable docker.service
systemctl enable arbalet.service

# build containers
cd ../prod
docker-compose up --no-start
docker-compose run --rm app init
cd $directory/install

# ethernet interfaces
netplan_config `ip link show | grep \ en | cut --delimiter=: -f 2`
cp hosts /etc/hosts
cp hostname /etc/hostname

# firewall
read -p "Do you want to set up a firewall ? (y/N)" reply
ufw_config $reply

# Disable systemd-resolved
systemctl stop systemd-resolved
systemctl disable systemd-resolved
systemctl disable systemd-networkd-wait-online.service
systemctl mask systemd-networkd-wait-online.service
