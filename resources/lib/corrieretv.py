import urllib2
import time
from datetime import datetime
from email.utils import parsedate_tz
from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
import xbmc

class CorriereTV:
    __USERAGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0"

    def __init__(self):
        opener = urllib2.build_opener()
        # Use Firefox User-Agent
        opener.addheaders = [('User-Agent', self.__USERAGENT)]
        urllib2.install_opener(opener)

    def getChannels(self):
        pageUrl = "http://www.corriere.it/rss/"
        data = urllib2.urlopen(pageUrl).read()
        tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        links = tree.find("div", {"id": "rss"}).findAll("a")
        channels = []
        for link in links:
            channel = {}
            channel["title"] = link.text
            channel["url"] = link["href"]
            if channel["url"].find("http://static.video.corriereobjects.it/widget/content/playlist/xml/") == -1:
                continue
            channels.append(channel)
        
        return channels

    def getVideoByChannel(self, url):
        # RSS 2.0 only
        xmldata = urllib2.urlopen(url).read()
        dom = minidom.parseString(xmldata)

        videos = []
        for videoNode in dom.getElementsByTagName('item'):
            video = {}
            videoId = videoNode.getElementsByTagName('guid')[0].firstChild.data
            video["title"] = videoNode.getElementsByTagName('title')[0].firstChild.data.strip()
            # print video["title"].encode('utf-8')
            # print self.getVideoMetaDataURL(videoId)
            
            video["description"] = videoNode.getElementsByTagName('description')[0].firstChild.data
            t = parsedate_tz(videoNode.getElementsByTagName('pubDate')[0].firstChild.data)
            video["date"] = t[:9]

            metadata = self.getVideoMetaData(videoId)
            if metadata != {}:
                video.update(metadata)
                videos.append(video)
            
        return videos
        
    def getVideoMetaDataURL(self, videoId):
        url = "http://static2.video.corriereobjects.it/widget/content/video/rss/video_%s.rss" % videoId
        return url

    def getVideoMetaData(self, videoId):
        metadata = {}
        
        url = self.getVideoMetaDataURL(videoId)
        try:
            xmldata = urllib2.urlopen(url).read()
            dom = minidom.parseString(xmldata)

            metadata["url"] = dom.getElementsByTagName('media:content')[0].attributes["url"].value
            metadata["url"] = metadata["url"].replace("/z/", "/i/").replace("manifest.f4m","master.m3u8")
            thumbs = dom.getElementsByTagName('media:thumbnail')
            for thumb in thumbs:
                width = thumb.attributes["width"].value
                if width == "298" or width == "480":
                    metadata["thumb"] = thumb.attributes["url"].value
                    break
        except:
             xbmc.log("[CorriereTV] Error retrieving metadata: %s" % url, xbmc.LOGDEBUG) 
            
        return metadata
        