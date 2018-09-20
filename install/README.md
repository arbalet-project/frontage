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

# Network config for 16.04
sudo cp interfaces /etc/network/interfaces

# Network config for Netplan 18.04
sudo cp 10-arbalet.yaml /etc/netplan/10-arbalet.yaml
sudo netplan apply

# DNS, hostname and DHCP
sudo apt install dnsmasq
sudo cp dnsmasq.conf /etc/dnsmasq.conf
sudo cp hosts /etc/hosts
sudo cp hostname /etc/hostname
sudo cp resolv.conf /etc/resolv.conf

# Initialize production environment
cd ..
nano .env  # Set random passwords
sudo systemctl edit artnet
# Add a [Service] section with the 2 rabbitMQ credential strings, i.e.:
# [Service]
# Environment="RABBITMQ_DEFAULT_USER=frontage"
# Environment="RABBITMQ_DEFAULT_PASS="
docker-compose -f docker-compose.prod.yml run --rm app init # Create your admin password here

```

# Sentry config
```
cd Arbalet/frontage/sentry
docker-compose run --rm web config generate-secret-key
nano docker-compose.yml  # Add the Sentry's secret key to the environment file
docker-compose run --rm web upgrade # Build the database. Use the interactive prompts to create a user account.
```

* Open a web browser to [192.168.0.42:9000](192.168.0.42:9000) and login
* Set `Root URL [REQUIRED]` to http://192.168.0.42:9000 and some e-mail address
* Go to `New Project > Python > Project settings > Client Keys (DSN)` and paste the `DSN` **(PRIVATE)** in .env (back)
* Go to `New Project > Angular > Project settings > Client Keys (DSN)` and paste the `DSN (Public)` in `environment.ts` (front)

```
cd ../install
sudo cp sentry.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sentry.service

sudo reboot
```

# Manage services
```
sudo service arbalet stop
sudo service arbalet start
sudo systemctl status arbalet.service
sudo journalctl -u arbalet -f

```

```
docker-compose -f docker-compose.prod.yml run --rm app set_admin_credentials  # Change your admin password
docker-compose -f docker-compose.prod.yml run --rm app reset  # Factory reset (Dropping DB)
```

# Troubleshooting
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  password authentication failed for user "some_suer"
```
First make sure `.env` has non-empty random passwords. In case the prod server is being reinstalled, make sure you destroy all the volumes `docker-compose -f docker-compose.prod.yml down -v`. Also do not forget `-f` to specify the prod config.
