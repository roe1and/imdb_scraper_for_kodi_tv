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

months = {'January': '01', 'February': '02', 'March': '03',
          'April': '04', 'May': '05', 'June': '06',
          'July': '07', 'August': '08', 'September': '09',
          'October': '10', 'November': '11', 'December': '12'}

tv_directory = options.directory
imdb_id = options.imid
episodes = {}
'''
for d in os.listdir(tv_directory):
    if d.startswith('Season'):
        season = d.replace('Season ', '').strip()
        response = urllib2.urlopen('http://uk.imdb.com/title/%s/episodes?season=%s' % (imdb_id, season))
        html = response.read()
        soup = BeautifulSoup.BeautifulSoup(html, 'lxml')
        list_items = soup.findAll('div', {'class': 'list_item'})
        for i in range(len(list_items)):
            ep_url = list_items[i].find('a', {'itemprop': 'url'})
            href = str(ep_url['href'])
            episode = href[30:]
            episode_id = href[7:16]
            season_episode = 'S%02dE%02d' % (int(season), int(episode))
            episodes[season_episode] = episode_id
'''
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
    def __init__(self, sn_ep):
        self.sn_ep = sn_ep
        # http://www.imdb.com/title/tt1539157/?ref_=ttep_ep1
        # response = urllib2.urlopen('http://uk.imdb.com/title/%s/' % episodes[self.sn_ep])
        response = urllib2.urlopen('http://uk.imdb.com/title/tt2207831/')
        html = response.read()
        self.soup = BeautifulSoup.BeautifulSoup(html, 'lxml')

    #<title>"Kooperasiestories" Intensies en bedoelings (TV episode) - IMDb</title>
    @property
    def title(self):
        title = self.soup.find('title').text
        title = str(title)
        title = title.encode('utf-8')
        title = title.split('"')
        title = title[2].split('(')
        title = title[0]
        title = title.strip()
        return title

    #<span class="rating">7.9<span class="ofTen">/10</span></span>
    @property
    def rating(self):
        rating = self.soup.find('span', {'class', 'rating'}).text
        rating = rating.split('/')[0]
        return rating
    
    # <h4 class="inline">Release Date:</h4> 17 September 2009 (USA)
    # , text = re.compile('your regex here'), attrs = 
    @property
    def director(self):
        director_block = self.soup.find('div', attrs = {'itemprop': 'director'})
        director = director_block.find('span', {'itemprop': 'name'}).text
        director = str(director)
        director = director.encode('utf-8')
        return director

    @property
    def studio(self):
        studio_block = self.soup.find('span', attrs = {'itemtype': 'http://schema.org/Organization'})
        #studio = studio_block.find('span', {'itemprop': 'name'}).text
        studio = str(studio_block)
        studio = studio.encode('utf-8')
        return studio

    @property
    def plot(self):
        plot = self.soup.find('div', attrs = {'class': 'inline', 'itemprop': 'description'})
        plot = plot.find('p')
        plot = str(plot.encode('utf-8')[4:].split('<em')[0].strip())
        #plot = plot
        return plot

    @property
    def writer(self):
        writer_block = self.soup.find('div', attrs = {'itemprop': 'creator'})
        writer = writer_block.find('span', {'itemprop': 'name'}).text
        writer = str(writer)
        writer = writer.encode('utf-8')
        return writer

    @property
    def airdate(self):
        #for sibling in self.soup.findAll('h4', {'class': 'inline'}):
        #    print sibling
        title = self.soup.find('h4', text = re.compile('Release Date:'), attrs = {'class': 'inline'})
        title_str = str(title.next_sibling)
        day = re.search('([0-9]{2}|[0-9]{1})', title_str)
        year = re.search('([0-9]{4})', title_str)
        for month in months:
            if month in title_str:
                int_month = months[month]
        new_year = '%s-%s-%02d' % (year.group(1), int_month, int(day.group(1)))
        new_year = new_year.encode('utf-8')
        return new_year

    def _actors(self):
        actors = []
        actors_soup = self.soup.findAll('td', {'itemprop': 'actor'})
        for i in range(len(actors_soup)):
            actor_name = actors_soup[i].find('span', {'itemprop': 'name'}).text
            actor_name_string = str(actor_name)
            actor = actor_name_string.encode('utf-8')
            actors.append(actor)
        characters = []
        characters_soup = self.soup.findAll('td', {'class': 'character'})
        for i in range(len(characters_soup)):
            char = characters_soup[i].find('a').text
            char_str = str(char)
            char = char_str.encode('utf-8')
            characters.append(char.strip())
        a_c = zip(actors, characters)
        return a_c


