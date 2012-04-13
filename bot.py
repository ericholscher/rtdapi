import json
import redis
import slumber
import string

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
        data = json.loads(msg['data'])['data']
        print "Got %s in %s from %s" % (data['message'], data['channel'], data['sender'])
        for command, func in COMMANDS.items():
            if command in data['message']:
                send(data['channel'], func(data))
            else:
                print data['message']

def Info(data):
    cmd = '!info '
    project = data['message'].replace(cmd, '')
    val = api.project(project).get()
    #ret_val = " ".join(val.keys())
    ret_val = "{absolute_url}".format(**val)
    ret_val = "http://readthedocs.org%s" % ret_val
    return ret_val


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

