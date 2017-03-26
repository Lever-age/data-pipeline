#!/usr/bin/python
# coding: utf-8

import probablepeople



people_fields_to_strip_periods = ['FirstInitial', 'MiddleInitial', 'LastInitial', 'SuffixGenerational', 'SuffixOther', \
    'SecondFirstInitial', 'SecondMiddleInitial', 'SecondLastInitial', 'SecondSuffixGenerational', 'SecondSuffixOther', \
    'CorporationLegalType', 'SecondCorporationLegalType']



def clean_name(full_name):


    """
    This function takes an text address (street address, city, state, zip), tokenizes it with the usaddress library,
    and runs basic search and replace to help standardize the address

    """


    try:


        original_name = full_name.upper().replace('  ',', ')


        # Make edits to original_name before calling probablepeople



        probablepeople_name = probablepeople.tag(original_name)



        #print 'probable name:', probablepeople_name

        name_dict = dict(probablepeople_name[0])

        name_type = probablepeople_name[1]

        name_dict['name_type'] = name_type

        name_dict['original_name'] = original_name

        # Remove trailing '.' from any abbreviations
        for field in people_fields_to_strip_periods:
            if field in name_dict:
                name_dict[field] = name_dict[field].strip('.')


        #print 'probable name dict:', name_dict

        return name_dict


    except Exception as e:

        print 'probablepeople ERROR:'
        print e

        return e




