"""
Окно с результатами расчета.
Содержит таблицы с рассчитанными значениями и график характеристики.
"""

from tkinter import *
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config.constants import AppStyles


class ResultsWindow:
    """
    Окно для отображения результатов расчета.
    Управляет отображением таблиц и графика.
    """

    def __init__(self, parent, controller):
        """
        Инициализация окна результатов.

        Args:
            parent: Родительское окно
            controller: Контроллер приложения
        """
        self.parent = parent
        self.controller = controller
        self.window = None
        self.scrollable_frame = None

    def show(self, params, device_type, arbitrary_point=None):
        """
        Отображение окна с результатами.

        Args:
            params: Параметры для расчета
            device_type: Тип устройства
            arbitrary_point: Произвольная точка (I_brake, I_diff)
        """
        self._create_window()
        self._display_results(params, device_type, arbitrary_point)

    def _create_window(self):
        """Создание окна результатов"""
        self.window = Toplevel(self.parent)
        self.window.title("Результаты расчета характеристик защиты")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width - 100}x{screen_height - 100}+50+50")
        self.window.state('zoomed')
        self.window.configure(bg=AppStyles.LIGHT_BG)

        self.window.protocol("WM_DELETE_WINDOW", self._close)
        self.window.bind('<Escape>', lambda e: self._close())

        # Создание прокручиваемого контейнера
        main_container = ttk.Frame(self.window)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = Canvas(main_container, highlightthickness=0, bg=AppStyles.LIGHT_BG)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._bind_mousewheel(canvas)

    def _bind_mousewheel(self, canvas):
        """Привязка обработчика колеса мыши"""

        def on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")

        self.window.bind("<MouseWheel>", on_mousewheel)
        self.window.bind("<Button-4>", on_mousewheel)
        self.window.bind("<Button-5>", on_mousewheel)

    def _display_results(self, params, device_type, arbitrary_point):
        """Отображение результатов"""
        currents = self.controller.calculate_currents_full(params, device_type)

        # Получаем 6 значений из get_break_points
        I_brake1, I_brake2, y1, y2, k1, k2 = self.controller.get_break_points(params, device_type)

        # Создание контейнера для таблиц и графика
        container = ttk.Frame(self.scrollable_frame)
        container.pack(fill="both", expand=True)

        # Левая панель - таблицы
        left_panel = ttk.Frame(container)
        left_panel.pack(side="left", fill="both", expand=True)

        self._create_table1(params, currents, device_type, left_panel)
        self._create_table2(I_brake1, I_brake2, y1, y2, left_panel)
        self._create_table3(k1, k2, left_panel)  # используем полученные k1, k2
        self._create_table4(params, currents, device_type, arbitrary_point, left_panel)

        # Правая панель - график
        right_panel = ttk.Frame(container)
        right_panel.pack(side="right", fill="both", expand=True, padx=10)

        self._create_plot(right_panel, params, device_type, I_brake1, y1, I_brake2, y2, k1, k2, arbitrary_point)

    def _create_table1(self, params, currents, device_type, parent):
        """Создание таблицы с основными параметрами"""
        frame = ttk.LabelFrame(parent, text="1. Основные параметры", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        tree = ttk.Treeview(frame, columns=("Parameter", "HV Side", "LV Side"), show="headings", height=11)

        tree.column("Parameter", width=500, anchor="w")
        tree.column("HV Side", width=200, anchor="center")
        tree.column("LV Side", width=200, anchor="center")

        tree.heading("Parameter", text="Параметр")
        tree.heading("HV Side", text="Сторона ВН")
        tree.heading("LV Side", text="Сторона НН")

        tree.tag_configure('oddrow', background='white')
        tree.tag_configure('evenrow', background='#f8f9fa')

        data = [
            ("Номинальный ток, А", currents['I_nom_hv'], currents['I_nom_lv']),
            ("Коэффициент ТТ (ВН/НН)",
             f"{params['CT_hv_perv']}/{params['CT_hv_sec']}",
             f"{params['CT_lv_perv']}/{params['CT_lv_sec']}"),
            ("Вторичный ток при номинальном первичном токе, А", currents['I_sec_hv'], currents['I_sec_lv']),
            ("Вторичный ток РЕТОМ-61 в одно плечо (ВН), А", currents['Id_hv'], "-"),
            ("Вторичный ток РЕТОМ-61 в одно плечо (НН), А", "-", currents['Id_lv']),
        ]

        data.extend([
            ("Вторичный ток РЕТОМ-61 (т.1) (режим работы ДЗТ), А", currents['retom_hv1'], currents['retom_lv1']),
            ("Вторичный ток РЕТОМ-61 (т.2) (режим работы ДЗТ), А", currents['retom_hv2'], currents['retom_lv2']),
        ])

        for i, row_data in enumerate(data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=row_data, tags=(tag,))

        tree.pack(fill="both", expand=True)

    def _create_table2(self, I_brake1, I_brake2, y1, y2, parent):
        """Создание таблицы с токами характеристик"""
        frame = ttk.LabelFrame(parent, text="2. Токи характеристик", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        tree = ttk.Treeview(frame, columns=("Parameter", "HV Side", "LV Side"), show="headings", height=3)

        tree.column("Parameter", width=500, anchor="w")
        tree.column("HV Side", width=200, anchor="center")
        tree.column("LV Side", width=200, anchor="center")

        tree.heading("Parameter", text="Параметр")
        tree.heading("HV Side", text="Тормозной ток")
        tree.heading("LV Side", text="Дифференциальный ток")

        tree.tag_configure('oddrow', background='white')
        tree.tag_configure('evenrow', background='#f8f9fa')

        data = [
            ("Ток в т.1, о.е (I ном)", I_brake1, y1),
            ("Ток в т.2, о.е (I ном)", f"{I_brake2:.2f}", f"{y2:.2f}"),
        ]

        for i, row_data in enumerate(data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=row_data, tags=(tag,))

        tree.pack(fill="both", expand=True)

    def _create_table3(self, k1, k2, parent):
        """Создание таблицы с наклонами характеристик"""
        frame = ttk.LabelFrame(parent, text="3. Наклоны характеристик", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        tree = ttk.Treeview(frame, columns=("Parameter", "HV Side", "LV Side"), show="headings", height=2)

        tree.column("Parameter", width=500, anchor="w")
        tree.column("HV Side", width=200, anchor="center")
        tree.column("LV Side", width=200, anchor="center")

        tree.heading("Parameter", text="Параметр")
        tree.heading("HV Side", text="Наклон в (tg φ)")
        tree.heading("LV Side", text="Наклон в (°)")

        tree.tag_configure('oddrow', background='white')
        tree.tag_configure('evenrow', background='#f8f9fa')

        # Используем уже преобразованные k1 и k2
        data = [
            ("Наклон 1-й зоны (k1)", f"{k1:.3f}",
             f"{np.degrees(np.arctan(k1)):.2f}°"),
            ("Наклон 2-й зоны (k2)", f"{k2:.3f}",
             f"{np.degrees(np.arctan(k2)):.2f}°"),
        ]

        for i, row_data in enumerate(data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=row_data, tags=(tag,))

        tree.pack(fill="both", expand=True)

    def _create_table4(self, params, currents, device_type, arbitrary_point, parent):
        """Создание таблицы с параметрами блокировок"""
        frame = ttk.LabelFrame(parent, text="4. Блокировки", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        tree = ttk.Treeview(frame, columns=("Parameter", "HV Side", "LV Side"), show="headings", height=4)

        tree.column("Parameter", width=500, anchor="w")
        tree.column("HV Side", width=200, anchor="center")
        tree.column("LV Side", width=200, anchor="center")

        tree.heading("Parameter", text="Параметр")
        tree.heading("HV Side", text="Ток блокировки, А")
        tree.heading("LV Side", text="Уставка, %")

        tree.tag_configure('oddrow', background='white')
        tree.tag_configure('evenrow', background='#f8f9fa')

        # Получаем данные блокировок от конкретного устройства
        data = self.controller.get_blocking_currents(params, device_type, arbitrary_point)

        for i, row_data in enumerate(data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=row_data, tags=(tag,))

        tree.pack(fill="both", expand=True)

    def _create_plot(self, parent, params, device_type, x1, y1, x2, y2, k1, k2, arbitrary_point):
        """Создание графика тормозной характеристики"""
        plot_frame = ttk.LabelFrame(parent, text="Тормозная характеристика", padding=5)
        plot_frame.pack(fill="both", expand=True, padx=5, pady=5)

        fig = plt.figure(figsize=(9, 9), dpi=100, facecolor='white')
        fig.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.9)

        ax = fig.add_subplot(111, facecolor='white')

        # Построение характеристики
        I_brake = np.linspace(0, params['zona_x'] * x2, 500)
        current_characteristic = self.controller.calculate_characteristic_full(I_brake, params, device_type)

        # Определяем название устройства
        if device_type == "MR_801":
            device_name = "МР-801"
        elif "RET_521" in device_type:
            device_name = "RET-521"
        elif "RET_670" in device_type:
            device_name = "RET-670"
        else:
            device_name = device_type

        line, = ax.plot(I_brake, current_characteristic, 'b-', linewidth=3,
                        label=f'Характеристика {device_name}')

        # Добавление линий для точек излома
        ax.plot([x1, x1], [0, y1], 'k--', alpha=1, linewidth=1.5)
        ax.plot([0, x1], [y1, y1], 'k--', alpha=1, linewidth=1.5)
        ax.plot([x2, x2], [0, y2], 'k--', alpha=1, linewidth=1.5)
        ax.plot([0, x2], [y2, y2], 'k--', alpha=1, linewidth=1.5)

        # Маркеры точек излома
        ax.plot(x1, y1, 'ro', markersize=8, label=f'$I_{{\\text{{d1}}}}$ = {y1:.2f}')
        ax.plot(x2, y2, 'ro', markersize=8, label=f'$I_{{\\text{{d2}}}}$ = {y2:.2f}')

        # Подписи точек
        label_style = {'color': 'black', 'fontsize': 10, 'bbox': dict(fc='white', alpha=0, edgecolor='none')}
        ax.text(x2 * 0.01, y1, f'$I_{{\\text{{d1}}}}$ = {y1:.2f}', **label_style, ha='left', va='bottom')
        ax.text(x2 * 0.01, y2, f'$I_{{\\text{{d2}}}}$ = {y2:.2f}', **label_style, ha='left', va='bottom')
        ax.text(x1 + x2 * 0.01, 0, f'$I_{{\\text{{t1}}}}$ = {x1:.2f}', **label_style, ha='left', va='bottom')
        ax.text(x2 * 1.01, 0, f'$I_{{\\text{{t2}}}}$ = {x2:.2f}', **label_style, ha='left', va='bottom')

        # Заливка зон
        ax.fill_between(I_brake, current_characteristic,
                        params['zona_y'] * y2,
                        color='red', alpha=0.15, label='Зона срабатывания')
        ax.fill_between(I_brake, 0, current_characteristic,
                        color='green', alpha=0.15, label='Зона блокировки')

        # Подписи наклонов - используем уже преобразованные k1 и k2
        k1_text = f'k1 = {k1:.3f}\nα1 = {np.degrees(np.arctan(k1)):.1f}°'
        k2_text = f'k2 = {k2:.3f}\nα2 = {np.degrees(np.arctan(k2)):.1f}°'

        ax.text(x1 - x2 * 0.02, y1 + y2 * 0.1 * (params['zona_y'] / 2.5), k1_text,
                bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.8, ec='black'),
                fontsize=10, ha='right', va='bottom')
        ax.text(x2 - x2 * 0.02, y2 + 0.1 * y2 * (params['zona_y'] / 2.5), k2_text,
                bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.8, ec='black'),
                fontsize=10, ha='right', va='bottom')

        # Добавление расчетной точки
        if arbitrary_point:
            I_brake_point = arbitrary_point['I_brake']
            I_diff_point = arbitrary_point['I_diff']
            ax.scatter(I_brake_point, I_diff_point, color='red', s=100, zorder=5,
                       label=f'Расчетная точка ({I_brake_point:.2f}, {I_diff_point:.2f})')
            ax.plot([I_brake_point, I_brake_point], [0, I_diff_point], 'k--', alpha=1, linewidth=1.5)
            ax.plot([0, I_brake_point], [I_diff_point, I_diff_point], 'k--', alpha=1, linewidth=1.5)

            ax.text(I_brake_point * 1.01, 0, f'$I_{{\\text{{t}}}}$ = {I_brake_point:.2f}', **label_style, ha='left',
                    va='bottom')
            ax.text(x2 * 0.01, I_diff_point, f'$I_{{\\text{{d}}}}$ = {I_diff_point:.2f}', **label_style, ha='left',
                    va='bottom')

        # Настройка внешнего вида
        ax.set_title(f'Тормозная характеристика {device_name}', fontsize=12, pad=10)
        ax.set_xlabel(r'Ток торможения, $I_{\text{торм}}$ [$I_{\text{ном}}$]', fontsize=11, labelpad=5)
        ax.set_ylabel(r'Ток срабатывания, $I_{\text{дифф}}$ [$I_{\text{ном}}$]', fontsize=11, labelpad=5)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='upper left', fontsize=10, framealpha=1)
        ax.set_xlim(0, params['zona_x'] * x2)
        ax.set_ylim(0, params['zona_y'] * y2)

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)

    def _close(self):
        """Закрытие окна результатов"""
        if self.window:
            plt.close('all')
            self.window.destroy()
            self.window = None