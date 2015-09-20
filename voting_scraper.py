import requests
import itertools
from lxml import html
from time import sleep
import os
import argparse

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

def get_votes(year, absTo5):
    VY = VotingYear(year)
    bill_num = 3
    if absTo5:
        absValue = str(.5)
    else:
        absValue = 'ABS'
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
                    VY.voter_dict[voter[0]].append(absValue)
            else:
                VY.voter_dict[voter[0]] = [voter[0].replace(',', ' ')]
                for prior_votes in range(bill_num-3):
                    VY.voter_dict[voter[0]].append('NP')
                if voter[1] == 'Yea':
                    VY.voter_dict[voter[0]].append(str(1))
                elif voter[1] == 'Nay':
                    VY.voter_dict[voter[0]].append(str(0))
                else:
                    VY.voter_dict[voter[0]].append(absValue)
        names_and_votes_dict = dict(names_and_votes)
        for voter in VY.voter_dict:
            if voter not in names_and_votes_dict:
                VY.voter_dict[voter].append('NP')
        bill_num += 1
        sleep(1)
    return VY
def save_votes(VY, ignore_NP):
    out_file = open(str(VY.year) + '.csv', 'w')
    for bill_name in VY.bill_names:
        out_file.write((bill_name.replace(',', ' ') + ',').encode('utf8'))
    out_file.seek(-1, os.SEEK_END)
    out_file.write('\n')
    if ignore_NP:
        for rep in VY.voter_dict:
            if 'NP' not in VY.voter_dict[rep]:
                out_file.write((','.join(VY.voter_dict[rep])+'\n').encode('utf8'))
    else:
        for rep in VY.voter_dict:
            out_file.write((','.join(VY.voter_dict[rep])+'\n').encode('utf8'))
    out_file.close()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('year',\
        help='The year whose voting data is to be downloaded')
    parser.add_argument('--ignore_NP', action='store_true',\
        help='Do not save any rows which have the value \'NP\'')
    parser.add_argument('--absTo5', action='store_true',\
        help='Store ABS value as .5')
    args = parser.parse_args()
    ignore_NP =  args.ignore_NP
    year = args.year
    VY = get_votes(year, args.absTo5)
    save_votes(VY, ignore_NP)
