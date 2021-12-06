
import tkinter as tk
import time
import winsound
import matplotlib.pyplot as plt
from  matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pyproj
from tkinter import *
import json
import numpy
import geojson
from geojson import Feature, Point, FeatureCollection, Polygon, MultiLineString
import random
import utm
from shapely.geometry import shape, GeometryCollection, Polygon, LineString, MultiLineString
import shapely.ops as ops
import matplotlib.pyplot as plt
import serial
import keyboard

import time
from datetime import datetime
import pyautogui
import logging
import pytz
#logging.basicConfig(filename='GPRCoveragelogs.txt', level=logging.DEBUG,format='%(asctime)s-%(levelname)s-%(message)s')

import geopandas as gpd
from shapely.ops import cascaded_union, unary_union
import plotly.express as px
import plotly.graph_objects as go




print(pyautogui.size())

def geoscopeon():
    # moves to (519,1060) in 1 sec
    pyautogui.moveTo(611, 533, duration = .1)

    # simulates a click at the present
    # mouse position
    pyautogui.click()
    
    
def geoscopeoff():
    # moves to (519,1060) in 1 sec
    pyautogui.moveTo(708, 533, duration = .1)

    # simulates a click at the present
    # mouse position
    pyautogui.click()



def readGPS(self,gps,GPSlatitude,GPSlongitude,GPSspeed,GPSheading,timestring,gpsFix):
    data = self.gps.readline()
    data=data.decode() #must convert byte to string
    message = data[0:6]
    #print(data)
    if (message == "$GPRMC"):
        # GPRMC = Recommended minimum specific GPS/Transit data
        # Reading the GPS fix data is an alternative approach that also works
        parts = data.split(",")
        if parts[2] == 'V':
            # V = Warning, most likely, there are no satellites in view...
            print ("GPS receiver warning")
        else:            
            # Get the position data that was transmitted with the GPRMC message
            # In this example, I'm only interested in the longitude and latitude
            # for other values, that can be read, refer to: http://aprs.gids.nl/nmea/#rmc
            LatDir=parts[4]
            LongDir=parts[6]
            self.GPSlongitude = formatDegreesMinutes(parts[5],"Long",LongDir)
            self.GPSlatitude = formatDegreesMinutes(parts[3],"Lat",LatDir)
            self.GPSspeed=float(parts[7])*1.15077945
            self.course=parts[8]
            Date=parts[9]
            self.day=int(Date[:2])
            self.month=int(Date[2:4])
            self.year=int("20"+Date[4:])
            #timestring=datetime(year,month,day)       
            #print ("Your position: lon = " + str(GPSlongitude) + ", lat = " + str(GPSlatitude) + " GPSspeed = " + str(GPSspeed)+" Course = " + str(course))
            data = gps.readline()
            data=data.decode() #must convert byte to string
            message = data[0:6]
            

    if (message == "$GPGGA"):
        # GPRMC = Recommended minimum specific GPS/Transit data
        # Reading the GPS fix data is an alternative approach that also works
        parts = data.split(",")
        if parts[6] == 0:
            # V = Warning, most likely, there are no satellites in view...
            print ("GPS receiver warning")
        else:
            # Get the position data that was transmitted with the GPRMC message
            # In this example, I'm only interested in the longitude and latitude
            # for other values, that can be read, refer to: http://aprs.gids.nl/nmea/#rmc
            LatDir=parts[3]
            LongDir=parts[5]
            self.GPSlongitude = formatDegreesMinutes(parts[4],"Long",LongDir)
            self.GPSlatitude = formatDegreesMinutes(parts[2],"Lat",LatDir)
            Time=parts[1]
            self.Hour=int(Time[:2])
            self.Minute=int(Time[2:4])
            self.Second=int(Time[4:6])
            self.gpsFix=parts[6]
            timestring=datetime(self.year, self.month, self.day, self.Hour, self.Minute,self.Second)
            timestring = timestring.astimezone(target_time_zone)
            #print ("Your position: lon = " + str(GPSlongitude) + ", lat = " + str(GPSlatitude))
    self.GPSstring.destroy()
    self.GPSstring = tk.Label(top, text ="Time "+str(self.Hour)+":"+str(self.Minute)+":"+str(self.Second)+"  Lat " +str(self.GPSlatitude)+" Long "+str(self.GPSlongitude))
    self.GPSstring.pack()

    return(self.GPSlatitude,self.GPSlongitude,self.GPSspeed,self.GPSheading,self.timestring,self.gpsFix) 



