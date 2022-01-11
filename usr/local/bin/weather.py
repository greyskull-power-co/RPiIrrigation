#!/usr/bin/env python
import urllib
import MySQLdb
import time
import os
import subprocess




while True:

	if float(40) <= float(time.strftime("%H%M")) <= float(48):


		db = MySQLdb.connect("localhost","yourUser","yourPassword","agriculture" )

		cursor = db.cursor()
		latRaw = db.cursor()
		lonRaw = db.cursor()

		latRaw.execute("SELECT lat FROM weather")
		lonRaw.execute("SELECT lon FROM weather")

		lat = str(latRaw.fetchall()).replace("'","").replace("(","").replace(")","").replace(",","").replace("Decimal","")
		lon = str(lonRaw.fetchall()).replace("'","").replace("(","").replace(")","").replace(",","").replace("Decimal","")

		link = "https://forecast.weather.gov/MapClick.php?lat={0}&lon={1}&unit=0&lg=english&FcstType=text&TextType=1".format(lat, lon)
		f = urllib.urlopen(link)
		myfile = f.read()
		if "<b>{0}: </b>".format(time.strftime("%A")) in myfile:
			today = myfile.split("<b>{0}: </b>".format(time.strftime("%A")))[1]

			dayforecast = today.split("<br>")[0]

			if "Chance of precipitation is" in dayforecast:
	        		dayprecip = dayforecast.split("Chance of precipitation is")[1]
			else:
	        		dayprecip = "0%"

			amPrecip = dayprecip.split("%")[0]

			cursor.execute("UPDATE weather SET todayRain=%s,last_update=NOW() WHERE config = 1", [amPrecip])
			db.commit()
			db.close()
                elif "<b>Today: </b>" in myfile:
                        today = myfile.split("<b>Today: </b>")[1]
                        dayforecast = today.split("<br>")[0]

                        if "Chance of precipitation is" in dayforecast:
                                dayprecip = dayforecast.split("Chance of precipitation is")[1]
                        else:
                                dayprecip = "0%"

                        amPrecip = dayprecip.split("%")[0]

                        cursor.execute("UPDATE weather SET todayRain=%s,last_update=NOW() WHERE config = 1", [amPrecip])
                        db.commit()
                        db.close()


		else:
                        cursor.execute("UPDATE weather SET todayRain=0,last_update=NOW() WHERE config = 1")
                        db.commit()
                        db.close()

	else:
            pass
	time.sleep(300)

