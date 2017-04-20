#!/usr/bin/python

import os

import pycurl
from StringIO import StringIO

import json

from urllib import urlencode

from models import session, PoliticalDonation, CiceroDistrict, PoliticalDonationContributor, PoliticalDonationContributorAddress
from models import PoliticalDonationContributorAddressCiceroDetails, PoliticalDonationContributorAddressCiceroRaw


token = '4kz-a90df93759f3875046dc'
user = ''# 1346

# Function to do our API calls (returns object made from JSON)
# Copied from Cicero's PHP example
# http://cicero.azavea.com/docs/hello_world_php.html
def get_cicero_response(url, postfields=''):

    #print('postfields:', postfields)

    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)

    if postfields != '':
        #print('adding post fields option')
        c.setopt(c.POSTFIELDS, postfields)

    c.perform()
    c.close()

    result_json = buffer.getvalue()
    # Body is a string in some encoding.
    # In Python 2, we can print it without knowing what the encoding is.
    #print(result_json)

    #print result_json

    #print dir(result_json)

    return json.loads(result_json)




def get_cicero_legislatrive_response(address, token, user):


    # Check for address from addr1 and zipcode5
    try:

        existing_response = session.query(PoliticalDonationContributorAddressCiceroRaw)\
            .filter(PoliticalDonationContributorAddressCiceroRaw.addr1==address.addr1)\
            .filter(PoliticalDonationContributorAddressCiceroRaw.zipcode5==address.zipcode[:5])\
            .one()

        print 'returning cached response'

        return json.loads(existing_response.response)

    except Exception, e:

        post_address_encoded = 'search_loc='+address.addr1.replace(' ', '+')+','+address.zipcode[:5]+'&token='+token+'&user='+str(user)+'&f=json'
        print(post_address_encoded)

        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://cicero.azavea.com/v3.1/legislative_district')
        #c.setopt(c.REFERER, 'http://leveragecampaignfinance.org/')
        c.setopt(c.POST, True)

        c.setopt(c.WRITEDATA, buffer)

        c.setopt(c.POSTFIELDS, post_address_encoded)

        c.perform()
        c.close()

        result_json = buffer.getvalue()

        print result_json

        result = json.loads(result_json)

        cicero_raw = PoliticalDonationContributorAddressCiceroRaw()
        cicero_raw.addr1 = address.addr1
        cicero_raw.zipcode5 = address.zipcode[:5]
        cicero_raw.response = result_json

        session.add(cicero_raw)        
        session.commit()

        return result





# Obtain a token:
if token == '' or user == '':
    postfields = {"username":os.environ.get('CICERO_USER'), "password":os.environ.get('CICERO_PASS')}
    response = get_cicero_response('http://cicero.azavea.com/v3.1/token/new.json', urlencode(postfields))
    print(response)

    try:
        response['success'] == True

        token = response['token']
        user = response['user']

    except Exception, e:

        print('Error getting token.', str(e))



#print('token:', token)
#print('user:', user)


processed_list = []


# Get addresses for committee 601 from state = 'PA' 
addresses = session.query(PoliticalDonationContributorAddress)\
    .join(PoliticalDonationContributorAddress.contributors)\
    .join(PoliticalDonationContributor.donations)\
    .filter(PoliticalDonationContributorAddress.state == 'PA')\
    .filter(PoliticalDonation.committee_id == 601)

for address in addresses:

    if address.addr1+address.zipcode[:5] in processed_list:
        continue

    processed_list.append(address.addr1+address.zipcode[:5])

    cicero_objs = get_cicero_legislatrive_response(address, token, user)

    break
