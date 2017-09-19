#!/usr/bin/python
# coding: utf-8

import sys

import os

import csv

import json

import datetime

from models import *

from functions import *

from standardize_us_address import *


current_dir = os.path.dirname(os.path.realpath(__file__))

year = int(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.now().year

file_location = current_dir+'/Explorer.Transactions.'+str(year)+'.YTD.txt'


# amount_list is used to clean the amount
amount_list = list('1234567890.,-')


address_pre_token_replacement_dict = dict()



total_contributed = 0



line = 1

csvfile = open(file_location, 'r')

csvreader = csv.reader(csvfile, delimiter='\t', quotechar='"')

de_election_db_cache = DeElectionDBCache()
de_election_db_cache.load_cache()


header_row = next(csvreader)   # skip the first line

print(header_row)

city_list = []

ignore_doc_types = ['Independent Expenditure', 'Campaign Finance Report (Cover Page)', 'Campaign Finance Statement']

for row in csvreader:

    line += 1

    #print(len(row))
    #break

    if len(row) == 23:

        for i in range(len(row)):
            row[i] = row[i].strip()

        row_dict = dict(zip(header_row, row))

        #print(line, row_dict['DocType'])


        # cat Explorer.Transactions.2016.YTD.txt | grep 'Independent Expenditure'
        # Skip 'Independent Expenditure'
        if row_dict['DocType'] in ignore_doc_types:
            continue

        # Some lines are empty
        if row_dict['EntityName'] == '':
            continue

        # Only store first 5 digits of zipcode
        row_dict['EntityZip'] = row_dict['EntityZip'][:5]

        #print(row_dict)
        #break
        """
        donation = RawDonation(**row_dict)

        session.add(donation)
        session.commit()
        """



        # Look for weird characters in amounts
        received_list = list(row_dict['Amount'])

        extra_chars = [c for c in received_list if c not in amount_list] 

        if len(extra_chars):
            print("ERROR: line",line,': extra chars in amount:', ''.join(extra_chars))

        donation_amount = ''.join(re.findall('([0-9\.-])', row_dict['Amount']))

        #print 'donation:', donation_amount

        donation_date_obj = datetime.datetime.strptime(row_dict['SubDate'], '%m/%d/%Y')

        committee_id = de_election_db_cache.return_donation_commitee_id_from_name(row_dict['FilerName'])

        contribution_type_id = de_election_db_cache.return_contribution_type_id_from_name(row_dict['DocType'])

        #contributor_type_id = de_election_db_cache.return_contributor_type_id_from_name(row_dict[''])
        contributor_type_id = 0

        filing_period_id = de_election_db_cache.return_filing_period_id_from_name(row_dict['Cycle'])

        employer_name_id = 0
        if row_dict['EmployerName'] != '':
            employer_name_id = de_election_db_cache.return_employer_name_id_from_name(row_dict['EmployerName'])

        employer_occupation_id = 0
        if row_dict['Occupation'] != '':
            employer_occupation_id = de_election_db_cache.return_employer_occupation_id_from_name(row_dict['Occupation'])


        office_id = 0

        is_fixed_asset = 1 if row_dict['Amended'] == 'Y' else 0


        ## Restart Here!


        # 'Total of Contributions not exceeding $100'
        is_annonymous = 0
        contributor_id = 0
        contributor_address_id = 0

        if row_dict['EntityName'] == 'Total of Contributions not exceeding $100':
            is_annonymous = 1

        else:

            full_name = ''

            bad_name = False
            bad_addy = False

            better_name = row_dict['EntityName'].replace('&', 'AND')

            name_dict = clean_name(better_name)


            if type(name_dict) is not dict:

                print 'name ERROR:'
                bad_name = True

            mailing_address = row_dict['EntityAddressLine1'].upper().replace('  ',', ')

            # Will want to clean up address before using. Check where NotAddress field is set!
            for r in address_pre_token_replacement_dict:
                mailing_address = mailing_address.replace(r, address_pre_token_replacement_dict[r])



            address_dict = standardize_us_address(mailing_address)


            if type(address_dict) is not dict:

                print 'addy ERROR:'
                bad_addy = True



            #ensure_address_fields_list = ['PlaceName', 'StateName', 'ZipCode']

            #for field in ensure_address_fields_list:
            #    if not bad_addy and field not in address_dict:
            #        address_dict[field] = ''


            if bad_addy or address_dict['address_type'] in ['Ambiguous', 'Intersection']:

                contributor_address_id = 0

            elif address_dict['address_type'] == 'PO Box':

                # Get address
                try:

                    contributor_address = session.query(PoliticalDonationContributorAddress)\
                        .filter(PoliticalDonationContributorAddress.address_type == 'PO Box')\
                        .filter(PoliticalDonationContributorAddress.po_box == address_dict['USPSBoxID'])\
                        .filter(PoliticalDonationContributorAddress.zipcode == row_dict['EntityZip'])\
                        .one()

                except Exception as e:


                    contributor_address = PoliticalDonationContributorAddress()
                    contributor_address.address_type = address_dict['address_type']

                    contributor_address.po_box = address_dict['USPSBoxID']
                    contributor_address.city = row_dict['EntityCity']
                    contributor_address.state = row_dict['EntityState']
                    contributor_address.zipcode = row_dict['EntityZip']

                    session.add(contributor_address)        
                    session.commit()

                contributor_address_id = contributor_address.id

            else: # Should be a normal address

                addr1 = ''

                addr_build_list = ['AddressNumber', 'AddressNumberSuffix', 'StreetNamePreDirectional', 'StreetName', \
                    'StreetNamePostType', 'StreetNamePostDirectional']

                for field in addr_build_list:

                    if field in address_dict:
                        addr1 = addr1+' '+address_dict[field]

                addr1 = addr1.strip()

                #print addr1
                #if line > 8:
                #    break

                # Get address
                try:

                    #print('Checking address')

                    contributor_address = session.query(PoliticalDonationContributorAddress)\
                        .filter(PoliticalDonationContributorAddress.address_type == 'Street Address')\
                        .filter(PoliticalDonationContributorAddress.addr1 == addr1)\
                        .filter(PoliticalDonationContributorAddress.zipcode == row_dict['EntityZip'])

                    #print('obj:', PoliticalDonationContributorAddress)

                    contributor_address = contributor_address.one()

                except Exception as e:

                    #print("Error", e)
                    #print("Didn't find address:", addr1)


                    contributor_address = PoliticalDonationContributorAddress()
                    contributor_address.address_type = address_dict['address_type']

                    street = ''

                    street_build_list = ['StreetNamePreDirectional', 'StreetName', \
                        'StreetNamePostType', 'StreetNamePostDirectional']

                    for field in street_build_list:

                        if field in address_dict:
                            street = street+' '+address_dict[field]

                    street = street.strip()

                    number = ''

                    if 'AddressNumber' in address_dict:
                        number = address_dict['AddressNumber']

                    contributor_address.addr1 = addr1
                    contributor_address.number = number
                    contributor_address.street = street

                    contributor_address.city = row_dict['EntityCity']
                    contributor_address.state = row_dict['EntityState']
                    contributor_address.zipcode = row_dict['EntityZip']

                    session.add(contributor_address)        
                    session.commit()

                contributor_address_id = contributor_address.id


            is_person = 0
            is_business = 0

            name_prefix = ''
            name_first = ''
            name_middle = ''
            name_last = ''
            name_suffix = ''




            # Only split out name for individuals, 
            if not bad_name and 'name_type' in name_dict and name_dict['name_type'] in ['Person', 'Household']:

                is_person = 1

                if 'PrefixMarital' in name_dict: 
                    name_prefix = name_dict['PrefixMarital']
                elif 'PrefixOther' in name_dict:
                    name_prefix = name_dict['PrefixOther']

                if 'GivenName' in name_dict: 
                    name_first = name_dict['GivenName']
                elif 'FirstInitial' in name_dict:
                    name_first = name_dict['FirstInitial']

                if 'MiddleName' in name_dict: 
                    name_middle = name_dict['MiddleName']
                elif 'MiddleInitial' in name_dict:
                    name_middle = name_dict['MiddleInitial']

                if 'Surname' in name_dict: 
                    name_last = name_dict['Surname']
                elif 'LastInitial' in name_dict:
                    name_last = name_dict['LastInitial']

                if 'SuffixGenerational' in name_dict: 
                    name_suffix = name_dict['SuffixGenerational']
                elif 'SuffixOther' in name_dict:
                    name_suffix = name_dict['SuffixOther']



                # Check if contributor already exists from first,last,suffix,addr1,zipcode
                try:

                    contributor = session.query(PoliticalDonationContributor)\
                        .filter(PoliticalDonationContributor.address_id == contributor_address_id)\
                        .filter(PoliticalDonationContributor.name_first == name_first)\
                        .filter(PoliticalDonationContributor.name_last == name_last)\
                        .filter(PoliticalDonationContributor.name_suffix == name_suffix)\
                        .one()

                except Exception as e:


                    contributor = PoliticalDonationContributor()
                    contributor.address_id = contributor_address_id
                    contributor.name_prefix = name_prefix
                    contributor.name_first = name_first
                    contributor.name_middle = name_middle
                    contributor.name_last = name_last
                    contributor.name_suffix = name_suffix
                    contributor.name_business = ''

                    contributor.is_person = is_person
                    contributor.is_business = is_business

                    session.add(contributor)        
                    session.commit()

                contributor_id = contributor.id

            # Don't store individual names
            elif not bad_name and 'name_type' in name_dict and  name_dict['name_type'] == 'Corporation':

                is_business = 1

                if 'CorporationName' in name_dict:
                    corporation = name_dict['CorporationName']

                    if 'ShortForm' in name_dict:
                        corporation += ' '+name_dict['ShortForm']

                    if 'CorporationNameOrganization' in name_dict:
                        corporation += ' '+name_dict['CorporationNameOrganization']

                    if 'CorporationCommitteeType' in name_dict:
                        corporation += ' '+name_dict['CorporationCommitteeType']                        


                else:
                    corporation = name_dict['ShortForm']

                    if 'CorporationNameBranchType' in name_dict:
                        corporation += ' '+name_dict['CorporationNameBranchType']

                    if 'CorporationNameBranchIdentifier' in name_dict:
                        corporation += ' '+name_dict['CorporationNameBranchIdentifier']                        


                # Check if contributor already exists from full_name,addr1,zipcode
                try:

                    contributor = session.query(PoliticalDonationContributor)\
                        .filter(PoliticalDonationContributor.address_id == contributor_address_id)\
                        .filter(PoliticalDonationContributor.name_business == corporation)\
                        .one()

                except Exception as e:

                    contributor = PoliticalDonationContributor()
                    contributor.address_id = contributor_address_id
                    contributor.name_business = corporation

                    contributor.is_person = is_person
                    contributor.is_business = is_business

                    session.add(contributor)        
                    session.commit()

                contributor_id = contributor.id


            else:

                contributor_id = 0



        # Store all donations, including multiple annonymous (under $100) and unknown (badly formed people, address)
        #if True:
        if row_dict['Amount']:

            try:

                donation = PoliticalDonation()
                donation.is_annonymous = is_annonymous
                donation.contributor_id = contributor_id
                donation.contributor_type_id = contributor_type_id
                donation.contribution_type_id = contribution_type_id
                donation.committee_id = committee_id
                donation.filing_period_id = filing_period_id
                donation.employer_name_id = employer_name_id
                donation.employer_occupation_id = employer_occupation_id

                donation.donation_date = donation_date_obj 
                donation.donation_amount = donation_amount
                donation.provided_name = row_dict['EntityName']
                donation.provided_address = row_dict['EntityAddressLine1']
                donation.is_fixed_asset = is_fixed_asset

                session.add(donation)        
                session.commit()

                total_contributed = total_contributed + float(donation_amount)

            except Exception as e:
                print("Error saving PoliticalDonation:", e)


    else:
        print("ERROR: ", line, row)


print 'total contributed:', total_contributed



