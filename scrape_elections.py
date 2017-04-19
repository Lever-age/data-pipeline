#!/usr/bin/python

import os

from sqlalchemy import create_engine

import requests

from bs4 import BeautifulSoup

from re import escape as re_escape


current_dir = os.path.dirname(os.path.realpath(__file__))


file_location = current_dir+'/leverage.sqlite'


engine = create_engine('sqlite:///'+file_location)
conn = engine.connect()


#result = conn.execute("select * from campaign_info")
#assert result.keys() == ["a", "b"]

#conn.execute("insert into x (a, b) values (1, 1)")

#for row in result:
#    print row['campaign_id']


result = conn.execute("select max(campaign_id) from campaign_info")
next_campaign_id = result.first()[0]+1

#print next_campaign_id

result = conn.execute("select max(candidate_id) from candidate_info")
next_candidate_id = result.first()[0]+1


def get_candidate_id(conn, candidate_name):

    #candidate_name = re_escape(candidate_name)

    #candidate_name = candidate_name.replace("'", "\\'")

    result = conn.execute("select candidate_id from candidate_info where candidate_name = '"+candidate_name+"'")

    try:
        candidate_id = result.first()[0]
        print 'Found candidate:', candidate_name

    except Exception, e:

        print 'Adding candidate:', candidate_name

        result = conn.execute("select max(candidate_id) from candidate_info")
        candidate_id = result.first()[0]+1

        conn.execute("insert into candidate_info (candidate_id, candidate_name) values ("+str(candidate_id)+", '"+candidate_name+"')")

    return candidate_id



def get_campaign_id(conn, candidate_id, election_year, election_cycle, position, party):

    #candidate_name = re_escape(candidate_name)

    #candidate_name = candidate_name.replace("'", "\\'")

    result = conn.execute("SELECT candidate_id FROM campaign_info WHERE \
        election_year="+str(election_year)+" AND election_cycle='"+election_cycle+"' AND \
        candidate_id="+str(candidate_id)+" AND candidate_position='"+position+"' AND \
        candidate_party='"+party+"'")

    try:
        campaign_id = result.first()[0]
        print 'Found campaign for candidate_id:', candidate_id

    except Exception, e:

        print 'Adding campaign for candidate_id:', candidate_id

        result = conn.execute("select max(campaign_id) from campaign_info")
        campaign_id = result.first()[0]+1

        conn.execute("insert into campaign_info \
            (campaign_id, election_year, election_cycle, candidate_id, candidate_position, candidate_party) VALUES \
            ("+str(campaign_id)+", "+str(election_year)+", '"+election_cycle+"', "+str(candidate_id)+", '"+position+"', '"+party+"')")

    return campaign_id



"""
soup = BeautifulSoup(r.content) # r.text ?


    for tr in soup.find_all("tr", class_="dataRowShaded"):
        #print tr
        candidate = process_de_candidate_table_row(tr)
        add_cadidate_from_tr_if_not_exist(candidate, date_found, page_found)


    for tr in soup.find_all("tr", class_="dataRowLight"):
        candidate = process_de_candidate_table_row(tr)
        add_cadidate_from_tr_if_not_exist(candidate, date_found, page_found)

"""

"""
election_url = 'https://philadelphiavotes.com//en/voters/candidates-for-office'

r = requests.get(election_url, allow_redirects=False)


real_content_list = r.content.split('<div class="catItemIntroText">')

real_content = real_content_list[1]

real_content_list = real_content.split('Please note')

real_content = real_content_list[0]

print real_content
"""

