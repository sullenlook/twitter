#!/usr/bin/python
# -*- coding: utf-8 -*-
# Post to Twitter
# Par Cédric Boverie (cedbv)

# This plugin requires a web server (like Apache) with SiriServer-WebAddons (a php script) installed.
# https://github.com/cedbv/SiriServer-WebAddons
# TODO: Use a db instead of twitter.conf
# TODO: documentation

import re
from plugin import *
import ConfigParser

try:
   import tweepy
except ImportError:
   raise NecessaryModuleNotFound("Tweepy library not found. Please install Tweepy library! e.g. sudo easy_install tweepy")

twitterConfigFile = APIKeyForAPI("webaddons_path")+"/twitter.conf"
webaddons_url = APIKeyForAPI("webaddons_url")

class Twitter(Plugin):

    res = {
        'twitter': {
            'de-DE': u".*(Twitter|tweet|twit)(.*)",
            'fr-FR': u".*(Twitter|tweeter|tweet|twit|tuiteur)(.*)",
        },
        'what_to_tweet': {
            'de-DE': u"Was willst Du twittern?",
            'fr-FR': u"Que voulez-vous tweeter ?",
        },
        'what_to_tweet_say': {
            'de-DE': u"Was willst Du tweeten?",
            'fr-FR': u"Que voulez-vous twiter ?",
        },
        'success': {
            'de-DE': u"Ich hab \"{0}\" getwittert.",
            'fr-FR': u"J'ai envoyé \"{0}\" sur Twitter.",
        },
        'success_say': {
            'de-DE': u"Ich hab \"{0}\" an Twitter gesendet.",
            'fr-FR': u"J'ai envoyé \"{0}\" sur Twitteur.",
        },
        'failure': {
            'de-DE': u"Etwas hat nicht wie erwartet funktionieren. Versuchen Sie es später erneut.",
            'fr-FR': u"Quelque chose s'est mal passé. Veuillez réessayer plus tard.",
        },
        'not_ready': {
            'de-DE': u"Dein Twitter-Account ist nicht konfiguriert. Verbinde mit den folgenden Button:",
            'fr-FR': u"Votre compte Twitter n'est pas configuré. Vous pouvez vous connecter avec ce bouton :",
        },
    }

    @register("fr-FR", res["twitter"]["fr-FR"])
    @register("de-DE", res["twitter"]["de-DE"])
    def tweet(self, speech, language, regex):

        if regex.group(2) != None:
            twitterMsg = regex.group(2).strip()
        else:
            twitterMsg = ""

        config = ConfigParser.RawConfigParser()
        config.read(twitterConfigFile)
        try:
            consumer_key = config.get("consumer","consumer_key")
            consumer_secret = config.get("consumer","consumer_secret")
            access_token = config.get(self.assistant.accountIdentifier,"access_token")
            access_token_secret = config.get(self.assistant.accountIdentifier,"access_token_secret")
        except:
            access_token = ""
            access_token_secret = ""

        if access_token != "" and access_token_secret != "":
            if twitterMsg == "":
                twitterMsg = self. ask(self.res["what_to_tweet"][language],self.res["what_to_tweet_say"][language])

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            try:
                api.update_status(twitterMsg)
                self.say(self.res["success"][language].format(twitterMsg),self.res["success_say"][language].format(twitterMsg))
            except:
                self.say(self.res["failure"][language])
        else:
            self.say(self.res["not_ready"][language])
            url = webaddons_url+"/twitter.php?id=" + self.assistant.accountIdentifier

            view = UIAddViews(self.refId)
            button = UIButton()
            button.text = u"Connectez-vous sur Twitter"
            link = UIOpenLink("")
            link.ref = url.replace("//","")
            button.commands = [link]
            view.views = [button]
            self.send_object(view)
            
        self.complete_request()