def formatDegreesMinutes(coordinates, type, direction):
    parts = coordinates.split(".")
    left = parts[0]    
    right = parts[1]

    if type=="Lat":
        degrees = int(left[:2])
        minutes=int(float(left[2:]+right)/60)


    
    if type=="Long":
        degrees = int(left[:3])
        minutes=int(float(left[3:]+right)/60)


    if direction == "W" or direction == "S":
        degrees=-degrees
    string=str(degrees) + "." + str(minutes)
    Coordinates=float(string[:-2])
    return Coordinates






lines=[]
jsonarray=[]
linestring=[]
readingnumber=0

target_time_zone =  pytz.timezone('US/Eastern')


contiuneproject=True
contiunereadings=True


def get_bool(prompt):
    while True:
        try:
           return {"t":True,"f":False}[input(prompt).lower()]
        except KeyError:
           print("Invalid input please enter t or f!")


def generatejson(array):
  string=geojson.Feature(geometry=geojson.MultiLineString(array))  # doctest: +ELLIPSIS
  return(string)


def utmpolyconverter(jsonName):
  #load in data
  with open(jsonName) as f:
      data = json.load(f)

  #traverse data in json string
  for feature in data['features']:
      #all coordinates
      coords = feature['geometry']['coordinates']
      #coordList is for each individual polygon
      for coordList in coords:

          #each point in list
          for coordPair in coordList:
              #print (coordPair)
              lat = coordPair[1]           
              lon = coordPair[0]
              lat_grid, lon_grid = numpy.meshgrid(lat, lon)
              #do transformation
              x, y ,z,s= utm.from_latlon(lat_grid, lon_grid)
              coordPair[0]=x[0][0]
              coordPair[1]=y[0][0]

  return (coordList)

def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return zip(*[iter(iterable)]*n)

def utmlineconverter(jsonName):
  #load in data
  with open(jsonName) as f:
      data = json.load(f)

  #traverse data in json string
  for feature in data['features']:
    #all coordinates
    coords = feature['geometry']['coordinates']
    #coordList is for each individual polygon
    for coordList in coords:
      for coordPair in coordList:
          #print (coordPair)
          lat = coordPair[1]            
          lon = coordPair[0]
          lat_grid, lon_grid = numpy.meshgrid(lat, lon)
          #do transformation
          x, y ,z,s= utm.from_latlon(lat_grid, lon_grid)
          coordPair[0]=x[0][0]
          coordPair[1]=y[0][0]

    line = LineString(coordList) #convert corrdinates to line string
    dilated = line.buffer(1, cap_style=2) #expand line to have area
    lines.append(dilated) #combine all linestrings into a multi polygon and send back
  return (lines)


#print(utmpolyconverter("coverage.json"))





#print(utmlineconverter("path.json"))
def measurecoverage(filename,runspath,rootpath):
    #get bridge poly


    #   with open("coverage.json") as f:
    #   bridgepoly = json.load(f)["features"]

    # # with open("path.json") as f:
    # #   scanpath = json.load(f)["features"]

    Bridgestring = utmpolyconverter(rootpath+"coverage.json")
    bridgepolygon = Polygon(Bridgestring)
    bridgearea=bridgepolygon.area

    #get current path poly
    lines = utmlineconverter(runspath+filename)
    lines=unary_union(lines)
    Intersection=bridgepolygon.intersection(lines)
    patharea=Intersection.area

    coverageprecent=round(patharea/bridgearea*100,2)

    base = gpd.GeoSeries(bridgepolygon)
    scanpaths = gpd.GeoSeries(Intersection)

    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    fig.suptitle("Coverage Precent "+str(coverageprecent)+"%", fontsize=14, fontweight='bold')
    base.plot(ax=ax,facecolor="none", edgecolor="black")
    scanpaths.plot(ax=ax,color='red')
    plt.show();


    # t = np.arange(0, 3, .01)

    # f0 = tk.Frame()

    # # fig = plt.figure(figsize=(8, 8))

    # # fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

    # canvas = FigureCanvasTkAgg(fig, f0)
    # toolbar = NavigationToolbar2Tk(canvas, f0)
    # toolbar.update()
    # canvas._tkcanvas.pack(fill=tk.BOTH, expand=1)


    # f0.pack(fill=tk.BOTH, expand=1)
    # top.update()  



    return (coverageprecent)




token = 'pk.eyJ1Ijoicm9zc2N1dHRzIiwiYSI6ImNrdW9iYnl6ajA3OXMycHBnb2JxbXZpY3gifQ.RD-jqtc5p3UJnrLcJhZHLA'