real_content = """        <p>
    On May 16, 2017, Philadelphia voters will cast Primary Election ballots for the following offices:</p>

<hr />
<p>
    Note, ballot numbers are displayed below in brackets: [].</p>
<h3>
    Justice Of The Supreme Court-Dem</h3>
<h5>
    Statewide (Vote for 1)</h5>
<ul>
    <li>
        [1] Dwayne Woodruff (Democratic)</li>
</ul>
<h3>
    Justice Of The Supreme Court-Rep</h3>
<h5>
    Statewide (Vote for not more than 4)</h5>
<ul>
    <li>
        [101] Sallie Mundy (Republican)</li>
</ul>
<h3>
    Judge Of The Superior Court-Dem</h3>
<h5>
    Statewide (Vote for not more than 4)</h5>
<ul>
    <li>
        [2] Carolyn H Nichols (Democratic)</li>
    <li>
        [3] Geoff Moulton (Democratic)</li>
    <li>
        [4] Maria Mclaughlin (Democratic)</li>
    <li>
        [5] Debbie Kunselman (Democratic)</li>
    <li>
        [6] Bill Caye (Democratic)</li>
</ul>
<h3>
    Judge Of The Superior Court-Rep</h3>
<h5>
    Statewide (Vote for not more than 4)</h5>
<ul>
    <li>
        [102] Emil Giordano (Republican)</li>
    <li>
        [103] Craig Stedman (Republican)</li>
    <li>
        [104] Wade A Kagarise (Republican)</li>
    <li>
        [105] Mary Murray (Republican)</li>
    <li>
        [106] Paula A Patrick (Republican)</li>
</ul>
<h3>
    Judge Of The Commonwealth Court-Dem</h3>
<h5>
    Statewide (Vote for not more than 2)</h5>
<ul>
    <li>
        [7] Timothy Barry (Democratic)</li>
    <li>
        [8] Joe Cosgrove (Democratic)</li>
    <li>
        [9] Ellen Ceisler (Democratic)</li>
    <li>
        [10] Todd Eagen (Democratic)</li>
    <li>
        [11] Irene M Clark (Democratic)</li>
    <li>
        [12] Bryan Barbin (Democratic)</li>
</ul>
<h3>
    Judge Of The Commonwealth Court-Rep</h3>
<h5>
    Statewide (Vote for not more than 2)</h5>
<ul>
    <li>
        [107] Paul Lalley (Republican)</li>
    <li>
        [108] Christine Fizzano Cannon (Republican)</li>
</ul>
<h3>
    Judge Of The Court Of Common Pleas-Dem</h3>
<h5>
    1st Judicial District (Vote for not more than 10)</h5>
<ul>
    <li>
        [13] Stella Tsai (Democratic)</li>
    <li>
        [14] Vikki Kristiansson (Democratic)</li>
    <li>
        [15] Deborah Cianfrani (Democratic)</li>
    <li>
        [16] John Macoretta (Democratic)</li>
    <li>
        [17] Rania Major (Democratic)</li>
    <li>
        [18] Henry Mcgregor Sias (Democratic)</li>
    <li>
        [19] Lawrence J Bozzelli (Democratic)</li>
    <li>
        [20] Vincent Furlong (Democratic)</li>
    <li>
        [21] Brian Mclaughlin (Democratic)</li>
    <li>
        [22] Shanese Johnson (Democratic)</li>
    <li>
        [23] Mark B Cohen (Democratic)</li>
    <li>
        [24] Daniel R Sulman (Democratic)</li>
<!--    <li>
        [25] Matthew C Monroe (Democratic)</li>
--> <li>
        [26] Leon Goodman (Democratic)</li>
    <li>
        [27] Deborah Canty (Democratic)</li>
<!--    <li>
        [28] Dawn M Tancredi (Democratic)</li>
--> <li>
        [29] Wendi Barish (Democratic)</li>
    <li>
        [30] Leonard Deutchman (Democratic)</li>
    <li>
        [31] Zac Shaffer (Democratic)</li>
    <li>
        [32] Jennifer Schultz (Democratic)</li>
    <li>
        [33] Vincent Melchiorre (Democratic)</li>
    <li>
        [34] Betsy Wahl (Democratic)</li>
    <li>
        [35] Jon Marshall (Democratic)</li>
    <li>
        [36] David Conroy (Democratic)</li>
    <li>
        [37] Mark J Moore (Democratic)</li>
    <li>
        [38] Danyl S Patterson (Democratic)</li>
    <li>
        [39] Terri M Booker (Democratic)</li>
    <li>
        [40] Lucretia C Clemons (Democratic)</li>
    <li>
        [41] Christian Dicicco (Democratic)</li>
<!--    <li>
        [42] Crystal B Powell (Democratic)</li>
--> <li>
        [43] Bill Rice (Democratic)</li>
</ul>
<h3>
    Judge Of The Court Of Common Pleas-Rep</h3>
<h5>
    1st Judicial District (Vote for not more than 3)</h5>
<ul>
    <li>
        [109] Vincent Furlong (Republican)</li>
</ul>
<h3>
    Judge Of The Municipal Court-Dem</h3>
<h5>
    1st Judicial District (Vote for not more than 3)</h5>
<ul>
    <li>
        [44] Matt Wolf (Democratic)</li>
    <li>
        [45] Marissa Brumbach (Democratic)</li>
    <li>
        [46] George Twardy (Democratic)</li>
    <li>
        [47] Betsy Wahl (Democratic)</li>
    <li>
        [48] Jon Marshall (Democratic)</li>
    <li>
        [49] Sherman Toppin (Democratic)</li>
    <li>
        [50] Christian Dicicco (Democratic)</li>
    <li>
        [51] Bill Rice (Democratic)</li>
    <li>
        [52] Crystal B Powell (Democratic)</li>
</ul>
<h3>
    District Attorney-Dem</h3>
<h5>
    Citywide (Vote for 1)</h5>
<ul>
    <li>
        [53] Rich Negrin (Democratic)</li>
    <li>
        [54] Joe Khan (Democratic)</li>
    <li>
        [55] Michael W Untermeyer (Democratic)</li>
    <li>
        [56] Tariq Karim El-Shabazz (Democratic)</li>
    <li>
        [57] Lawrence S Krasner (Democratic)</li>
    <li>
        [58] Teresa Carr Deni (Democratic)</li>
    <li>
        [59] John ONeill (Democratic)</li>
</ul>
<h3>
    District Attorney-Rep</h3>
<h5>
    Citywide (Vote for 1)</h5>
<ul>
    <li>
        [110] Beth Grossman (Republican)</li>
</ul>
<h3>
    City Controller-Dem</h3>
<h5>
    Citywide (Vote for 1)</h5>
<ul>
    <li>
        [61] Rebecca Rhynhart (Democratic)</li>
    <li>
        [62] Alan L Butkovitz (Democratic)</li>
</ul>
<h3>
    City Controller-Rep</h3>
<h5>
    Division 01-02 (Vote for 1)</h5>
<ul>
    <li>
        [111] Michael Tomlinson (Republican)</li>
</ul>
<p>"""


#print real_content

h3_sections = real_content.split('<h3>')

# Get rid of initial entry
h3_sections.reverse()
h3_sections.pop()
h3_sections.reverse()

for h3_section in h3_sections:
    internal_split = h3_section.split('</h3>')

    #print internal_split
    #break

    race_split = internal_split[0].strip().split('-')

    race = race_split[0]

    print race

    soup = BeautifulSoup(internal_split[1]) # r.text ?

    for li in soup.find_all("li"):
        #print tr
        candidate = li.get_text().strip()

        #print candidate

        candidate_split = candidate.split(']')

        candidate = candidate_split[1].strip()

        candidate_split = candidate.split('(')

        candidate = candidate_split[0].strip()

        party = candidate_split[1].replace(')', '').strip()

        #print(candidate, party)

        candidate_id = get_candidate_id(conn, candidate)

        #print candidate_id

        campaign_id = get_campaign_id(conn, candidate_id, 2017, 'primary', race, party)






