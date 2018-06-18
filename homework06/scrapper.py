import requests
from bs4 import BeautifulSoup


def extract_news(parser):
    """ Extract news from a given web page """
    news_list = []

    news_pattern = {
        'author': '',
        'comments': '',
        'points': '',
        'title': '',
        'url': '',
    }
    content = parser.table.findAll('table')[1]

    # rank = 1 #номер текущей новости на странице
    for i in range(30):
        if content.find(attrs={"class": "subtext"}).find(attrs={"class": "hnuser"}) is not None:
            author = content.find(attrs={"class": "subtext"}).find(attrs={"class": "hnuser"}).text
        else:
            author = 'Unknown'
        if len(content.find(attrs={"class": "subtext"}).findAll('a')) >= 3 and 'comments' in \
                str(content.find(attrs={"class": "subtext"}).findAll('a')[3]):
            comments = content.find(attrs={"class": "subtext"}).findAll('a')[3].text.replace("\xa0comments", "")
        else:
            comments = "Unknown"
        if content.find(attrs={"class": "subtext"}).find(attrs={"class": "score"}) is not None:
            points = content.find(attrs={"class": "subtext"}).find(attrs={"class": "score"}).text.replace(" points", "")
        else:
            points = 'Unknown'
        title = content.find(attrs={"class": "athing"}).find(attrs={"class": "storylink"}).text
        if content.find(attrs={"class": "sitestr"}) is not None:
            url = content.find(attrs={"class": "sitestr"}).text
        else:
            url = 'Unknown'
        news_pattern['author'], news_pattern['comments'], news_pattern['points'], news_pattern['title'], news_pattern[
            'url'] = \
            author, comments, points, title, url

        # rank = int(content.find(attrs= {"class" : "rank"}).text.replace(".", ""))

        news_list.append(news_pattern)
        news_pattern = {
            'author': '',
            'comments': '',
            'points': '',
            'title': '',
            'url': '',
        }
        content.find(attrs={"class": "athing"}).decompose()
        content.find(attrs={"class": "subtext"}).decompose()
    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    numbers = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
    reversed_number_list = []
    number_list = []
    page_number = ''
    if '/news?p=' in parser:
        for i in range(len(parser))[::-1]:
            if parser[i] in numbers:
                reversed_number_list.append(parser[i])
                parser.replace(parser[i], '')
            else:
                break
        for j in reversed(reversed_number_list):
            number_list.append(j)
        for k in number_list:
            page_number += k
        page_number = str(int(page_number)+1)
    else:
        page_number = '2'
    return 'news?p='+page_number


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(url)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news


if __name__ == "__main__":
    print(get_news("https://news.ycombinator.com/", 1))




