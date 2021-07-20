from telebot import types, TeleBot
from webserver import keep_alive
import sqlite3

bot = TeleBot('1919841754:AAHoKroSygO1G3QsJe9R-5QQMtfj5hEsy94')

conn = sqlite3.connect('VapesDB', check_same_thread=False)
cmd = conn.cursor()


@bot.message_handler(commands=['start'])
def welcome(msg):
    id = msg.chat.id
    bot.send_sticker(
        id, 'CAACAgIAAxkBAAECloJg8anh-l2wL1maGWYaJpckn-LgagACkg8AArkiUUhR-T_aqYRkrSAE'
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    itemList = types.KeyboardButton('Каталог')
    itemShow = types.KeyboardButton('Показать корзину')
    itemClear = types.KeyboardButton('Очистить корзину')

    markup.add(itemList, itemShow, itemClear)

    bot.send_message(
        id, 'Добро Пожаловать, {0.first_name}!'.format(
            msg.from_user, bot.get_me()), parse_mode='html', reply_markup=markup
    )


def getTastes():
    return cmd.execute('select taste, name from Products').fetchall()


def makeInlKbrdBtn(obj):
    return types.InlineKeyboardButton(
        obj[0], callback_data=obj[1]
    )


def getStash(id):
    cmd.execute(f'''
        select p.taste, oi.amount, p.price
        from customers as c, products as p, orderItems as oi, orders as o
        where
            c.id = {id}
        and
            o.customer_id = {id}
        and
            oi.order_id = o.id
        and
            o.status like 'stash'
        and
            oi.product_id = p.id
    ''')
    return cmd.fetchall()


@bot.message_handler(content_types=['text'])
def blabla(message):
    if message.chat.type == 'private':
        id = message.chat.id

        if message.text.lower() == 'каталог':

            markup = types.InlineKeyboardMarkup(row_width=2)
            tastes = getTastes()

            for i in range(0, len(tastes) - 1, 2):
                markup.add(
                    makeInlKbrdBtn(tastes[i]),
                    makeInlKbrdBtn(tastes[i+1])
                )
            if len(tastes) % 2:
                markup.add(
                    makeInlKbrdBtn(tastes[len(tastes) - 1])
                )

            # photo = open(r'D:\TG_bot\Photo\photo.jpg', 'rb')
            # bot.send_photo(message.chat.id, photo)
            bot.send_message(id, 'Вот что есть в наличии', reply_markup=markup)

        elif message.text.lower() == 'показать корзину':
            markup = types.InlineKeyboardMarkup(row_width=1)

            itemGood = makeInlKbrdBtn(('Оформить заказ', 'good'))
            itemBad = makeInlKbrdBtn(('Исправить', 'bad'))

            markup.add(itemGood)
            markup.add(itemBad)

            str_stash = ''
            stash = getStash(id)

            for item in stash:
                str_stash += f'{item[0]}: {item[1]}\n'

            if not len(stash):
                bot.send_message(id, 'Ваш заказ пуст 😢')
            else:
                bot.send_message(id, str_stash, reply_markup=markup)

        elif message.text.lower() == 'очистить корзину':
            bot.send_message(id, 'Корзина обнулена')

        else:
            bot.send_message(id, 'Я не знаю что ответить 😢')


@ bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    id = call.message.chat.id
    if call.message:
        if call.data == 'good':
            send = bot.send_message(
                id, 'Спасибо за заказ! Напишите адрес доставки и контактный номер телефонa')
            bot.register_next_step_handler(send, save_adress)

        else:
            addItem(call)
            conn.commit()

def save_adress(message):
    address = message.text
    cmd.execute(
        f'insert into customers (address) select {address}')

def addItem(call):
    cust_id = call.message.chat.id
    product_name = call.data

    cmd.execute(f'select ID from Customers where ID = {cust_id}')
    if not cmd.fetchone():
        cmd.execute(
            f'insert into customers (ID) select {cust_id}')

    cmd.execute(f'select ID from Products where name = \'{product_name}\'')
    product_id = cmd.fetchone()
    if not product_id:
        raise('No such product')
    product_id = product_id[0]

    cmd.execute(
        f'select ID from Orders where customer_id = {cust_id} and status like \'stash\''
    )
    order_id = cmd.fetchone()
    if not order_id:
        cmd.execute(f'insert into Orders (customer_id) select {cust_id}')
        cmd.execute('select max(ID) from Orders')
        order_id = cmd.fetchone()
    order_id = order_id[0]

    cmd.execute(
        f'select ID from OrderItems where order_id = {order_id} and product_id={product_id}')
    orderItem_id = cmd.fetchone()
    if not orderItem_id:
        cmd.execute(
            f'insert into OrderItems (order_id, product_id) select {order_id}, {product_id}'
        )
    else:
        orderItem_id = orderItem_id[0]
        cmd.execute(
            f'update OrderItems set amount=amount+1 where id = {orderItem_id}'
        )

keep_alive()
bot.polling()
