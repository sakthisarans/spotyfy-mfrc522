connection={'ssid':'********','pwd':'*******','ip':'***.***.***.***','frame_pwd':'*************'}
link=f'http://{connection["ip"]}/?pwd={connection["frame_pwd"]}&input='
import mfrc522
import time
import machine
from machine import Pin,ADC
import network
import ntptime
import urequests,json
time.sleep(2)
buzz=Pin(5,Pin.OUT)
led=Pin('LED',Pin.OUT).high()
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(connection['ssid'],connection['pwd'])
count=0



while not wlan.isconnected():
    print('waiting for connection...',wlan.isconnected())
    time.sleep(2)
    count=count+1
    if count>10:
        machine.reset()
print(wlan.status())
ip=wlan.ifconfig()[0]
print(ip)
led=Pin('LED',Pin.OUT)

count=0
TEMPERATURE_UNITS = {
    "standard": "K",
    "metric": "°C",
    "imperial": "°F",
}
 
SPEED_UNITS = {
    "standard": "m/s",
    "metric": "m/s",
    "imperial": "mph",
}
units = "metric"


    
def RUN():
    
    rdr = mfrc522.MFRC522(sck=2, miso=4, mosi=3, cs=1, rst=0)
    sss=''
    out=''
    volume=50
    playpause=Pin(16,Pin.IN,Pin.PULL_UP)
    playback=True
    yaxis=ADC(28)
    xaxis=ADC(27)
    datasend=False
    segment=4
    try:
        while True:
            try:
                x=(int(xaxis.read_u16()/100))
                y=(int(yaxis.read_u16()/100))
                print(playpause.value())
                if(playpause.value()==0):
                    print((urequests.get(link+'playback:'+str(playback)).text))
                    playback=not playback
                        
                if x<100:
                    
                    volume=volume+3
                    if volume>100:
                        volume=100
                    print(str(link+str('volume:'+str(volume))))
                    print(urequests.get(str(link+str('volume:'+str(volume)))).text)
                    time.sleep(1)
                    
                elif x>500:
                    
                    volume=volume-3
                    if volume<0:
                        volume=0
                    print(str(link+str('volume:'+str(volume))))
                    print(urequests.get(str(link+str('volume:'+str(volume)))).text)
                    time.sleep(1)
                    
                if ((x>300 and x<400) and datasend):
                    pass
                    #send(str('volume:'+str(volume)))
                    datasend=not datasend
                if y<100:
                    print((urequests.get(link+'playback:'+'next').text))
                    time.sleep(1)
                elif y>500:
                    print((urequests.get(link+'playback:'+'previous').text))
                    time.sleep(1)
            except Exception as ex:
                print(ex)
            time.sleep(0.02)

            #print(sens.value())
            print("Place card before reader.",end='\r')
            (stat, tag_type) = rdr.request(rdr.REQIDL)

            if stat == rdr.OK:

                (stat, raw_uid) = rdr.anticoll()

                if stat == rdr.OK:
                    print("CARD DETECTED",end='\r')
                    if rdr.select_tag(raw_uid) == rdr.OK:

                        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                        if rdr.auth(rdr.AUTHENT1A, segment, key, raw_uid) == rdr.OK:
                            data = rdr.read(segment)
                            datastr = ""
                            for i in data:
                                datastr = datastr + (chr(i))
                               
                            out=out+str(datastr)
                            segment=segment+1
                            rdr.stop_crypto1()
                            if(chr(data[len(data)-1])=='*'):
                                out=out.replace('*',"")
                                print(out)
                                buzz.high()
                                time.sleep(0.5)
                                buzz.low()
                                try:
                                    print((urequests.get(str(link+'url:'+out))).text)
                                except Exception as ex:
                                    print(ex)
                                    pass
                                segment=4
                                out=''
                                global led
                                led.high()
                                time.sleep(1)
                                led.low()
                                
                        else:
                            print("AUTH ERR")
                    else:
                        print("Failed to select tag")
    except KeyboardInterrupt:
        print("EXITING PROGRAM")



if __name__=="__main__":
    try:
        print(time.localtime())
    except Exception as ex:
        print('error')
        print(ex)
    buzz.high()
    time.sleep(0.5)
    buzz.low()
    RUN()

