from sqlHandler import SQLHandler
from telebot import types, TeleBot
from settings import settings as SETS

bot = TeleBot(SETS['token'])


def makeInlKbrdBtn(obj):
    return types.InlineKeyboardButton(
        obj[0], callback_data=obj[1]
    )


@bot.message_handler(commands=['start'])
def welcome(msg):
    chat = msg.chat

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    itemList = types.KeyboardButton('Каталог')
    itemStash = types.KeyboardButton('Показать Корзину')
    itemClear = types.KeyboardButton('Очистить Корзину')
    itemCheck = types.KeyboardButton('Оформить Заказ')

    markup.add(itemList)
    markup.add(itemStash, itemClear, itemCheck)

    bot.send_message(
        chat.id, f'Привет, {chat.first_name}\nНапиши \"help\",чтобы узнать, что я умею', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def parse(msg):
    chat = msg.chat
    text = msg.text.lower()

    handle = SQLHandler(SETS['db'])

    if text == 'каталог':
        tastes = handle.getAllTasteName()
        markup = types.InlineKeyboardMarkup(row_width=2)

        for i in range(0, len(tastes) - 1, 2):
            markup.add(
                makeInlKbrdBtn(tastes[i]),
                makeInlKbrdBtn(tastes[i+1])
            )
        if len(tastes) % 2:
            markup.add(
                makeInlKbrdBtn(tastes[len(tastes) - 1])
            )

        bot.send_message(chat.id, 'Вот весь ассортимент', reply_markup=markup)

    elif text == 'показать корзину':
        output = ''

        stash = handle.getStash(chat.id)
        if not stash:
            output += 'Тут как-то пустовато'
        else:
            for item in stash:
                output += f'{item[0]}: {item[1]}\n'

        bot.send_message(chat.id, output)

    elif text == 'очистить корзину':
        handle.clearStash(chat.id)
        handle.commit()

    elif text == 'оформить заказ':
        handle.checkout(chat)
        handle.commit()
        bot.send_message(chat.id, 'Ну тут надо бы к оплате')

    else:
        bot.send_message(chat.id, 'Я не знаю, что на это ответить :c')

    handle.close()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat = call.message.chat
    handle = SQLHandler(SETS['db'])

    if call.message:
        if call.data == 'a':
            pass
        else:
            handle.insertToStash(call)
            handle.commit()
            bot.answer_callback_query(
                callback_query_id=call.id, show_alert=False, text="Добавлено!")

    handle.close()


bot.infinity_polling()
