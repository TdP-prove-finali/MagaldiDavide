import flet as ft
from flet_core import ButtonStyle


class View(ft.UserControl):

    def __init__(self, page: ft.Page):
        super().__init__()

        self._page = page
        self._page.title = "Thesis Project - MAGALDI DAVIDE"
        self._page.horizontal_alignment = "CENTER"
        self._page.vertical_alignment = "START"
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self.page_container = None
        self._controller = None

        self._title = None
        self.txt_result = None
        self.dd_store = None
        self.dd_algorithm = None
        self.dd_product = None
        self.btn_forecast = None
        self.btn_quantities = None
        self.parameters_row = None
        self.additional_row = None
        self.txt_max_stock = None
        self.btn_optimization = None
        self.txt_listview1 = None
        self.safety_stock = None
        self.alpha = None
        self.beta = None
        self.nav_text = None
        self.current_page = 0
        self.nav_buttons = None

    def load_interface(self):
        self._page.bgcolor = "#D5D5D5"
        self._title = ft.Text(
            "Bicycle Retailer Management Support",
            color="#1E3A8A",
            size=36,
            weight="bold"
        )
        bike_icon = ft.Icon(ft.icons.DIRECTIONS_BIKE, size=40, color="#1E40AF")
        self._page.add(ft.Row([self._title, bike_icon], alignment=ft.MainAxisAlignment.CENTER))
        self._page.add(ft.Divider(thickness=2, color="#1E40AF"))
        self.page_container = ft.Stack(expand=True, controls=[])
        self._page.add(self.page_container)
        self._build_main_page()
        self._build_subinventory_page()
        self.nav_text = ft.Text(
            "To create an optimal sub-inventory go to the next page",
            italic=True,
            color="#1E40AF"
        )
        self._page.add(self.nav_text)
        self.nav_buttons = ft.Row([
            ft.ElevatedButton("Back", on_click=self._prev_page, disabled=True, style=ButtonStyle(color="#1E3A8A")),
            ft.ElevatedButton("Next", on_click=self._next_page, style=ButtonStyle(color="#1E3A8A"))
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        self._page.add(self.nav_buttons)
        self._show_page(0)
        self._page.update()

    # PAGE 1
    def _build_main_page(self):
        self.dd_store = ft.Dropdown(label="Select a store", width=200, on_change=self._controller.buildGraph)
        self._controller.fillDDStore()
        self.dd_algorithm = ft.Dropdown(label="Select the forecasting algorithm", width=300, on_change=self._controller.handleAlgorithm)
        self.dd_product = ft.Dropdown(label="Select the product", width=450)
        dropdown_row = ft.Row([self.dd_store, self.dd_algorithm, self.dd_product],
                              alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        self.parameters_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        self.btn_forecast = ft.ElevatedButton("CALCULATE FORECAST", on_click=self._controller.handleForecast, disabled=True, style=ButtonStyle(color="#1E3A8A"))
        self.btn_quantities = ft.ElevatedButton("CALCULATE ORDER QUANTITIES", on_click=self._controller.handleOrderQuantities, disabled=True, style=ButtonStyle(color="#1E3A8A"))
        buttons_row = ft.Row([self.btn_forecast, self.btn_quantities], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        self.additional_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        self.txt_listview1 = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)
        listview_container = ft.Container(
            content=self.txt_listview1,
            bgcolor="#F7F7F7",
            padding=10,
            border_radius=5,
            height=200,
            width=800
        )

        page1_content = ft.Column([
            dropdown_row,
            self.parameters_row,
            buttons_row,
            self.additional_row,
            listview_container
        ], spacing=20, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page1 = ft.Container(content=page1_content, expand=True, padding=20)
        self.page_container.controls.append(self.page1)

    # PAGE 2
    def _build_subinventory_page(self):
        self.txt_max_stock = ft.TextField(label="Insert the quantity to stock", width=400)
        self.btn_optimization = ft.ElevatedButton("CREATE OPTIMAL SUB-INVENTORY", disabled=True, on_click=self._controller.handleOptimization, style=ButtonStyle(color="#1E3A8A"))
        opt_row = ft.Row([self.txt_max_stock, self.btn_optimization], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        self.txt_result = ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=True)
        result_container = ft.Container(
            content=self.txt_result,
            bgcolor="#F7F7F7",
            padding=10,
            border_radius=5,
            height=300,
            width=800
        )

        page2_content = ft.Column([
            ft.Row([ft.Icon(ft.icons.DIRECTIONS_BIKE, size=24, color="#1E3A8A"),
                    ft.Text("Sub-inventory Creation", size=24, weight="bold", color="#1E3A8A")],
                   alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Divider(thickness=1, color="#CBD5E1"),
            opt_row,
            result_container
        ], spacing=20, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page2 = ft.Container(content=page2_content, expand=True, padding=20)
        self.page_container.controls.append(self.page2)

    # NAVIGATION
    def _show_page(self, page_index):
        for i, p in enumerate(self.page_container.controls):
            p.visible = i == page_index
        self.current_page = page_index

        if page_index == 0:
            self.nav_text.value = "To create an optimal sub-inventory go to the next page"
        else:
            self.nav_text.value = "For demand forecasting go back to the previous page"
        self.nav_text.update()

        self.nav_buttons.controls[0].disabled = (page_index == 0)
        self.nav_buttons.controls[1].disabled = (page_index == len(self.page_container.controls) - 1)
        self._page.update()

    def _next_page(self, e):
        if self.current_page < len(self.page_container.controls) - 1:
            self._show_page(self.current_page + 1)

    def _prev_page(self, e):
        if self.current_page > 0:
            self._show_page(self.current_page - 1)

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()





