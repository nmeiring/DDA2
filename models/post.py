from google.appengine.ext import db

from jinja_utilities import *


class Post(db.Model):
    email = db.StringProperty(required = True)
    product = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)
        
    def as_dict(self):
        time_fmt = '%x'
        d = {'email': self.email,
             'product': self.product,
             'created': self.created.strftime(time_fmt),
             }
        return d