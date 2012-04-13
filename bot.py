import json
import redis
import slumber
import string
import shlex

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
                        send(data['channel'], output)

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
            ret_val = "http://readthedocs.org%s" % ret_val
        return ret_val
    except Exception, e:
        print "Error: %s" % e
        print "Moving on, yo."


def Status(data):
    cmd = '!%s ' % string.lower(Status.__name__)
    project = data['message'].replace(cmd, '')
    val = api.build(project).get(limit=1)
    #import ipdb; ipdb.set_trace()
    obj = val['objects'][0]
    status = "Passed" if obj['success'] else "Failed"
    ret_val = "%s: http://readthedocs.org%s (%s)" % (status, obj['absolute_url'], obj['date'])
    return ret_val

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
            ret_val = "http://readthedocs.org%s" % ret_val
        return ret_val
    except Exception, e:
        print "Error: %s" % e
        print "Moving on, yo."

loco = locals().copy()
shit_we_need = [loco[func] for func in loco if str(type(loco[func])) == "<type 'function'>" and loco[func].__name__[0].isupper()]

COMMANDS = {}

for shit in shit_we_need:
    COMMANDS[string.lower(shit.__name__)] = shit

api = slumber.API(base_url='http://readthedocs.org/api/v1/')
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

