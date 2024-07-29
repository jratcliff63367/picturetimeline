# This is a python script which does the following:
#  Point it at a directory which contains a series of photographs (edit: source_directory to point to your folder)
#  When you run the script it will do the following:
#    Scan all images in that directory
#    Collect all images which have a valid time and date stamp as well as geolocation data
#    It will then sort all of those images by date 
#    Then, for each image, it will use the openmaps API to do a reverse geolocation lookup on the GPS coordinate
#    in each image. It will look for the nearest business, address, city, state, and country.
#    If it can get that information from the OpenMaps API and the location is different that the previous image
#    then it will write out an entry to a CSV file that you can later import into a spreadhsheet tool like Google sheets
#
#    You will end up with a detailed timeline of 'where every picture was taken' including a link to Google Maps to take
#    you to that specific location.
import os
import csv
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from datetime import datetime
from collections import namedtuple

# Define a namedtuple to store photo metadata
PhotoMetadata = namedtuple('PhotoMetadata', ['date_time', 'image_path', 'latitude', 'longitude'])

def get_exif_data(image_path):
    """Extract EXIF data from an image and return date, time, latitude, and longitude if available."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return None
        
        exif = {TAGS[k]: v for k, v in exif_data.items() if k in TAGS}
        
        gps_info = exif.get('GPSInfo')
        if not gps_info:
            return None
        
        gps_data = {GPSTAGS.get(t, t): gps_info[t] for t in gps_info}
        
        gps_latitude = gps_data.get('GPSLatitude')
        gps_latitude_ref = gps_data.get('GPSLatitudeRef')
        gps_longitude = gps_data.get('GPSLongitude')
        gps_longitude_ref = gps_data.get('GPSLongitudeRef')
        
        if not gps_latitude or not gps_longitude or not gps_latitude_ref or not gps_longitude_ref:
            return None
        
        # Convert GPS coordinates to decimal degrees
        lat = convert_to_degrees(gps_latitude, gps_latitude_ref)
        lon = convert_to_degrees(gps_longitude, gps_longitude_ref)
        
        date_time = exif.get('DateTimeOriginal')
        if not date_time:
            return None
        
        return PhotoMetadata(date_time=date_time, image_path=image_path, latitude=lat, longitude=lon)
    except Exception as e:
        print(f"Error reading EXIF data from {image_path}: {e}")
        return None

def convert_to_degrees(value, ref):
    """Convert GPS coordinates to decimal degrees."""
    try:
        d = float(value[0].numerator) / float(value[0].denominator)
        m = float(value[1].numerator) / float(value[1].denominator)
        s = float(value[2].numerator) / float(value[2].denominator)
        
        degrees = d + (m / 60.0) + (s / 3600.0)
        if ref in ['S', 'W']:
            degrees = -degrees
        return degrees
    except Exception as e:
        print(f"Error converting GPS data: {e}")
        return None

def reverse_geocode(lat, lon):
    """Reverse geocode latitude and longitude to get address details using Nominatim API."""
    try:
        geolocator = Nominatim(user_agent="photo_timeline_script")
        location = geolocator.reverse((lat, lon), language='en')
        
        if not location:
            return None, None, None, None, None
        
        address = location.raw['address']
        road = address.get('road', '')
        city = address.get('city', address.get('town', address.get('village', '')))
        state = address.get('state', '')
        country = address.get('country', '')
        
        # Assuming the nearest business is the name of the location if available
        business = address.get('shop', address.get('amenity', ''))
        
        return business, road, city, state, country
    except Exception as e:
        print(f"Error during reverse geocoding: {e}")
        return None, None, None, None, None

def process_images(directory):
    """Process all images in the directory and generate a CSV timeline."""
    photos = []
    print("Scanning for pictures...")
    
    # Walk through all subdirectories to find image files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png')):
                image_path = os.path.join(root, file)
                metadata = get_exif_data(image_path)
                if metadata:
                    photos.append(metadata)

    print("Sorting pictures...")
    # Sort photos by date and time
    photos.sort(key=lambda x: datetime.strptime(x.date_time, '%Y:%m:%d %H:%M:%S'))
    
    # Create CSV file
    output_file = os.path.join(directory, 'photo_timeline.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'date photo taken', 'time photo taken', 'image path', 'nearest business', 
            'nearest street address', 'nearest city', 'nearest state', 'nearest country', 
            'GPS coordinates', 'Google Maps link'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        
        writer.writeheader()
        
        print("Writing to CSV...")
        previous_entry = None
        for i, photo in enumerate(photos):
            date, time = photo.date_time.split(' ')
            business, road, city, state, country = reverse_geocode(photo.latitude, photo.longitude)
            
            # Ensure values are not None
            business = business if business else ''
            road = road if road else ''
            city = city if city else ''
            state = state if state else ''
            country = country if country else ''
            
            gps_coordinates = f"{photo.latitude}, {photo.longitude}"
            google_maps_link = f"https://www.google.com/maps/search/?api=1&query={photo.latitude},{photo.longitude}"
            
            current_entry = (business, road, city, state, country)
            if current_entry != previous_entry:
                try:
                    row = {
                        'date photo taken': date,
                        'time photo taken': time,
                        'image path': photo.image_path,
                        'nearest business': business.encode('ascii', 'ignore').decode('ascii'),
                        'nearest street address': road.encode('ascii', 'ignore').decode('ascii'),
                        'nearest city': city.encode('ascii', 'ignore').decode('ascii'),
                        'nearest state': state.encode('ascii', 'ignore').decode('ascii'),
                        'nearest country': country.encode('ascii', 'ignore').decode('ascii'),
                        'GPS coordinates': gps_coordinates,
                        'Google Maps link': google_maps_link
                    }
                    writer.writerow(row)
                except UnicodeEncodeError as e:
                    print(f"Encoding error: {e}. Skipping record: {photo}")
                previous_entry = current_entry
            if (i + 1) % 100 == 0 or (i + 1) == len(photos):
                print(f"Written {i + 1}/{len(photos)} records to CSV")

if __name__ == '__main__':
    # Assign your source directory here
    source_directory = 'e:/gather-pics'
    process_images(source_directory)
    print("Timeline CSV has been generated successfully.")
