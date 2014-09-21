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
# Rev. 1.0.0

import urllib, urllib2, sys, hashlib
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import XbmcHelpers
common = XbmcHelpers

USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25'

class iProstoTv():
    def __init__(self):
        self.id = 'plugin.video.iprosto.tv'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')
        self.token = hashlib.sha1(self.addon.getSetting('token')).hexdigest()

        self.language = self.addon.getLocalizedString
        self.handle = int(sys.argv[1])
        self.url = 'http://www.iprosto.tv'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = None
        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None

        if mode == 'play':
            self.play(url)
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
        self.index(self.url)
        xbmcplugin.endOfDirectory(self.handle, True)

    def index(self, url):
        response = self.get(url)
        rows = common.parseDOM(response, "div")

        links = common.parseDOM(rows, "div", attrs={"class": "hide"})
        titles = common.parseDOM(rows, "div", attrs={"class": "name"})
        images = common.parseDOM(rows, "img", ret='src')

        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=play&url=%s' % links[i]
            item = xbmcgui.ListItem(title, thumbnailImage=images[i])
            item.setInfo(type='Video', infoLabels={'title': title, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def play(self, url):
        if self.token == '7c222fb2927d828af22f592134e8932480637c0d':
            url = '%s|User-Agent=%s' % (url, urllib.quote(USER_AGENT))
            item = xbmcgui.ListItem(path = url)
            xbmcplugin.setResolvedUrl(self.handle, True, item)

plugin = iProstoTv()
plugin.main()
