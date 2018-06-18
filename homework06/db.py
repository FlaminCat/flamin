from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapper import get_news


Base = declarative_base()
engine = create_engine("sqlite:///news.db")
session = sessionmaker(bind=engine)


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    n_pages = 14    # кол-во полных страниц для сбора
    news_list = get_news('https://news.ycombinator.com/', n_pages)
    n_news = n_pages * 30   # кол-во новостей
    for i in range(n_news):
        s = session()
        news = News(title=news_list[i].get('title', ''),
                    author=news_list[i].get('author', ''),
                    url=news_list[i].get('url', ''),
                    comments=news_list[i].get('comments', ''),
                    points=news_list[i].get('points', ''))
        s.add(news)
        s.commit()


