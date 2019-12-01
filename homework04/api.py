import requests
from datetime import datetime
# import plotly
import time


config = {
    'VK_ACCESS_TOKEN': 'fbbdb9bff0e2c5d9dc642f55ffe3f93f48431cf291cda2577995225da1000665834dfcbc93155cdedbcd8',
    'PLOTLY_USERNAME': 'FlaminCat',
    'PLOTLY_API_KEY': 'Y3WgL8CzjiRLkpIDRyVj'
}


def get(url, params={}, timeout=2, max_retries=5, backoff_factor=0.3):
    """ Выполнить GET-запрос

    :param url: адрес, на который необходимо выполнить запрос
    :param params: параметры запроса
    :param timeout: максимальное время ожидания ответа от сервера
    :param max_retries: максимальное число повторных запросов
    :param backoff_factor: коэффициент экспоненциального нарастания задержки
    """


    for a in range(max_retries):
        backoff_delay = backoff_factor * (2 ** (a - 1))
        try:
            response = requests.get(url, params=params, timeout=timeout)
        except requests.exceptions.ReadTimeout:
            print('read timeout.')
            time.sleep(backoff_delay)
            continue
        except requests.exceptions.ConnectTimeout:
            print('connect timeout.')
            time.sleep(backoff_delay)
            continue
        except requests.exceptions.ConnectionError:
            print('Seems like dns lookup failed..')
            return None
        except requests.exceptions.HTTPError as err:
            print('Oops. HTTP Error occured')
            print('Response is: {content}'.format(content=err.response.content))
            return None
        if response.status_code == 200:
            return response
        else:
            print('Connection problem occurred')
            return None
    print("max retries passed")
    return None


def get_friends(user_id, fields='bdate'):
    """ Вернуть данных о друзьях пользователя

    :param user_id: идентификатор пользователя, список друзей которого нужно получить
    :param fields: список полей, которые нужно получить для каждого пользователя
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert isinstance(fields, str), "fields must be string"
    assert user_id > 0, "user_id must be positive integer"
    access_token = '{VK_ACCESS_TOKEN}'.format(**config)
    domain = "https://api.vk.com/method"
    query_params = {
    'domain': domain,
    'access_token': access_token,
    'user_id': user_id,
    'fields': fields
    }
    query = "{domain}/friends.get?access_token={access_token}&user_id={user_id}&fields={fields}&v=5.53".format(**query_params)
    print(query)
    ans = get(query)
    print(ans.json)
    if ans:
        return ans.json()["response"]["items"]
    else:
        return None


def age_predict(user_id):
    """ Наивный прогноз возраста по возрасту друзей

    Возраст считается как медиана среди возраста всех друзей пользователя

    :param user_id: идентификатор пользователя
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    rp = get_friends(user_id)
    if rp:
        count = 0
        age_sum = 0
        for e in range(len(rp)):
            if 'bdate' in rp[e]:
                if len(rp[e]['bdate']) > 7:
                    age_sum += age(rp[e]['bdate'])
                    count += 1
        age_pr = round(age_sum / count, 1)
        return age_pr
    else:
        return rp


def age(bdate):
    bdate = bdate.split(".")

    day = int(bdate[0])
    month = int(bdate[1])
    year = int(bdate[2])
    now = datetime.now()

    cd = now.day
    cm = now.month
    cy = now.year
    if month > cm:
        age = cy - year - 1
    elif month == cm:
        if day > cd:
            age = cy - year - 1
        else:
            age = cy - year
    else:
        age = cy - year
    return age


def messages_get_history(user_id, count=20, offset=0):
    """ Получить историю переписки с указанным пользователем

    :param user_id: идентификатор пользователя, с которым нужно получить историю переписки
    :param offset: смещение в истории переписки
    :param count: число сообщений, которое нужно получить
    """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    assert isinstance(offset, int), "offset must be positive integer"
    assert offset >= 0, "user_id must be positive integer"
    assert count >= 0, "user_id must be positive integer"
    access_token = '{VK_ACCESS_TOKEN}'.format(**config)
    domain = "https://api.vk.com/method"
    query_params = {
    'domain': domain,
    'access_token': access_token,
    'offset': offset,
    'count': count,
    'user_id': user_id
    }
    query = "{domain}/messages.getHistory?access_token={access_token}&offset={offset}&count={count}&user_id={user_id}&v=5.53".format(**query_params)
    meslst = get(query).json()
    return meslst


def count_dates_from_messages(messages):
    """ Получить список дат и их частот

    :param messages: список сообщений
    """
    dalist = []
    freqlist = []
    for a in range(len(messages['response']['items'])):
        date = datetime.fromtimestamp(messages['response']['items'][a]['date']).strftime("%d-%m-%Y")
        if date in dalist:
            b = dalist.index(date)
            freqlist[b] += 1
        else:
            dalist.append(date)
            freqlist.append(1)
    return dalist, freqlist


def plotly_messages_freq(dalist, freqlist):
    """ Построение графика с помощью Plot.ly

    :param freq_list: список дат и их частот
    """
    username = '{PLOTLY_USERNAME}'.format(**config)
    api_key = '{PLOTLY_API_KEY}'.format(**config)
    plotly.tools.set_credentials_file(username=username, api_key=api_key)
    import plotly.plotly as py
    import plotly.graph_objs as go
    data = [go.Scatter(x=dalist,y=freqlist)]
    py.iplot(data)
    pass


def get_network(users_ids, as_edgelist=True):
    edgelist = []
    for i in users_ids:
        hfriends = get_friends(i, fields = 'sex')
        hfidlist = []
        for b in range(len(hfriends)):
            hfidlist.append(hfriends[b]['id'])
        for c in users_ids:
            if c in hfidlist:
                tup = (users_ids.index(i), users_ids.index(c))
                if tup not in edgelist:
                    tup = (users_ids.index(c), users_ids.index(i))
                    if tup not in edgelist:
                        edgelist.append(tup)
    plot_graph(edgelist)


def plot_graph(edges):
    import networkx as nx
    import matplotlib.pyplot as plt
    import os
    G = nx.Graph()
    G.add_edges_from(edges)
    options = {
        'node_size': 140,
        'width': 1,
        "with_labels": True,
        "font_weight": 'normal'
    }
    nx.clustering(G)
    nx.draw(G, **options)
    plt.savefig("path.png")
    os.system("start chrome path.png")


if __name__ == "__main__":
    # meslst = messages_get_history(22623485, 100)
    # dalist, freqlist = count_dates_from_messages(meslst)
    # plotly_messages_freq(dalist, freqlist)
    a = age_predict(173033681)
    print(a)
    # get_network([22623485, 91513280, 73585018, 50415474, 63572038, 126912463, 1290164, 95876322, 249635751, 3263771,
    # 11086613, 31373259])
