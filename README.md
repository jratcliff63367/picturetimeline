# picturetimeline
This is a python script which can generate a timeline from a random collection of photographs

This is a python script which does the following:

Point it at a directory which contains a series of photographs (edit: source_directory to point to your folder)

When you run the script it will do the following:

Scan all images in that directory

Collect all images which have a valid time and date stamp as well as geolocation data

It will then sort all of those images by date

Then, for each image, it will use the openmaps API to do a reverse geolocation lookup on the GPS coordinate

in each image. It will look for the nearest business, address, city, state, and country.

If it can get that information from the OpenMaps API and the location is different that the previous image

then it will write out an entry to a CSV file that you can later import into a spreadhsheet tool like Google sheets

You will end up with a detailed timeline of 'where every picture was taken' including a link to Google Maps to take

you to that specific location.

I did not write this script myself.

However, I did iterate with ChatGPT4o to create it.

I have run this script against a library of over 100k photographs and it worked great!
