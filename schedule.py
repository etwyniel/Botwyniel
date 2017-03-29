from ics import Calendar
from requests import get
from datetime import datetime

def get_calendar(_class="INFOS2INT1-2", week=0):
    return Calendar(get(
        f"http://ichronos.net/ics/{_class}/{week}.ics").text)

def next_event(c):
    now = datetime.now().isoformat()
    for event in c.events:
        if event.begin.isoformat() >= now:
            return event

def next_events(c, n=5):
    now = datetime.now().isoformat()
    events = []
    i = 0
    while i < len(c.events) and n > 0:
        if c.events[i].begin.datetime.isoformat() >= now:
            events.append(c.events[i])
            n -= 1
        i += 1
    return events

def next_day_events(c):
    first_event = None
    now = datetime.now().isoformat()
    events = []
    i = 0
    while i < len(c.events) and (first_event is None or
            first_event.begin.datetime.date() ==
            c.events[i].begin.datetime.date()):
        if c.events[i].begin.datetime.isoformat() >= now:
            if first_event is None:
                first_event = c.events[i]
            events.append(c.events[i])
        i += 1
    return events
