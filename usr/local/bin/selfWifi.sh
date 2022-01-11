#!/bin/sh
sudo ip link set wlan0 down
sleep 3
sudo rm /etc/dhcpcd.conf
sleep 1
sudo cp /etc/dhcpcd.conf.self /etc/dhcpcd.conf
sudo systemctl daemon-reload
sudo service dhcpcd stop
sudo ip link set wlan0 up
sudo systemctl enable hostapd.service
sudo systemctl enable dnsmasq.service
sudo service hostapd start
sudo service dnsmasq start
sudo service dhcpcd start
