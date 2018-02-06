from google.appengine.ext import ndb

class Message(ndb.Model):
    nombre = ndb.StringProperty()
    email = ndb.StringProperty()
    texto = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)

