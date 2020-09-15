from geopy.geocoders import Nominatim
import json
import sys
import os


data = []
#open should be dynamical obviously
json_name = sys.argv[1]
im_name = sys.argv[2]

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

latlong_str = str(lat) + ', ' + str(long)
geolocator = Nominatim(user_agent="SV4VILoc")
location = geolocator.reverse(latlong_str)
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

if 'house_number' not in names['address']:
    output_string = 'Du befindest dich in der ' + names["address"]["road"] + ' Straße'
else:
    output_string = 'Du befindest dich in der ' + names["address"]["road"] + ' Straße Nummer ' + names["address"]["house_number"]

print(output_string)
print('On google maps: ')
maps_string = 'http://www.google.com/maps/place/' + str(lat) + ',' + str(long)
print(maps_string)
#loc_addr = location.address
#print(location.address)


    