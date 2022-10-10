#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : gazellegames.py
# Version            : 1.2
# Author             : Ooggle (@Ooggle_)
# Date created       : 07 Oct 2022

# MIT License
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from urllib import request, parse
from json import loads

from novaprinter import prettyPrinter

# you need to generate a token in your settings -> API Keys section (select "User" and "Torrents" permissions for the engine to work)
# https://gazellegames.net/user.php?action=edit
api_token = ""

class gazellegames(object):
    url = "https://gazellegames.net"
    name = "gazellegames"
    token = api_token
    authkey = ""
    torrent_pass = ""
    supported_categories = {
        "all":      "0",
        "games":    "1",
        "software": "2",
        "books":    "3",
        "music":    "4"
    }

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat="all"):
        # retrieve the authkey + torrent_pass
        opener = request.build_opener()
        opener.addheaders = [("X-API-Key", self.token)]
        with opener.open("%s/api.php?request=quick_user" % self.url) as f:
            result_text = f.read().decode('utf-8')

        user_result = loads(result_text)["response"]
        self.authkey = user_result["authkey"]
        self.torrent_pass = user_result["passkey"]

        # perform the actual search
        payload = {"search_type": "torrents", "searchstr": parse.unquote(what)}
        if cat != "all":
            payload["filter_cat[%s]" % self.supported_categories[cat]] = 1

        data = parse.urlencode(payload)
        data = data.encode('ascii')

        opener = request.build_opener()
        opener.addheaders = [("X-API-Key", self.token)]
        with opener.open("%s/api.php?request=search" % self.url, data=data) as f:
            result_text = f.read().decode('utf-8')

        search_result = loads(result_text)["response"]
        for torrent_groups in search_result:
            for torrents in search_result[torrent_groups]["Torrents"]:
                t = search_result[torrent_groups]["Torrents"][torrents]

                additional_infos_string = ""
                additional_infos = ["Miscellaneous", "GameDOXType", "Format", "Language", "Region"]
                for i in range(len(additional_infos)):
                    if t[additional_infos[i]] != "":
                        if len(additional_infos_string) == 0:
                            additional_infos_string+= "("
                        else:
                            additional_infos_string+= " - "
                        additional_infos_string+= t[additional_infos[i]]
                if len(additional_infos_string) != 0:
                    additional_infos_string+= ")"
                    final_torrent_string = "%s --- %s" % (t["ReleaseTitle"], additional_infos_string)
                    final_torrent_string = final_torrent_string.replace("|", "")

                    line = {"link": "%s/torrents.php?action=download&id=%s&authkey=%s&torrent_pass=%s" % (self.url, t["ID"], self.authkey, self.torrent_pass),
                            "name": final_torrent_string,
                            "size": "%s B" % t["Size"],
                            "seeds": t["Seeders"],
                            "leech": t["Leechers"],
                            "engine_url": self.url,
                            "desc_link": "%s/torrents.php?id=%s&torrentid=%s" % (self.url, t["GroupID"], t["ID"])}
                    prettyPrinter(line)
