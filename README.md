# picturetimeline
This is a python script which can generate a timeline from a random collection of photographs

Don't forget to do a PIP install on:

 pip install Pillow

 pip install geopy

This is a python script which does the following:

Point it at a directory (and sub-directories) which contains a series of photographs (edit: source_directory to point to your folder)

When you run the script it will do the following:

Scan all images in that directory (and sub-directories)

Collect all images which have a valid time and date stamp as well as geolocation data

It will then sort all of those images by date

Then, for each image, it will use the openmaps API to do a reverse geolocation lookup on the GPS coordinate in each image. It will look for the nearest business, address, city, state, and country.

If it can get that information from the OpenMaps API and the location is different that the previous image then it will write out an entry to a CSV file that you can later import into a spreadhsheet tool like Google sheets

You will end up with a detailed timeline of 'where every picture was taken' including a link to Google Maps to take you to that specific location.

I did not write this script myself. However, I did iterate with ChatGPT4o to create it.

I have run this script against a library of over 100k photographs and it worked great!

If you have improvements to this script either give it more features or make it more robust doing reverse geolocation lookups, please feel free to submit these changes.

I used ChatGPT4o to create the following python script which I have found to be generally very useful.

What it does is that it creates a timeline from a random sequence of photographs.

If you have a whole bunch of photographs that you have taken from all around the world, what this script will do is scan them all, sort them by time and date, and then do a reverse geolocation lookup to find the nearest business, street address, city, state, and country and then write them out to a CSV file; including a hyperlink to Google maps for each one.

If two or more pictures in a row are from the same location it only writes out one entry into the spreadsheet.

I found this to be generally quite useful and I have run it against over a 100k photographs and it worked great.

I barely know how to code in Python myself, and learning APIs is quite time consuming. I had to iterate quite a bit to get ChatGPTo to produce valid output. However, I was able to iterate on it and eventually get good results.

One note, reverse geolocation lookup APIs have some limitations. It doesn't give an exact street address and, in general, it cannot report a valid nearest business. This isn't an issue with the script itself, however, it's just a limitation of the openmaps API. I did try using the Google maps API (which you have to pay for) and it did not produce appreciably better results so I'm leaving it with Openmaps API as the default.

I just hard coded the path name for where to scan for photos, so be sure to edit 'source_directory' for your folder.