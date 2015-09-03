# imdb_scraper_for_kodi_tv
Very much a work in progress. 

Kodi scrapes this data automatically from thetvdb.com but occasionally it is stubborn or (as in my case) the title is foreign and not in thetvdb. This script was developed using Python2.7 and needs BeautifulSoup and lxml to function properly. mediainfo is also needed.

Another prerequisite is that the files reside in the following directory structure:

/Series title A/Season X/Series title SXXEXX<br>
/Series title A/Season X/Series title SXXEXY<br>
/Series title A/Season X/Series title SXXEXZ<br>
/Series title A/Season Y/Series title SXXEXX<br>
/Series title A/Season Y/Series title SXXEXY<br>
/Series title A/Season Y/Series title SXXEXZ<br>
/Series title A/Season Z/Series title SXXEXX<br>
/Series title A/Season Z/Series title SXXEXY<br>
/Series title A/Season Z/Series title SXXEXZ<br>

To do:<br>
Determin the number of seasons from the files not IMDB.<br>
Create XSL template for output data.<br>
