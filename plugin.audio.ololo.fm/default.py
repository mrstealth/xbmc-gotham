#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 2.0.0
# -*- coding: utf-8 -*-

import os, sys, urllib, urllib2, re
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import json, XbmcHelpers
import Translit as translit

translit = translit.Translit()
common = XbmcHelpers


class Ololo():
    def __init__(self):
        self.id = 'plugin.audio.ololo.fm'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://ololo.fm'

        self.icover = os.path.join(self.path, 'resources/icons/cover.png')
        self.inext = os.path.join(self.path, 'resources/icons/next.png')

    def init(self):
        params = common.getParameters(sys.argv[2])
        mode = url  = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None

        if mode == 'play':
            self.play(url)
        if mode == 'playlist':
            self.getPlaylist(url)
        if mode == 'genres':
            self.listGenres()
        if mode == 'search':
            self.search()
        elif mode is None:
            self.main()


    def main(self):
        page = common.fetchPage({"link": self.url})
        content = common.parseDOM(page["content"], "div", attrs={"class": "content"})
        items = common.parseDOM(content, "li")

        try:
            for item in items:
                link = common.parseDOM(item, "a", ret="href")[-1]
                title = common.parseDOM(item, "a")[-1]
                image = common.parseDOM(item, "img", ret="src")[0]

                uri = sys.argv[0] + '?mode=%s&url=%s' % ('playlist', urllib.quote(self.url + link))
                item = xbmcgui.ListItem(title, iconImage=self.url+image)
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        except IndexError:
            pass

        xbmcplugin.endOfDirectory(self.handle, True)


    def getPlaylist(self, url):
        page = common.fetchPage({"link": url})
        content = common.parseDOM(page["content"], "div", attrs={"class": "content"})
        ids = common.parseDOM(content, "a", attrs={"class": "listen_href"}, ret="data-url")

        try:
            playlist = self.getVKPlaylist(ids)
            # print playlist

            # {
            #     u'artist': u'MIX 2013 ',
            #     u'url': u'url',
            #     u'title': u'(\u0421\u0431\u043e\u0440\u043d\u0438\u043a \u0445\u0438\u0442\u043e\u0432 2013)',
            #     u'genre': 2,
            #     u'duration': 4714,
            #     u'aid': 252489687,
            #     u'owner_id': 229829031
            # }


            for track in playlist['response']:
                # uri = sys.argv[0] + '?mode=%s&url=%s' % ('play', urllib.quote_plus(track['url']))
                uri = sys.argv[0] + '?mode=%s&url=%s' % ('play', urllib.quote_plus(track['url']))
                item = xbmcgui.ListItem("%s - %s" % (track['title'], track['artist']), iconImage=self.icover)
                item.setProperty('IsPlayable', 'true')
                item.setProperty('mimetype', 'audio/mpeg')

                item.setInfo(
                    type='music',
                    infoLabels={
                        'title': track['title'],
                        'artist': track['artist'],
                        'album': 'ololo.fm',
                        'genre': 'ololo.fm',
                        'duration': track['duration']
                    }
                )

                xbmcplugin.addDirectoryItem(self.handle, uri, item, False)


        except IndexError:
            self.showErrorMessage('Unable to get a MP3 playlist')
            return False
            # pass

        xbmcplugin.endOfDirectory(self.handle, True)


    def play(self, url):
        print "*** play URL %s" % url
        item = xbmcgui.ListItem(path=url, iconImage=self.icover, thumbnailImage=self.icover)
        # item.setProperty('mimetype', 'audio/mpeg')
        xbmcplugin.setResolvedUrl(self.handle, True, item)


    def getVKPlaylist(self, ids):
        import time

        timestamp = str(int(time.time()))

        # ids = ids[0:2]
        string = '","'.join(ids)
        query ='"%s"' % string

        url = 'http://ololo.fm/js.api.array.php?query=[%s]&_=%s' % (query, timestamp)
        request = urllib2.Request(url)
        request.add_header('Host', 'ololo.fm')
        response = urllib2.urlopen(request).read()

        vk_url = response.split('"')[1]
        request = urllib2.Request(vk_url)
        request.add_header('Host', 'api.vk.com')
        response = urllib2.urlopen(request).read()

        return self.to_hash(response)


    def to_hash(self, response):
        import json
        string = response.replace('audioArray(', '').replace(');', '')
        return json.loads(string)


    def showErrorMessage(self, msg):
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10*1000)))


    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')


plugin = Ololo()
plugin.init()
