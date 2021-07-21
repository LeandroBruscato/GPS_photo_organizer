from os import error
from geopy.geocoders import Nominatim
import os
import shutil
import time

# initialize Nominatim API 
geolocator = Nominatim(user_agent="geoapiExercises")

from pprint import pprint
from PIL import Image
import piexif

codec = 'ISO-8859-1'  # or latin-1

def exif_to_tag(exif_dict):
    exif_tag_dict = {}
    thumbnail = exif_dict.pop('thumbnail')
    exif_tag_dict['thumbnail'] = thumbnail.decode(codec)

    for ifd in exif_dict:
        exif_tag_dict[ifd] = {}
        for tag in exif_dict[ifd]:
            try:
                element = exif_dict[ifd][tag].decode(codec)

            except AttributeError:
                element = exif_dict[ifd][tag]

            exif_tag_dict[ifd][piexif.TAGS[ifd][tag]["name"]] = element

    return exif_tag_dict


def get_coordinates(info):
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
            e = info['GPS'+key]
            ref = info['GPS'+key+'Ref']
            info[key] = ( str(e[0][0]/e[0][1]) + '°' +
                          str(e[1][0]/e[1][1]) + '′' +
                          str(e[2][0]/e[2][1]) + '″ ' +
                          ref )

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]

def get_decimal_coordinates(info):
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
            e = info['GPS'+key]
            ref = info['GPS'+key+'Ref']
            info[key] = ( e[0][0]/e[0][1] +
                          e[1][0]/e[1][1] / 60 +
                          e[2][0]/e[2][1] / 3600
                        ) * (-1 if ref in ['S','W'] else 1)

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]


def GetCityByGPS(fileName):
    try:
        im = Image.open(fileName)

        exif_dict = piexif.load(im.info.get('exif'))
        exif_dict = exif_to_tag(exif_dict)
        [Latitude,Longitude] = get_decimal_coordinates(exif_dict['GPS'])
        location = geolocator.reverse(str(Latitude)+","+str(Longitude))
        cityTag = 'city'
        townTag = 'town'
        dictAddress = (location.raw)['address']
        if cityTag in dictAddress:
            return dictAddress[cityTag]
        elif townTag in dictAddress:
            return dictAddress[townTag]
        else:
            return "Unknown!"
    except :        
        return "Unknown!"

def MoveFile(fileName, folder):  
    try:
        file_path = os.path.join(os.path.abspath(os.getcwd()), fileName)
        dir_path = os.path.join(os.path.abspath(os.getcwd()), folder)
        if not os.path.exists(folder):
            os.makedirs(folder)

        if not os.path.exists(os.path.join(dir_path, fileName)):
            shutil.move(file_path, dir_path)
        else:
            os.remove(fileName)
    except :
        return "Error"

def main():
    import glob, os
    import pathlib
    pathlib.Path().resolve()
    os.chdir(pathlib.Path().resolve())
    for fileName in glob.glob("*.jpg"):
        print(fileName)
        folder = GetCityByGPS(fileName)
        MoveFile(fileName, folder)
        times = 1
        while(os.path.exists(os.path.join(fileName)) and times < 10):
            time.sleep(times)
            times += 1
            MoveFile(fileName, folder)

        
if __name__ == '__main__':
   main()