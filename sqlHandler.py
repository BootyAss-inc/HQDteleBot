import pprint
import sqlite3
import json
from settings import settings as SETS


class SQLHandler():
    def __init__(self, dbName):
        self.con = sqlite3.connect(dbName, check_same_thread=False)
        self.cur = self.con.cursor()

    def recreateTables(self):
        self.dropTables()
        self.createTables()
        self.insertProducts()

    def dropTables(self):
        self.dropOrderedItems()
        self.dropStashedItems()
        self.dropOrders()
        self.dropClients()
        self.dropProducts()

    def dropClients(self):
        self.execute('drop table if exists Clients')

    def dropOrders(self):
        self.execute('drop table if exists Orders')

    def dropProducts(self):
        self.execute('drop table if exists Products')

    def dropOrderedItems(self):
        self.execute('drop table if exists OrderedItems')

    def dropStashedItems(self):
        self.execute('drop table if exists StashedItems')

    def createTables(self):
        self.createClients()
        self.createOrders()
        self.createProducts()
        self.createStashedItems()
        self.createOrderedItems()

    def createClients(self):
        self.execute('''
        create table Clients (
            id          int         not null	primary key,
            name        varchar(30) not null,
            username    varchar(30) not null,
            address     varchar(30) null,
            phone       varchar(30) null
        )
        ''')

    def createOrders(self):
        # status: Собирается, Собран, Доставляется, Доставлен
        self.execute('''
        create table Orders (
            id          integer	    not null    primary key	autoincrement,
            client_id   int		    not null,
            paid        varchar     null        default 'n',
            status      varchar(30) null,
            foreign key (client_id) references Clients(id)
        )
        ''')

    def createOrderedItems(self):
        self.execute('''
        create table Products (
            id          integer		not null    primary key	autoincrement,
            name 		varchar(30)	not null,
            taste 		varchar(30)	not null,
            brand 		varchar(30)	not null,
            amount      int 		not null
        )
        ''')

    def createStashedItems(self):
        self.execute('''
        create table OrderedItems (
            id          integer	not null    primary key	autoincrement,
            order_id   	int		not null,
			product_id  int		not null,
            amount      int 	not null,
            foreign key (order_id) references Orders(id),
			foreign key (product_id) references Products(id)
        )
        ''')

    def createProducts(self):
        self.execute('''
        create table StashedItems (
            id          integer	not null    primary key	autoincrement,
            client_id   int		not null,
			product_id  int		not null,
            amount      int 	not null,
            foreign key (client_id) references Clients(id),
			foreign key (product_id) references Products(id)
        )
        ''')

    def insertProducts(self):
        with open('generate.json', encoding='utf-8') as jsonFile:
            data = json.load(jsonFile)

        for p in data['products']:
            print(p)
            name, taste, brand, amount = p['name'], p['taste'], p['brand'], p['amount']
            self.execute(
                f'insert into Products (name, taste, brand, amount) values (\'{name}\', \'{taste}\', \'{brand}\', {amount})')

    def insertToStash(self, call):
        chat = call.message.chat

        self.execute(f'select id from Clients where id = {chat.id}')
        if not self.cur.fetchone():
            self.execute(
                f'insert into Clients (id, name, username) values ({chat.id}, \'{chat.first_name}\', \'{chat.username}\')')

        self.execute(f'select id from Products where name = \'{call.data}\'')
        product_id = self.cur.fetchone()[0]

        self.execute(
            f'select id from StashedItems where product_id = {product_id}')
        item_id = self.cur.fetchone()
        if not item_id:
            self.execute(
                f'insert into StashedItems (client_id, product_id, amount) values ({chat.id}, {product_id}, 1)')
        else:
            self.execute(
                f'update StashedItems set amount = amount + 1 where id = {item_id[0]}')

    def commit(self):
        self.con.commit()

    def getAllClients(self):
        self.execute('select * from Clients')
        return self.cur.fetchall()

    def getAllTasteName(self):
        self.execute('select taste, name from Products')
        return self.cur.fetchall()

    def getStash(self, id):
        self.execute(f'''
        select 
            p.taste
           ,s.amount
        from StashedItems s
        inner join Products p
        on s.product_id = p.id
        where s.client_id = {id}
        ''')
        return self.cur.fetchall()

    def clearStash(self, id):
        self.execute(f'delete from StashedItems where client_id = {id}')

    def addOrder(self, data, chat):
        self.execute(f'''
        select id 
        from Orders 
        where   client_id = {chat.id}
            and paid = 'n'
            and status = \'Собирается\'
        ''')
        order_id = self.cur.fetchone()
        if not order_id:
            self.execute(
                f'insert into Orders (client_id, status) values({chat.id}, \'Собирается\')')
            self.execute('select max(id) from Orders')
            order_id = self.cur.fetchone()

        for item in data:
            print(item[2])
            print(item[3])
            self.execute(
                f'insert into OrderedItems (order_id, product_id, amount) values ({order_id[0]}, {item[2]}, {item[3]})')

    def checkout(self, chat):
        self.execute(f'select * from StashedItems where client_id = {chat.id}')
        self.addOrder(self.cur.fetchall(), chat)

        self.execute(f'delete from StashedItems where client_id = {chat.id}')

    def execute(self, cmd):
        self.cur.execute(cmd)

    def close(self):
        self.con.close()


def main():
    handle = SQLHandler(SETS['db'])

    while True:
        try:
            cmd = input().lower()

            if cmd == 'create':
                handle.createTables()

            elif cmd == 'drop':
                handle.dropTables()

            elif cmd == 'products':
                handle.insertProducts()
                handle.commit()

            elif cmd == 'recreate':
                handle.recreateTables()

        except EOFError as E:   # ctrl+Z for quit
            handle.close()
            exit()

        else:
            handle.commit()


if __name__ == '__main__':
    main()
