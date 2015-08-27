#!/usr/bin/python
# -*- coding: utf-8 -*-
import feedparser
import time
import re

TITLE_RE = r'(?P<type>\w*): ?(?P<name>.*) \((?P<state>\w\w)\)'
DESCRIPTION_RE = r'CONTACT: ?(?P<contact>.*) (?P<phone>\d?-?\d{3}-\d{3}-\d{4}).?'
ID_RE = r'caseNum=(?P<id>\d+)'
KID_FEED_URL = "http://www.missingkids.com/missingkids/servlet/XmlServlet?act=rss"
STATES = { # http://code.activestate.com/recipes/577305/
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}


class MissingKid(object):
    """
    Object that contains all data for a given missing kid.

    :pram data: a dictionary that comes from KidsFeed
    :type data: dict

    :var type: might change but currrently only Missing
    :var name: name of person missing
    :var state: US state in full
    :var time: time of report upload
    :var href: the URL of the kid on missingkids.com
    :var image: the URL of the kid's picture
    :var contact: who should be contacted
    :var phone: number which the contact can be reached
    """

    def __init__(self, data):
        self.data = data
        self.href = None
        self.parse()

    def parse(self):
        self.parse_title()
        self.parse_time()
        self.parse_links()
        self.parse_id()
        self.parse_description()

    def parse_title(self):
        """
        format for the title
        Missing: <NAME> (<STATE>)
        """
        self.raw_title = self.data['title']
        self.title = re.search(TITLE_RE, self.raw_title)

        self.type_raw = self.title.group('type')
        self.name_raw = self.title.group('name')
        self.state_raw = self.title.group('state')

        self.name = self.parse_name(self.name_raw)
        self.type = self.parse_type(self.type_raw)
        self.state = self.parse_state(self.state_raw)

    def parse_time(self):
        self.time_raw = self.data['published']
        self.time = time.strptime(self.time_raw[:-4], # remove timezone
                                  "%a, %d %b %Y %H:%M:%S")

    def parse_links(self):
        link = self.data['links']
        self.href = link[0]['href'] # webpage
        self.image = link[1]['href'] # image uri

    def parse_id(self):
        self.id_raw = re.search(ID_RE, self.href) # pull case num from url
        self.id = int(self.id_raw.group('id'))

    def parse_description(self):
        """
        The description is made up of the data that is throughout the xml.
        We choose to take the imformation from those tags and not use one
        large regular expression to pull out all that data. The data that
        does not come with a tag is the contact and the phone
        """

        self.raw_description = self.data['description']
        self.description = re.search(DESCRIPTION_RE, self.raw_description)
        self.contact = self.description.group('contact')
        self.phone = self.description.group('phone')

    @staticmethod
    def parse_state(state_raw):
        try:
            state = STATES[state_raw]
        except KeyError:
            state = state_raw
        return state

    @staticmethod
    def parse_name(name_raw):
        return name_raw.title()

    @staticmethod
    def parse_type(type_raw):
        return type_raw

    def __str__(self):
        return "{type}: {name} from {state}".format(type=self.type,
                                                    name=self.name,
                                                    state=self.state)


class KidsFeed(object):
    """
    Takes a url and makes a list of MissingKids

    :pram url: the url from missingkids.com
    :type url: str

    :var missing_kids:
    :vartype missing_kids: list of MissingKid
    """

    def __init__(self, url):
        self.url = url
        self.feed = feedparser.parse(self.url)
        self.kids_list = self.feed['items']
        self._missing_kids = []
        self._missing_kids_ids = []

    @property
    def missing_kids_ids(self):
        if not self._missing_kids_ids:
            self._missing_kids_ids = self.kids_ids()
        return self._missing_kids_ids

    @property
    def missing_kids(self):
        if not self._missing_kids:
            self._missing_kids = self.kids()
        return self._missing_kids

    def kids_ids(self):
        for kid_data in self.kids_list:
            href = kid_data['links'][0]['href']
            id_raw = re.search(ID_RE, href) # pull case num from url
            id = int(id_raw.group('id'))
            self._missing_kids_ids.append(id)
        return self._missing_kids_ids


    def kids(self):
        for kid_data in self.kids_list:
            missing_kid = MissingKid(kid_data)
            self._missing_kids.append(missing_kid)
        return self._missing_kids


if __name__ == "__main__":
    kid_feed = KidsFeed(KID_FEED_URL)
    for id in kid_feed.missing_kids_ids:
        print(id)
