from geopy.geocoders import Nominatim
import json


data = []
#open should be dynamical obviously
with open('/home/dominik/SV4VI/Experimental/OpenSfM/data/lund/localize/localize.json') as json_file:
    data = json.load(json_file)

#first is image name in loc folder
    
lat = data["01.jpg"]["gps"][0]
long = data["01.jpg"]["gps"][1]

latlong_str = str(lat) + ', ' + str(long)
geolocator = Nominatim(user_agent="SV4VILoc")
location = geolocator.reverse(latlong_str)
print(location.raw)
loc_addr = location.raw

with open("/home/dominik/SV4VI/Experimental/OpenSfM/data/lund/localize/loc_name.json", "w") as write_file:
    json.dump(loc_addr, write_file)

with open('/home/dominik/SV4VI/Experimental/OpenSfM/data/lund/localize/loc_name.json') as json_file:
    names = json.load(json_file)

output_string = 'Du befindest dich in der ' + names["address"]["road"] + ' Straße Nummer ' + names["address"]["house_number"]
print(output_string)
#loc_addr = location.address
#print(location.address)


    