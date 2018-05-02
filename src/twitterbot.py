

import requests
from fake_useragent import UserAgent
import sys
import re
import time
import random
from bs4 import BeautifulSoup


class LoginDataError (Exception):
    pass


class TwitterBot ():
    urls = {
        "login0": "https://twitter.com/login",
        "login1": "https://twitter.com/sessions",
        "popular_medias_by_tag": "https://twitter.com/search",
        "most_recent_medias_by_tag": "https://twitter.com/search?f=tweets&vertical=default",
        "popular_users_by_tag": "https://twitter.com/i/search/typeahead.json?count=10&filters=false",
    }

    def __init__ (self):
        self.s = requests.Session()
        self.s.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Host": "twitter.com",
            "User-Agent": UserAgent().firefox, # NOT .ie .chrome
        })

    def login (self, username, password):
        self.s.headers.update({
            "Referer": "https://twiter.com",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        r = self.s.get(self.urls["login0"], timeout= 5)
        time.sleep(random.uniform(1, 2))
        authenticity_token = re.search(u'<input.*value="(.+)".*name="authenticity_token".*>', r.text).group(1)
        self.s.headers.update({
            "Referer": "https://twiter.com/login",
        })
        r = self.s.post(self.urls["login1"], params= {
                                                         "session[username_or_email]": username,
                                                         "session[password]": password, 
                                                         "authenticity_token": authenticity_token,
                                                     }, allow_redirects= False, timeout= 5)
        time.sleep(random.uniform(1, 2))
        if r.headers["location"] != "https://twitter.com/":
            raise LoginDataError ("Wrong username_or_email or password")

    def _htmlTweetToDict (self, html_tweet):
        html_tweet_content = html_tweet.find("div", attrs= {"class": "content"})
        html_tweet_actions = html_tweet_content.find("div", class_= "ProfileTweet-actionCountList u-hiddenVisually")
        return {
            "id": html_tweet.attrs["data-tweet-id"],
            "text": html_tweet_content.find("div", attrs= {"class": "js-tweet-text-container"}).get_text(),
            "timestamp": int(html_tweet_content.find("span", class_= "_timestamp js-short-timestamp js-relative-timestamp").attrs["data-time"]),
            "retweets_count": int(html_tweet_actions.find("span", class_= "ProfileTweet-action--retweet u-hiddenVisually").findChildren()[0]\
                                              .attrs["data-tweet-stat-count"]),
            "likes_count": int(html_tweet_actions.find("span", class_= "ProfileTweet-action--favorite u-hiddenVisually").findChildren()[0]\
                                              .attrs["data-tweet-stat-count"]),
            #"reweeted_by_viewer": False,
            #"liked_by_viewer": False,
            "owner": {
                "id": html_tweet.attrs["data-user-id"],
                "username": html_tweet.attrs["data-screen-name"],
                "name": html_tweet.attrs["data-name"],
                "follows_viewer": html_tweet.attrs["data-follows-you"],
                "followed_by_viewer": html_tweet.attrs["data-you-follow"],
                "blocked_by_viewer": html_tweet.attrs["data-you-block"],
                #"verified": False,
            },
        }

    def _getMediasByTag (self, url, tag):
        self.s.headers.update({
            "Referer": "https://twitter.com/search-home",
        })
        r = self.s.get(url, params= {
                                        "q": tag,
                                    }, allow_redirects= False, timeout= 5)
        soup = BeautifulSoup (r.text, "html.parser")
        tweets = soup.find(id= "stream-items-id").find_all("li", attrs= {"data-item-type": "tweet"})
        return [self._htmlTweetToDict(tweet.findChildren()[0]) for tweet in tweets]

    def getPopularMediasByTag (self, tag):
        return self._getMediasByTag(self.urls["popular_medias_by_tag"], tag)

    def getMostRecentMediasByTag (self, tag):
        return self._getMediasByTag(self.urls["most_recent_medias_by_tag"], tag)

    def getPopularUsersByTag (self, tag):
        r = self.s.get(self.urls["popular_users_by_tag"], params= {
                                                              "q": tag,
                                                          }, timeout= 5)
        return r.json()["users"]


if __name__ == "__main__":
    bot = TwitterBot ()
    #bot.login("username" ,"password")

