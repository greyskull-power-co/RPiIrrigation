#!/usr/bin/env python
import urllib
import MySQLdb
import time
import os
import subprocess
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


pins = {8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 29, 31, 32, 33, 35, 36, 37, 38, 40}


#reference chart of database
#| Field            | Type         | Null | Key | Default | Extra |
#+------------------+--------------+------+-----+---------+-------+
#0| zone             | int(2)       | NO   | PRI | NULL    |       |
#1| nickName         | varchar(24)  | YES  |     | NULL    |       |
#2| onTimeA          | int(4)       | YES  |     | NULL    |       |
#3| onTimeB          | int(4)       | YES  |     | NULL    |       |
#4| onTimeC          | int(4)       | YES  |     | NULL    |       |
#5| onTimeD          | int(4)       | YES  |     | NULL    |       |
#6| onTimeE          | int(4)       | YES  |     | NULL    |       |
#7| offTimeA         | int(4)       | YES  |     | NULL    |       |
#8| offTimeB         | int(4)       | YES  |     | NULL    |       |
#9| offTimeC         | int(4)       | YES  |     | NULL    |       |
#10| offTimeD         | int(4)       | YES  |     | NULL    |       |
#11| offTimeE         | int(4)       | YES  |     | NULL    |       |
#12| onTimeModA       | int(4)       | YES  |     | NULL    |       |
#13| onTimeModB       | int(4)       | YES  |     | NULL    |       |
#14| onTimeModC       | int(4)       | YES  |     | NULL    |       |
#15| onTimeModD       | int(4)       | YES  |     | NULL    |       |
#16| onTimeModE       | int(4)       | YES  |     | NULL    |       |
#17| offTimeModA      | int(4)       | YES  |     | NULL    |       |
#18| offTimeModB      | int(4)       | YES  |     | NULL    |       |
#19| offTimeModC      | int(4)       | YES  |     | NULL    |       |
#20| offTimeModD      | int(4)       | YES  |     | NULL    |       |
#21| offTimeModE      | int(4)       | YES  |     | NULL    |       |
#22| restrictions     | varchar(12)  | YES  |     | NULL    |       |
#23| manualOverride   | varchar(3)   | YES  |     | NULL    |       |
#24| active           | varchar(3)   | YES  |     | NULL    |       |
#25| sprinklers       | int(2)       | YES  |     | NULL    |       |
#26| gallonsPerMinute | decimal(5,3) | YES  |     | NULL    |       |
#27| delay            | varchar(3)   | YES  |     | NULL    |       |
#28| pin              | int(3)       | YES  |     | NULL    |       |
#29| last_update      | datetime     | YES  |     | NULL    |       |
#+------------------+--------------+------+-----+---------+-------+


