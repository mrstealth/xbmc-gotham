#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 2.0.5
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import sys
import re
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import XbmcHelpers
common = XbmcHelpers


import Translit as translit
translit = translit.Translit(encoding='cp1251')


# UnifiedSearch module
try:
    sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
    from unified_search import UnifiedSearch
except:
    xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Warning", 'Please install UnifiedSearch add-on!', str(10 * 1000)))


class NowFilms():
    def __init__(self):
        self.id = 'plugin.video.mrstealth.nowfilms.ru'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString

        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://nowfilms.ru'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.debug = False

    def main(self):
        self.log("Addon: %s"  % self.id)
        self.log("Handle: %d" % self.handle)
        self.log("Params: %s" % self.params)

        params = common.getParameters(self.params)

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = params['page'] if 'page' in params else 1

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.playItem(url)
        if mode == 'search':
            self.search(keyword, unified)
        if mode == 'genres':
            self.listGenres(url)
        if mode == 'show':
            self.getFilmInfo(url)
        if mode == 'category':
            self.getCategoryItems(url, page)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00][%s][/COLOR]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        # uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://kinoprosmotr.net/serial/")
        # item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1001), thumbnailImage=self.icon)
        # xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        # uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://kinoprosmotr.net/mult/")
        # item = xbmcgui.ListItem("[COLOR=FF00FFF0]%s[/COLOR]" % self.language(1002), thumbnailImage=self.icon)
        # xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategoryItems(self.url, 1)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url, page):
        print "*** Get category items %s" % url
        page_url = "%s/page/%s/" % (url, str(int(page)))
        response = common.fetchPage({"link": page_url})
        items = 0

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"id": "container"})
            movies = common.parseDOM(content, "div", attrs={"class": "new_movie3"})
            links_cont = common.parseDOM(movies, "span", attrs={"class": "new_movie8"})
            infos_cont = common.parseDOM(movies, "span", attrs={"class": "new_movie14"})
          
            images_cont = common.parseDOM(movies, "span", attrs={"class": "new_movie4 oops"})
            if not images_cont:
                images_cont = common.parseDOM(movies, "span", attrs={"class": "new_movie4"})

            titles = common.parseDOM(movies, "span", attrs={"class": "new_movinfo1"})
            links = common.parseDOM(links_cont, "a", ret="href")
            images = common.parseDOM(images_cont, "img", ret="src")

            descs = common.parseDOM(infos_cont, "span", attrs={"class": "new_movinfo3"})
            pagenav = common.parseDOM(content, "div", attrs={"class": "navigation"})

            # print len(titles)
            # print len(images)
            # print len(links)
            # print len(descs)

            for i, title in enumerate(titles):
                items += 1
                title = self.strip(self.encode(title))
                image = self.url+images[i]

                genres_cont = common.parseDOM(movies[i], "span", attrs={"class": "new_movinfo2"})
                genres = common.parseDOM(genres_cont, "a")
                genre = self.encode(', '.join(genres))

                rating = float(common.parseDOM(movies[i], "span", attrs={"class": "new_movkin"})[0]) if common.parseDOM(movies[i], "span", attrs={"class": "new_movkin"}) else 0
                description = self.encode(descs[i])

                uri = sys.argv[0] + '?mode=show&url=%s' % (links[i])
                item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
                item.setInfo(type='Video', infoLabels={'title': title, 'genre': genre, 'plot': description, 'rating': rating})

                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        if pagenav and not items < 25:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(9000), thumbnailImage=self.inext, iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getFilmInfo(self, url):
        print "*** getFilmInfo for url %s " % url

        response = common.fetchPage({"link": url})
        container = common.parseDOM(response["content"], "div", attrs={"class": "full"})

        js_container = common.parseDOM(container, "div", attrs={"id": "dengger"})
        source = common.parseDOM(js_container, "script", attrs={"type": "text/javascript"})[0]

        title = common.parseDOM(container, "h1")[0] 
        image = common.parseDOM(container, "img", attrs={"id": "imgbigp"}, ret="src")[0] 

        infos_cont = common.parseDOM(container, "ul", attrs={"class": "reset"})[-1]
        quality_cont = common.parseDOM(container, "div", attrs={"class": "full6"})
        description = common.parseDOM(container, "div", attrs={"class": "full_r disable_select"})[0]  

        quality = common.parseDOM(quality_cont, "b")
        # duration = common.parseDOM(infos_cont, "li")[1].split(' ')[0]
        year = common.parseDOM(infos_cont, "li")[2]
        genres = common.parseDOM(infos_cont, "li")[-1]
        rating = common.parseDOM(container, "span", attrs={"class": "new_movkin"})


        # print xbmcgui.ICON_OVERLAY_WATCHED
        # print xbmcgui.ICON_OVERLAY_UNWATCHED
        # print xbmcgui.ICON_OVERLAY_HD

        movie = source.split('file":"')[-1].split('"};')[0] if 'file":"' in source else None
        playlist = source.split(',pl:"')[-1].split('"};')[0] if ',pl:"' in source else None
        playlist = playlist.split('",')[0] if playlist and '",' in playlist else playlist


        title = self.encode(title)
        quality = quality[0] if quality else ''
        image = self.url+image
        genres = self.encode(genres)
        description = common.stripTags(self.encode(description))
        rating = float(rating[0]) if rating else 0

        labels = {
            'title': title, 
            'genre': genres, 
            'plot': description, 
            'playCount': 0, 
            'year': year, 
            # 'duration': duration,
            'rating' : rating
        }

        if not playlist:
            links = movie.split(',') if ',' in movie else [movie]

            for i, link in enumerate(links):
                link_title = "[%dp - %s] %s" % (((i*240)+480), quality, title)
                uri = sys.argv[0] + '?mode=play&url=%s' % link
                item = xbmcgui.ListItem(link_title,  iconImage=image, thumbnailImage=image)

                item.setInfo(type='Video', infoLabels=labels)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

            xbmc.executebuiltin('Container.SetViewMode(52)')

        else:
            response = common.fetchPage({"link": playlist})
            response = eval(response["content"])

            if 'playlist' in response['playlist'][0]:
                print "This is a season multiple seasons"

                for season in response['playlist']:
                    episods = season['playlist']

                    for episode in episods:
                        etitle =  episode['comment'].replace('<br>', ' ')

                        uri = sys.argv[0] + '?mode=play&url=%s' % episode['file']
                        item = xbmcgui.ListItem(common.stripTags(etitle), iconImage=image, thumbnailImage=image)
 
                        item.setInfo(type='Video', infoLabels=labels)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)
            else:
                print "This is one season"
                for episode in response['playlist']:
                    try:
                        etitle = episode['comment']
                    except KeyError:
                        etitle = episode['commet']

                    url = episode['file']

                    uri = sys.argv[0] + '?mode=play&url=%s' % url
                    item = xbmcgui.ListItem(common.stripTags(etitle), iconImage=image, thumbnailImage=image)

                    item.setInfo(type='Video', infoLabels=labels)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

            xbmc.executebuiltin('Container.SetViewMode(51)')

        xbmcplugin.endOfDirectory(self.handle, True)


    def listGenres(self, url):
        print "list genres"
        response = common.fetchPage({"link": url})
        menu = common.parseDOM(response["content"], "ul", attrs={"class": "reset flymenu2"})
        genres = common.parseDOM(menu, "li")

        for i, genre in enumerate(genres[:-2]):
            title = common.parseDOM(genre, "a")[0]
            link = common.parseDOM(genre, "a", ret="href")[0]

            uri = sys.argv[0] + '?mode=category&url=%s' % self.url + link
            item = xbmcgui.ListItem(self.encode(title), iconImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def getPlaylist(self, url):
        print "getPlaylist"

    def playItem(self, url):
        print "*** play url %s" % url
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(4000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()
        return keyword

    def search(self, keyword, unified):
        self.showErrorMessage('Not yet implemented')

    def search(self, keyword, unified):
        keyword = translit.rus(keyword) if unified else self.getUserInput()
        unified_search_results = []

        if keyword:      
            url = 'http://nowfilms.ru/index.php?do=search'

            # Advanced search: titles only
            values = {
                "beforeafter":  "after",
                "catlist[]":    0,
                "do" :          "search",
                "full_search":  1,
                "replyless":    0,
                "replylimit":   0,
                "resorder":     "desc",
                "result_from":  1,
                "search_start": 1,
                "searchdate" :  0,
                "searchuser":   "",
                "showposts":    0,
                "sortby":       "date",
                "story" :       keyword,
                "subaction":    "search",
                "titleonly":    0
            }

            headers = {
                "Host" : "nowfilms.ru",
                "Referer" : 'http://nowfilms.ru/index.php?do=search',
                "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:35.0) Gecko/20100101 Firefox/35.0"
            }

            # Send request to server
            request = urllib2.Request(url, urllib.urlencode(values), headers)
            response = urllib2.urlopen(request)
            content = response.read()

            movies = common.parseDOM(content, "div", attrs={"class": "new_movie3"})
            titles = common.parseDOM(movies, "span", attrs={"class": "new_movinfo1"})
            link_container = common.parseDOM(movies, "span", attrs={"class": "new_movie8"}) 
            links = common.parseDOM(link_container, "a",  ret="href")

            image_container = common.parseDOM(movies, "span", attrs={"class": "new_movie4 oops"}) 
            images = common.parseDOM(image_container, "img",  ret="src")


            if unified:
                self.log("Perform unified search and return results")

                for i, title in enumerate(titles):
                    unified_search_results.append({'title':  self.encode(self.strip(title)), 'url': links[i], 'image': self.url + images[i], 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                for i, title in enumerate(titles):
                    uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
                    item = xbmcgui.ListItem(self.encode(self.strip(title)), thumbnailImage=self.url + images[i])
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                xbmc.executebuiltin('Container.SetViewMode(50)')
                xbmcplugin.endOfDirectory(self.handle, True)

        else:
            self.menu()



    # *** Add-on helpers
    def log(self, message):
        if self.debug:
            print "### %s: %s" % (self.id, message)

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)

    def showErrorMessage(self, msg):
        print msg
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    def strip(self, string):
        return common.stripTags(string)

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')


# class URLParser():
#     def parse(self, string):
#         links = re.findall(r'(?:http://|www.).*?["]', string)
#         return list(set(self.filter(links)))

#     def filter(self, links):
#         links = self.strip(links)
#         return [l for l in links if l.endswith('.mp4') or l.endswith('.mp4') or l.endswith('.txt')]

#     def strip(self, links):
#         return [l.replace('"', '') for l in links]

nowfilms = NowFilms()
nowfilms.main()
