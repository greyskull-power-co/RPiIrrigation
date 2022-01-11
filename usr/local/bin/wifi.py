#!/usr/bin/python
import serial
from serial import SerialException
import serial.tools.list_ports
import time
import os
import subprocess
import MySQLdb

while True:
#       configure the sql user
        db = MySQLdb.connect("localhost","yourUser","yourPassword","agriculture")
        cursor = db.cursor()
#       <scripts to get network statuses>
        localAddress = str(subprocess.check_output("ifconfig wlan0 | grep netmask | cut -d 't' -f 2 | cut -d ' ' -f 2 | cut -d 'n' -f 1", shell=True).decode('utf-8'))
        localGateway = subprocess.check_output("ip route show | grep default | cut -d 'a' -f 3 | cut -d ' ' -f 2 | cut -d ' ' -f 1", shell=True).decode('utf-8')
#       <get services status>
        dnsmasqStatus = str(subprocess.check_output("service dnsmasq status | grep active | cut -d':' -f2 | cut -d' ' -f2", shell=True).decode('utf-8'))
        weatherStatus = str(subprocess.check_output("systemctl status weather | grep 'Active'", shell=True).decode('utf-8'))
        hostapdStatus = str(subprocess.check_output("service hostapd status | grep active | cut -d':' -f2 | cut -d' ' -f2", shell=True).decode('utf-8'))
        connection = os.system("ping -c1 -w3 " + str(localGateway))
#       <check to see what end users preference is (hotspot or join)>
        request = db.cursor()
        request.execute("SELECT selfWifi FROM network")
        request = (str(request.fetchall()).replace("'","").replace("(","").replace(")","").replace(",","").replace("L",""))

        db.commit()

#       <generate a non routed hotspot if not already doing so>
        if request == "yes":   
                if "192.168.4.1" in localAddress:
                        if "inactive" in dnsmasqStatus:
                                os.system("sh /usr/local/bin/dnsmasqStart.sh")
                        cursor.execute('''UPDATE network SET count=0 WHERE uid=1''')
                        db.commit()
                else:
                        os.system("sh /usr/local/bin/selfWifi.sh")
#       <attempt to join a nearby wifi>
        else:
                if connection == 0:
#       <if successfully online, set the count to 0>
                        cursor.execute('''UPDATE network set count=0 where uid=1''')
                        if "active (running)" not in weatherStatus:
                                os.system("systemctl start weather")
                        db.commit()
                else:
                        os.system("sh /usr/local/bin/joinWifi.sh")
                        ct = db.cursor()
                        ct.execute("SELECT count FROM network where uid=1")
                        ct = (str(ct.fetchall()).replace("'","").replace("(","").replace(")","").replace(",","").replace("L",""))
                        udate = db.cursor()
#       <attempt to join, if failed increase the count by one each time>
                        udate.execute("""UPDATE network SET count = count + 1 WHERE uid=1""")
                        db.commit()
                        if float(ct) > 3:
#       <if the count is greater than three, indicates three failed attempts - fail over to local hotspot>
                                udate.execute('''UPDATE network SET selfWifi="yes" WHERE uid=1''')
                                db.commit()
#       <take a break>
        time.sleep(15)
#       <close any connections>
        db.close()
