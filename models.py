from google.appengine.ext import search
from google.appengine.ext import db
import datetime

class TexRender(db.Model):
    pic = db.BlobProperty(required=True)

class Reference(search.SearchableModel):
    title = db.StringProperty(required=True)
    subtitle = db.StringProperty()
    authors = db.StringListProperty()
    url = db.LinkProperty()
    tags = db.StringListProperty()
    pic = db.ReferenceProperty(TexRender)    
    def __unicode__(self):
        if self.subtitle:
            return self.title + " -- " + self.subtitle
        return self.title
        
class DisplayCard(db.Model):
    question = db.TextProperty(required=True)
    answer = db.TextProperty()

class FlashCard(search.SearchableModel):
    question = db.TextProperty(required=True)
    answer = db.TextProperty(required=True)
    tags = db.StringProperty(required=True)
    importance = db.RatingProperty()
    url = db.LinkProperty()
    reference = db.ReferenceProperty(Reference)
    # hidden
    user = db.UserProperty()
    mtime = db.DateTimeProperty(auto_now_add=True)
    display = db.ReferenceProperty(DisplayCard)


class Note(search.SearchableModel):
    text = db.TextProperty(required=True)
    url = db.LinkProperty()
    tags = db.StringProperty(required=True)
    about = db.SelfReferenceProperty()
    reference = db.ReferenceProperty(Reference)
    #hidden
    user = db.UserProperty()
    mtime = db.DateTimeProperty(auto_now_add=True)
    display = db.ReferenceProperty(DisplayCard)
    def __unicode__(self):
        return self.text[:50] + "... " + self.mtime.isoformat()
    # children = db.ReferenceListProperty()
    # parent = db.ReferenceListProperty()
    
    
class UserStat(db.Model):
    pic = db.ReferenceProperty(TexRender)
    user = db.UserProperty()

# TODO: add user commenting capabilities