while True:
    db = MySQLdb.connect("localhost","yourUser","yourPassword","agriculture" )
    cursor = db.cursor()
    try:
        for i in pins:
            GPIO.setup(i, GPIO.OUT)
            cursor.execute("SELECT * from wateringSchedule WHERE pin=" + str(i))
            row = cursor.fetchall()
            formatted = (str(row).replace("(","").replace("'","").replace(")","" ).replace(" ","").replace("L",""))
            data = formatted.split(",")
            zone = data[0]
            onTimeA = float(data[2])
            onTimeB = float(data[3])
            onTimeC = float(data[4])
            onTimeD = float(data[5])
            onTimeE = float(data[6])
            offTimeA = float(data[7])
            offTimeB = float(data[8])
            offTimeC = float(data[9])
            offTimeD = float(data[10])
            offTimeE = float(data[11])
            manualOverride = data[23]
            restrictions = data[22]
            dayDigit = time.strftime("%d")
            dayName = time.strftime("%A")
            currentTime = float(time.strftime("%H%M"))
            db.commit()
            def waterTime():
                if onTimeA <= currentTime < offTimeA:
                    cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'yes') ON DUPLICATE KEY UPDATE active='yes'" % (zone))
                    GPIO.output(i, GPIO.HIGH)
                    db.commit()
                elif onTimeB <= currentTime < offTimeB:
                    cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'yes') ON DUPLICATE KEY UPDATE active='yes'" % (zone))
                    GPIO.output(i, GPIO.HIGH)
                    db.commit()
                elif onTimeC <= currentTime < offTimeC:
                    cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'yes') ON DUPLICATE KEY UPDATE active='yes'" % (zone))
                    GPIO.output(i, GPIO.HIGH)
                    db.commit()
                elif onTimeD <= currentTime < offTimeD:
                    cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'yes') ON DUPLICATE KEY UPDATE active='yes'" % (zone))
                    GPIO.output(i, GPIO.HIGH)
                    db.commit()
                elif onTimeE <= currentTime < offTimeE:
                    cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'yes') ON DUPLICATE KEY UPDATE active='yes'" % (zone))
                    GPIO.output(i, GPIO.HIGH)
                    db.commit()
                else:
                    cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'no') ON DUPLICATE KEY UPDATE active='no'" % (zone))
                    GPIO.output(i, GPIO.LOW)
                    db.commit()
    #check if manually disabled
            if manualOverride == "0":
                GPIO.output(i, GPIO.LOW)
                cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'no') ON DUPLICATE KEY UPDATE active='no'" % (zone))
                db.commit()
            elif manualOverride == "1":
    #automation takes over here
                GPIO.output(i, GPIO.LOW)
                cursor.execute("SELECT * from weather")
                weatherRow = cursor.fetchall()
                weatherFormat = (str(weatherRow).replace("(","").replace("'","").replace(")","" ).replace(" ","").replace("L",""))
                weatherData = weatherFormat.split(",")
                todayRain = weatherData[1]
                rainThreshold = weatherData[2]
                db.commit()
		#do not water if chance of rain is = or higher than threshold
                if todayRain >= rainThreshold:
                    GPIO.output(i, GPIO.LOW)
                    cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'no') ON DUPLICATE KEY UPDATE active='no'" % (zone))
                    db.commit()
		#if rain not expected, check watering bans
                if todayRain < rainThreshold:
                    if restrictions == "1":
                        waterTime()
                    elif restrictions == "odd" and float(dayDigit) % 2 > 0:
                        waterTime()
                    elif restrictions == "even" and float(dayDigit) % 2 == 0:
                        waterTime()
                    elif restrictions == "3" and float(dayDigit) % 3 == 0:
                        waterTime()
                    elif restrictions == "4" and float(dayDigit) % 4 == 0:
                        waterTime()
                    elif restrictions == "5" and float(dayDigit) % 5 == 0:
                        waterTime()
                    elif restrictions == "6" and float(dayDigit) % 6 == 0:
                        waterTime()
                    elif "m" in restrictions and time.strftime("%a") == "Mon" or "t" in restrictions and time.strftime("%a") == "Tue" or "w" in restrictions and time.strftime("%a") == "Wed" or "Th" in restrictions and time.strftime("%a") == "Thu" or "f" in restrictions and time.strftime("%a") == "Fri" or "Sa" in restrictions and time.strftime("%a") == "Sat" or "Su" in restrictions and time.strftime("%a") == "Sun" or "d01" in restrictions and time.strftime("%d") == "01" or "d02" in restrictions and time.strftime("%d") == "02" or "d03" in restrictions and time.strftime("%d") == "03" or "d04" in restrictions and time.strftime("%d") == "04" or "d05" in restrictions and time.strftime("%d") == "05" or "d06" in restrictions and time.strftime("%d") == "06" or "d07" in restrictions and time.strftime("%d") == "07" or "d08" in restrictions and time.strftime("%d") == "08" or "d09" in restrictions and time.strftime("%d") == "09" or "d10" in restrictions and time.strftime("%d") == "10" or "d11" in restrictions and time.strftime("%d") == "11" or "d12" in restrictions and time.strftime("%d") == "12" or "d13" in restrictions and time.strftime("%d") == "13" or "d14" in restrictions and time.strftime("%d") == "14" or "d15" in restrictions and time.strftime("%d") == "15" or "d16" in restrictions and time.strftime("%d") == "16" or "d17" in restrictions and time.strftime("%d") == "17" or "d18" in restrictions and time.strftime("%d") == "18" or "d19" in restrictions and time.strftime("%d") == "19" or "d20" in restrictions and time.strftime("%d") == "20" or "d21" in restrictions and time.strftime("%d") == "21" or "d22" in restrictions and time.strftime("%d") == "22" or "d23" in restrictions and time.strftime("%d") == "23" or "d24" in restrictions and time.strftime("%d") == "24" or "d25" in restrictions and time.strftime("%d") == "25" or "d26" in restrictions and time.strftime("%d") == "26" or "d27" in restrictions and time.strftime("%d") == "27" or "d28" in restrictions and time.strftime("%d") == "28" or "d29" in restrictions and time.strftime("%d") == "29" or "d30" in restrictions and time.strftime("%d") == "30" or "d31" in restrictions and time.strftime("%d") == "31":
                        waterTime()
                    else:
	                GPIO.output(i, GPIO.LOW)
                        cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'no') ON DUPLICATE KEY UPDATE active='no'" % (zone))
                        db.commit()
    #check if manually enabled
            elif manualOverride == "2":
                GPIO.output(i, GPIO.HIGH)
                cursor.execute("INSERT INTO wateringSchedule(zone, active) values (%s, 'yes') ON DUPLICATE KEY UPDATE active='yes'" % (zone))
                db.commit()
		
    except Exception as e:
        print(e)
		
    time.sleep(2)


