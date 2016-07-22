import feedparser
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
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


RSS_URLS = ['http://feeds.feedburner.com/Mashable']

# RSS_URLS = [
#     'http://feeds.feedburner.com/Mashable',   # lista testiranja RSS URL-ova
#     'http://feeds.feedburner.com/crunchgear']


@manager.command
def insert():
    """Pokreni spremanje aktivnih feeds"""
    posts = []
    for url in RSS_URLS:
        posts.extend(feedparser.parse(url).entries)

    for feed in posts:
        exists = db.session.query(Feeds.id).filter_by(title=feed.title).scalar() is not None
        if not exists:
            clean_published = feed.published.replace(",", "")[:-6]
            db.session.add(Feeds(
                title=feed.title, published=datetime.strptime(clean_published, '%a %d %b %Y %H:%M:%S'), link=feed.link,
                authors=" ".join(feed.authors[0].values()), media_thumbnail=feed.media_thumbnail[0]["url"]))
            db.session.commit()


@app.route("/")
def main():
    articles = []
    for url in RSS_URLS:
        articles.extend(feedparser.parse(url).entries)  # sakupi live postove i posalji u template
    return render_template("home.html", articles=articles)


@app.route('/connect', defaults={'page': 1, 'id': 0, 'page1': 1})
@app.route("/connect/<int:page>/<int:id>/<int:page1>")
def connect(page, id, page1):
    pages = Feeds.query.order_by(Feeds.published.desc()).paginate(page, 20, False)      # paginacija database feeds
    feeds = db.session.query(Feeds).filter_by(id=id)                                    # povezivanje id feeds-a
    if feeds.all() == []:
        feeds = []
    articles = Feeds.query.order_by(Feeds.published.desc()).paginate(page1, 20, False)  # paginacija feeds linkova

    return render_template("connect.html", pages=pages, posts=feeds, pages1=articles)


@app.route('/autocomplete')
def autocomplete():
    search = request.args.get('q')
    query = db.session.query(Feeds.authors).filter(Feeds.authors.like('%' + str(search) + '%'))
    results = [mv[0] for mv in query.distinct()]
    return jsonify(matching_results=results)


@app.route('/auto', defaults={'id': 0})
@app.route('/auto/<int:id>')
def auto(id):
    author = request.args.get('author')
    articles = db.session.query(Feeds).order_by(Feeds.published.desc()).filter(Feeds.authors == author).all()
    # for i in articles:  # debuging
    #     print i.title
    return render_template("autocomplete.html", articles=articles)


if __name__ == "__main__":
    manager.run()
