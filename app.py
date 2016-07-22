import feedparser
import os
from datetime import datetime
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_bootstrap import Bootstrap

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '\x01\x1c\xa1a\xe5D\x82\x89(\xfa\xed/\x97l\xbf\xee4\xbcF\x1b\xadZ1\xf7'  # os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)


class Feeds(db.Model):
    __tablename__ = 'feeds'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.UnicodeText(64))
    published = db.Column(db.DateTime(), default=datetime.utcnow)
    link = db.Column(db.String(64))
    authors = db.Column(db.String(64))
    media_thumbnail = db.Column(db.String(64))

# RSS_URLS = [
#     'http://feeds.feedburner.com/Mashable',
#     'http://feeds.feedburner.com/crunchgear']

RSS_URLS = ['http://feeds.feedburner.com/Mashable']


@app.route("/")
def main():
    articles = []
    for url in RSS_URLS:
        articles.extend(feedparser.parse(url).entries)  # sakupi live postove i posalji u template
    return render_template("home.html", articles=articles)


if __name__ == "__main__":
    manager.run()
