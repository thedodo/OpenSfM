from geopy.geocoders import Nominatim
import json
import sys
import os
import overpy
import numpy as np
from geopy import distance

#if road name is not available => search for closest street
#search in a radius
def searchForStreet(radius):
    
    query_test = """way(around:""" + str(radius)+ ',' + str(lat) + "," + str(long) + """);out;"""
    result_test = api.query(query_test)
    test_way = result_test.ways[0]
    test_nodes = test_way.get_nodes(resolve_missing=True)
    location = geolocator.reverse(str(test_nodes[0].lat) + ',' + str(test_nodes[0].lon)) #zoom=16
    return location


lat = sys.argv[1]
long = sys.argv[2]
lat = float(lat)
long = float(long)

latlong_str = str(lat) + ', ' + str(long)
geolocator = Nominatim(user_agent="SV4VILoc")
location = geolocator.reverse(latlong_str) #zoom=16
print(location.raw)
loc_addr = location.raw 


if 'road' not in loc_addr['address']:

    output_string = 'Leider konnte keine Straße gefunden werden'
    search_string = 'Suche in 50m Radius nach Straße'

    print(output_string)
    print(search_string)
    
    radius = 50.0
    loc = searchForStreet(radius)
    #if loc empty!
    print(location.raw["display_name"])
    print('On google maps: ')
    maps_string = 'http://www.google.com/maps/place/' + str(lat) + ',' + str(long)
    print(maps_string)
    exit()
    
    
    
if 'house_number' not in loc_addr['address']:
    output_string = 'Du befindest dich in der ' + loc_addr["address"]["road"] + ' Straße'
else:
    output_string = 'Du befindest dich in der ' + loc_addr["address"]["road"] + ' Straße Nummer ' + loc_addr["address"]["house_number"]

print(output_string)

road_name = loc_addr["address"]["road"]

lat_s = round(lat,1) - 0.1
long_s = round(long,1) - 0.1

lat_l = round(lat,1) + 0.1
long_l = round(long,1) + 0.1

bbox_string = '(' + str(lat_s) + ',' + str(long_s) + ',' + str(lat_l) + ',' + str(long_l) + ')'


query_string = """way["name"=""" + road_name + "]"+bbox_string+";out;"""
print(query_string)

api = overpy.Overpass()
result = api.query(query_string)

way = result.ways[0]
nodes = way.get_nodes(resolve_missing=True)


#possible accuracy => if 10 nodes in street (evenly spaced?????) then node 2 is 20%!
street_perc = 1.0/len(nodes)


cur_pos = (lat, long)

dist = 100000000
s_pos = -1

for pos in range(0,len(nodes)):
    
    node_pos = (nodes[pos].lat, nodes[pos].lon)
    c_dist = distance.distance(cur_pos, node_pos).km
    if(dist > c_dist):
        dist = c_dist
        s_pos = pos
    
perc = int((street_perc * s_pos) * 100)

print('Du hast die Strasse zu %i prozent passiert'  %perc)

print('On google maps: ')
maps_string = 'http://www.google.com/maps/place/' + str(lat) + ',' + str(long)
print(maps_string)
