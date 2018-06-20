from bottle import (
    route, run, template, request, redirect
)

from scrapper import get_news
from db import News, session
from bayes import NaiveBayesClassifier
import string


@route("/news")
@route("/")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():
    s = session()
    label = request.GET.get('label', '')
    id = request.GET.get('id', '')
    s.query(News).filter(News.id == id).update({'label': label})
    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    s = session()
    last_news = get_news('https://news.ycombinator.com/', 3)
    db_news = []
    news_pattern = {
        'author': '',
        'comments': '',
        'points': '',
        'title': '',
        'url': '',
    }
    db_size = s.query(News.id).count()
    for i in range(1, db_size+1):
        title = s.query(News).filter(News.id == i).first().title
        author = s.query(News).filter(News.id == i).first().author
        comments = s.query(News).filter(News.id == i).first().comments
        points = s.query(News).filter(News.id == i).first().points
        url = s.query(News).filter(News.id == i).first().url
        news_pattern['author'], news_pattern['comments'], news_pattern['points'], news_pattern['title'], news_pattern[
            'url'] = \
            author, comments, points, title, url
        db_news.append(news_pattern)
        news_pattern = {
            'author': '',
            'comments': '',
            'points': '',
            'title': '',
            'url': '',
        }
    for j in last_news:
        if s.query(News).filter(News.title == j.get('title', '')).first() is not None:
            if j.get('author', '') != s.query(News).filter(News.title == j.get('title', '')).first().author:
                pass
        else:
            news = News(title=j.get('title', ''),
                        author=j.get('author', ''),
                        url=j.get('url', ''),
                        comments=j.get('comments', ''),
                        points=j.get('points', ''))
            s.add(news)
            s.commit()
    redirect("/news")


@route("/classify")
def classify_news():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    classified_news = []
    titles = []
    for k in rows:
        titles.append(k.title)
    titles = [clean(x).lower() for x in titles]
    prediction = model.predict(titles)
    for j in range(len(prediction)):
        if prediction[j] == 'good':
            classified_news.append(rows[j])
        else:
            break
    return template('news_recommendations', rows=classified_news)


@route("/delete")
def delete():
    s = session()
    s.query(News).filter(News.id > 360).delete()
    s.commit()
    redirect("/news")


def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator).lower()


if __name__ == "__main__":
    s = session()
    rows = s.query(News).filter(News.label != None).all()
    X_train = [clean(row.title) for row in rows]
    y_train = [row.label for row in rows]
    model = NaiveBayesClassifier()
    model.fit(X_train, y_train)
    run(host="localhost", port=8080)
