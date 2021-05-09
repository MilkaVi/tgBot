import vk_api
from pyowm.utils.config import get_default_config
from vk_api import audio
import pyowm
import urllib.request as urllib2
import kokq
import requests
import urllib.request
from bs4 import BeautifulSoup
import telebot
import pb
import datetime
import pytz
import json
P_TIMEZONE = pytz.timezone('Europe/Minsk')
TIMEZONE_COMMON_NAME = 'Vitebsk'
REQUEST_STATUS_CODE = 200
token="1834784024:AAHfminb0_d_GPfvTmI5cL9sWBGZ94gPJ1k"
config_dict = get_default_config()
config_dict['language'] = 'ru'
owm = pyowm.OWM("e84b528e1117f14ab871db532fe4767f", config_dict)

bot = telebot.TeleBot(token)
login = ''
my_id = ''
do=0
posle=0
music = ''
place = ''
login=''
password=''


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('зарегистрироваться', 'погода','новости')
    user_markup.row('скачать все треки', 'скачать трек',"конвертер валют")
    user_markup.row('узнать расписание', "калькулятор",'/stop')
    bot.send_message(message.from_user.id, '...', reply_markup=user_markup)

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.from_user.id, '..', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'зарегистрироваться':
        bot.send_message(message.from_user.id, "Login - ")
        bot.register_next_step_handler(message, get_login)

    if message.text=="конвертер валют":
        keybord=telebot.types.InlineKeyboardMarkup()
        keybord.row(telebot.types.InlineKeyboardButton("USD",callback_data="get-USD"))
        keybord.row(telebot.types.InlineKeyboardButton("EUR", callback_data="get-EUR"),
                    telebot.types.InlineKeyboardButton("RUB", callback_data="get-RUB"))
        bot.send_message(message.from_user.id,'Выберю валюту',reply_markup=keybord)

    if message.text == "скачать все треки":

        bot.send_message(message.from_user.id, "c какой песни скачивать №  ")
        bot.register_next_step_handler(message, get_posle)

    if message.text == "скачать трек":
        downl_1trek(message,login,password)

    if message.text=='новости':
        try:
            main(message)
        except:
            bot.send_message(message.from_user.id,"ошибка сервера")

    if message.text == 'узнать расписание':
        try:
            urllib2.urlretrieve("https://vsu.by/images/rasp/mf/2019.10.25/%D0%A4%D0%9C%D0%B8%D0%98%D0%A2_9_%D0%BD%D0%B5%D0%B4_28.10-02.11.2019.xlsx",
        'расписание.xlsx')
            item = open('расписание.xlsx', 'rb')
            bot.send_chat_action(message.from_user.id, 'upload_document')
            bot.send_document(message.from_user.id, item)
            item.close()
            o = kokq.main()

            bot.send_message(message.from_user.id, o)

        except requests.exceptions.ReadTimeout:
            bot.send_message(message.from_user.id, " Р°Рµ")

    if message.text == 'погода':
        bot.send_message(message.from_user.id,"Погоду где вы хотите узнать? -")
        bot.register_next_step_handler(message, get_owm)

    if message.text=='калькулятор':
       bot.send_message(message.from_user.id,"Это  калькулятор который умеет выполнять следующие команды:"
                                             "сложение(+),вычитание(-),деление(/),умножение(*),"
                                             "возведение в степень(**)")
       bot.send_message(message.from_user.id,"введите выражение ")
       bot.register_next_step_handler(message,calc )



def get_posle(message):
    global posle
    posle = int(message.text)
    bot.send_message(message.from_user.id, "по какую №")
    bot.register_next_step_handler(message, get_do)


def get_do(message):
    global do
    do = int(message.text)
    bot.send_message(message.from_user.id, "отправьте любой символ для начала загрузки")
    bot.register_next_step_handler(message, get_downl)

