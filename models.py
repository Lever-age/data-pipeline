# coding: utf-8
import re

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Index, Integer
from sqlalchemy import Numeric, SmallInteger, String, Table, Text, Boolean
from sqlalchemy import desc, distinct, text, func

from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql://finance_user:finance_pass@localhost/pa_philly_campaign_finance?charset=utf8&use_unicode=0')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
metadata = Base.metadata


class RawDonation(Base):
    __tablename__ = 'raw_donations'

    id = Column(Integer, primary_key=True)
    FilerName = Column(String(128), nullable=False)
    Year = Column(String(32), nullable=False)
    Cycle = Column(String(32), nullable=False)
    DocType = Column(String(64), nullable=False)
    EntityName = Column(String(128), nullable=False)
    EntityAddressLine1 = Column(String(64), nullable=False)
    EntityAddressLine2 = Column(String(64), nullable=False)
    EntityCity = Column(String(64), nullable=False)
    EntityState = Column(String(32), nullable=False)
    EntityZip = Column(String(32), nullable=False)
    Occupation = Column(String(64), nullable=False)
    EmployerName = Column(String(128), nullable=False)
    EmployerAddressLine1 = Column(String(64), nullable=False)
    EmployerAddressLine2 = Column(String(64), nullable=False)
    EmployerCity = Column(String(64), nullable=False)
    EmployerState = Column(String(32), nullable=False)
    EmployerZip = Column(String(32), nullable=False)
    Date = Column(String(32), nullable=False)
    Amount = Column(String(32), nullable=False)
    Description = Column(String(255), nullable=False)
    Amended = Column(String(64), nullable=False)
    SubDate = Column(String(32), nullable=False)
    FiledBy = Column(String(128), nullable=False)






