#!/usr/bin/env python
# -*- coding: utf-8 -*
# title           :instagram.py
# description     :python script for see anonymously stories from instagram.
# author          :bayusec
# date            :09/08/2019
# version         :0.4
# usage           :python instagram.py
# url             :https://github.com/bayusec/instagram_downloader
# python_version  :2.7
# ==============================================================================
import json
import requests
import time
from bs4 import BeautifulSoup
import pickle
import os


class Instagram:
    def __init__(self):
        self.url = "https://www.instagram.com"
        self.ulr_login = "https://www.instagram.com/accounts/login/ajax/"
        self.file_cookies = "igcookie.txt"
        self.url_token = "/static/bundles/metro/Consumer.js/1d807fe68382.js"
        self.regex_token = [";var R=50,", "h="]
        # self.username = ""
        # self.password = ""
        self.userslist = []
        self.preloadlink = ""
        self.hash_query = ""
        self.headers = {"Accept": "*/*",
                        "Accept-Language": "en-US,es-ES;q=0.7,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Host": "www.instagram.com",
                        "Origin": "https://www.instagram.com",
                        "Referer": "https://www.instagram.com/",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/60.0",
                        "X-Instagram-AJAX": "1",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-Requested-With": "XMLHttpRequest"}

        self.url = "https://www.instagram.com"
        self.url_login = "https://www.instagram.com/accounts/login/ajax/"
        self.sesion = requests.session()

    def checkcookies(self):
        if not os.path.isfile(self.file_cookies) or os.stat(self.file_cookies).st_size == 0:
            return False
        else:
            with open(self.file_cookies, 'rb') as f:
                self.sesion.cookies.update(pickle.load(f).cookies)
            return True

    def login(self, user, password):
        # Getting token
        freq = self.sesion.get(self.url)
        csrftoken = freq.cookies["csrftoken"]
        # using token in headers
        self.headers["x-csrftoken"] = csrftoken
        data = {"username": user,
                "password": password}
        time.sleep(1)
        # Login in instagram
        req = self.sesion.post(self.url_login, data=data, headers=self.headers)
        authjson = req.json()
        if not authjson["authenticated"]:
            return False
        # dump cookies to the cookie file
        with open(self.file_cookies, 'wb') as f:
            pickle.dump(self.sesion, f)
        return True

    def getpreloadlink(self):
        time.sleep(2)
        index = self.sesion.get(self.url)
        objpreload = BeautifulSoup(index.text, "lxml")
        htmlpreload = objpreload.find_all("link", {"rel": "preload"})
        for hp in htmlpreload:
            if hp["href"].startswith("/graphql/"):
                self.preloadlink = hp["href"]
                break

    def gethashfromjs(self):
        req_js = self.sesion.get(self.url + self.url_token)
        for i in req_js.text.split("function"):
            if self.regex_token[0] in i:
                for hsh in i.split(","):
                    if self.regex_token[1] in hsh:
                        self.hash_query = hsh.split('"')[1]

    def getuserslist(self):
        requsers = self.sesion.get(self.url + self.preloadlink)
        jsonusers = requsers.json()

        users = []
        objusers = jsonusers["data"]["user"]["feed_reels_tray"]["edge_reels_tray_to_reel"]["edges"]
        for objuser in objusers:
            # ARMANDO LISTA DE USUARIOS
            self.userslist.append(str(objuser["node"]["id"]))

    def getstories(self):
        self.getpreloadlink()
        self.gethashfromjs()
        self.getuserslist()
        output = []
        last = '{"reel_ids":["' + '","'.join(
            self.userslist) + '"],"highlight_reel_ids":[],"precomposed_overlay":false,"story_viewer_fetch_count":50}'
        url_stories = self.url + "/graphql/query/?query_hash=" + self.hash_query + "&variables=" + last

        req_stories = self.sesion.get(url_stories)
        json_stories = req_stories.json()
        for user_storie in json_stories["data"]["reels_media"]:
            part_storie = []
            part_user = {}
            part_user['username'] = str(user_storie["owner"]["username"])
            # showing stories
            for st in user_storie["items"]:
                part_link = {}
                if st["is_video"]:
                    part_link['is_video'] = 1
                    part_link['link'] = st["video_resources"][0]["src"]
                else:
                    part_link['is_video'] = 0
                    part_link['link'] = st["display_resources"][0]["src"]
                part_storie.append(part_link)
            part_user['stories'] = part_storie
            output.append(part_user)
        self.savecookies()
        return json.dumps(output)

    def savecookies(self):
        open(self.file_cookies, 'w').close()
        with open(self.file_cookies, 'wb') as f:
            pickle.dump(self.sesion, f)

    def quickstart(self, username, password):
        if not self.checkcookies():
            msg_login = self.login(username, password)
            if not msg_login:
                raise SystemExit("Error in User or Password.")
        # load session from cookie file
        else:
            with open(self.file_cookies, 'rb') as f:
                self.sesion.cookies.update(pickle.load(f).cookies)
        return self.getstories()


# ig = Instagram()
# print ig.quickstart("", "")
