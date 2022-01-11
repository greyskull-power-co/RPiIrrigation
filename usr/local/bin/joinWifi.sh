#!/bin/sh
sudo service hostapd stop
sudo service dnsmasq stop
sudo ip link set wlan0 down
#sudo python /usr/local/bin/createWpaSupplicant.py
sleep 3
sudo rm /etc/dhcpcd.conf
sleep 1
sudo cp /etc/dhcpcd.conf.orig /etc/dhcpcd.conf
sudo ip link set wlan0 up
sudo systemctl daemon-reload
sudo service dhcpcd stop
sleep 1
sudo service dhcpcd start
sudo systemctl disable hostapd.service
sudo systemctl disable dnsmasq.service