def get_downl(message):
        try:
            vk_session = vk_api.VkApi(login=login, password=password)
            vk_session.auth()
            vk = vk_session.get_api()
            vk_audio = audio.VkAudio(vk_session)
            count = 1
            print(my_id);
            for i in vk_audio.get(owner_id=my_id):
                if (count >= posle) and (count <= do):
                    url = i["url"]
                    urllib2.urlretrieve(url, i["title"] + '.mp3')
                    item = open(i["title"] + '.mp3', 'rb')
                    bot.send_chat_action(message.from_user.id, 'upload_audio')
                    bot.send_message(message.from_user.id, str(count) + "-----------")
                    bot.send_audio(message.from_user.id, item)
                    item.close()
                if count > do:
                    break
                count = count + 1
        except:
            bot.send_message(message.from_user.id,
                             "Проверьте вошли ли вы в систему, если да то неверный ID.Введите еще раз ID-")
            bot.register_next_step_handler(message, get_myid)




def downl_1trek(message,login,password):
    try:
        vk_session = vk_api.VkApi(login=login, password=password)
        vk_session.auth()
        vk = vk_session.get_api()
        vk_audio = audio.VkAudio(vk_session)
        bot.send_message(message.from_user.id, "название трека - ")
        bot.register_next_step_handler(message, get_track)
        proverka = 0
        print(my_id);
        for i in vk_audio.get(owner_id=my_id):
            print(i["title"]);
            if i["title"] == music:

                url = i["url"]
                r = requests.get(url)
                bot.send_audio(message.from_user.id, r.content)
                #urllib2.urlretrieve(url, i["title"] + '.mp3')
               # item = open(i["title"] + '.mp3', 'rb')
               # bot.send_chat_action(message.from_user.id, 'upload_audio')
               # bot.send_audio(message.from_user.id, item)
               # item.close()
                proverka = 1
        if proverka == 0:
            bot.send_message(message.from_user.id, "Неверное название песни")
    except:
        bot.send_message(message.from_user.id,"Проверьте вошли ли вы в систему, если да"
                                              " то неверный ID. Введите повторно ID, если неверный логин или пароль вам предложат ввести повторно -")
        bot.register_next_step_handler(message, get_myid)




def get_track(message):
        global music
        music = message.text



def main(message):
  parse(message,get_html('https://news.tut.by/world/'))




def parse(message,html):
  soup=BeautifulSoup(html)
  span=soup.find_all("span",class_="entry-note")
  count=0
  for i in range(0, len(span)):
   count=count+1
   bot.send_message(message.from_user.id, str(count)+'.')
   bot.send_message(message.from_user.id, span[i])



def get_html(url):
  response=urllib.request.urlopen(url)
  return response.read()



@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('get-'):
        get_ex_callback(query)
    else:
        try:
            if json.loads(data)['t'] == 'u':
                edit_message_callback(query)
        except ValueError:
            pass




def edit_message_callback(query):
    data = json.loads(query.data)['e']
    exchange_now = pb.get_exchange('Витебск')
    text = serialize_ex(
        exchange_now,data['c'],
	get_exchange_diff(get_ex_from_iq_data(data),exchange_now,data['c'])
    ) + '\n' + get_edited_signature()
    if query.message:
        bot.edit_message_text(text,query.message.chat.id,query.message.message_id,reply_markup=get_update_keyboard(exchange_now,data['c']),parse_mode='HTML')
    elif query.inline_message_id:
        bot.edit_message_text(
            text,
	    inline_message_id=query.inline_message_id,
	    reply_markup=get_update_keyboard(exchange_now,data['c']),
	    parse_mode='HTML'
	)





def get_ex_from_iq_data(exc_json):
    return {
        'buy': exc_json['b'],
	'sale': exc_json['s']
    }




def get_exchange_diff(last, now,a):
    print(last)
    print(now)
    return {
        'sale_diff': float("%.6f" % (float(now[a+"_in"]) - float(last["sale"]))),'buy_diff': float("%.6f" % (float(now[a+"_out"]) - float(last["buy"])))
    }



def get_edited_signature():
    return '<i>Updated ' + \
           str(datetime.datetime.now(P_TIMEZONE).strftime('%H:%M:%S')) + \
           ' (' + TIMEZONE_COMMON_NAME + ')</i>'



def iq_callback(query):
    data = query.data
    if data.startswith('get-'):
        get_ex_callback(query)



def get_ex_callback(query):
  bot.answer_callback_query(query.id)
  send_exchange_result(query.message, query.data[4:])