fig = go.Figure(go.Scattermapbox())
fig.update_layout(mapbox_style="satellite-streets", mapbox_accesstoken=token)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#fig.show()


# with open("coverage.json") as f:
#   bridgepoly = json.load(f)["features"]

# with open("path.json") as f:
#   scanpath = json.load(f)["features"]


latlist=[]

lonlist=[]

inlat=39.221864
inlong=-76.837014

# fig.add_trace(go.Scattermapbox(
#     mode = "markers+lines",
#     lon = latlist,
#     lat = lonlist,
#     marker = {'size': 10}))

# fig.update_layout(
#     mapbox = {
#         'style': "satellite-streets",
#         'accesstoken': token,
#         'center': { 'lon': inlong, 'lat': inlat},
#         'zoom': 12, 'layers': [{
#             'source': {
#                 'type': "FeatureCollection",
#                 'features': bridgepolygon
#             },
#             'type': "fill", 'below': "traces", 'color': "royalblue"}]},
#     margin = {'l':0, 'r':0, 'b':0, 't':0})


  # fig.update_mapboxes(layers=[
  #     {
  #         'source': feature, 
  #         'type': "line", 
  #         'line': {'width': 5},
  #         'below': "traces", 
  #         'color': "royalblue"
  #     } for feature in scanpath.features])
  




# for i in range(0,10):
#   inlat=randrange(30)
#   inlong=randrange(50)
#   latlist,lonlist=plotdata(latlist,lonlist,inlat,inlong)
#   print(latlist,lonlist)

#fig.show() 



#write reprojected json to new file
# with open('path_to_new_file.json', 'w') as f:
#     f.write(json.dumps(data))
  

# Sq. Meters	5177.03
# Sq. Kilometers	0.01
# Sq. Feet	55725.07
# Acres	1.28
# Sq. Miles	0.00


#save the site geometery

r=0
t=0


#jobname = input("Enter the Project Name: ")

# while True:
#   linestring=[]
#   readingnumber+=1
  
#   check=get_bool("Start reading num "+str(readingnumber)+"? ")
#   if check==True:
# #    try:
# #      while True:
#     for r in range(0,4):
#       linestring.append(tuple((random.randrange(-7684289,-7684120)/100000,random.randrange(3920819,3920881)/100000)))#add gps points here
#       jsonarray.append(linestring)
#       r+=1
      
# #    except KeyboardInterrupt:
# #      pass
#   t+=1
#   #print(jsonarray)
#   #print(generatejson(jsonarray))

#   #print(geojson.FeatureCollection(generatejson(jsonarray)))
#   filename=jobname+" Run#"+str(readingnumber)+'.json'   
#   with open(filename, 'w') as f:#save a copy of file after everyrun
#     f.write(geojson.dumps(geojson.FeatureCollection([generatejson(jsonarray)]), indent=4))
    
    
    
    
    
  
# while True:
#   linestring=[]
#   readingnumber+=1
#   r=0
  
#   check=get_bool("Start reading num "+str(readingnumber)+"? ")
#   if check==True:
#     geoscopeon()
#     while True:  #making a loop
#         try:  #used try so that if user pressed other than the given key error will not be shown
#             if keyboard.is_pressed(' '): #if key space is pressed.You can also use right,left,up,down and others like a,b,c,etc.
#                 print('You Pressed A Key!')
#                 geoscopeoff()
#                 #pause gpr here
#                 break #finishing the loop
#             else:
#                 #print(r)
#                 time.sleep(.5)
#                 latmove,longmove,GPSspeed,GPSheading,timestring,gpsFix=readGPS(gps,GPSlatitude,GPSlongitude,GPSspeed,GPSheading,timestring,gpsFix)
#                 #print(latmove)
#                 #print(longmove)
#                 linestring.append(tuple((longmove,latmove)))#add gps points here
#                 jsonarray.append(linestring)
#                 r+=1
#         except:
#             print("error")


  
#   print(r) 
#   t+=1        
#   filename=jobname+" Run#"+str(readingnumber)+'.json'    
#   #print(jsonarray)
#   with open(filename, 'w') as f:#save a copy of file after everyrun
#     f.write(geojson.dumps(geojson.FeatureCollection([generatejson(jsonarray)]), indent=4))
    

 
#   measurecoverage(str(filename))



