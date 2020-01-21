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

def id_predicate(first_letter):
    return lambda stop: stop['id'][0] == first_letter


def find_stop(predicate, stops):
    matching = list(filter(predicate, stops))
    if not matching:
        return None
    else:
        return matching[0]

# zawsze: planned time, mixed time i actual relative time
# a jak jest trackowany to dodatkowo się pojawia actual time


def stops(name):
    r = requests.get('https://mpk.jacekk.net/stops/', params={'query': name}).text
    data = json.loads(r)
    return [find_stop(id_predicate('t'), data),
            find_stop(id_predicate('b'), data)]


def passage_url(stop):
    is_bus = stop['id'][0] == 'b'
    if is_bus:
        url_tpe = 'bus'
    else:
        url_tpe = 'tram'
    stop_id = stop['id'][1:]
    return 'https://mpk.jacekk.net/proxy_{}.php/services/passageInfo/stopPassages/stop?stop={}&mode=departure'.format(url_tpe, stop_id)


def format_passage(passage):
    def fformat(t):
        if 'actualTime' in t:
            # has relative
            minutes = int(t['actualRelativeTime']) // 60
            return '{}m ({}) {} {}'.format(minutes, t['actualTime'], t['patternText'], t['direction'])
        else:
            return '{} {} {}'.format(t['plannedTime'], t['patternText'], t['direction'])
    trip_strs = [fformat(t) for t in passage]
    return ' | '.join(trip_strs)


def fetch_passage(stop):
    r = requests.get(passage_url(stop)).text
    data = json.loads(r)
    return data

def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def parse_query3(query):
    words = query.split(' ')
    numbers = list(filter(lambda x: is_int(x) and x[0] != '+' and x[0] != '-', words))
    offsets = list(filter(is_offset_word, words))

    if len(numbers) >= 2 or len(offsets) >= 2:
        stop, None, None

    if len(numbers) == 1:
        line = int(numbers[0])
    else:
        line = None

    if len(offsets) == 1:
        offset = int(offsets[0][1:])
    else:
        offset = None

    stop = ' '.join([word for word in words if word not in numbers and word not in offsets])
    return stop, line, offset


def parse_query2(query):
    words = query.split(' ')
    if len(words) > 1 and is_int(words[-1]):
        return str(words[-1]), ' '.join(words[0:-1])
    elif len(words) > 1 and is_int(words[0]):
        return str(words[0]), ' '.join(words[1:])
    else:
        return None, query


def parse_query(query):
    stop, line, offset = parse_query3(query)
    pass_pred = lambda _: True
    if offset:
        offset_pred = (lambda x: int(x['actualRelativeTime']) >= offset * 60)
    else:
        offset_pred = pass_pred

    if line:
        line_pred = lambda passage: passage['patternText'] == str(line)
    else:
        line_pred = pass_pred
    
    return stop, lambda passage: offset_pred(passage) and line_pred(passage)


def is_offset_word(s):
    return len(s) >= 2 and s[0] == '+' and is_int(s[1:])


def passages(query, stop_selector):
    if not query:
        return None, None
    stop_name, passage_filter = parse_query(query)
    stop = stop_selector(stops(stop_name))
    if not stop:
        return None, None
    return stop, list(filter(passage_filter, fetch_passage(stop)['actual']))


def tram_passages(query):
    return passages(query, lambda x: x[0])


def bus_passages(query):
    return passages(query, lambda x: x[1])


def bot_passage(passage_f):
    def f(bot, trigger):
        stop, passage = passage_f(trigger.group(2))
        if not stop or not passage:
            bot.say('No jakaś chujnia')
        else:
            bot.say(stop['name'] + ': ' + format_passage(passage))

    return f


@commands('bus')
def bus(bot, trigger):
    bot_passage(bus_passages)(bot, trigger)


@commands('tram')
def tram(bot, trigger):
    bot_passage(tram_passages)(bot, trigger)
