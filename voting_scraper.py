import requests
import itertools
from lxml import html
from time import sleep
import os

URL_PREFIX = "http://clerk.house.gov/evs/"
URL_MIDFIX = "/roll"
URL_POSTFIX = ".xml"


class VotingYear(object):
    def __init__(self, year):
        self.year = year
        self.voter_dict = {}
        self.bill_names = ['Name']
def groupN(lst, n):
    return list(itertools.izip(*[itertools.islice(lst, i, None, n)\
        for i in range(n)]))

def pageToTupleArray(page):
    page_list = page.xpath(".//body/*/*/*/*/text()")
    names_and_votes_list = [item for item in page_list if '\r' not in item]
    return groupN(names_and_votes_list, 2)

def get_votes(year):
    VY = VotingYear(year)
    bill_num = 3
    while True:
        request_url = URL_PREFIX + str(year) + URL_MIDFIX\
            + '{0:03d}'.format(bill_num) + URL_POSTFIX
        print "Requesting: ", request_url
        try:
            page = html.parse(request_url)
        except IOError:
            try:
                page = html.parse(request_url)
            except IOError:
                print 'Unable to download ', request_url
        if page.getroot().attrib != {}:
            print "FINISHED"
            break
        bill_name = (page.xpath("//body/*/*/*/text()")[5].replace(',', ' ')\
            + ':' + page.xpath("//body/*/*/*/text()")[6]\
            + ':' + page.xpath("//body/*/*/*/text()")[11]).replace(',', ' ')\
            .replace('\r', '').replace('\n', '')
        VY.bill_names.append(bill_name)
        names_and_votes = pageToTupleArray(page)
        for voter in names_and_votes:
            if voter[0] in VY.voter_dict:
                if voter[1] == 'Yea' or voter[1] == 'Aye':
                    VY.voter_dict[voter[0]].append(str(1))
                elif voter[1] == 'Nay' or voter[1] == 'No':
                    VY.voter_dict[voter[0]].append(str(0))
                else:
                    VY.voter_dict[voter[0]].append('ABS')
            else:
                VY.voter_dict[voter[0]] = [voter[0].replace(',', ' ')]
                for prior_votes in range(bill_num-3):
                    VY.voter_dict[voter[0]].append('NP')
                if voter[1] == 'Yea':
                    VY.voter_dict[voter[0]].append(str(1))
                elif voter[1] == 'Nay':
                    VY.voter_dict[voter[0]].append(str(0))
                else:
                    VY.voter_dict[voter[0]].append('ABS')
        names_and_votes_dict = dict(names_and_votes)
        for voter in VY.voter_dict:
            if voter not in names_and_votes_dict:
                VY.voter_dict[voter].append('NP')
        bill_num += 1
        sleep(1)
    return VY
def save_votes(VY):
    out_file = open(str(VY.year) + '.csv', 'w')
    for bill_name in VY.bill_names:
        out_file.write((bill_name.replace(',', ' ') + ',').encode('utf8'))
    out_file.seek(-1, os.SEEK_END)
    out_file.write('\n')
    for rep in VY.voter_dict:
        out_file.write((','.join(VY.voter_dict[rep])+'\n').encode('utf8'))
    out_file.close()
if __name__ == '__main__':
    year = raw_input('Enter the year: ')
    VY = get_votes(year)
    save_votes(VY)
