#!/bin/bash
#sudo visudo
#www-data ALL = NOPASSWD: /sbin/reboot, /sbin/shutdown
#www-data ALL = NOPASSWD: /bin/systemctl start logging, /bin/systemctl stop logging, /bin/systemctl status logging
#www-data ALL = NOPASSWD: /bin/date
#www-data ALL = NOPASSWD: /sbin/iwlist wlan0 scan

echo "running updates"
sudo apt-get update && apt-get upgrade -y
echo "installing dependencies"
sudo apt-get -y install mysql-common mysql-client-5.5
sudo apt-get -y install mysql-server python-mysqldb php5-mysql apache2 libapache2-mod-php5 python-serial
sudo apt-get -y install python-pip
echo "creating hotspot capabilities"
sudo apt-get -y install hostapd
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq

#copy the key files
echo "copying key files"
sudo cp -r var/www/html/* /var/www/html/
sudo cp -r usr/local/bin/* /usr/local/bin/
sudo cp -r lib/systemd/system/* /lib/systemd/system/

#sudo chmod 755 /usr/local/bin/controller.py
#sudo chmod 755 /usr/local/bin/logger.py

#activate the services
echo "establishing services"
sudo chmod 644 /lib/systemd/system/controller.service
sudo chmod 644 /lib/systemd/system/logging.service
sudo chmod 644 /lib/systemd/system/sysMon.service
sudo chmod 644 /lib/systemd/system/autohotspot.service
sudo chmod 644 /lib/systemd/system/weather.service

#modify keyfiles
echo "modifying keyfiles"
echo "DAEMON_CONF=/etc/hostapd/hostapd.conf" >> /etc/default/hostapd
echo "no-resolv" >> /etc/dnsmasq.conf
echo "interface=wlan0" >> /etc/dnsmasq.conf
echo "bind-interfaces" >> /etc/dnsmasq.conf
echo "dhcp-range=10.0.0.50,10.0.0.150,12h" >> /etc/dnsmasq.conf

#activating services
echo "setting service for controller"
sudo systemctl enable controller.service
sudo systemctl enable logging.service
sudo systemctl enable autohotspot.service
sudo systemctl enable sysMon.service
sudo systemctl enable weather.service

sudo service controller start
sudo service logging start
sudo service sysMon start
sudo service apache2 restart
sudo service weather start
