import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import MySQLdb
import subprocess
import time
import os
import shutil

#database define
db = MySQLdb.connect("localhost","yourUser","yourpassword","agriculture" )
cursor = db.cursor()
active_clients = set()

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print ('new connection')

        #setting nodelay below may increase bandwidth
        self.set_nodelay(True)


    def on_message(self, message):
        datastream = str(message).split(",")
        if ("loadingWeather" in datastream[0]):
            try:
                db.ping(True)
                cursor.execute("SELECT * from weather")
                row = cursor.fetchall()
                self.write_message( str(row).replace("(","").replace("'","").replace(")","" ).replace(" ",""))
            except Exception as e:
                print(e)
        if ("loadingZone" in datastream[0]):
            db.ping(True)
            cursor.execute("SELECT * from wateringSchedule WHERE zone=%s" %  (datastream[1]))
            row = cursor.fetchall()
            self.write_message("loadingZone," + str(row).replace("(","").replace("'","").replace(")","" ).replace(" ",""))
        if ("zoneSet" in datastream[0]):
            try:
                zone = datastream[1]
                cycle = datastream[2]
                onTime = datastream[3].replace(":","")
                offTime = datastream[4].replace(":","")
                db.ping(True)
                cursor.execute("INSERT INTO wateringSchedule(zone,onTime%s, offTime%s) values (%s, %s, %s) ON DUPLICATE KEY UPDATE onTime%s=%s, offTime%s=%s" % (cycle, cycle, zone, onTime, offTime, cycle, onTime, cycle, offTime))
                db.commit()
            except Exception as e:
                print(e)
        if ("nameSet" in datastream[0]):
            try:
                zone = datastream[1]
                nname = str(datastream[2])
                db.ping(True)
                cursor.execute("INSERT INTO wateringSchedule(zone, nickName) values (%s, '%s') ON DUPLICATE KEY UPDATE nickName='%s'" % (zone, nname, nname))
                db.commit()
            except Exception as e:
                print(e)
        if ("overview" in datastream[0]):
            try:
                db.ping(True)
                cursor.execute("SELECT * from wateringSchedule WHERE zone=%s" %  (datastream[1]))
                row = cursor.fetchall()
                self.write_message("overview," + str(row).replace("(","").replace("'","").replace(")","" ).replace(" ",""))
            except Exception as e:
                print(e)
        if ("zipLookup" in datastream[0]):
            try:
                zipp = datastream[1].lstrip("0")
                db.ping(True)
                cursor.execute("SELECT * from zips WHERE zip=%s" % zipp)
                row = cursor.fetchall()
                self.write_message("zipLookup," + str(row).replace("(","").replace("'","").replace(")","" ).replace(" ",""))
                db.commit()
            except Exception as e:
                print(e)
        if ("geoLookup" in datastream[0]):
            try:
                db.ping(True)
                cursor.execute("SELECT lat from weather")
                lat = cursor.fetchall()
                latFormat = ( "'" + str(lat).replace("(","").replace("'","").replace(")","" ).replace(" ","").replace(",","").replace("Decimal","") + "%'" )
                db.commit()
                cursor.execute("SELECT lon from weather")
                lon = cursor.fetchall()
                lonFormat = ( "'" + str(lon).replace("(","").replace("'","").replace(",","").replace(")","" ).replace(" ","").replace("Decimal","") + "%'" )
                db.commit()
                cursor.execute("SELECT * from zips WHERE lat LIKE %s and lon LIKE %s" % (latFormat, lonFormat) )
                row = cursor.fetchall()
                self.write_message("geoLookup," + str(row).replace("(","").replace("'","").replace(")","" ).replace(" ",""))
                db.commit()
            except Exception as e:
                print(e)
        if ("zipSubmit" in datastream[0]):
            try:
                db.ping(True)
                zipp = datastream[1].lstrip("0")
                cursor.execute("SELECT * from zips WHERE zip=%s" % zipp)
                row = cursor.fetchall()
                results = ( str(row).replace("(","").replace("'","").replace(")","" ).replace(" ","").replace("Decimal","") )
                array = results.split(",")
                lat = array[3]
                lon = array[4]
                cursor.execute("INSERT INTO weather(config, lat, lon) values ('1', '%s', '%s') ON DUPLICATE KEY UPDATE lat=%s, lon=%s" % (lat, lon, lat, lon))
                db.commit()
            except Exception as e:
                print(e)
        if ("weather" in datastream[0]):
            try:
                db.ping(True)
                cursor.execute("SELECT * from weather WHERE config=1")
                row = cursor.fetchall()
                self.write_message("weather," + str(row).replace("(","").replace("'","").replace(")","" ).replace(" ","").replace("datetime.datetime",""))
                db.commit()
            except Exception as e:
                print(e)
        if ("manualOverride" in datastream[0]):
            try:
                db.ping(True)
                #print (datastream)
                zoneNumber = datastream[1]
                override = datastream[2]
                #print( zoneNumber )
                cursor.execute("INSERT INTO wateringSchedule (zone, manualOverride) values ( %s, %s ) ON DUPLICATE KEY UPDATE manualOverride=%s" % (zoneNumber, override, override))
                db.commit()
            except Exception as e:
                print(e)
        if ("restrictions" in datastream[0]):
            try:
                db.ping(True)
                zone = datastream[1]
                restrict = datastream[2]
                cursor.execute("INSERT INTO wateringSchedule(zone, restrictions) values ( %s, %s ) ON DUPLICATE KEY UPDATE restrictions=%s" % (zone, restrict, restrict))
                db.commit()
            except Exception as e:
                print(e)
        if ("pop" in datastream[0]):
            try:
                db.ping(True)
                pop = datastream[1]
                cursor.execute("INSERT INTO weather(config, rainThreshold) values ( '1', %s ) ON DUPLICATE KEY UPDATE rainThreshold=%s" % ( pop,pop ))
                db.commit()
            except Exception as e:
                print(e)
        if ("wifi" in datastream[0]):
            try:
                db.ping(True)
                print("wifi")
                ssid = datastream[1]
                password = datastream[2]
                cursor.execute("INSERT INTO wifi(uid, ssid, wpapsk) values ( '1', %s, %s ) ON DUPLICATE KEY UPDATE ssid=%s, wpapsk=%s" % ( ssid,password,ssid,password ))
                db.commit()
            except Exception as e:
                print(e)
        if ("email" in datastream[0]):
            try:
                db.ping(True)
                email = datastream[1]
                #frequency = datastream[2]
                cursor.execute("INSERT INTO notifications(uid, recipient, frequency) values ( '1', %s, '1' ) ON DUPLICATE KEY UPDATE recipient=%s, frequency='1'" % ( email,email))
                db.commit()
            except Exception as e:
                print(e)
        if ("frequency" in datastream[0]):
            try:
                db.ping(True)
                frequency = datastream[1]
                cursor.execute("INSERT INTO notifications(uid, frequency) values ( '1', %s ) ON DUPLICATE KEY UPDATE frequency=%s" % ( frequency,frequency))
                db.commit()
            except Exception as e:
                print(e)
        if ("join" in datastream[0]):
            try:
                db.ping(True)
                selfWifi = datastream[1]
                cursor.execute("INSERT INTO network(uid, selfWifi, count) values ( '1', %s, '0' ) ON DUPLICATE KEY UPDATE selfWifi=%s, count='0'" % ( selfWifi,selfWifi))
                db.commit()
            except Exception as e:
                print(e)
        if ("time" in datastream[0]):
            try:
                date = time.strftime("%b") + "-" + time.strftime("%d") + "-" + time.strftime("%Y") + " " + time.strftime("%-I") + ":" + time.strftime("%M") + time.strftime("%p")
                self.write_message("time," + date )
            except Exception as e:
                print(e)
        if ("ntwk" in datastream[0]):
            try:
                arg_list = [ '/sbin/iwgetid', '-r' ]
                args = ' '.join(arg_list)

                proc = subprocess.Popen(arg_list, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)

                (output, dummy) = proc.communicate()
                self.write_message("ntwk," + output )
            except Exception as e:
                print(e)
        if ("systemStatus" in datastream[0]):
            try:
                uptime = str(subprocess.check_output("uptime", shell=True).decode('utf-8'))
                total, used, free = shutil.disk_usage("/")
                freeSpace = round((((used // (2**30)) / (total // (2**30))) * 100),2)
                temp = str(subprocess.check_output("vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*'", shell=True).decode('utf-8'))
                #self.write_message("systemStatus," + uptime + "," + str(freeSpace) + "% disk used," + temp)
                self.write_message("systemStatus," + str(freeSpace) + "% disk used," + temp + "," + uptime)
            except Exception as e:
                print(e)
        if ("shutdown" in datastream[0]):
            try:
                os.system("shutdown -h now")
            except Exception as e:
                print(e)
        if ("ntc" in datastream[0]):
            try:
                db.ping(True)
                cursor.execute("SELECT recipient from notifications WHERE uid='1'")
                row = cursor.fetchall()
                results = str(row).replace("(","").replace("'","").replace(")","" ).replace(" ","").replace(",","")
				
                cursor.execute("SELECT frequency from notifications WHERE uid='1'")
                row2 = cursor.fetchall()
                results2 = str(row2).replace("(","").replace("'","").replace(")","" ).replace(" ","").replace(",","")
                self.write_message("ntc," + results + "," + results2)
                db.commit()
            except Exception as e:
                print(e)
    def on_close(self):
        print ('connection closed')

 
    def check_origin(self, origin):
        return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print ('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.instance().start()