class XmlWriter(object):
    """docstring for XmlWriter"""
    def __init__(self):
        self.root = etree.Element("episodedetails")

    def write_xml(self, record, video):
        self.fileinfo = etree.SubElement(self.root, "fileinfo")
        self.streamdetails = etree.SubElement(self.fileinfo, "streamdetails")
        self.video = etree.SubElement(self.streamdetails, "video")
        self.width = etree.SubElement(self.video, "width")
        self.width.text = 'video.width'
        self.height = etree.SubElement(self.video, "height")
        self.height.text = 'video.height'
        self.aspect = etree.SubElement(self.video, "aspect")
        self.aspect.text = 'video.aspect'
        self.codec = etree.SubElement(self.video, "codec")
        self.codec.text = video.mediadetails()['Video']['Codec ID']
        self.format = etree.SubElement(self.video, "format")
        self.format.text = 'AVC'
        self.duration = etree.SubElement(self.video, "duration")
        self.duration.text = 'video.duration'
        self.bitrate = etree.SubElement(self.video, "bitrate")
        self.bitrate.text = 'video.vbitrate'
        self.container = etree.SubElement(self.video, "container")
        self.container.text = '.m4v'
        self.audio = etree.SubElement(self.streamdetails, "audio")
        self.codec = etree.SubElement(self.audio, "codec")
        self.codec.text = video.mediadetails()['Audio']['Format']
        self.channels = etree.SubElement(self.audio, "channels")
        self.channels.text = video.mediadetails()['Audio']['Channel(s)'].split(' ')[0]
        self.bitrate = etree.SubElement(self.audio, "bitrate")
        self.bitrate.text = '160'
        self.title = etree.SubElement(self.root, "title")
        self.title.text = record.title
        self.season_no = 'record.episode_ser_iss.split(' ')[1]'
        self.episode_no = 'record.episode_ser_iss.split(' ')[3]'
        self.season = etree.SubElement(self.root, "season")
        self.season.text = self.season_no[0]
        self.episode = etree.SubElement(self.root, "episode")
        self.episode.text = self.episode_no.strip()
        self.aired = etree.SubElement(self.root, "aired")
        self.aired.text = record.airdate
        self.plot = etree.SubElement(self.root, "plot")
        self.plot.text = 'plot'
        self.playcount = etree.SubElement(self.root, "playcount")
        self.playcount.text = '0'
        self.lastplayed = etree.SubElement(self.root, "lastplayed")
        self.playcount.text = ''
        self.director = etree.SubElement(self.root, "director")
        self.director.text = record.director
        self.studio = etree.SubElement(self.root, "studio")
        self.studio.text = 'SABC'
        #for actr in record._actors():
        #    self.actor = etree.SubElement(self.root, "actor")
        #    self.name = etree.SubElement(self.actor, "name")
        #    self.name.text = actr[0].decode('utf-8')
        #    self.role = etree.SubElement(self.actor, "role")
        #    self.role.text = actr[1].decode('utf-8')
        content = etree.tostring(self.root, pretty_print=True)
        print content

if __name__ == '__main__':

    for root, dirs, files in os.walk(tv_directory):
        for f in files:
            if f.endswith(('avi', 'mp4', 'm4v', 'mkv')):
                fname = os.path.join(root, f)
                sn_ep = re.search('(S[0-9]{2}E[0-9]{2})', f)
                try:
                    episode = sn_ep.group(1)
                except AttributeError:
                    print 'Error encountered. Please check that'
                    print 'your episodes are named correctly. Each episode'
                    print 'should contain a string that matches this: '
                    print 'S[0-9]E[0-9]'
                    exit(1)
                fileinfo = GetInfo(fname)
                #print fileinfo.mediadetails()['General']['Format']
                print fileinfo.mediadetails()['Video']['Codec ID']
                print episode
                httpdata = IMDBData(episode)
                print httpdata.studio
                output = XmlWriter()
                output.write_xml(httpdata, fileinfo)
                #print httpdata._actors()
                exit(1)
