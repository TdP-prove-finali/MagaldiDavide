from database.DB_connect import DBConnect
from model.products import Product
from model.stores import Store


class DAO():

    @staticmethod
    def getStores():
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """select * from stores s"""
        cursor.execute(query)

        res = []
        for row in cursor:
            res.append(Store(**row))

        cursor.close()
        cnx.close()
        return res

    @staticmethod
    def getProducts(store):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """select p.* from(select oi.product_id, count(distinct year(o.order_date)) as c from order_items oi 
            join orders o 
            on o.order_id  = oi.order_id 
            where o.store_id = %s and (year(o.order_date) = 2016 or year(o.order_date) = 2017)
            group by product_id) mytab
            join products p 
            on p.product_id = mytab.product_id
            where c = 2"""
        cursor.execute(query, (store, ))

        res = []
        for row in cursor:
            res.append(Product(**row))

        cursor.close()
        cnx.close()
        return res

    @staticmethod
    def getEdges(store_id):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor()
        query = """select pid1, pid2, count(distinct oid1) as weight from ((select oi.order_id as oid1, oi.product_id as pid1 from order_items oi 
                    join orders o 
                    on oi.order_id = o.order_id 
                    where o.store_id = %s and (year(o.order_date) = 2016 or year(o.order_date) = 2017)) tab
                    join (select oi.order_id as oid2, oi.product_id as pid2 from order_items oi 
                    join orders o 
                    on oi.order_id = o.order_id 
                    where o.store_id = %s and (year(o.order_date) = 2016 or year(o.order_date) = 2017)) tab2
                    on tab.oid1 = tab2.oid2 and tab.pid1 < tab2.pid2)
                    where pid1 in (select product_id from(select oi.product_id, count(distinct year(o.order_date)) as c from order_items oi 
                    join orders o 
                    on o.order_id  = oi.order_id 
                    where o.store_id = %s and (year(o.order_date) = 2016 or year(o.order_date) = 2017)
                    group by product_id) mytab
                    where c = 2) and pid2 in (select product_id from(select oi.product_id, count(distinct year(o.order_date)) as c from order_items oi 
                    join orders o 
                    on o.order_id  = oi.order_id 
                    where o.store_id = %s and (year(o.order_date) = 2016 or year(o.order_date) = 2017)
                    group by product_id) mytab
                    where c = 2)
                    group by pid1, pid2
                    order by weight desc"""
        cursor.execute(query, (store_id, store_id, store_id, store_id))

        res = []
        for row in cursor:
            res.append(row)

        cursor.close()
        cnx.close()
        return res

    @staticmethod
    def getYears(current_year):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """select year(order_date) as year from orders o
                    where year(order_date) <> %s
                    group by year(order_date)"""
        cursor.execute(query, (current_year, ))

        res = []
        for row in cursor:
            res.append(int(row['year']))

        cursor.close()
        cnx.close()
        return res

    @staticmethod
    def getSales(product_id, store_id, current_year):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor()
        query = """select year(order_date), month(order_date), sum(oi.quantity) from orders o 
                    join order_items oi 
                    on oi.order_id  = o.order_id 
                    join products p 
                    on p.product_id = oi.product_id 
                    where oi.product_id = %s and store_id = %s and year(order_date) <> %s
                    group by year(order_date), month(order_date), o.store_id, oi.product_id 
                    order by year(order_date), month(order_date) """
        cursor.execute(query, (product_id, store_id, current_year))

        res = []
        for row in cursor:
            res.append(row)

        cursor.close()
        cnx.close()
        return res

    @staticmethod
    def getStockedQuantity(product_id, store_id):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """select quantity from stocks s 
                    where product_id = %s and store_id = %s"""
        cursor.execute(query, (product_id, store_id))

        res = 0
        for row in cursor:
            res = row['quantity']

        cursor.close()
        cnx.close()
        return res

    @staticmethod
    def getAllStocks(store_id):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor()
        query = """select * from stocks s 
                    where store_id = %s"""
        cursor.execute(query, (store_id, ))

        res = []
        for row in cursor:
            res.append(row)

        cursor.close()
        cnx.close()
        return res
