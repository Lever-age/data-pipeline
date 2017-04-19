#!/usr/bin/python

import os

import pycurl
from StringIO import StringIO

import json

from urllib import urlencode

from cicero import *


from models import session, PoliticalDonation, CiceroDistrict, PoliticalDonationContributor, PoliticalDonationContributorAddress
from models import PoliticalDonationContributorAddressCiceroDetails, PoliticalDonationContributorAddressCiceroRaw


"""
UPDATE political_donation_contributor_address_cicero_raw r,  political_donation_contributor_address a
SET r.address_id = a.id
WHERE r.zipcode = a.zipcode and r.addr1 = a.addr1
"""



#print('token:', token)
#print('user:', user)


processed_list = []


cicero = CiceroRestConnection(os.environ.get('CICERO_USER'), os.environ.get('CICERO_PASS'))

#district = cicero.get_legislative_district(search_loc="1717 GREEN ST, 19130")

cicero_districts = session.query(CiceroDistrict)
cicero_district_dict = {d.cicero_id: d for d in cicero_districts}

print('cicero district ids dict', [d for d in cicero_district_dict])

# Get addresses for committee 601 from state = 'PA' 
addresses = session.query(PoliticalDonationContributorAddress)\
    .join(PoliticalDonationContributorAddress.contributors)\
    .join(PoliticalDonationContributor.donations)\
    .filter(PoliticalDonationContributorAddress.state == 'PA')\
    .filter(PoliticalDonationContributorAddress.city.like('Ph%'))\
    .filter(PoliticalDonation.committee_id == 601)

#print addresses



num_new = 0
num_cached = 0
num_broken = 0

for address in addresses:

    if address.addr1+address.zipcode[:5] in processed_list:
        continue

    processed_list.append(address.addr1+address.zipcode[:5])


    # Check for cached cicero info from addr1 and zipcode5
    try:

        existing_response = session.query(PoliticalDonationContributorAddressCiceroRaw)\
            .filter(PoliticalDonationContributorAddressCiceroRaw.addr1==address.addr1)\
            .filter(PoliticalDonationContributorAddressCiceroRaw.zipcode5==address.zipcode[:5])\
            .one()

        print 'found cached response'

        num_cached += 1

        #return json.loads(existing_response.response)
        cicerto_district_ids = existing_response.district_ids.split(',')
        address.cicero_districts = [cicero_district_dict[int(id)] for id in cicerto_district_ids]


    except Exception, e:

        cicero_result = cicero.get_legislative_district(search_loc=address.addr1+','+address.zipcode[:5])

        #print cicero_result

        #print json.dumps(str(cicero_result))

        try:

            candidate = cicero_result.response.results.candidates[0]

            print(candidate.x, candidate.y)

            cicero_raw = PoliticalDonationContributorAddressCiceroRaw()
            cicero_raw.addr1 = address.addr1
            cicero_raw.zipcode5 = address.zipcode[:5]
            cicero_raw.district_ids = ','.join([str(d.id) for d in candidate.districts])
            cicero_raw.geo_x = candidate.x
            cicero_raw.geo_y = candidate.y
            cicero_raw.match_addr=candidate.match_addr
            cicero_raw.raw_text = json.dumps(str(cicero_result))

            session.add(cicero_raw) 

            """
            new_cicero_details = PoliticalDonationContributorAddressCiceroDetails(address=address, wkid=candidate.wkid,\
                score=candidate.score, geo_x=candidate.x, geo_y=candidate.y, match_addr=candidate.match_addr,\
                match_postal=candidate.match_postal, match_country=candidate.match_country,locator=candidate.locator,\
                match_region=candidate.match_region, match_subregion=candidate.match_subregion, match_city=candidate.match_city,\
                partial_match=candidate.partial_match, geoservice=candidate.geoservice)
            """ 

            new_cicero_details = PoliticalDonationContributorAddressCiceroDetails(address=address, wkid=candidate.wkid,\
                score=candidate.score, geo_x=candidate.x, geo_y=candidate.y, match_addr=candidate.match_addr,\
                locator=candidate.locator, geoservice=candidate.geoservice)

            session.add(new_cicero_details)        

            for district in candidate.districts:

                if district.id not in cicero_district_dict:

                    valid_to = district.valid_to if district.valid_to else ''


                    """
                    new_district = CiceroDistrict(cicero_id=district.id, sk=district.id, district_type=district.district_type,\
                        valid_from=district.valid_from, valid_to=valid_to, country=district.country, state=district.state,
                        city=district.city, subtype=district.subtype, district_id=district.district_id, 
                        num_officials=district.num_officials, label=district.label, ocd_id=district.ocd_id,
                        data=district.data, last_update_date=district.last_update_date)
                    """

                    # Remove num_officials, ocd_id

                    new_district = CiceroDistrict(cicero_id=district.id, sk=district.id, district_type=district.district_type,\
                        valid_from=district.valid_from, valid_to=valid_to, country=district.country, state=district.state,\
                        city=district.city, subtype=district.subtype, district_id=district.district_id, \
                        label=district.label,\
                        data=json.dumps(district.data), last_update_date=district.last_update_date)

                    session.add(new_district)

                    session.commit()

                    cicero_district_dict[district.id] = new_district


            address.cicero_districts = [cicero_district_dict[d.id] for d in candidate.districts]

            session.add(address)

            num_new += 1

        except Exception, e:

            print('Error accessing Cicero data:', e)

            num_broken += 1


    session.commit()

    #break


print('found '+str(num_new)+' new address and '+str(num_cached)+' cached and '+str(num_broken)+' broken.')