class Application(tk.Frame, object):
    def __init__(self, master=None):
        super(Application, self).__init__(master)  # Call baseclass constructor.
        self.after_id = None
        self.secs = 0
        self.r=0
        
        cominstructions = tk.Label(top, text = "*Remember to Update Coverage.json for your scan area")
        cominstructions.pack()
        cominstructions2 = tk.Label(top, text = "*Get com port from device manager ex'COM5'")
        cominstructions2.pack()
        comlabel = tk.Label(top, text = "Enter Com Port")
        comlabel.pack()
        self.comNum = tk.Entry(top, width = 30)
        self.comNum.pack()
        namelabel = tk.Label(top, text = "Enter Project Name")
        namelabel.pack()
        self.name = tk.Entry(top, width = 30)
        self.name.pack()
        self.check=False
        self.readingnumber=1
        self.jsonarray=[]
        self.linestring=[]
        self.runnumber=0       
        self.day,self.month,self.year,self.Hour,self.Second,self.Minute,self.gpsFix,self.GPSlatitude,self.GPSlongitude,self.GPSspeed,self.GPSheading,self.timestring,self.gpsFix=1,1,2021,0,0,0,0,0,0,0,0,0,0
        self.GPSstring = tk.Label(top, text ="Time "+str(self.Hour)+":"+str(self.Minute)+":"+str(self.Second)+"  Lat " +str(self.GPSlatitude)+" Long "+str(self.GPSlongitude))
        self.GPSstring.pack()
        


        
        # Create widgets,
        self.controlButton = tk.Button(top, height=2, width=20, text="Start", command=self.start)
        #stopButton = tk.Button(top, height=2, width=20, text="Stop", command=self.stop)
        self.controlButton.pack()
        #stopButton.pack()

    def beeper(self):
        #print("running") 
        self.secs += 1
        if self.checkon== True:  # Every other second.
            latmove,longmove,self.GPSspeed,self.GPSheading,self.timestring,self.gpsFix=readGPS(self,self.gps,self.GPSlatitude,self.GPSlongitude,self.GPSspeed,self.GPSheading,self.timestring,self.gpsFix)

            try:
                latmove,longmove,self.GPSspeed,self.GPSheading,self.timestring,self.gpsFix=readGPS(self,self.gps,self.GPSlatitude,self.GPSlongitude,self.GPSspeed,self.GPSheading,self.timestring,self.gpsFix)
                self.linestring.append(tuple((longmove,latmove)))#add gps points here
                self.jsonarray.append(self.linestring)
                self.r+=1
                self.after(1000,self.beeper)
            except:
                print("error")
                self.after(250,self.beeper)
        
                
        

    def start(self):
        self.checkon=True
        if self.runnumber==0:
            self.gps= serial.Serial(port=self.comNum.get(),baudrate = 115200,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
            self.runnumber+=1
        geoscopeon()
        self.controlButton.destroy()
        self.controlButton = tk.Button(top, height=2, width=20, text="Stop", command=self.stop)
        self.controlButton.pack()
        self.secs = 0
        self.beeper()  # Start repeated checking.

    def processingDisplay(self):
        self.controlButton.destroy()
        self.controlButton = tk.Button(top, height=2, width=20, text="Processing..")
        self.controlButton.pack()
        


    def stop(self):        
        self.checkon=False
        geoscopeoff()
        
        self.controlButton.destroy()
        self.controlButton = tk.Button(top, height=2, width=20, text="Processing..")
        self.controlButton.pack()
        top.update()  
           
        self.start_time = time.time()
        self.readingnumber+=1        
        filename=self.name.get()+" Run#"+str(self.readingnumber)+'.json' 
        runspath= "C:\\Users\\14438\\OneDrive\\Desktop\\gprcoverage_app\\Runs\\" 
        rootpath= "C:\\Users\\14438\\OneDrive\\Desktop\\gprcoverage_app\\"
        #print(jsonarray)
        with open(runspath+filename, 'w') as f:#save a copy of file after everyrun
            f.write(geojson.dumps(geojson.FeatureCollection([generatejson(self.jsonarray)]), indent=4))
        measurecoverage(filename,runspath,rootpath)
        self.controlButton.destroy()
        self.controlButton = tk.Button(top, height=2, width=20, text="Start Run "+str(self.readingnumber), command=self.start)
        self.controlButton.pack()
        

        if self.after_id:
            top.after_cancel(self.after_id)
            self.after_id = None

            self.controlButton.destroy()
            self.controlButton = tk.Button(top, height=2, width=20, text="Start Run "+str(self.readingnumber), command=self.start)
            self.controlButton.pack()


if __name__ == '__main__':
    top = tk.Tk()
    app = Application()
    app.master.title('MapAwareness')
    #app.master.minsize('height=600, width=400')
    app.master.geometry('400x200+1200+100')
    #app.master.attributes('-alpha',.5)
    app.mainloop()