class PoliticalDonationCommittee(Base):
    __tablename__ = 'political_donation_committee'

    id = Column(Integer, primary_key=True)

    candidate_id = Column(Integer, server_default='0')

    #candidate_id = Column(Integer, ForeignKey(Candidate.id), nullable=False, index=True)
    #candidate = relationship(Candidate, backref=backref('donation_committees', order_by=id))

    is_candidates = Column(Boolean())

    committee_name = Column(String(64), nullable=False)
    committee_slug = Column(String(32), nullable=False, server_default='')    
    committee_description = Column(Text, server_default='')

    donations_2015 = Column(Numeric(10, 2), nullable=False)
    donations_2016 = Column(Numeric(10, 2), nullable=False)    

    def __repr__(self):
        return "<PoliticalDonationCommittee(committee_name='%s')>" % (self.committee_name)

    #@hybrid_property
    def number_of_donations(self):
        return len(self.donations)


    #@hybrid_property
    def number_of_donators(self):
        contributor_id_list = [d.contributor_id for d in self.donations]
        contributor_id_set = set(contributor_id_list)
        return len(contributor_id_set)


    #@hybrid_property
    def donation_total(self):
        return sum([d.donation_amount for d in self.donations])


    def format_donations_2015(self):
        return "{:,}".format(self.donations_2015)

    def format_donations_2016(self):
        return "{:,}".format(self.donations_2016)


    def donation_column_total(self):
        return self.donations_2015 + self.donations_2016


    def format_donation_column_total(self):
        return "{:,}".format(self.donation_column_total())


    def donations_by_state(self):

        return session.query(PoliticalDonationContributorAddress.state, 
                                func.count('*').label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationContributorAddress.contributors)\
            .join(PoliticalDonationContributor.donations)\
            .filter(PoliticalDonation.committee_id==self.id)\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .group_by(PoliticalDonationContributorAddress.state)\
            .order_by(desc('num_c'))\


    def non_individual_contributions(self, limit=100):

        return session.query(PoliticalDonationContributor, 
                                func.count('*').label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationContributor.donations)\
            .filter(PoliticalDonation.committee_id == self.id)\
            .filter(PoliticalDonation.contributor_type_id != app.config['CONTRIBUTOR_TYPE_INDIVIDUAL_ID'])\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .group_by(PoliticalDonationContributor.id)\
            .order_by(desc('total_donation'))\
            .limit(limit)



    def contributors_by_type(self, limit=100):

        return session.query(PoliticalDonationContributorType.type_name, 
                                func.count('*').label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationContributorType.donations)\
            .filter(PoliticalDonation.committee_id==self.id)\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .group_by(PoliticalDonationContributorType.id)\
            .order_by(desc('total_donation'))\
            .limit(limit)



    def contributions_by_type(self, limit=100):

        return session.query(PoliticalDonationContributionType.type_name, 
                                func.count('*').label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationContributionType.donations)\
            .filter(PoliticalDonation.committee_id==self.id)\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .group_by(PoliticalDonationContributionType.id)\
            .order_by(desc('total_donation'))\
            .limit(limit)



    def shared_donors_contribs_to_other_committees(self, limit=250):

        donation_2 = aliased(PoliticalDonation)

        #    .filter(PoliticalDonation.contributor_type_id != app.config['CONTRIBUTOR_TYPE_INDIVIDUAL_ID'])\
        #    .filter(donation_2.contributor_type_id != app.config['CONTRIBUTOR_TYPE_INDIVIDUAL_ID'])\

        return session.query(PoliticalDonationCommittee, 
                                func.count('*').label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationCommittee.donations)\
            .join(donation_2, PoliticalDonation.contributor_id==donation_2.contributor_id)\
            .filter(donation_2.contributor_id == PoliticalDonation.contributor_id)\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .filter(~donation_2.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .filter(PoliticalDonation.committee_id != self.id)\
            .filter(donation_2.committee_id == self.id)\
            .filter(PoliticalDonation.contributor_id > 0)\
            .group_by(PoliticalDonationCommittee.id)\
            .order_by(desc('num_c'))\
            .limit(limit)


"""

SELECT c.id, c.committee_name, c.candidate_id, COUNT(*) AS num_c, SUM(d.donation_amount) as total_donation
    FROM `de_political_donation_committee` c
        JOIN `de_political_donation` d ON c.id = d.committee_id
        JOIN `de_political_donation` d2 ON d.contributor_id = d2.contributor_id
    WHERE d.contributor_type_id != 1
        AND d2.contributor_type_id != 1
        AND c.id != 47
        AND d2.committee_id = 47
        AND d.contributor_id > 0
    GROUP BY c.id  
ORDER BY `num_c` ASC
"""


class PoliticalDonationContributionType(Base):
    __tablename__ = 'political_donation_contribution_type'

    id = Column(Integer, primary_key=True)
    type_name = Column(String(128), nullable=False)
    type_slug = Column(String(32), nullable=False, server_default='')    
    type_description = Column(Text, server_default='')

    def __repr__(self):
        return "<PoliticalDonationContributionType(type_name='%s')>" % (self.type_name)




t_political_donation_contributor_address_cicero_district_set = Table(
    'political_donation_contributor_address_cicero_district_set', metadata,
    Column('address_id', Integer, ForeignKey('political_donation_contributor_address.id'), nullable=False, index=True),
    Column('cicero_district_id', Integer, ForeignKey('cicero_district.id'), nullable=False, index=True)
)




class CiceroDistrict(Base):
    __tablename__ = 'cicero_district'

    id = Column(Integer, primary_key=True)

    cicero_id = Column(Integer)
    sk = Column(Integer)

    district_type = Column(String(64), server_default=text(""), nullable=False)
    valid_from = Column(String(32), server_default=text(""), nullable=False)
    valid_to = Column(String(32), server_default=text(""), nullable=False)
    country = Column(String(64), server_default=text(""), nullable=False)
    state = Column(String(64), server_default=text(""), nullable=False)
    city = Column(String(64), server_default=text(""), nullable=False)
    subtype = Column(String(64), server_default=text(""), nullable=False)
    district_id = Column(String(64), server_default=text(""), nullable=False)
    #num_officials = Column(Integer, server_default=text("0"), nullable=False)
    label = Column(String(64), server_default=text(""), nullable=False)
    #ocd_id = Column(String(128), server_default=text(""), nullable=False)
    data = Column(Text, server_default=text(""), nullable=False)
    last_update_date = Column(String(32), server_default=text(""), nullable=False)





class PoliticalDonationContributorAddress(Base):
    __tablename__ = 'political_donation_contributor_address'
    #__table_args__ = (
    #    Index('city', 'city', 'state'),
    #    Index('is_person', 'is_person', 'is_business')
    #)

    id = Column(Integer, primary_key=True)

    address_type = Column(String(128), server_default=text(""), nullable=False)


    addr1 = Column(String(128), nullable=False, server_default='')
    addr2 = Column(String(128), nullable=False, server_default='')
    #addr3 = Column(String(128), nullable=False, server_default='')


    po_box = Column(String(16), server_default=text(""), nullable=False)


    city = Column(String(64), nullable=False)
    state = Column(String(32), nullable=False)

    #state_obj = 



    zipcode = Column(String(16), nullable=False, index=True)

    slug = Column(String(64), nullable=False, server_default='')    

    num_individual_contribs = Column(Integer, nullable=False, server_default='0')
    num_non_individual_contribs = Column(Integer, nullable=False, server_default='0')

    cicero_districts = relationship(CiceroDistrict, secondary=t_political_donation_contributor_address_cicero_district_set,
        backref=backref('addresses'))    

    def __repr__(self):
        return "<PoliticalDonationContributorAddress(addr1='%s')>" % (self.addr1)



class PoliticalDonationContributorAddressCiceroDetails(Base):
    __tablename__ = 'political_donation_contributor_address_cicero_details'

    id = Column(Integer, primary_key=True)

    address_id = Column(Integer, ForeignKey(PoliticalDonationContributorAddress.id), nullable=False, index=True)
    address = relationship(PoliticalDonationContributorAddress, backref=backref('cicero_detail', order_by=id))

    wkid = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)

    geo_x = Column(Numeric(12, 8), nullable=False)
    geo_y = Column(Numeric(12, 8), nullable=False)

    match_addr = Column(String(128), nullable=False, server_default='')
    #match_postal = Column(String(32), nullable=False, server_default='')
    #match_country = Column(String(32), nullable=False, server_default='')
    locator = Column(String(64), nullable=False, server_default='')
    #match_region = Column(String(32), nullable=False, server_default='')
    #match_subregion = Column(String(32), nullable=False, server_default='')
    #match_city = Column(String(64), nullable=False, server_default='')
    partial_match = Column(Boolean, nullable=False, server_default='')
    geoservice = Column(String(32), nullable=False, server_default='')


