import sqlite3
from pprint import pprint


def createDB():
    dropDB()

    cmd.execute('''
    create table Customers (
        ID      integer         not null    primary key,
        name    varchar(32),
        address varchar(32)
    )
    ''')

    cmd.execute('''
    create table Orders (
        ID          integer     not null    primary key autoincrement,
        customer_id int         not null,
        status      varchar(10) default 'stash',   

        foreign key (customer_id) references Customers (ID)
    )
    ''')

    cmd.execute('''
    create table OrderItems (
        ID          integer not null    primary key autoincrement,
        order_id    int     not null,
        product_id  int     not null,
        amount      int     default 1,

        foreign key (order_id) references Orders (ID)
        foreign key (product_id) references Products (ID)
    )
    ''')

    cmd.execute('''
    create table Products(
        ID      integer     not null    primary key autoincrement,
        brand   varchar(32) not null,
        name    varchar(32) not null,
        taste   varchar(32) not null,
        price   int not null default 200,
        description varchar(32) default 'none'
    )
    ''')


def dropDB():
    cmd.execute('''PRAGMA foreign_keys=OFF''')
    cmd.execute('drop table if exists Customers')
    cmd.execute('drop table if exists Orders')
    cmd.execute('drop table if exists OrderItems')
    cmd.execute('drop table if exists Products')
    cmd.execute('''PRAGMA foreign_keys=ON''')


def deleteDB():
    dropDB()
    createDB()


def showDB():
    cmd.execute('''
        SELECT
            *
        FROM
            Customers ''')
    pprint(cmd.fetchall())
    cmd.execute('''
        SELECT
            *
        FROM
            Orders ''')
    pprint(cmd.fetchall())
    cmd.execute('''
        SELECT
            *
        FROM
            OrderItems ''')
    pprint(cmd.fetchall())
    cmd.execute('''
        SELECT
            *
        FROM
            Products ''')
    pprint(cmd.fetchall())


def insertProducts():
    cmd.execute('''
    insert into Products (brand, taste, name)
    select 'HQD', 'Банан',            'Banana'
    union all 
    select 'HQD', 'Ананас',           'Pineapple'
    union all
    select 'HQD', 'Личи и Мята',      'LycheeMint'
    union all
    select 'HQD', 'Манго и Гуава',    'MangoGuava'
    union all
    select 'HQD', 'Энергетик',        'Energetic'
    union all
    select 'HQD', 'Клубника',         'Strawberry'
    union all
    select 'HQD', 'Черника',          'Blueberry'
    union all
    select 'HQD', 'Черная Смородина', 'BlackCurrant'
    union all
    select 'HQD', 'Черника и Малина', 'BlueberryRaspberry'
    ''')


def recreate():
    dropDB()
    createDB()
    insertProducts()


def korzina():
    cmd.execute('''
    select c.id, p.taste, o.amount
    FROM customers as c, products as p, orderItems as o
    WHERE 
    (
        o.product_id = p.id
    )
    AND
    (
        o.order_id = (
            select id from orders where customer_id = c.id
        )
    )
    ''')
    data = cmd.fetchall()
    print('{:>10s}'.format('ID Клиента'), end='')
    print('{:>20s}'.format('Вкус'), end='')
    print('{:>10s}'.format('Кол-во'))
    print('-'*40)
    for order in data:
        print('{:10d}'.format(order[0]), end='')
        print('{:>20s}'.format(order[1]), end='')
        print('{:10d}'.format(order[2]))


conn = sqlite3.connect('VapesDB', check_same_thread=False)
cmd = conn.cursor()

while(True):
    inp = input('>').lower()
    if inp == 'drop':
        dropDB()
    if inp == 'new':
        recreate()
        conn.commit()
    if inp == 'show':
        korzina()
