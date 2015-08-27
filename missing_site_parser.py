import feedparser
import requests
import time
import json
import re

log.basicConfig(filename='missing_kids.log', level=log.INFO)
ID_RE = r'caseNum=(?P<id>\d+)'
MISSING_KIDS_XML_URL = "http://www.missingkids.com/missingkids/servlet/XmlServlet?act=rss"
MISSING_KIDS_JSON_URL = "http://www.missingkids.com/missingkids/servlet/JSONDataServlet" #NOQA
MISSING_KIDS_JSON_GET = {
    'action': 'childDetail',
    'orgPrefix': 'NCMC',
    'seqNum': 1,
    'caseLang': 'en_US',
    'searchLang': 'en_US',
    'LanguageId': 'en_US',
    'caseNum': None,
}


def get_missing_kids_ids(url_feed=MISSING_KIDS_XML_URL):
    id_list = []
    feed = feedparser.parse(url_feed)
    for data in feed['items']:
        href = data['links'][0]['href'] # webpage
        id_raw = re.search(ID_RE, href) # pull case num from url
        id = int(id_raw.group('id'))
        id_list.append(id)
    return id_list


class Kid(object):
    def __init__(self, id, url=MISSING_KIDS_JSON_URL, data=MISSING_KIDS_JSON_GET):
        self._request = self.get_request(id, url, data)
        self.id = id
        self.url = self._request.url
        self.raw_data = json.loads(self._request.text)
        self.success = self.parse_data()

    def __str__(self):
        if self.success:
            return "%s %s" % (self._data_clean['childBean']['firstName'],
                              self._data_clean['childBean']['lastName'],)
        else:
            return "Failed to get %i" % self.id

    def parse_data(self):
        self._data_clean = self.raw_data
        if 'error' == self.raw_data.get('status'):
            return False
        else:
            return True

    @staticmethod
    def get_request(id, url, data):
        data.update({'caseNum': id})
        return requests.get(url, params=data)


if __name__ == "__main__":
    id_list = get_missing_kids_ids()
    kid_list = []
    for id in id_list:
        kid = Kid(id)
        print(kid)
        kid_list.append(kid)
