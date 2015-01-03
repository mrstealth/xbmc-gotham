#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *  Copyright (C) 2011 MrStealth
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
#
# Writer (c) 2014, MrStealth
# Rev. 2.0.0

import urllib, urllib2, sys, socket
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import XbmcHelpers

socket.setdefaulttimeout(30)
common = XbmcHelpers


class Tivix():
    def __init__(self):
        self.id = 'plugin.video.tivix.net'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://tivix.net'


    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = None
        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = params['page'] if 'page' in params else 1

        if mode == 'play':
            self.play(url)
        if mode == 'show':
            self.show(url)
        if mode == 'index':
            self.index(url, page)
        elif mode == None:
            self.menu()


    def get(self, url):
        request = urllib2.Request(url)
        request.add_header('Host', 'iprosto.tv')
        request.add_header('User-Agent', USER_AGENT)
        response = urllib2.urlopen(request)

        return response.read()


    def menu(self):
        self.genres()
        xbmcplugin.endOfDirectory(self.handle, True)


    def index(self, url, page):
        page_url = self.url if page == 0 else "%s/page/%s/" % (url, str(int(page)))

        response = common.fetchPage({"link": page_url})
        content = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
        pagenav = common.parseDOM(response["content"], "div", attrs={"class": "bot-navigation"}) 
        
        boxes = common.parseDOM(content, "div", attrs={"class": "all_tv"})
        links = common.parseDOM(boxes, "a", ret='href')
        titles = common.parseDOM(boxes, "b")
        images = common.parseDOM(boxes, "img", ret='src')
        items = 0

        for i, title in enumerate(titles):
            items += 1

            if links[i] == "http://tivix.net/263-predlozheniya-pozhelaniya-zamechaniya-po-saytu.html":
                continue

            image = self.url + images[i]

            uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
            item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
            # item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        if pagenav and not items < 56:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("index", url, str(int(page) + 1))
            item = xbmcgui.ListItem('Next page >>', iconImage=self.icon, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def show(self, link):
        streams = self.getStreamURL(link)

        print "**** STREAMS FOUND %d" % len(streams)

        for i, stream in enumerate(streams):
            uri = sys.argv[0] + '?mode=play&url=%s' % urllib.quote_plus(stream)
            item = xbmcgui.ListItem("Stream %d" % (i+1), iconImage=self.icon, thumbnailImage=self.icon)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def genres(self):
        response = common.fetchPage({"link": self.url})
        menu = common.parseDOM(response["content"], "div", attrs={"class": "menuuuuuu"})[0]
        titles = common.parseDOM(menu, "a")
        links = common.parseDOM(menu, "a", ret="href")

        for i, link in enumerate(links):
            uri = sys.argv[0] + '?mode=index&url=%s' % urllib.quote_plus(self.url+link)
            item = xbmcgui.ListItem(titles[i], iconImage=self.icon, thumbnailImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(50)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def getStreamURL(self, link):
        response = common.fetchPage({"link": link})
        players = common.parseDOM(response["content"], "object")
        streams = []

        print "**** NUMBER OF PLAYERS %d" % len(players)

        for player in players:
            streams.append(player.split('&file=')[-1].split('&st=')[0])

        return streams


    def play(self, stream):
        if 'm3u8' in stream:
            print "M3U8"
            url = stream
        else:
            print "RTMP"
            url = stream
            url += " swfUrl=http://tivix.net/templates/Default/style/uppod.swf"
            url += " pageURL=http://tivix.net"
            url += " swfVfy=true live=true"
        
        item = xbmcgui.ListItem(path = url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)


plugin = Tivix()
plugin.main()
