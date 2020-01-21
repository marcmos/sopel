import json
import sys

import requests

from sopel.module import rule, commands, priority, example, unblockable

if sys.version_info.major >= 3:
    unicode = str

def setup(bot):
    pass


def shutdown(bot):
    pass

@commands('gachi')
def gachi(bot, trigger):
    r = requests.get('https://supinic.com/api/track/search', params={'name': trigger.group(2), 'includeTags': '6'}).text
    data = json.loads(r)
    #trips = data['actual'][0:3]
    #s = ["{} {} {}".format(t['plannedTime'], t['patternText'], t['direction']) for t in trips]
    #print(trigger.group(2))
    bot.say(data['data'][0]['name'] + ': ' + data['data'][0]['parsedLink'])
