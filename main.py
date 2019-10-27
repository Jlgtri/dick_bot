import telebot
import queue
import threading
import time
import datetime
import random

bot = telebot.TeleBot('643454815:AAEgQ3cw3SUT-WqXGm39qLrjPl-WEPpz5Xk')
dick_user_list = []
dicksize_queue = queue.Queue()
dickfight_queue = queue.Queue()
autodelete_queue = queue.Queue()

bot_messages = {
    "global": {
        "in_game": "{0}, теперь ты в игре самый длинный песюн!",
        "unknown": "Произошел КЕК. Попробуй еще раз.",
        "unregistered": "Ты незареган. Напиши /dick чтобы исправить это.",
    },

    "mydick": {
        "mydick_def": "{0}, твий дик довжиною {1} см",
        "mydick_zero": "{0}, у тебе дика нема",
        "mydick_top1": "{0}, у тебе самый большой песюн! {1} см!!!"
    },

    "dicksize": {
        "no_dick": "{0}, у тебя нет песюна. Играй дальше, чтобы получить его!",
        "dick_increased": "{0}, твой песюн увеличился на {1} см. Теперь его длина {2} см.",
        "dick_decreased": "{0}, твой песюн уменьшился на {1} см. Теперь его длина {2} см.",
        "dick_lost": "{0}, искренне сочувствую утрате вашего песюна. Удачи!",
        "dick_unchanged": "{0}, твой песюн не изменился.",
        "dick_zero_unchanged": "{0}, твой песюн не изменился. Его все также нет.",
        "cooldown": "{0}, сутки еще не прошли, осталось ждать {1}",
    },

    "dickfight": {
        "game_created": "Ты в игре, кто хочет посоревноватся??",
        "game_over": "{0} вийграв. Вот його вийграш: +{1}см",
        "low_money": "У тебе нема стильки дика.",
        "invalid": "Та нормальну ставку напиши дебил.",
        "same_user": "Нельзя сам с собой играть, придурок.",
        "wrong_chat": "Ты переплутав чат, гуляй.",
        "cancel": "Ну все, расходимся."
    },
}


@bot.message_handler(commands=['mydick'])
def dicksize_request(message):
    user = identify_user(message)
    size = user['size']

    if size == 0:
        bot.send_message(user["chat_id"], bot_messages["mydick"]["mydick_zero"].format(user["first_name"]),
                         disable_notification=True)
    else:
        bot.send_message(user["chat_id"], bot_messages["mydick"]["mydick_def"].format(user["first_name"], user["size"]),
                         disable_notification=True)
    autodelete_queue.put((time.time()+5, message))


@bot.message_handler(commands=['dick'])
def dicksize_request(message):
    dicksize_queue.put(message)     # Добавляем запрос в очередь конкретно этой команды
    autodelete_queue.put((time.time()+5, message))


@bot.message_handler(commands=['dickfight'])
def dickfight_request(message):
    dickfight_queue.put(message)     # Добавляем запрос в очередь конкретно этой команды
    autodelete_queue.put((time.time()+5, message))


def check_for_cooldown(user):
    cooldown = 1    # в секундах
    return cooldown - (int(time.time()) - user["last_try"])


def create_user(message):
    # Создаем обьект юзера
    dick_user = {'user_id': message.from_user.id,
                 'chat_id': message.chat.id,
                 'first_name': message.from_user.first_name,
                 'size': 0,
                 }
    dick_user_list.append(dick_user)  # Добавляем в конец списка юзеров
    return dick_user_list[-1]


def identify_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    for user in dick_user_list:
        if user['user_id'] == user_id and\
                user['chat_id'] == chat_id:  # Если юзер существует
            break
    else:
        user = create_user(message)
        bot.send_message(user["chat_id"], bot_messages["global"]["in_game"].format(user["first_name"]))

    return user