def send_exchange_result(message, ex_code):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
    message.chat.id, serialize_ex(pb.get_exchange("Витебск"),ex_code),
        reply_markup=get_update_keyboard(pb.get_exchange("Витебск"),ex_code),
	parse_mode='HTML'
    )



def get_update_keyboard(ex,ex_code):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                'Update',
                callback_data=json.dumps({
                    't': 'u',
                    'e': {
                        'b': ex[ex_code+"_out"],
                        's': ex[ex_code+'_in'],
                        'c':ex_code
                    }
                }).replace(' ', '')
            ),
            telebot.types.InlineKeyboardButton('Share', switch_inline_query="BYN")
        )
        return keyboard




def serialize_ex(ex_json,ex_code,diff=None ):
    result = '<b>'+ex_code + ' -> ' + 'BYN' + ':</b>\n\n' + \
             'Buy: ' + ex_json[ex_code+"_out"]
    if diff:
        result += ' ' + serialize_exchange_diff(diff['buy_diff']) + '\n' + \
                  'Sell: ' + ex_json[ex_code+"_in"] + \
                  ' ' + serialize_exchange_diff(diff['sale_diff']) + '\n'
    else:
        result += '\nSell: ' + ex_json[ex_code+"_in"] + '\n'
    return result




def serialize_exchange_diff(diff):
    result = ''
    if diff > 0:
        result = '(' + str(diff) + "↗" ")"
    if diff <0:
        result = '(' + str(diff) + '↘'')'
    return result


def get_login(message):
    global login
    bot.delete_message(message.from_user.id, message.message_id)
    login = message.text
    bot.send_message(message.from_user.id, 'Password -  ')
    bot.register_next_step_handler(message, get_password)





def get_password(message):
    global password
    bot.delete_message(message.from_user.id,message.message_id)
    password = message.text
    bot.send_message(message.from_user.id, 'ID -  ')
    bot.register_next_step_handler(message, get_myid)





def get_myid(message):
    global my_id
    bot.delete_message(message.from_user.id, message.message_id)
    my_id = message.text
    bot.send_message(message.from_user.id, 'введите любой символ')
    bot.register_next_step_handler(message,get_auth)






def get_auth(message):
    try:
     vk_session = vk_api.VkApi(login=login, password=password)
     vk_session.auth()
     bot.send_message(message.from_user.id, "Вошли в систему успешно")
    except:
     bot.send_message(message.from_user.id, "Неверный логин или пароль.Повторите попытку")
     bot.send_message(message.from_user.id, "Login-")
     bot.register_next_step_handler(message, get_login)




def get_owm(message):
    try:
     global place
     place = message.text
     mgr = owm.weather_manager()
     observation = mgr.weather_at_place(place)
     w = observation.weather

     temp = w.temperature('celsius')["temp"]
     bot.send_message(message.from_user.id, 'температура: '+str(temp)+' градусов')
     bot.send_message(message.from_user.id, "ветер: "+str(w.wind()['speed'])+"м/c " + "cтатус:  " +w.detailed_status)
    except:
        bot.send_message(message.from_user.id, 'Не нашел такой город')


def calc(message):
    text=message.text
    result=0
    if text=="end":
        bot.send_message(message.from_user.id,"вышли с калькулятора")
        return
    if "+" in text:
        pos=text.find("+")
        a1=int(text[:pos])
        a2=int(text[pos+1:])
        result=a1+a2
    if "-" in text:
        pos=text.find("-")
        a1=int(text[:pos])
        a2=int(text[pos+1:])
        result=a1-a2
    if "**" in text:
        pos = text.find("*")
        a1 = int(text[:pos])
        a2 = int(text[pos + 2:])
        result = a1 ** a2
    elif "*" in text:
          pos=text.find("*")
          a1=int(text[:pos])
          a2=int(text[pos+1:])
          result=a1*a2
    if "/" in text:
        pos=text.find("/")
        a1=int(text[:pos])
        a2=int(text[pos+1:])
        if a2!=0:
         result=a1/a2
        else:
            bot.send_message(message.from_user.id,"На ноль делить нельзя")

    bot.send_message(message.from_user.id,text+"="+str(result))
    bot.send_message(message.from_user.id, "введите end,если хотите выйти с калькулятора")
    bot.register_next_step_handler(message,calc)

bot.polling(none_stop=True)