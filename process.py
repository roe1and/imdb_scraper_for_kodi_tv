#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import urllib2
import subprocess
import bs4 as BeautifulSoup
from lxml.html.soupparser import fromstring
import lxml.etree as etree
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory", help="input directory")
parser.add_option("-i", "--imid", dest="imid", help="imdb id")
(options, args) = parser.parse_args()

if options.directory is None or options.imid is None:
    print 'Please specify an input directory and imdb directory'
    exit(1)

tv_directory = options.directory
imdb_id = options.imid


class GetInfo(object):
    '''Process the file'''
    def __init__(self, fullfilename):
        self.fullfilename = fullfilename
        self.filename = self.fullfilename.split('/')[6]
        self.season = self.fullfilename.split('/')[5].split(' ')[1]
        self.match = re.search('[sS][0-9]{1,2}[eE]([0-9]{1,2})', self.filename)
        self.episode = int(self.match.group(1))
        self.escapedfullfilename = self.fullfilename.replace(' ', '\\ ')
        self.command = 'mediainfo %s' % (self.escapedfullfilename)
        self.mediainfo = subprocess.check_output([self.command], shell=True)
        self.filedetails = {}


    def print_details(self):
        '''Print details to screen'''
        print self.fullfilename
        #print self.filename
        #print self.episode
        #print self.season
        print self.mediainfo
        print self.escapedfullfilename

    def mediadetails(self):
        '''Parse file details'''
        media_details = self.mediainfo.split('\n\n')
        for section in media_details:
            section_head = section.split('\n')[0]
            section_details = {}
            for line in section.split('\n'):
                if ':' in line:
                    section_details[line.split(':')[0].strip()] = line.split(':')[1].strip()
            self.filedetails[section_head] = section_details
        return self.filedetails


class IMDBData(object):
    def __init__(self, imdb):
        self.imdb = imdb
        response = urllib2.urlopen('http://uk.imdb.com/title/%s/episodes?season=1' % self.imdb)
        html = response.read()
        self.soup = BeautifulSoup.BeautifulSoup(html, 'lxml')

    def _actors(self):
        actors = []
        actors_soup = self.soup.findAll('td', {'itemprop': 'actor'})
        for i in range(len(actors_soup)):
            actor_name = actors_soup[i].find('span', {'itemprop': 'name'})
            actor_name_string = str(actor_name)
            actor = fromstring(actor_name_string).find('.//span').text
            actor = actor.encode('utf-8')
            actors.append(actor)
        characters = []
        characters_soup = self.soup.findAll('td', {'class': 'character'})
        for i in range(len(characters_soup)):
            char = str(characters_soup[i])
            char = fromstring(char).find('.//div').text
            char = char.encode('utf-8')
            characters.append(char.strip())
        a_c = zip(actors, characters)
        return a_c

if __name__ == '__main__':

    for root, dirs, files in os.walk(tv_directory):
        for f in files:
            if f.endswith(('avi', 'mp4', 'm4v', 'mkv')):
                fname = os.path.join(root, f)
                fileinfo = GetInfo(fname)
                print fileinfo.mediadetails()['General']['Format']
                httpdata = IMDBData(imdb_id)
                print httpdata._actors()
