import json
import queue
import time

import pymorphy2
import telebot

from num2text import num2text

bot = telebot.TeleBot('1057142794:AAGgZd7PeHiwCDQZDMcVzwtv0bvv8rWKgMI', num_threads=3)
morph = pymorphy2.MorphAnalyzer()
autodelete_queue = queue.Queue()


def time_left_to_text(time_left):
    if time_left < 60:
        noun = "секунда"
        num = time_left
        if str(num).endswith("1") and num != 11:
            return str(num) + " " + "секунду"
    elif time_left < 3600:
        noun = "минута"
        num = time_left // 60
        if str(num).endswith("1") and num != 11:
            return str(num) + " " + "минуту"
    elif time_left < 86400:
        noun = "час"
        num = time_left // 3600
    else:
        num = time_left // 86400
        noun = "день"

    word = morph.parse(noun)[0]
    v1, v2, v3 = word.inflect({'sing', 'nomn'}), word.inflect({'gent'}), word.inflect({'plur', 'gent'})

    return str(num) + " " + num2text(num=num, main_units=((v1.word, v2.word, v3.word), 'm'))[-1]


# сохранение в файл
def save(data):
    with open('data', 'w', encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2)
        outfile.close()


def adel(timeout, message):
    autodelete_queue.put((time.time()+timeout, message))