class PoliticalDonationContributorAddressCiceroRaw(Base):
    __tablename__ = 'political_donation_contributor_address_cicero_raw'

    id = Column(Integer, primary_key=True)

    #address_id = Column(Integer, ForeignKey(PoliticalDonationContributorAddress.id), nullable=False, index=True)
    #address = relationship(PoliticalDonationContributorAddress, backref=backref('cicero_raw', order_by=id))


    addr1 = Column(String(128), nullable=False, server_default='')

    zipcode5 = Column(String(16), nullable=False, index=True)

    district_ids = Column(String(128), nullable=False, server_default='')

    geo_x = Column(Numeric(12, 8), nullable=False)
    geo_y = Column(Numeric(12, 8), nullable=False)
    match_addr = Column(String(128), nullable=False, server_default='')

    raw_text = Column(Text, nullable=False, server_default='')

    def __repr__(self):
        return "<PoliticalDonationContributorAddressCiceroRaw(addr1='%s')>" % (self.addr1)







class PoliticalDonationContributor(Base):
    __tablename__ = 'political_donation_contributor'
    #__table_args__ = (
    #    Index('city', 'city', 'state'),
    #    Index('is_person', 'is_person', 'is_business')
    #)

    id = Column(Integer, primary_key=True)
    #full_name = Column(String(128), nullable=False, server_default='')
    #full_address = Column(String(255), nullable=False, server_default='')

    address_id = Column(Integer, ForeignKey(PoliticalDonationContributorAddress.id), nullable=False, index=True)
    address = relationship(PoliticalDonationContributorAddress, backref=backref('contributors', order_by=id))


    name_prefix = Column(String(64), nullable=False, server_default='')
    name_first = Column(String(64), nullable=False, server_default='')
    name_middle = Column(String(64), nullable=False, server_default='')
    name_last = Column(String(64), nullable=False, server_default='')
    name_suffix = Column(String(64), nullable=False, server_default='')

    name_business = Column(String(255), nullable=False, server_default='')

    slug = Column(String(64), nullable=False, server_default='')    

    is_person = Column(SmallInteger, nullable=False, server_default='0')
    is_business = Column(SmallInteger, nullable=False, server_default='0')

    num_contributions = Column(Integer, nullable=False, server_default='0')
    num_committees_contrib_to = Column(Integer, nullable=False, server_default='0')


    total_contributed_2015 = Column(Numeric(10, 2), nullable=False)
    total_contributed_2016 = Column(Numeric(10, 2), nullable=False)        

    def __repr__(self):
        return "<PoliticalDonationContributor(full_name='%s')>" % (self.full_name)


    def format_total_contributed_2015(self):
        return "{:,}".format(self.total_contributed_2015)

    def format_total_contributed_2016(self):
        return "{:,}".format(self.total_contributed_2016)


    def contribution_column_total(self):
        return self.total_contributed_2015 + self.total_contributed_2016


    def format_contribution_column_total(self):
        return "{:,}".format(self.contribution_column_total())


    def formatted_name(self):
        if self.name_business != '':
            return self.name_business
        else:
            return self.name_first+' '+self.name_last


    def committees_donated_to(self, limit=100):

        return session.query(PoliticalDonationCommittee,
                                func.count('*').label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationCommittee.donations)\
            .filter(PoliticalDonation.contributor_id == self.id)\
            .filter(PoliticalDonation.contributor_type_id != app.config['CONTRIBUTOR_TYPE_INDIVIDUAL_ID'])\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .group_by(PoliticalDonationCommittee.id)\
            .order_by(desc('total_donation'))\
            .limit(limit)


    def related_contributors(self):

        donation_2 = aliased(PoliticalDonation)

        contributor_2 = aliased(PoliticalDonationContributor)

        #    .filter(PoliticalDonation.contributor_type_id != app.config['CONTRIBUTOR_TYPE_INDIVIDUAL_ID'])\
        #    .filter(donation_2.contributor_type_id != app.config['CONTRIBUTOR_TYPE_INDIVIDUAL_ID'])\

        return session.query(PoliticalDonationContributor, 
                                func.count(distinct(PoliticalDonation.committee)).label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationContributor.donations)\
            .join(PoliticalDonation.committee)\
            .join(donation_2, PoliticalDonationCommittee.id==donation_2.committee_id)\
            .join(contributor_2, donation_2.contributor_id==contributor_2.id)\
            .filter(donation_2.contributor_id == self.id)\
            .filter(PoliticalDonation.contributor_id != self.id)\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .filter(~donation_2.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .filter(PoliticalDonation.contributor_type_id != app.config['CONTRIBUTOR_TYPE_INDIVIDUAL_ID'])\
            .filter(donation_2.contributor_type_id != app.config['CONTRIBUTOR_TYPE_INDIVIDUAL_ID'])\
            .filter(PoliticalDonation.contributor_id > 0)\
            .group_by(PoliticalDonationContributor.id)\
            .order_by(desc('num_c'))\


    def contributions_by_type(self, limit=100):

        return session.query(PoliticalDonationContributionType.type_name, 
                                func.count('*').label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationContributionType.donations)\
            .filter(PoliticalDonation.contributor_id==self.id)\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .group_by(PoliticalDonationContributionType.id)\
            .order_by(desc('total_donation'))\
            .limit(limit)


    def contributors_by_type(self, limit=100):

        return session.query(PoliticalDonationContributorType.type_name, 
                                func.count('*').label('num_c'), 
                                func.sum(PoliticalDonation.donation_amount).label('total_donation'))\
            .join(PoliticalDonationContributorType.donations)\
            .filter(PoliticalDonation.contributor_id==self.id)\
            .filter(~PoliticalDonation.contribution_type_id.in_(app.config['CONTRIBUTION_TYPE_IDS_TO_IGNORE']))\
            .group_by(PoliticalDonationContributorType.id)\
            .order_by(desc('total_donation'))\
            .limit(limit)







class PoliticalDonationContributorType(Base):
    __tablename__ = 'political_donation_contributor_type'

    id = Column(Integer, primary_key=True)
    type_name = Column(String(64), nullable=False)
    type_slug = Column(String(32), nullable=False, server_default='')    
    type_description = Column(Text, server_default='')

    def __repr__(self):
        return "<PoliticalDonationContributorType(type_name='%s')>" % (self.type_name)



class PoliticalDonationFilingPeriod(Base):
    __tablename__ = 'political_donation_filing_period'

    id = Column(Integer, primary_key=True)
    period_name = Column(String(64), nullable=False)
    period_slug = Column(String(32), nullable=False, server_default='')    
    period_description = Column(Text, server_default='')

    def __repr__(self):
        return "<PoliticalDonationFilingPeriod(period_name='%s')>" % (self.period_name)


class PoliticalDonationEmployerName(Base):
    __tablename__ = 'political_donation_employer_name'

    id = Column(Integer, primary_key=True)
    employer_name = Column(String(128), nullable=False)
    employer_slug = Column(String(32), nullable=False, server_default='')    
    employer_description = Column(Text, server_default='')

    def __repr__(self):
        return "<PoliticalDonationEmployerName(employer_name='%s')>" % (self.employer_name)


class PoliticalDonationEmployerOccupation(Base):
    __tablename__ = 'political_donation_employer_occupation'

    id = Column(Integer, primary_key=True)
    occupation_name = Column(String(64), nullable=False)
    occupation_slug = Column(String(32), nullable=False, server_default='')    
    occupation_description = Column(Text, server_default='')

    def __repr__(self):
        return "<PoliticalDonationEmployerOccupation(occupation_name='%s')>" % (self.occupation_name)



class PoliticalDonation(Base):
    __tablename__ = 'political_donation'

    id = Column(Integer, primary_key=True)

    is_annonymous = Column(SmallInteger, nullable=False, server_default='0')

    #contributor_id = Column(Integer, nullable=False)
    contributor_id = Column(Integer, ForeignKey(PoliticalDonationContributor.id), nullable=False, index=True)
    contributor = relationship(PoliticalDonationContributor, backref=backref('donations', order_by=id))

    #contributor_type_id = Column(Integer, nullable=False)
    contributor_type_id = Column(Integer, ForeignKey(PoliticalDonationContributorType.id), nullable=False, index=True)
    contributor_type = relationship(PoliticalDonationContributorType, backref=backref('donations', order_by=id))

    #contribution_type_id = Column(Integer, nullable=False)
    contribution_type_id = Column(Integer, ForeignKey(PoliticalDonationContributionType.id), nullable=False, index=True)
    contribution_type = relationship(PoliticalDonationContributionType, backref=backref('donations', order_by=id))

    #committee_id = Column(Integer, nullable=False)
    committee_id = Column(Integer, ForeignKey(PoliticalDonationCommittee.id), nullable=False, index=True)
    committee = relationship(PoliticalDonationCommittee, backref=backref('donations', order_by=id))

    #filing_period_id = Column(Integer, nullable=False)
    filing_period_id = Column(Integer, ForeignKey(PoliticalDonationFilingPeriod.id), nullable=False, index=True)
    filing_period = relationship(PoliticalDonationFilingPeriod, backref=backref('donations', order_by=id))

    employer_name_id = Column(Integer, ForeignKey(PoliticalDonationEmployerName.id), nullable=False, index=True)
    employer_name = relationship(PoliticalDonationEmployerName, backref=backref('donations', order_by=id))

    employer_occupation_id = Column(Integer, ForeignKey(PoliticalDonationEmployerOccupation.id), nullable=False, index=True)
    employer_occupation = relationship(PoliticalDonationEmployerOccupation, backref=backref('donations', order_by=id))

    # Not linking:
    # PoliticalDonationElectionOffice

    donation_date = Column(DateTime, nullable=False)
    donation_amount = Column(Numeric(10, 2), nullable=False)
    provided_name = Column(String(128), nullable=False)
    provided_address = Column(String(128), nullable=False)
    is_fixed_asset = Column(SmallInteger, nullable=False)

    def __repr__(self):
        return "<PoliticalDonation(contributor_id='%s')>" % (self.contributor_id)


    def format_donation_date(self):
        return str(self.donation_date.strftime('%b %-d, %Y'))












def return_donation_commitee_id_from_name(name):

    try:

        committee = session.query(PoliticalDonationCommittee)\
            .filter(PoliticalDonationCommittee.committee_name == name).one()

    except Exception as e:

        committee = PoliticalDonationCommittee()
        committee.committee_name = name
        committee.is_candidates = 0
        committee.candidate_id = 0
        committee.donations_2015 = 0
        committee.donations_2016 = 0

        session.add(committee)        
        session.commit()

    return committee.id


def return_contribution_type_id_from_name(name):

    try:

        contribution_type = session.query(PoliticalDonationContributionType)\
            .filter(PoliticalDonationContributionType.type_name == name).one()

    except Exception as e:

        contribution_type = PoliticalDonationContributionType()
        contribution_type.type_name = name

        session.add(contribution_type)        
        session.commit()

    return contribution_type.id


def return_contributor_type_id_from_name(name):

    try:

        contributor_type = session.query(PoliticalDonationContributorType)\
            .filter(PoliticalDonationContributorType.type_name == name).one()

    except Exception as e:

        contributor_type = PoliticalDonationContributorType()
        contributor_type.type_name = name

        session.add(contributor_type)        
        session.commit()

    return contributor_type.id


def return_filing_period_id_from_name(name):

    try:

        filing_period = session.query(PoliticalDonationFilingPeriod)\
            .filter(PoliticalDonationFilingPeriod.period_name == name).one()

    except Exception as e:

        filing_period = PoliticalDonationFilingPeriod()
        filing_period.period_name = name

        session.add(filing_period)        
        session.commit()

    return filing_period.id


def return_employer_name_id_from_name(name):

    try:

        employer_name = session.query(PoliticalDonationEmployerName)\
            .filter(PoliticalDonationEmployerName.employer_name == name).one()

    except Exception as e:

        employer_name = PoliticalDonationEmployerName()
        employer_name.employer_name = name

        session.add(employer_name)        
        session.commit()

    return employer_name.id


def return_employer_occupation_id_from_name(name):

    try:

        occupation = session.query(PoliticalDonationEmployerOccupation)\
            .filter(PoliticalDonationEmployerOccupation.occupation_name == name).one()

    except Exception as e:

        occupation = PoliticalDonationEmployerOccupation()
        occupation.occupation_name = name

        session.add(occupation)        
        session.commit()

    return occupation.id


"""
def return_office_id_from_name_and_district(name, district):

    try:

        office = session.query(PoliticalDonationElectionOffice)\
            .filter(PoliticalDonationElectionOffice.office_name == name)\
            .filter(PoliticalDonationElectionOffice.office_district == district).one()

    except Exception as e:

        office = PoliticalDonationElectionOffice()
        office.office_name = name
        office.office_district = district

        session.add(office)        
        session.commit()

    return office.id

"""





class DeElectionDBCache:

    census_last_names = {}    
    state_abbrs = {}

    donation_committees = {}
    contribution_types = {}
    contributor_types = {}
    election_offices  = {}
    employer_names  = {}
    employer_occupations  = {}

    def load_cache(self):


        """
        self.state_abbrs = {}
        state_abbrs = State.query
        for s in state_abbrs:
            index = s.abbreviation.upper()
            self.state_abbrs[index] = s.id
        """



        self.donation_committees = {}
        committees = session.query(PoliticalDonationCommittee)
        for c in committees:
            index = ''.join(re.findall('([a-z0-9])', c.committee_name.lower()))
            self.donation_committees[index] = c.id

        self.contribution_types = {}
        contribution_types = session.query(PoliticalDonationContributionType)
        for c in contribution_types:
            index = ''.join(re.findall('([a-z0-9])', c.type_name.lower()))
            self.contribution_types[index] = c.id


        self.contributor_types = {}
        contributor_types = session.query(PoliticalDonationContributorType)
        for c in contributor_types:
            index = ''.join(re.findall('([a-z0-9])', c.type_name.lower()))
            self.contributor_types[index] = c.id


        self.election_offices = {}
        election_offices = session.query(PoliticalDonationFilingPeriod)
        for c in election_offices:
            index = ''.join(re.findall('([a-z0-9])', c.period_name.lower()))
            self.election_offices[index] = c.id


        self.employer_names = {}
        employer_names = session.query(PoliticalDonationEmployerName)
        for c in employer_names:
            index = ''.join(re.findall('([a-z0-9])', c.employer_name.lower()))
            self.employer_names[index] = c.id


        self.employer_occupations = {}
        employer_occupations = session.query(PoliticalDonationEmployerOccupation)
        for c in employer_occupations:
            index = ''.join(re.findall('([a-z0-9])', c.occupation_name.lower()))
            self.employer_occupations[index] = c.id

        """
        self.offices = {}
        offices = session.query(PoliticalDonationElectionOffice)
        for c in offices:
            index = ''.join(re.findall('([a-z0-9])', c.office_name.lower()))
            if index not in self.offices:
                self.offices[index] = {}
            self.offices[index][c.office_district] = c.id
        """


    def return_census_last_name_id_from_name(self, name):
        index = name.upper()
        if index not in self.census_last_names:
            return 0
        return self.census_last_names[index]


    def return_state_id_from_name(self, name):
        index = name.upper()
        if index not in self.state_abbrs:
            return 0
        return self.state_abbrs[index]




    def return_donation_commitee_id_from_name(self, name):
        index = ''.join(re.findall('([a-z0-9])', name.lower()))
        if index not in self.donation_committees:
            self.donation_committees[index] = return_donation_commitee_id_from_name(name)
        return self.donation_committees[index]


    def return_contribution_type_id_from_name(self, name):
        index = ''.join(re.findall('([a-z0-9])', name.lower()))
        if index not in self.contribution_types:
            self.contribution_types[index] = return_contribution_type_id_from_name(name)
        return self.contribution_types[index]


    def return_contributor_type_id_from_name(self, name):
        index = ''.join(re.findall('([a-z0-9])', name.lower()))
        if index not in self.contributor_types:
            self.contributor_types[index] = return_contributor_type_id_from_name(name)
        return self.contributor_types[index]


    def return_filing_period_id_from_name(self, name):
        index = ''.join(re.findall('([a-z0-9])', name.lower()))
        if index not in self.election_offices:
            self.election_offices[index] = return_filing_period_id_from_name(name)
        return self.election_offices[index]


    def return_employer_name_id_from_name(self, name):
        index = ''.join(re.findall('([a-z0-9])', name.lower()))
        if index not in self.employer_names:
            self.employer_names[index] = return_employer_name_id_from_name(name)
        return self.employer_names[index]


    def return_employer_occupation_id_from_name(self, name):
        index = ''.join(re.findall('([a-z0-9])', name.lower()))
        if index not in self.employer_occupations:
            self.employer_occupations[index] = return_employer_occupation_id_from_name(name)
        return self.employer_occupations[index]


    def return_office_id_from_name_and_district(self, name, district):
        index = ''.join(re.findall('([a-z0-9])', name.lower()))
        if index not in self.offices:
            self.offices[index] = {}
            self.offices[index][district] = return_office_id_from_name_and_district(name, district)
        elif district not in self.offices[index]:
            self.offices[index][district] = return_office_id_from_name_and_district(name, district)
        return self.offices[index][district]


