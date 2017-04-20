#!/usr/bin/python

import os

import csv

"""
import pycurl
from StringIO import StringIO

import json

from urllib import urlencode
"""

from models import session, OpenAddresses




file_location = '/home/chris/projects/openaddresses/us/pa/philadelphia.csv'


line = 1

num_added = 0

csvfile = open(file_location, 'r')

csvreader = csv.reader(csvfile) #, delimiter=',', quotechar='"'

header_row = next(csvreader)   # skip the first line

numerical_list = list('1234567890.-')

processed_list = {}


print(header_row)

for row in csvreader:

    line += 1

    row_dict = dict(zip(header_row, row))

    for i in row_dict:
        #print dir(td)

        row_dict[i] = row_dict[i].strip()

    #print row_dict
    #break

    if row_dict['POSTCODE'] == '' or row_dict['NUMBER'] == '' or row_dict['STREET'] == '':
        print("Error with line and row: ", line, row)
        continue

    zipcode = int(row_dict['POSTCODE'][:5])

    if zipcode not in processed_list:
        processed_list[zipcode] = []

    addr1 = row_dict['NUMBER']+' '+row_dict['STREET']

    if addr1 not in processed_list[zipcode]:
        processed_list[zipcode].append(addr1)


        try:

            open_addy = OpenAddresses()
            open_addy.number = row_dict['NUMBER']
            open_addy.street = row_dict['STREET']
            open_addy.zipcode5 = zipcode
            open_addy.longitude = row_dict['LON']
            open_addy.latitude = row_dict['LAT']

            session.add(open_addy) 

            num_added += 1

        except Exception, e:

            print('Error accessing Cicero data:', e)

            num_broken += 1


    session.commit()

    #break


print('found '+str(num_added)+' in '+str(line)+' lines.')


