import copy
import math

import networkx as nx

from database.DAO import DAO


class Model:

    def __init__(self):
        self._products = []
        self._product_idMap = {}
        self._graph = nx.Graph()
        self.years = []
        self.sales_for_quarters = {}
        self.forecast = 0.0
        self.product_id = None
        self.store_id = None
        self.best_sol = []
        self.min_cost = 100000000
        self.max_score = 0
        self.stocks = {}

    def getStores(self):
        return DAO.getStores()

    def getProducts(self, store):
        self._products = DAO.getProducts(store)
        return self._products

    def getEdges(self, store_id):
        return DAO.getEdges(store_id)

    def buildGraph(self, store_id):
        self.store_id = store_id
        for p in self._products:
            self._product_idMap[p.product_id] = p
        self._graph.clear()
        self._graph.add_nodes_from(self._products)
        edges = self.getEdges(store_id)
        for e in edges:
            self._graph.add_edge(self._product_idMap[e[0]], self._product_idMap[e[1]], weight=e[2])

    def forecastByMovingAverage(self, product_id, store_id):
        self.product_id = product_id
        self.store_id = store_id
        self.getSalesForQuarters(product_id, store_id)
        sum = 0
        for s in self.sales_for_quarters.values():
            sum += s
        self.forecast = sum/len(self.sales_for_quarters.values())
        return round(self.forecast, 2)

    def forecastByExponentialSmoothing(self, product_id, store_id, alpha):
        self.product_id = product_id
        self.store_id = store_id
        self.getSalesForQuarters(product_id, store_id)
        self.forecast = list(self.sales_for_quarters.values())[0]
        for d in self.sales_for_quarters.values():
            self.forecast = float(self.forecast) * (1-alpha) + float(d) * alpha
        return round(self.forecast, 2)

    def forecastByExponentialSmoothingwithTrend(self, product_id, store_id, alpha, beta):
        self.product_id = product_id
        self.store_id = store_id
        self.getSalesForQuarters(product_id, store_id)
        self.forecast = list(self.sales_for_quarters.values())[0]
        f = list(self.sales_for_quarters.values())[0]
        trend = 0
        for d in list(self.sales_for_quarters.values())[1:]:
            f_previous = float(f)
            f = float(self.forecast) * (1-alpha) + float(d) * alpha
            trend = (f - f_previous) * beta + trend * (1-beta)
            self.forecast = f+trend
        if self.forecast < 0:
            return 0
        return round(self.forecast, 2)

    def getSalesForQuarters(self, product_id, store_id):
        self.years = DAO.getYears(2018)
        sales = DAO.getSales(product_id, store_id, 2018)
        qt1, qt2, qt3, qt4 = 0, 0, 0, 0
        year = self.years[0]
        i = 0
        for row in sales:
            i += 1
            if int(row[0]) == year:
                if 1 <= int(row[1]) <= 3:
                    qt1 += row[2]
                elif 4 <= int(row[1]) <= 6:
                    qt2 += row[2]
                elif 7 <= int(row[1]) <= 9:
                    qt3 += row[2]
                elif 10 <= int(row[1]) <= 12:
                    qt4 += row[2]
                # if last row of last year --> update
                if i == len(sales):
                    self.sales_for_quarters[f"{year}-{1}"] = qt1
                    self.sales_for_quarters[f"{year}-{2}"] = qt2
                    self.sales_for_quarters[f"{year}-{3}"] = qt3
                    self.sales_for_quarters[f"{year}-{4}"] = qt4
            else:
                self.sales_for_quarters[f"{year}-{1}"] = qt1
                self.sales_for_quarters[f"{year}-{2}"] = qt2
                self.sales_for_quarters[f"{year}-{3}"] = qt3
                self.sales_for_quarters[f"{year}-{4}"] = qt4
                year += 1
                qt1, qt2, qt3, qt4 = 0, 0, 0, 0
                if 1 <= int(row[1]) <= 3:
                    qt1 += row[2]
                elif 4 <= int(row[1]) <= 6:
                    qt2 += row[2]
                elif 7 <= int(row[1]) <= 9:
                    qt3 += row[2]
                elif 10 <= int(row[1]) <= 12:
                    qt4 += row[2]

    def calculateOrderQuantities(self, safety_stock):
        new_sales = math.ceil(self.forecast)
        in_stock = DAO.getStockedQuantity(self.product_id, self.store_id)
        if new_sales + safety_stock > in_stock:
            to_order = new_sales + safety_stock - in_stock
        else:
            to_order = 0
        return to_order

    def getOptimalSubInventory(self, stock_quantity):
        min_stock = round(0.9*stock_quantity)
        max_stock = round(1.1*stock_quantity)
        self.best_sol = []
        self.min_cost = 100000000
        self.max_score = 0
        self.getStocks()
        node_list = list(self._graph.nodes)  # add
        for i, n in enumerate(node_list):  # for n in self._graph.nodes:
            if (self.stocks[f"{self.store_id}-{n.product_id}"] <= max_stock
                    and self.stocks[f"{self.store_id}-{n.product_id}"] != 0):
                partial = [n]
                self.findNext(partial, min_stock, max_stock, i+1)
        return self.best_sol, self.min_cost, self.getStocked(self.best_sol)

    def findNext(self, partial, min_stock, max_stock, start_index=0):
        if min_stock <= self.getStocked(partial) <= max_stock:
            cost = self.getStockCost(partial)
            score = self.getScore(partial)
            if cost < self.min_cost and score > self.max_score:
                self.best_sol = copy.deepcopy(partial)
                self.min_cost = cost
                self.max_score = score
            return

        # pruning
        if self.getStockCost(partial) >= self.min_cost:
            return

        for i in range(start_index, len(self._graph.nodes)):  # for n in self._graph.nodes:
            n = list(self._graph.nodes)[i]  #add
            if (n not in partial
                    and self.getStocked(partial)+self.stocks[f"{self.store_id}-{n.product_id}"] <= max_stock
                    and self.stocks[f"{self.store_id}-{n.product_id}"] > 0):
                partial.append(n)
                self.findNext(partial, min_stock, max_stock, i+1)
                partial.pop()

    def getStocks(self):
        all_stocks = DAO.getAllStocks(self.store_id)
        for r in all_stocks:
            if r[1] in self._product_idMap.keys():
                self.stocks[f"{self.store_id}-{r[1]}"] = r[2]

    def getStocked(self, partial):
        stocked = 0
        for p in partial:
            stocked += self.stocks[f"{self.store_id}-{p.product_id}"]
        return stocked

    def getStockCost(self, partial):
        cost = 0
        for p in partial:
            cost += 0.02 * p.list_price * self.stocks[f"{self.store_id}-{p.product_id}"]
        return cost

    def getScore(self, partial):
        score = 0
        for i in range(len(partial)):
            for j in range(i+1, len(partial)):
                if self._graph.has_edge(partial[i], partial[j]):
                    score += self._graph.get_edge_data(partial[i], partial[j])['weight']
        return score
