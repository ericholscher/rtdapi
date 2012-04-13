import slumber
import json
import requests

#val = api.project.get(slug='read-the-docs')
#val = api.project('pip').get()

#val = api.build.get(pk=49252)
#val = api.build.get(project__slug='read-the-docs')

#val = api.user.get(username='eric')
#val = api.file.search.get(q='awesome')

#val = api.version('pip').get()
#val = api.version('pip').get(slug='1.0.1')

#val = api.version('pip').highest.get()
#val = api.version('pip').highest('0.8').get()


class Pillow(object):

    cache = {}

    def dump_objs(self):
        for obj in self.val['objects']:
            print json.dumps(obj, indent=4)

    def dump(self, val):
        print json.dumps(val, indent=4)

    def _visit(self, item):
        cached = self.cache.get(item, None)
        if cached:
            return (cached, True)
        if item.startswith('/api'):
            print "Crawling %s" % item
            resp = requests.get('http://readthedocs.org%s' % item)
            content = json.loads(resp.content)
            self.cache[item] = content
            return (content, True)
        return (item, False)

    def _dispatch_dict(self, items):
        for key, obj in items.items():
            #Don't recurse forever.
            if key != "resource_uri":
                if isinstance(obj, unicode):
                    content, created = self._visit(obj)
                    items[key] = content
                    if created:
                        self.dispatch(items[key])
                else:
                    self.dispatch(items[key])

    def _dispatch_list(self, items):
        for key, obj in enumerate(items):
            if isinstance(obj, unicode):
                content, created = self._visit(obj)
                items[key] = content
                if created:
                    self.dispatch(items[key])
            else:
                self.dispatch(items[key])

    def dispatch(self, obj):
        if isinstance(obj, list):
            self._dispatch_list(obj)
        if isinstance(obj, dict):
            self._dispatch_dict(obj)

    def crawl(self, items=None):
        """
        Handle the top-level crawling of a response from tastypie.

        This will handle a single response, or a list of items.
        """
        if not items:
            items = self.val
        if isinstance(items, list):
            for item in items:
                self._dispatch_dict(item)
        else:
            self._dispatch_dict(items)



if __name__ == '__main__':
    pill = Pellow()
    api = slumber.API(base_url='http://readthedocs.org/api/v1/')
    #data = api.build.get(project__slug='slumber')['objects']
    data = api.build.get()['objects']
    pill.crawl(data)
    pill.dump(data)
