import slumber

USERNAME = 'eric'
PASSWORD = 'test'

api = slumber.API(base_url='http://readthedocs.org/api/v1/', auth=(USERNAME, PASSWORD))

project = api.project.get(slug='read-the-docs')
user = api.user.get(username='coleifer')
project_objects = project['objects'][0]
user_objects = user['objects'][0]

data = {'users': project_objects['users'][:]}
data['users'].append(user_objects['resource_uri'])

print "Adding %s to %s" % (user_objects['username'], project_objects['slug'])
api.project(project_objects['id']).put(data)

project2 = api.project.get(slug='read-the-docs')
project2_objects = project2['objects'][0]
print "Before users: %s" % project_objects['users']
print "After users: %s" % project2_objects['users']