def dicksize():
    while True:
        message = dicksize_queue.get()
        old_size = -1
        dicksize_changed = True
        cooldown = False

        user = identify_user(message=message)
        if 'last_try' in user:
            time_left = check_for_cooldown(user)   # Проверяем сколько времени осталось до следующего раза
            if time_left < 0:
                old_size = user['size']
                add_size = dicksize_change(user)
            else:   # Если время еще не прошло, помечаем
                cooldown = True
        else:
            add_size = dicksize_change(user)

        # ОТВЕТ БОТА НА ИЗМЕНЕНИЕ ПЕСЮНА
        if cooldown:
            bot.send_message(user["chat_id"], bot_messages["dicksize"]["cooldown"].format(user["first_name"],
                                                                                          datetime.timedelta(seconds=time_left)),
                             disable_notification=True)
        elif dicksize_changed:
            if user['size'] == 0 and old_size == 0:
                bot.send_message(user["chat_id"], bot_messages["dicksize"]["dick_zero_unchanged"].format(user["first_name"]),
                                 disable_notification=True)
            elif user['size'] <= 0:
                if old_size > 0:    # Если был до этого, а потом пропал
                    bot.send_message(user["chat_id"], bot_messages["dicksize"]["dick_lost"].format(user["first_name"]),
                                     disable_notification=True)
                else:   # Если не было до этого
                    bot.send_message(user["chat_id"], bot_messages["dicksize"]["no_dick"].format(user["first_name"]),
                                     disable_notification=True)

            else:
                if add_size > 0:
                    bot.send_message(user["chat_id"], bot_messages["dicksize"]["dick_increased"].format(user["first_name"],
                                                                                                abs(add_size),
                                                                                                user['size']),
                                     disable_notification=True)
                elif add_size < 0:
                    bot.send_message(user["chat_id"], bot_messages["dicksize"]["dick_decreased"].format(user["first_name"],
                                                                                                abs(add_size),
                                                                                                user['size']),
                                     disable_notification=True)
                else:
                    bot.send_message(user["chat_id"], bot_messages["dicksize"]["dick_unchanged"].format(user["first_name"]),
                                     disable_notification=True)


def dicksize_change(user):
    rand = random.uniform(0, 1)     # Вероятность от 0 до 1

    if rand < .10:            # Шанс 10%
        add_size = random.choice((-4, 5))
    elif .10 <= rand < .25:   # Шанс 15%
        add_size = random.choice((-3, 4))
    elif .25 <= rand < .45:   # Шанс 20%
        add_size = random.choice((-2, 3))
    elif .45 <= rand < .60:   # Шанс 25%
        add_size = random.choice((-1, 2))
    else:                     # Шанс 40%
        add_size = random.choice((0, 1))

    user['size'] += add_size
    if user['size'] < 0:
        user['size'] = 0
    user['last_try'] = int(time.time())
    return add_size


def dickfight():
    fighters = []
    game_bet = 0
    while True:
        message = dickfight_queue.get()
        if len(fighters) == 1:  # Игра уже создана
            user = identify_user(message)
            if user["user_id"] is fighters[0]["user_id"]:     # Если тот же самый
                if message.text[-1] == "-":  # Ахрана атмена
                    bot.send_message(user["chat_id"], bot_messages["dickfight"]["cancel"],
                                     disable_notification=True)
                    fighters[0]["size"] += game_bet
                    fighters = []
                    game_bet = 0
                    continue

                bot.send_message(fighters[0]["chat_id"], bot_messages["dickfight"]["same_user"], disable_notification=True)
                continue
            elif user["chat_id"] != fighters[0]["chat_id"]:    # Если чат не совпадает
                bot.send_message(user["chat_id"], bot_messages["dickfight"]["wrong_chat"], disable_notification=True)
                continue
        else:
            user = identify_user(message)

            try:    # Проверка ставки на правильность
                game_bet = int(message.text.split(" ")[1].strip())
                if 1 > game_bet > 100:
                    raise ValueError("от 1 до 100")
            except:
                bot.send_message(user["chat_id"], bot_messages["dickfight"]["invalid"].format(),
                                 disable_notification=True)
                continue

        if game_bet > user["size"]:  # Если нема грошей
            bot.send_message(user["chat_id"], bot_messages["dickfight"]["low_money"].format(),
                             disable_notification=True)
            continue

        # Если все в порядке
        user["size"] -= game_bet
        fighters.append(user)

        if len(fighters) == 2:
            if fighters[0]["chat_id"] == fighters[1]["chat_id"]:
                winner = fighters[random.choice((0, 1))]

                bot.send_message(fighters[0]["chat_id"], bot_messages["dickfight"]["game_over"].format(winner["first_name"],
                                                                                                       game_bet*2),
                                 disable_notification=True)
                winner["size"] += game_bet*2
                fighters = []
                game_bet = 0
            else:
                bot.send_message(fighters[0]["chat_id"], bot_messages["global"]["unknown"], disable_notification=True)
                continue
        else:
            bot.send_message(user["chat_id"], bot_messages["dickfight"]["game_created"].format())


def autodelete():
    while True:     # to do = (time, item)
        todo = autodelete_queue.get()
        if time.time() > todo[0]:
            if type(todo[1]) is telebot.types.Message:
                message = todo[1]
                bot.delete_message(message.chat.id, message.message_id)
        else:
            autodelete_queue.put(todo)


threading.Thread(target=dicksize, name="dicksize").start()
threading.Thread(target=dickfight, name="dickfight").start()
threading.Thread(target=autodelete, name="autodelete").start()
bot.polling(none_stop=True, interval=0)
