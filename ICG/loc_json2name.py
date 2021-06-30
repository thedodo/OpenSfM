from geopy.geocoders import Nominatim
import json
import sys
import os
import overpy
import numpy as np
from geopy import distance
import os.path
from os import path

data = []
#open should be dynamical obviously
json_name = sys.argv[1]
im_name = sys.argv[2]

if not path.exists(json_name): 
    print("Leider konnte das Bild nicht lokalisiert werden")
    exit()

if os.stat(json_name).st_size == 2:
    print('Leider konnte keine Addresse gefunden werden')
    exit()

with open(json_name) as json_file:
    data = json.load(json_file)
    
print(data)

#first is image name in loc folder
if 'gps' not in data[im_name]:
    print('Leider konnte keine Addresse gefunden werden')
    exit()
    
lat = data[im_name]["gps"][0]
long = data[im_name]["gps"][1]


#47.058290, 15.458398
# 47.069860, 15.443725 

#Tummel close to road!
#lat = 47.069784
#long = 15.444058 

#Tummel on road!
#lat = 47.069860
#long = 15.443725

latlong_str = str(lat) + ', ' + str(long)
geolocator = Nominatim(user_agent="SV4VILoc")
location = geolocator.reverse(latlong_str) #zoom=16
print(location.raw)
loc_addr = location.raw

new_json = json_name.replace(json_name.split('/')[-1],'') + 'loc_name.json'

with open(new_json, "w") as write_file:
    json.dump(loc_addr, write_file)

with open(new_json) as json_file:
    names = json.load(json_file)

    
if 'address' not in names: 
    output_string = 'Leider konnte keine Addresse gefunden werden'
    exit()

if 'road' not in names['address']:
    output_string = 'Leider konnte keine Addresse gefunden werden'
    print(output_string)
    print('On google maps: ')
    maps_string = 'http://www.google.com/maps/place/' + str(lat) + ',' + str(long)
    print(maps_string)
    exit()    
    
if 'house_number' not in names['address']:
    output_string = 'Du befindest dich in der ' + names["address"]["road"] + ' Straße'
else:
    output_string = 'Du befindest dich in der ' + names["address"]["road"] + ' Straße Nummer ' + names["address"]["house_number"]

print(output_string)
print('On google maps: ')
maps_string = 'http://www.google.com/maps/place/' + str(lat) + ',' + str(long)
print(maps_string)

road_name = names["address"]["road"]

lat_s = round(lat,1) - 0.1
long_s = round(long,1) - 0.1

lat_l = round(lat,1) + 0.1
long_l = round(long,1) + 0.1

bbox_string = '(' + str(lat_s) + ',' + str(long_s) + ',' + str(lat_l) + ',' + str(long_l) + ')'


query_string = """way["name"=""" + road_name + "]"+bbox_string+";out;"""

api = overpy.Overpass()
result = api.query(query_string)

way = result.ways[0]
nodes = way.get_nodes(resolve_missing=True)


#possible accuracy => if 10 nodes in street (evenly spaced?????) then node 2 is 20%!
street_perc = 1.0/len(nodes)


#print(len(nodes))
cur_pos = (lat, long)
#
dist = 100000000
s_pos = -1

for pos in range(0,len(nodes)):
    
    #print('node: ', pos)
    #print('lat: ', nodes[pos].lat)
    #print('long: ', nodes[pos].lon)
    node_pos = (nodes[pos].lat, nodes[pos].lon)
    c_dist = distance.distance(cur_pos, node_pos).km
    if(dist > c_dist):
        dist = c_dist
        s_pos = pos
    
perc = int((street_perc * s_pos) * 100)

print('Du hast die Strasse zu %i prozent passiert'  %perc)
#wellington = (-41.32, 174.81)
#salamanca = (40.96, -5.50)
#print(distance.distance(wellington, salamanca).km)


      
#if road name is not available => search for closest street
#search in a radius of 50m
radius = 50.0
query_test = """way(around:""" + str(radius)+ ',' + str(lat) + "," + str(long) + """);out;"""
result_test = api.query(query_test)
#test_way = result_test.ways[0]

#print(result_test.ways)
test_way = result_test.ways[0]
test_nodes = test_way.get_nodes(resolve_missing=True)
#print(test_nodes)

#with this node get name again as before!!!!!!
location = geolocator.reverse(str(test_nodes[0].lat) + ',' + str(test_nodes[0].lon)) #zoom=16
print(location.raw)

print(location.raw["display_name"])



    