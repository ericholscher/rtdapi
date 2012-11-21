import json
import redis
import slumber
import string
import shlex
import re
from dateutil import parser
from datetime import datetime

PRODUCTION_DOMAIN = 'readthedocs.org'


host = "localhost"
r = redis.Redis(host=host)

def send(to, message):
    r.publish('out',
              json.dumps({
                  'version': 1,
                  'type': 'privmsg',
                  'data': {
                      'to': to,
                      'message': message,
                  }
              }))

def output():
    pubsub = r.pubsub()
    pubsub.subscribe('in')
    for msg in pubsub.listen():
        jsony = json.loads(msg['data'])
        if jsony['type'] == 'privmsg':
            data = jsony['data']
            print "Got %s in %s from %s" % (data['message'], data['channel'], data['sender'])
            for command, func in COMMANDS.items():
                if command in data['message']:
                    output = func(data)
                    if output:
                        if data['channel']:
                            print "Sending to channel"
                            send(data['channel'], output)
                        else:
                            print "Sending to sender"
                            send(data['sender'], output)



def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """

    now = datetime.utcnow()
    diff = now - dt
    
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default

##########
########## COMMANDS
##########

def Info(data):
    import inspect
    frame = inspect.currentframe()
    name = inspect.getframeinfo(frame)[2]
    func = globals()[name]
    #import ipdb; ipdb.set_trace()
    cmd = '!%s ' % string.lower(func.__name__)
    words = shlex.split(data['message'].encode('ascii'))
    #import ipdb; ipdb.set_trace()
    try:
        if len(words) > 2:
            project, command = words[1:]
        else:
            command = 'absolute_url'
            project = words[1]
        val = api.project(project).get()
        ret_val = "{%s}" % command
        ret_val = ret_val.format(**val)
        if ret_val.startswith('/'):
            ret_val = "http://%s%s" % (PRODUCTION_DOMAIN, ret_val)
        return ret_val
    except Exception, e:
        print "Error: %s" % e
        print "Moving on, yo."


def Status(data):
    cmd = '!%s ' % string.lower(Status.__name__)
    project = data['message'].replace(cmd, '')
    try:
        val = api.build(project).get(type='html', limit=1)
        #import ipdb; ipdb.set_trace()
        obj = val['objects'][0]
        status = "Passed" if obj['success'] else "Failed"
        date = parser.parse(obj['date'])
        ret_val = "%s: http://%s%s (%s)" % (PRODUCTION_DOMAIN, status, obj['absolute_url'], timesince(date))
        return ret_val
    except Exception, e:
        print "Status Error: %s" % e


def Search(data):
    cmd = '!%s ' % string.lower(Search.__name__)
    term = data['message'].replace(cmd, '')
    try:
        val = api.file.search.get(q=term)
        #import ipdb; ipdb.set_trace()
        name = val['objects'][0]['project']['name']
        url = val['objects'][0]['absolute_url']
        text = val['objects'][0]['text']
        text = re.sub('<[^<]+?>', '', text)
        text = text[50:]
        ret_val = "%s: http://%s%s " % (name, PRODUCTION_DOMAIN, url)
        return ret_val
    except Exception, e:
        print "Search failed: %s" % e

def Build(data):
    import inspect
    frame = inspect.currentframe()
    name = inspect.getframeinfo(frame)[2]
    func = globals()[name]
    #import ipdb; ipdb.set_trace()
    cmd = '!%s ' % string.lower(func.__name__)
    words = shlex.split(data['message'].encode('ascii'))
    try:
        if len(words) > 2:
            project, version = words[1:]
            print "Building %s at %s" % (project, version)
        else:
            version = 'latest'
            project = words[1]
        val = api.version('%s/%s' % (project, version)).build().get()
        ret_val = "Building" if val['building'] else "Failed"
        if ret_val.startswith('/'):
            ret_val = "http://%s%s" % (PRODUCTION_DOMAIN, ret_val)
        return ret_val
    except Exception, e:
        print "Error: %s" % e
        print "Moving on, yo."


loco = locals().copy()
shit_we_need = [loco[func] for func in loco if str(type(loco[func])) == "<type 'function'>" and loco[func].__name__[0].isupper()]

COMMANDS = {}

for shit in shit_we_need:
    COMMANDS[string.lower(shit.__name__)] = shit

api = slumber.API(base_url='http://%s/api/v1/' % PRODUCTION_DOMAIN)
output()

#val = api.project('pip').get()

#val = api.build.get(pk=49252)
#val = api.build.get(project__slug='read-the-docs')

#val = api.user.get(username='eric')
#val = api.file.search.get(q='awesome')

#val = api.version('pip').get()
#val = api.version('pip').get(slug='1.0.1')

#val = api.version('pip').highest.get()
#val = api.version('pip').highest('0.8').get()

