import random
from main_func import *

bot_messages = json.load(open("responses", encoding="utf-8"))


class DickFight:
    def __init__(self):
        self.finish_msg_delete_delay = 600
        self.fight_chats = {}
        self.msgs = []
        self.msg = self.Msg()

    def create_game(self, user, message):
        def check_bet(msg):
            import re
            value = re.sub(r'\s\s+', ' ', msg.text + " ").split(" ")[1].strip()
            if value == '' or value == ' ':
                value = 1
            else:
                try:  # Проверка ставки на правильность
                    value = int(value)
                    if 1 > value or value > 100:
                        raise ValueError("от 1 до 100")
                except ValueError:
                    return None
            return value

        self.msg.user = user
        game_bet = check_bet(message)

        if game_bet is None:
            self.msgs.append(self.msg.invalid())

        elif game_bet > user["size"]:  # Если нема грошей
            self.msgs.append(self.msg.low_money())

        else:
            user["size"] -= game_bet
            self.fight_chats[user["chat_id"]] = {"fighters": [user], "game_bet": game_bet}
            self.msgs.append(self.msg.game_created(game_bet))

    def join_game(self, user):
        self.msg.user = user
        fight = self.fight_chats[user["chat_id"]]
        if user["user_id"] is fight["fighters"][0]["user_id"]:  # Если тот же самый юзер
            self.msgs.append(self.msg.same_user())
            return
        user["size"] -= fight["game_bet"]
        fight["fighters"].append(user)

        rand = int(random.choice((0, 1)))
        winner, loser = fight["fighters"][rand],\
            fight["fighters"][int(not bool(rand))]
        winner["size"] += fight["game_bet"] * 2
        adel(self.finish_msg_delete_delay, self.msg.finish(winner, loser, fight["game_bet"]))
        self.fight_chats.pop(user["chat_id"])

        for msg in self.msgs:
            adel(1, msg)
        self.msgs = []

    def cancel_game(self, user):
        self.msg.user = user
        user["size"] += self.fight_chats[user["chat_id"]]["game_bet"]
        del self.fight_chats[user["chat_id"]]

        for msg in self.msgs:
            adel(1, msg)
        self.msgs = []

        adel(60, self.msg.cancel())

    class Msg:
        def __init__(self):
            self.user = None

        def game_created(self, game_bet):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dickfight"]["game_created"]
                                   .format(self.user["user_id"],
                                           self.user["first_name"],
                                           game_bet),
                                   parse_mode="Markdown")
            return msg

        def same_user(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dickfight"]["same_user"]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def low_money(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dickfight"]["low_money"]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def invalid(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dickfight"]["invalid"]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def cancel(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dickfight"]["cancel"]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def finish(self, winner, loser, game_bet):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dickfight"]["game_over"]
                                   [random.choice(range(0, len(bot_messages["dickfight"]["game_over"])))]
                                   .format(winner["user_id"], winner["first_name"],
                                           loser["user_id"], loser["first_name"],
                                           game_bet * 2),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg


class DickSize:
    def __init__(self):
        self.dicksize_cooldown = 86400
        self.msg_delete_delay = 300
        self.cooldown_msg_delete_delay = 60

        self.msg = self.Msg()

    def dick_size_change(self, user):
        self.msg.user = user

        def check_for_cooldown():
            time_left_val = self.dicksize_cooldown - (int(time.time()) - user["last_try"])
            return False if time_left_val <= 0 else True, time_left_val

        def dicksize_change():
            rand = random.uniform(0, 1)  # Вероятность от 0 до 1
            if rand < .10:  # Шанс 10%
                add_size = random.choice((-4, 5))
            elif .10 <= rand < .25:  # Шанс 15%
                add_size = random.choice((-3, 4))
            elif .25 <= rand < .45:  # Шанс 20%
                add_size = random.choice((-2, 3))
            elif .45 <= rand < .60:  # Шанс 25%
                add_size = random.choice((-1, 2))
            else:  # Шанс 40%
                add_size = random.choice((0, 1))
            return add_size

        cooldown, time_left = check_for_cooldown()
        if not cooldown:
            old_size = user['size']
            add_size = dicksize_change()
            user['size'] += add_size
            if user['size'] < 0:
                user['size'] = 0
            user['last_try'] = int(time.time())
            # if user_in_fight(user):
            # adel(60, self.msg.refuse())
        else:
            adel(self.cooldown_msg_delete_delay, self.msg.cooldown(time_left))
            return

        if user['size'] == 0 and old_size == 0: # Если не появился и не было до этого
            adel(self.msg_delete_delay, self.msg.dick_zero_unchanged())
        elif user['size'] <= 0:
            if old_size > 0:    # Если был до этого, а потом пропал
                adel(self.msg_delete_delay, self.msg.dick_lost())
            else:   # Если не было до этого
                adel(self.msg_delete_delay, self.msg.no_dick())
        else:
            if add_size > 0:  # Если увеличился
                adel(self.msg_delete_delay, self.msg.dick_increased(add_size))
            elif add_size < 0:  # Если уменьшился
                adel(self.msg_delete_delay, self.msg.dick_decreased(add_size))
            else:  # Если не изменился
                adel(self.msg_delete_delay, self.msg.dick_unchanged())

    class Msg:
        def __init__(self):
            self.user = None

        def refuse(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dicksize"]["refuse"]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def cooldown(self, time_left):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dicksize"]["cooldown"]
                                   [random.choice(range(0, len(bot_messages["dicksize"]["cooldown"])))]
                                   .format(self.user["user_id"], self.user["first_name"],
                                           time_left_to_text(time_left)),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def dick_zero_unchanged(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dicksize"]["dick_zero_unchanged"]
                                   [random.choice(range(0, len(bot_messages["dicksize"]["dick_zero_unchanged"])))]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def dick_lost(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dicksize"]["dick_lost"]
                                   [random.choice(range(0, len(bot_messages["dicksize"]["dick_lost"])))]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def no_dick(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dicksize"]["no_dick"]
                                   [random.choice(range(0, len(bot_messages["dicksize"]["no_dick"])))]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def dick_increased(self, add_size):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dicksize"]["dick_increased"]
                                   [random.choice(range(0, len(bot_messages["dicksize"]["dick_increased"])))]
                                   .format(self.user["user_id"], self.user["first_name"],
                                           add_size, self.user['size']),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def dick_decreased(self, add_size):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dicksize"]["dick_decreased"]
                                   [random.choice(range(0, len(bot_messages["dicksize"]["dick_decreased"])))]
                                   .format(self.user["user_id"], self.user["first_name"],
                                           abs(add_size), self.user['size']),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg

        def dick_unchanged(self):
            msg = bot.send_message(self.user["chat_id"],
                                   bot_messages["dicksize"]["dick_unchanged"]
                                   [random.choice(range(0, len(bot_messages["dicksize"]["dick_unchanged"])))]
                                   .format(self.user["user_id"], self.user["first_name"]),
                                   disable_notification=True,
                                   parse_mode="Markdown")
            return msg
