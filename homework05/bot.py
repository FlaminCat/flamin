import requests
import config
import telebot
from bs4 import BeautifulSoup


bot = telebot.TeleBot(config.access_token)


def get_page(group, week=''):
    if week:
        week = str(week) + '/'
    url = '{domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(
        domain=config.domain,
        week=week,
        group=group)
    response = requests.get(url)
    web_page = response.text
    return web_page


def get_schedule(web_page, day):
    soup = BeautifulSoup(web_page, "html5lib")
    schedule_table = soup.find("table", attrs={"id": day})

    if schedule_table is not None:
        times_list = schedule_table.find_all("td", attrs={"class": "time"})
        times_list = [time.span.text for time in times_list]

        week_list = schedule_table.find_all("dt", attrs={"style": "font-size:14px;"})
        week_list = [week_parity.text for week_parity in week_list if week_parity]

        locations_list = schedule_table.find_all("td", attrs={"class": "room"})
        locations_list = [room.span.text for room in locations_list]

        classrooms_list = schedule_table.find_all("dd", attrs={"class": "rasp_aud_mobile"})
        classrooms_list = [classroom.text for classroom in classrooms_list if classroom]

        lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
        lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
        lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

        return times_list, week_list, locations_list, classrooms_list, lessons_list

    else:
        return None


@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
def get_day(message):
    k = 0
    for i in message.text:
        if i == ' ':
            k += 1

    if k > 1:
        _, week, group = message.text.split()
        web_page = get_page(group, week)
    else:
        _, group = message.text.split()
        web_page = get_page(group)
    week_day = _.replace("/", "")
    day = ''    # необходимый день в формате '*number*day'
    commands = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    days = ['1day', '2day', '3day', '4day', '5day', '6day', '7day']
    for i in range(len(commands)):
        if commands[i] == week_day:
            day = days[i]

    if get_schedule(web_page, day) is not None:
        times_lst, week_lst, locations_lst, classroom_lst, lessons_lst = get_schedule(web_page, day)

        resp = ''
        for time, parity, location, classroom, lession in zip(times_lst, week_lst, locations_lst, classroom_lst,
                                                              lessons_lst):
            resp += '<b>{} {}</b>, {} {}, {}\n'.format(time, parity, location, classroom, lession)
        bot.send_message(message.chat.id, resp, parse_mode='HTML')

    else:
        bot.send_message(message.chat.id, 'No lessons', parse_mode='HTML')



@bot.message_handler(commands=['near'])
def get_near_lesson(message):
    import datetime
    now = datetime.datetime.now()
    date = datetime.date(now.year, now.month, now.day)
    cyear, cweek, cday = date.isocalendar()
    if cweek % 2 == 0:
        week = '1'
    else:
        week = '2'
    _, group = message.text.split()
    web_page = get_page(group, week)
    tomorrow = cday + 1
    if tomorrow == 8:
        tomorrow = 1
    day = '{}day'.format(str(tomorrow))

    time = '{}:{}'.format(now.hour, now.minute)

    if get_schedule(web_page, day) is not None:
        times_lst, week_lst, locations_lst, classroom_lst, lessons_lst = get_schedule(web_page, day)
        for i in range(len(times_lst)):
            if time < times_lst[i][:5] or time > times_lst[i][5:]:
                del (times_lst[i], locations_lst[i], classroom_lst[i], lessons_lst[i])

        if times_lst == []:
            get_first_lesson(tomorrow, web_page, message)
        else:
            resp = ''
            for time, parity, location, classroom, lession in zip(times_lst, week_lst, locations_lst, classroom_lst,
                                                                  lessons_lst):
                resp += '<b>{} {}</b>, {} {}, {}\n'.format(time, parity, location, classroom, lession)
            bot.send_message(message.chat.id, resp, parse_mode = 'HTML')

    else:
        get_first_lesson(tomorrow, web_page, message)


def get_first_lesson(tomorrow, web_page, message):
    day = '{}day'.format(str(tomorrow))
    if get_schedule(web_page, day) is not None:
        times_lst, week_lst, locations_lst, classroom_lst, lessons_lst = get_schedule(web_page, day)
        resp = ''
        for time, parity, location, classroom, lession in zip(times_lst, week_lst, locations_lst, classroom_lst,
                                                              lessons_lst):
            resp += '<b>{} {}</b>, {} {}, {}\n'.format(time, parity, location, classroom, lession)
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
    else:
        get_first_lesson(tomorrow+1, web_page, message)


@bot.message_handler(commands=['tomorrow'])
def get_tommorow(message):
    """ Получить расписание на следующий день """
    import datetime
    now = datetime.datetime.now()
    date = datetime.date(now.year, now.month, now.day)
    cyear, cweek, cday = date.isocalendar()
    tomorrow = cday + 1
    if tomorrow == 8:
        tomorrow = 1
    day = '{}day'.format(str(tomorrow))
    if cweek % 2 == 0:
        week = '1'
    else:
        week = '2'
    _, group = message.text.split()
    web_page = get_page(group, week)
    if get_schedule(web_page, day) is not None:
        times_lst, week_lst, locations_lst, classroom_lst, lessons_lst = get_schedule(web_page, day)

        resp = ''
        for time, parity, location, classroom, lession in zip(times_lst, week_lst, locations_lst, classroom_lst,
                                                              lessons_lst):
            resp += '<b>{} {}</b>, {} {}, {}\n'.format(time, parity, location, classroom, lession)
        bot.send_message(message.chat.id, resp, parse_mode='HTML')

    else:
        bot.send_message(message.chat.id, 'No lessons', parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
    """ Получить расписание на всю неделю для указанной группы """
    import datetime
    now = datetime.datetime.now()
    date = datetime.date(now.year, now.month, now.day)
    cyear, cweek, cday = date.isocalendar()
    if cweek % 2 == 0:
        week = '1'
    else:
        week = '2'
    _, group = message.text.split()
    web_page = get_page(group, week)
    days = ['1day', '2day', '3day', '4day', '5day', '6day']
    commands = ['Monday:', 'Tuesday:', 'Wednesday:', 'Thursday:', 'Friday:', 'Saturday:']
    for i in range(6):
        bot.send_message(message.chat.id, commands[i], parse_mode='HTML')
        if get_schedule(web_page, days[i]) is not None:
            times_lst, week_lst, locations_lst, classroom_lst, lessons_lst = get_schedule(web_page, days[i])

            resp = ''
            for time, parity, location, classroom, lession in zip(times_lst, week_lst, locations_lst, classroom_lst,
                                                                  lessons_lst):
                resp += '<b>{} {}</b>, {} {}, {}\n'.format(time, parity, location, classroom, lession)
            bot.send_message(message.chat.id, resp, parse_mode='HTML')

        else:
            bot.send_message(message.chat.id, 'No lessons', parse_mode='HTML')


if __name__ == '__main__':
    bot.polling(none_stop=True)
