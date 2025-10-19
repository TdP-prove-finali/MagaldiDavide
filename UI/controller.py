from datetime import datetime

import flet as ft


class Controller:

    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._selected_store = None
        self.store_id = None
        self._selected_algorithm = None
        self._selected_product = None
        self._products = []
        self.forecast = 0
        self.safety_stock = None

    def fillDDStore(self):
        stores = self._model.getStores()
        for s in stores:
            self._view.dd_store.options.append(ft.dropdown.Option(s.__str__()))

    def buildGraph(self, e):
        self._selected_store = e.control.value
        self._view.dd_product.value = None
        store_id = int(self._selected_store.split("-")[0])
        self.store_id = store_id
        self._products = self._model.getProducts(store_id)
        if self._selected_algorithm is not None:
            self._view.dd_product.options.clear()
            for p in self._products:
                self._view.dd_product.options.append(ft.dropdown.Option(key=p.product_id, text=p.product_name,
                                                                        data=p, on_click=self.readProduct))
            self._selected_product = self._view.dd_product.value
            if type(self._selected_product) == str:
                self._selected_product = None
            self._view.update_page()
        self._model.buildGraph(store_id)
        self.fillDDAlgorithm()
        self._view.btn_optimization.disabled = False
        self._view.txt_listview1.controls.clear()
        self._view.update_page()

    def fillDDAlgorithm(self):
        self._view.dd_algorithm.options.clear()
        self._view.dd_algorithm.options.extend([ft.dropdown.Option("Moving Average"), ft.dropdown.Option("Exponential Smoothing"),
                                                ft.dropdown.Option("Exponential Smoothing with Trend")])

    def handleAlgorithm(self, e):
        self._selected_algorithm = e.control.value
        self._view.parameters_row.controls.clear()
        if self._selected_algorithm == "Exponential Smoothing":
            self._view.alpha = ft.TextField(label="Alpha (α)", width=150)
            self._view.parameters_row.controls.append(self._view.alpha)
        elif self._selected_algorithm == "Exponential Smoothing with Trend":
            self._view.alpha = ft.TextField(label="Alpha (α)", width=150)
            self._view.beta = ft.TextField(label="Beta (β)", width=150)
            self._view.parameters_row.controls.extend([
                self._view.alpha, self._view.beta])
        self._view.parameters_row.update()
        self._view.dd_product.options.clear()
        for p in self._products:
            self._view.dd_product.options.append(ft.dropdown.Option(key=p.product_id, text=p.product_name,
                                                                    data=p, on_click=self.readProduct))
        self._view.update_page()

    def handleForecast(self, e):
        done = self.doForecast()
        if not done:
            return
        self._view.txt_listview1.controls.clear()
        self._view.txt_listview1.controls.append(ft.Text(f"Store {self._selected_store.__str__()}", size=18, weight='bold', color="#1E3A8A"))
        self._view.txt_listview1.controls.append(ft.Row([ft.Text(f"Forecast for next quarter for the product"),
                                                 ft.Text(f"{self._selected_product.__str__()}", weight='bold'),
                                                 ft.Text("using the algorithm"), ft.Text(f"{self._selected_algorithm}", weight='bold'),
                                                 ft.Text("is:"), ft.Text(f"{self.forecast}", weight='bold')], wrap=True))
        self._view.update_page()

    def doForecast(self):
        store_id = int(self._selected_store.split("-")[0])
        if self._selected_product is None:
            self._view.create_alert("Please, select a product!")
            return False
        product_id = self._selected_product.product_id

        if self._selected_algorithm == "Moving Average":
            self.forecast = self._model.forecastByMovingAverage(product_id, store_id)
            return True

        elif self._selected_algorithm == "Exponential Smoothing":
            # checks on input values
            alpha = self._view.alpha.value
            if alpha == "":
                self._view.create_alert("Please, insert a value for Alpha (α)!")
                return False
            try:
                alpha = float(alpha)
            except ValueError:
                self._view.create_alert("Alpha (α) must be a number!")
                return False
            if alpha < 0 or alpha > 1:
                self._view.create_alert("Alpha (α) value must be between 0 and 1!")
                return False
            self.forecast = self._model.forecastByExponentialSmoothing(product_id, store_id, alpha)
            return True

        elif self._selected_algorithm == "Exponential Smoothing with Trend":
            # checks on input values
            alpha = self._view.alpha.value
            beta = self._view.beta.value
            if alpha == "":
                self._view.create_alert("Please, insert a value for Alpha (α)!")
                return False
            if beta == "":
                self._view.create_alert("Please, insert a value for Beta (β)!")
                return False
            try:
                alpha = float(alpha)
            except ValueError:
                self._view.create_alert("Alpha (α) must be a number!")
                return False
            try:
                beta = float(beta)
            except ValueError:
                self._view.create_alert("Beta (β) must be a number!")
                return False
            if alpha < 0 or alpha > 1:
                self._view.create_alert("Alpha (α) value must be between 0 and 1!")
                return False
            if beta < 0 or beta > 1:
                self._view.create_alert("Beta (β) value must be between 0 and 1!")
                return False
            self.forecast = self._model.forecastByExponentialSmoothingwithTrend(product_id, store_id, alpha, beta)
            return True

    def handleOrderQuantities(self, e):
        if self._view.safety_stock is None:
            self._view.create_alert("Please, insert the desired safety stock in the box down here, then click again")
            self._view.additional_row.controls.clear()
            self._view.safety_stock = ft.TextField(label="Safety Stock", width=150)
            self._view.additional_row.controls.append(self._view.safety_stock)
            self._view.additional_row.update()
            return
        else:
            valid = self.check_input(self._view.safety_stock)
            if not valid:
                return
            done = self.doForecast()
            if not done:
                return
            to_order = self._model.calculateOrderQuantities(self.safety_stock)
            if to_order > 0:
                self._view.txt_listview1.controls.append(ft.Row([ft.Text(f"The quantity of"),
                                                         ft.Text(f"{self._selected_product.__str__()}", weight='bold'),
                                                         ft.Text("to be ordered is:"),
                                                         ft.Text(f"{to_order}", weight='bold')], wrap=True))
            else:
                self._view.txt_listview1.controls.append(ft.Text(f"There is enough product in the warehouse, no orders needed"))
            self._view.update_page()

    def check_input(self, input):
        self.safety_stock = input.value
        if self.safety_stock == "":
            self._view.create_alert("Please, insert the desired safety stock!")
            return False
        try:
            self.safety_stock = float(self.safety_stock)
            if self.safety_stock.is_integer():
                self.safety_stock = int(self.safety_stock)
            else:
                self._view.create_alert("Safety stock value must be an integer!")
                return False
        except ValueError:
            self._view.create_alert("Safety stock value must be an integer number!")
            return False
        if self.safety_stock < 0:
            self._view.create_alert("Safety stock value must be at least 0!")
            return False
        return True

    def handleOptimization(self, e):
        stock_quantity = self._view.txt_max_stock.value
        if stock_quantity == "":
            self._view.create_alert("Please, insert the quantity to stock!")
            return
        try:
            stock_quantity = float(stock_quantity)
        except ValueError:
            self._view.create_alert("The quantity must be a number")
            return
        if stock_quantity <= 0:
            self._view.create_alert("The quantity must be over 0")
            return
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Generating optimal sub-inventory, please wait a moment...", size=16, italic=True))
        self._view.update_page()
        time = datetime.now()
        stock_together, stock_cost, quantity = self._model.getOptimalSubInventory(stock_quantity)
        stocks = self._model.stocks
        self._view.txt_result.controls.clear()
        if quantity != 0:
            self._view.txt_result.controls.append(ft.Text("The products that should be stocked together in the sub-inventory are:", weight='bold'))
            for p in stock_together:
                self._view.txt_result.controls.append(ft.Text(f"{stocks[f'{self.store_id}-{p.product_id}']} units of {p.__str__()}", size=14))
            self._view.txt_result.controls.append(ft.Text(f"The quarterly stock cost for the sub-inventory with {quantity} units will be {round(stock_cost, 2)}€", weight='bold'))
            self._view.txt_result.controls.append(ft.Text(f"Created in {datetime.now()-time}", size=10, italic=True, color="#555555"))
        else:
            self._view.txt_result.controls.append(ft.Text("Unfortunately is not possible to find an optimal sub-inventory with the given quantity. Try again with a bigger quantity",
                                                          color='red'))
        self._view.update_page()

    def readProduct(self, e):
        self._selected_product = e.control.data
        self._view.btn_forecast.disabled = False
        self._view.btn_quantities.disabled = False
        self._view.update_page()
