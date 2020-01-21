import json
import sys

import requests

from sopel.module import rule, commands, priority, example, unblockable
from bs4 import BeautifulSoup
import urllib.parse


if sys.version_info.major >= 3:
    unicode = str

def setup(bot):
    pass


def shutdown(bot):
    pass

@commands('miejski-random')
def miejski(bot, trigger):
    url = 'https://www.miejski.pl/losuj'

    r = requests.get(url, allow_redirects=True)
    http = BeautifulSoup(r.text, 'html.parser')
    title = [x.get_text() for x in http.findAll("h1")]
    definition = [x.get_text() for x in http.findAll("div", {"class": "definition summary"})]
    example = [x.get_text() for x in http.findAll("div", {"class": "example"})]

    bot.say(title[0] + '---' + definition[0])


@commands('miejski')
def miejski2(bot, trigger):
    try:
        word = urllib.parse.quote_plus(trigger.group(2))
        url = 'https://www.miejski.pl/slowo-' + word
        r = requests.get(url, allow_redirects=True)
        http = BeautifulSoup(r.text, 'html.parser')
        title = [x.get_text() for x in http.findAll("h1")]
        definition = [x.get_text() for x in http.findAll("div", {"class": "definition summary"})]
        example = [x.get_text() for x in http.findAll("div", {"class": "example"})]
        s = title[0] + '---' + definition[0] + '---' + example[0]
        bot.say(s)
    except:
        bot.say(':(')
#    return s
#    bot.say(title[0] + '---' + definition[0])

