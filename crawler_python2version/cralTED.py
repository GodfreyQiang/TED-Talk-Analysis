from bs4 import BeautifulSoup
from selenium import webdriver
import urllib
import codecs
import os,glob
import json
import re
import warnings
import requests
import time

## python cralTED.py
## You might specify video quality (default 320k)
## video would be saved in VIDEOPATH
## script would be saved in SCRIPTPATH (.json format, including metadata)
## Read line 125-127 to speicfy videos to download
## line 126 gives an example to specify videos by tag/length
## Be careful with line 63-64 as you may wish to remove it
VIDEOPATH = 'video'
SCRIPTPATH = 'script'
QUALITY = '320k'

## Extract the talk name given a path and store it in dict_
## path: 'https://www.ted.com/talks?page=%d'%(i)
def enlist_talk_names(path,dict_):
    r = urllib.urlopen(path).read()
    soup = BeautifulSoup(r, "html.parser")
    talks= soup.find_all("a",class_='')
    for i in talks:
        if i.attrs['href'].find('/talks/')==0 and dict_.get(i.attrs['href'])!=1:
            dict_[i.attrs['href']]=1

    return dict_

## From the url
## Download the video to VIDEOPATH
## Get the meta, scripts and save as JSON to SCRIPTPATH
def extract_talk(path,talk_name):

    ## Return if exists
    #if os.path.isfile(os.path.join(VIDEOPATH,talk_name+'.mp4')):
    #    print "Exsited! %s\n"%talk_name
    #    return

    #print path

    ## Wait until fully loaded
    driver.get(path)
    timeout = time.time() + 15
    while not BeautifulSoup(driver.page_source, "html.parser").find_all(class_="Grid--with-gutter"):
        if time.time()>timeout:
            warnings.warn("Fail to load%s"%talk_name)
            break
        continue
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    info = {}

    duration = soup.find("meta",  {"property":"og:video:duration"})
    info['duration'] = duration['content'] if duration else ''
    ## Keep only videos within 12 mins
    if duration and int(float(duration['content']))>=60*12:
        return

    description = soup.find("meta",  {"name":"description"})
    info['description'] = description['content'] if description else ''

    author = soup.find("meta",  {"name":"author"})
    info['author'] = author['content'] if author else ''

    title = soup.find("meta",  {"property":"og:title"})
    info['title'] = title['content'] if title else ''

    tag = []
    for i in soup.find_all("meta",{"property":"og:video:tag"}):
        tag.append(i['content'])
    info['tag'] = tag

    release_date = soup.find("meta",  {"property":"og:video:release_date"})
    info['release_date'] = release_date['content'] if release_date else ''

    script = [];
    for i in soup.find_all(class_="Grid--with-gutter"):
        script_secton = {}
        script_secton['time'] = i.find('button').find_all('div')[1].text
        script_secton['text'] = i.find_all(class_="Grid__cell")[1].text.replace("\n"," ")
        script_secton['semantic'] = ''
        script_secton['semantic_confidence'] = ''
        script.append(script_secton)

    info['script'] = script

    ## Find Video Urls
    #if not soup.find(class_='talks-main'):
    #    return
    #videourls = re.search(r'https://download\.ted\.com/talks/[a-zA-Z0-9_.-]*\-' + QUALITY + '\.mp4?', soup.find(class_='talks-main').find_all('script')[-1].text)

    #if not videourls:
    #    return

    #info['videourl'] = videourls.group(0)

    with open(os.path.join(SCRIPTPATH,talk_name+'.json'), 'w') as fp:
        json.dump(info, fp)

    #if videourls:
    #    print "Downloading file:%s"%talk_name
    #    r = requests.get(videourls.group(0), stream = True)

    #    with open(os.path.join(VIDEOPATH,talk_name+'.mp4'), 'wb') as f:
    #        for chunk in r.iter_content(chunk_size = 1024*1024):
    #            if chunk:
    #                f.write(chunk)

    #    print "Downloaded! %s\n"%talk_name
    #else:
    #    warnings.warn("Video not found:%s"%talk_name)

## Dynamic loading
driver = webdriver.Chrome('./chromedriver')

## Specify the page for crawling
all_talk_names = {}
for i in xrange(30,40):
    # path = 'https://www.ted.com/talks?duration=6-12&page=%d&sort=newest'%(i)
    path='https://www.ted.com/talks?page=%d'%(i)
    all_talk_names=enlist_talk_names(path,all_talk_names)

for i in all_talk_names:
    extract_talk('https://www.ted.com'+i+'/transcript',i[7:])

driver.quit()
