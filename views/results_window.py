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
from utils.file_handlers import ResultsFileHandler


class ResultsWindow:
    """
    Окно для отображения результатов расчета.
    Управляет отображением таблиц и графика.
    """

    def __init__(self, parent, controller):
        """
        Инициализация окна результатов.
        """
        self.parent = parent
        self.controller = controller
        self.window = None
        self.scrollable_frame = None
        self.figure = None
        self.current_data = {}

    def show(self, params, device_type, arbitrary_point=None):
        """
        Отображение окна с результатами.
        """
        self._create_window()
        self._create_menu()
        self._display_results(params, device_type, arbitrary_point)

    def _create_window(self):
        """Создание окна результатов"""
        self.window = Toplevel(self.parent)
        self.window.title("Результаты расчета характеристик защиты")

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width - 100}x{screen_height - 100}+50+50")
        self.window.state('zoomed')
        self.window.configure(bg=AppStyles.BACKGROUND)

        self.window.protocol("WM_DELETE_WINDOW", self._close)
        self.window.bind('<Escape>', lambda e: self._close())

        # Создание прокручиваемого контейнера
        main_container = ttk.Frame(self.window)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = Canvas(main_container, highlightthickness=0, bg=AppStyles.BACKGROUND)
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

    def _create_menu(self):
        """Создание меню в окне результатов"""
        menubar = Menu(self.window)
        self.window.config(menu=menubar)

        # Меню "Файл"
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)

        file_menu.add_command(label="Сохранить результаты в файл",
                             command=self._on_save_results,
                             accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить график",
                             command=self._on_save_figure,
                             accelerator="Ctrl+G")
        file_menu.add_separator()
        file_menu.add_command(label="Закрыть",
                             command=self._close,
                             accelerator="Esc")

        # Меню "Вид"
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)

        view_menu.add_command(label="Обновить",
                             command=self._on_refresh)

        # Привязка горячих клавиш
        self.window.bind('<Control-s>', lambda e: self._on_save_results())
        self.window.bind('<Control-g>', lambda e: self._on_save_figure())
        self.window.bind('<Control-r>', lambda e: self._on_refresh())

    def _on_save_results(self):
        """Сохранение результатов в файл"""
        if self.current_data:
            ResultsFileHandler.save_results_to_file(
                self.current_data['params'],
                self.current_data['currents'],
                self.current_data['break_points'],
                self.current_data['blocking_data'],
                self.current_data['device_type'],
                self.current_data.get('arbitrary_point')
            )

    def _on_save_figure(self):
        """Сохранение графика в файл"""
        if self.figure:
            ResultsFileHandler.save_figure(self.figure)

    def _on_refresh(self):
        """Обновление окна результатов"""
        if self.current_data:
            self.update_results(
                self.current_data['params'],
                self.current_data['device_type'],
                self.current_data.get('arbitrary_point')
            )

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

    def _create_table(self, parent, title, columns, data, column_widths=None):
        """Универсальный метод для создания таблицы"""
        frame = ttk.LabelFrame(parent, text=title, padding=0)
        frame.pack(fill="x", padx=0, pady=0)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=len(data) + 1)

        # Настройка колонок
        if column_widths:
            for i, col in enumerate(columns):
                width = column_widths[i] if i < len(column_widths) else 100
                tree.column(col, width=width, anchor="w" if i == 0 else "center")
        else:
            default_width = 200
            for col in columns:
                tree.column(col, width=default_width, anchor="center")
            tree.column(columns[0], width=500, anchor="w")

        for col in columns:
            tree.heading(col, text=col)

        tree.tag_configure('oddrow', background='white')
        tree.tag_configure('evenrow', background='#f8f9fa')

        for i, row_data in enumerate(data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=row_data, tags=(tag,))

        tree.pack(fill="both", expand=True)

    def _display_results(self, params, device_type, arbitrary_point):
        """Отображение результатов"""
        # Сохраняем текущие данные

        if hasattr(self, 'scrollable_frame') and self.scrollable_frame:
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

        self.current_data = {
            'params': params,
            'device_type': device_type,
            'arbitrary_point': arbitrary_point
        }

        currents = self.controller.calculate_currents_full(params, device_type)
        self.current_data['currents'] = currents
        arbitrary_currents = self.controller.calculate_arbitrary_point_full(
            arbitrary_point['I_brake'],
            params,
            device_type
        )
        currents['retom_hv_arb'] = arbitrary_currents['retom_hv_arb']
        currents['retom_lv_arb'] = arbitrary_currents['retom_lv_arb']
        currents['retom_skvoz_arb_hv'] = arbitrary_currents['retom_skvoz_arb_hv']
        currents['retom_skvoz_arb_lv'] = arbitrary_currents['retom_skvoz_arb_lv']


        # Получаем точки излома
        I_brake1, I_brake2, y1, y2, k1, k2 = self.controller.get_break_points(params, device_type)
        self.current_data['break_points'] = (I_brake1, I_brake2, y1, y2, k1, k2)

        # Получаем данные блокировок
        blocking_data = self.controller.get_blocking_currents(params, device_type, arbitrary_point)
        self.current_data['blocking_data'] = blocking_data

        # Создание контейнера для таблиц и графика
        container = ttk.Frame(self.scrollable_frame)
        container.pack(fill="both", expand=True)

        # Левая панель - таблицы (устанавливаем фиксированную ширину)
        left_panel = ttk.Frame(container)
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        # Правая панель - график (занимает все оставшееся пространство)
        right_panel = ttk.Frame(container)
        right_panel.pack(side="right", fill="both", expand=True, padx=(0, 0))

        # Создание таблиц
        self._create_table1(left_panel, params, currents, device_type)
        self._create_table2(left_panel, I_brake1, I_brake2, y1, y2, arbitrary_point)
        self._create_table3(left_panel, k1, k2)
        self._create_table4(left_panel, blocking_data)

        # Создание графика
        self._create_plot(right_panel, params, device_type, I_brake1, y1, I_brake2, y2, k1, k2, arbitrary_point)

    def _create_table1(self, parent, params, currents, device_type):
        """Создание таблицы с основными параметрами"""
        data = [
            ("Номинальный ток, А", f"{currents['I_nom_hv']:.2f}", f"{currents['I_nom_lv']:.2f}"),
            ("Коэффициент ТТ (ВН/НН)",
             f"{params['CT_hv_perv']}/{params['CT_hv_sec']}",
             f"{params['CT_lv_perv']}/{params['CT_lv_sec']}"),
            ("Вторичный ток при номинальном первичном токе, А", f"{currents['I_sec_hv']:.2f}",
             f"{currents['I_sec_lv']:.2f}"),
            ("Вторичный ток РЕТОМ-61 в одно плечо (ВН), А", f"{currents['Id_hv']:.2f}", "0.00"),
            ("Вторичный ток РЕТОМ-61 в одно плечо (НН), А", "0.00", f"{currents['Id_lv']:.2f}"),
            ("Вторичный ток РЕТОМ-61 (т.1) (режим работы ДЗТ), А", currents['retom_hv1'], currents['retom_lv1']),
            ("Вторичный ток РЕТОМ-61 (т.1) (режим сквозного КЗ), А", currents['retom_skvoz_hv1'],
             currents['retom_skvoz_lv1']),
            ("Вторичный ток РЕТОМ-61 (т.2) (режим работы ДЗТ), А", currents['retom_hv2'], currents['retom_lv2']),
            ("Вторичный ток РЕТОМ-61 (т.2) (режим сквозного КЗ), А", currents['retom_skvoz_hv2'],
             currents['retom_skvoz_lv2']),
            ("Вторичный ток РЕТОМ-61 в произвольной точке (режим работы ДЗТ), А", currents['retom_hv_arb'],
             currents['retom_lv_arb']),
            ("Вторичный ток РЕТОМ-61 в произвольной точке (сквозное КЗ), А", currents['retom_skvoz_arb_hv'], currents['retom_skvoz_arb_lv'])
        ]

        self._create_table(
            parent,
            "1. Основные параметры",
            ("Параметры", "Сторона ВН", "Сторона НН"),
            data,
            [550, 125, 125]
        )

    def _create_table2(self, parent, I_brake1, I_brake2, y1, y2, arbitrary_point=None):
        """Создание таблицы с токами характеристик"""
        data = [
            ("Ток в т.1, о.е (I ном)", f"{I_brake1:.2f}", f"{y1:.2f}"),
            ("Ток в т.2, о.е (I ном)", f"{I_brake2:.2f}", f"{y2:.2f}"),
        ]

        # Добавляем произвольную точку, если она есть
        if arbitrary_point:
            data.append(("Ток в произвольной точке, о.е (I ном)",
                         f"{arbitrary_point['I_brake']:.2f}",
                         f"{arbitrary_point['I_diff']:.2f}"))

        self._create_table(
            parent,
            "2. Токи характеристик",
            ("Параметры", "Iт", "Id"),
            data,
            [450, 170, 170]
        )

    def _create_table3(self, parent, k1, k2):
        """Создание таблицы с наклонами характеристик"""
        data = [
            ("Наклон 1-й зоны (k1)", f"{k1:.2f}", f"{np.degrees(np.arctan(k1)):.2f}°"),
            ("Наклон 2-й зоны (k2)", f"{k2:.2f}", f"{np.degrees(np.arctan(k2)):.2f}°"),
        ]

        self._create_table(
            parent,
            "3. Наклоны характеристик",
            ("Параметры", "tg (φ)", "Градусы, °"),
            data,
            [450, 170, 170]
        )

    def _create_table4(self, parent, blocking_data):
        """Создание таблицы с параметрами блокировок"""
        self._create_table(
            parent,
            "4. Блокировки",
            ("Параметры", "Ток в РЕТОМ-61, А", "Проценты от I1, %"),
            blocking_data,
            [450, 170, 170]
        )

    def _create_plot(self, parent, params, device_type, x1, y1, x2, y2, k1, k2, arbitrary_point):
        """Создание графика тормозной характеристики"""
        plot_frame = ttk.LabelFrame(parent, text="Тормозная характеристика", padding=5)
        plot_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Создаем фигуру с увеличенной шириной
        fig = plt.figure(figsize=(10, 9), dpi=100, facecolor='white')
        fig.subplots_adjust(left=0.08, right=0.98, bottom=0.1, top=0.9)

        self.figure = fig  # Сохраняем ссылку для сохранения

        ax = fig.add_subplot(111, facecolor='white')

        # Построение характеристики
        # Определяем максимальные значения для осей с учетом произвольной точки
        max_x = params['zona_x'] * x2
        max_y = params['zona_y'] * y2

        # Если есть произвольная точка, расширяем пределы
        if arbitrary_point:
            I_brake_point = arbitrary_point['I_brake']
            I_diff_point = arbitrary_point['I_diff']

            # Добавляем запас 10% от значения точки
            max_x = max(max_x, I_brake_point * 1.1)
            max_y = max(max_y, I_diff_point * 1.1)

            # Увеличиваем количество точек для построения характеристики
            I_brake = np.linspace(0, max_x, 500)
        else:
            I_brake = np.linspace(0, max_x, 500)

        current_characteristic = self.controller.calculate_characteristic_full(I_brake, params, device_type)

        # Определяем название устройства
        device_names = {
            "MR_801": "МР-801",
            "RET_521_HV": "RET-521 (ВН)",
            "RET_521_LV": "RET-521 (НН)",
            "RET_670_HV": "RET-670 (ВН)",
            "RET_670_LV": "RET-670 (НН)",
            "SPAC810T_HV": "SPAC810-T (ВН)",
            "SPAC810T_LV": "SPAC810-T (НН)"
        }
        device_name = device_names.get(device_type, device_type)

        line, = ax.plot(I_brake, current_characteristic, 'b-', linewidth=3,
                        label=f'Характеристика {device_name}')

        # Добавление линий для точек излома
        self._add_break_lines(ax, x1, y1, x2, y2)

        # Маркеры точек излома
        ax.plot(x1, y1, 'ro', markersize=8, label=f'$I_{{\\text{{d1}}}}$ = {y1:.2f}')
        ax.plot(x2, y2, 'ro', markersize=8, label=f'$I_{{\\text{{d2}}}}$ = {y2:.2f}')

        # Подписи точек
        label_style = {'color': 'black', 'fontsize': 10, 'bbox': dict(fc='white', alpha=0, edgecolor='none')}
        self._add_point_labels(ax, x1, y1, x2, y2, label_style)

        # Заливка зон (только в пределах построенной характеристики)
        ax.fill_between(I_brake, current_characteristic,
                        max_y,
                        where=(I_brake <= max_x),
                        color='red', alpha=0.15, label='Зона срабатывания')
        ax.fill_between(I_brake, 0, current_characteristic,
                        where=(I_brake <= max_x),
                        color='green', alpha=0.15, label='Зона блокировки')

        # Подписи наклонов
        self._add_slope_labels(ax, x1, y1, x2, y2, k1, k2, params)

        # Добавление расчетной точки
        if arbitrary_point:
            self._add_arbitrary_point(ax, arbitrary_point, label_style, x2, max_x)

        # Настройка внешнего вида
        ax.set_title(f'Тормозная характеристика {device_name}', fontsize=12, pad=10)
        ax.set_xlabel(r'Ток торможения, $I_{\text{торм}}$ [$I_{\text{ном}}$]', fontsize=11, labelpad=5)
        ax.set_ylabel(r'Ток срабатывания, $I_{\text{дифф}}$ [$I_{\text{ном}}$]', fontsize=11, labelpad=5)

        # Настройка сетки - более заметная
        ax.grid(True, which='both', linestyle='-', linewidth=0.5, alpha=0.7, color='gray')
        ax.grid(True, which='minor', linestyle=':', linewidth=0.3, alpha=0.5)
        ax.minorticks_on()  # Включаем minor деления

        # Устанавливаем пределы с учетом произвольной точки
        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)

        # Создаем canvas и размещаем его
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)

        # Добавляем кнопку сохранения в правый верхний угол графика
        button_frame = ttk.Frame(canvas.get_tk_widget())
        button_frame.place(relx=1.0, x=-10, y=10, anchor="ne")

        save_button = ttk.Button(
            button_frame,
            text="💾 Сохранить график",
            command=self._on_save_figure,
            style="Accent.TButton" if hasattr(AppStyles, 'configure_styles') else "TButton"
        )
        save_button.pack()

    def _add_break_lines(self, ax, x1, y1, x2, y2):
        """Добавление линий излома"""
        ax.plot([x1, x1], [0, y1], 'k--', alpha=1, linewidth=1.5)
        ax.plot([0, x1], [y1, y1], 'k--', alpha=1, linewidth=1.5)
        ax.plot([x2, x2], [0, y2], 'k--', alpha=1, linewidth=1.5)
        ax.plot([0, x2], [y2, y2], 'k--', alpha=1, linewidth=1.5)

    def _add_point_labels(self, ax, x1, y1, x2, y2, label_style):
        """Добавление подписей точек"""
        ax.text(x2 * 0.01, y1, f'$I_{{\\text{{d1}}}}$ = {y1:.2f}', **label_style, ha='left', va='bottom')
        ax.text(x2 * 0.01, y2, f'$I_{{\\text{{d2}}}}$ = {y2:.2f}', **label_style, ha='left', va='bottom')
        ax.text(x1 + x2 * 0.01, 0, f'$I_{{\\text{{t1}}}}$ = {x1:.2f}', **label_style, ha='left', va='bottom')
        ax.text(x2 * 1.01, 0, f'$I_{{\\text{{t2}}}}$ = {x2:.2f}', **label_style, ha='left', va='bottom')

    def _add_slope_labels(self, ax, x1, y1, x2, y2, k1, k2, params):
        """Добавление подписей наклонов"""
        k1_text = f'k1 = {k1:.2f}\nα1 = {np.degrees(np.arctan(k1)):.1f}°'
        k2_text = f'k2 = {k2:.2f}\nα2 = {np.degrees(np.arctan(k2)):.1f}°'

        ax.text(x1 - x2 * 0.02, y1 + y2 * 0.1 * (params['zona_y'] / 2.5), k1_text,
                bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.8, ec='black'),
                fontsize=10, ha='right', va='bottom')
        ax.text(x2 - x2 * 0.02, y2 + 0.1 * y2 * (params['zona_y'] / 2.5), k2_text,
                bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.8, ec='black'),
                fontsize=10, ha='right', va='bottom')

    def _add_arbitrary_point(self, ax, point, label_style, x2, max_x):
        """Добавление произвольной точки на график"""
        I_brake_point = point['I_brake']
        I_diff_point = point['I_diff']
        ax.scatter(I_brake_point, I_diff_point, color='red', s=100, zorder=5,
                   label=f'Расчетная точка ({I_brake_point:.2f}, {I_diff_point:.2f})')
        ax.plot([I_brake_point, I_brake_point], [0, I_diff_point], 'k--', alpha=1, linewidth=1.5)
        ax.plot([0, I_brake_point], [I_diff_point, I_diff_point], 'k--', alpha=1, linewidth=1.5)

        # Корректируем позиции подписей с учетом новых пределов
        x_pos = I_brake_point * 1.01 if I_brake_point < max_x * 1.01 else I_brake_point * 1.01
        ax.text(x_pos, 0, f'$I_{{\\text{{t}}}}$ = {I_brake_point:.2f}', **label_style, ha='left', va='bottom')

        y_pos = I_diff_point * 1.01 if I_diff_point < ax.get_ylim()[1] * 0.9 else I_diff_point * 0.9
        ax.text(ax.get_xlim()[1] * 0.01, y_pos, f'$I_{{\\text{{d}}}}$ = {I_diff_point:.2f}', **label_style, ha='left',
                va='bottom')

    def update_results(self, params, device_type, arbitrary_point=None):
        """
        Обновление существующего окна с результатами.

        Args:
            params: Параметры для расчета
            device_type: Тип устройства
            arbitrary_point: Произвольная точка
        """
        # Очищаем содержимое scrollable_frame
        if self.scrollable_frame:
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            if self.figure:
                plt.close(self.figure)
                self.figure = None

        # Заново отображаем результаты
        self._display_results(params, device_type, arbitrary_point)

        # Обновляем заголовок окна
        self.window.title(f"Результаты расчета характеристик защиты - {device_type}")

    def _close(self):
        """Закрытие окна результатов"""
        if self.window:
            plt.close('all')
            self.window.destroy()
            self.window = None