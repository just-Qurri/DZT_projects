"""
Главное окно приложения.
"""

from tkinter import *
from tkinter import ttk, messagebox, font
from config.constants import AppStyles, DeviceConstants
from views.widgets import Card, InputField, Button, RadioGroup, ScrollableFrame
from views.theme import setup_theme
from utils.file_handlers import ConfigFileHandler


class MainWindow:
    """
    Главное окно приложения.
    """

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.selected_device = StringVar(value="MR_801")
        self.entries = {}

        # Настройка темы
        self.style = setup_theme(root)

        self._setup_window()
        self._create_menu()
        self._create_ui()

    def _setup_window(self):
        """Настройка окна"""
        self.root.title("🔧 Расчет характеристик дифференциальных защит")
        self.root.state('zoomed')
        self.root.configure(bg=AppStyles.BACKGROUND)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def _create_menu(self):
        """Создание главного меню"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)

        file_menu.add_command(label="Сохранить конфигурацию",
                             command=self._on_save_config,
                             accelerator="Ctrl+S")
        file_menu.add_command(label="Загрузить конфигурацию",
                             command=self._on_load_config,
                             accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Выход",
                             command=self._on_exit,
                             accelerator="Ctrl+Q")

        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Инструкция", command=self._on_help)
        help_menu.add_separator()
        help_menu.add_command(label="О программе", command=self._on_about)

    def _on_save_config(self):
        """Сохранение текущей конфигурации"""
        try:
            params = self._get_current_params()
            device_type = self.selected_device.get()
            ConfigFileHandler.save_config(params, device_type)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_load_config(self):
        """Загрузка конфигурации из файла"""
        device_type, params = ConfigFileHandler.load_config()

        if device_type and params:
            if device_type in DeviceConstants.DEFAULTS_BY_DEVICE:
                self.selected_device.set(device_type)
                for param, value in params.items():
                    if param in self.entries:
                        self.entries[param].set(str(value))
                        self.controller.update_device_params(device_type, {param: value})
            else:
                messagebox.showerror("Ошибка", f"Неизвестный тип устройства: {device_type}")

    def _on_exit(self):
        """Выход из программы"""
        if messagebox.askokcancel("Выход", "Закрыть программу?"):
            self.root.quit()

    @staticmethod
    def _on_help():
        """Показать инструкцию"""
        help_text = """
ИНСТРУКЦИЯ ПО РАБОТЕ С ПРОГРАММОЙ

1. ВЫБОР УСТРОЙСТВА
   - Выберите тип защитного устройства из списка
   - Для RET-521 и RET-670 доступны варианты выбора опорных сторон (ВН или НН)

2. ВВОД ПАРАМЕТРОВ
   - Заполните все поля ввода числовыми значениями
   - Параметры можно изменять в любой момент

3. РАСЧЕТ
   - Нажмите кнопку "Показать результаты" для расчета
   - Откроется окно с таблицами и графиком

4. РАБОТА С РЕЗУЛЬТАТАМИ
   - В окне результатов можно:
     * Сохранить результаты в текстовый файл (Ctrl+S)
     * Сохранить график в изображение (Ctrl+G)
     * Обновить данные (Ctrl+R)

5. СОХРАНЕНИЕ/ЗАГРУЗКА КОНФИГУРАЦИИ
   - Сохраните введенные параметры в JSON файл (Ctrl+S)
   - Загрузите ранее сохраненную конфигурацию (Ctrl+O)

6. ГОРЯЧИЕ КЛАВИШИ
   - Ctrl+S - сохранение конфигурации/результатов
   - Ctrl+O - загрузка конфигурации
   - Ctrl+G - сохранение графика
   - Ctrl+R - обновление результатов
   - Ctrl+Q - выход из программы
   - F1 - эта справка
   - Esc - закрыть окно результатов

Примечания:
- Все токи указываются в относительных единицах (Iном)
- Для МР-801 наклоны вводятся в градусах
- Для RET-521 наклоны вводятся в tg (коэффициент)
- Для RET-670 наклоны вводятся в процентах

© 2026 Программа для расчета характеристик дифференциальных защит"""
        messagebox.showinfo("Инструкция", help_text)

    @staticmethod
    def _on_about():
        """Информация о программе"""
        about_text = """
Расчет характеристик дифференциальных защит
    
Версия: 1.1

Программа предназначена для расчета и визуализации 
тормозных характеристик дифференциальных защит 
трансформаторов.

Поддерживаемые устройства:
• МР-801 (микропроцессорная защита)
• RET-521 (терминал ABB)
• RET-670 (терминал ABB)

Функции:
• Расчет токов для проверки на РЕТОМ-61
• Построение тормозных характеристик
• Сохранение/загрузка конфигураций
• Экспорт результатов в текстовый файл
• Сохранение графиков в PNG, PDF, SVG
• Подробная справка по работе

Требования:
• Python 3.7+
• Библиотеки: numpy, matplotlib

© 2026 Все права защищены."""

        messagebox.showinfo("О программе", about_text)

    def _create_ui(self):
        """Создание интерфейса"""
        main = ttk.Frame(self.root, style='Card.TFrame')
        main.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

        main.grid_columnconfigure(0, weight=88)
        main.grid_columnconfigure(1, weight=12)
        main.grid_rowconfigure(0, weight=1)

        left_col = ttk.Frame(main)
        left_col.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_col.grid_columnconfigure(0, weight=1)
        left_col.grid_rowconfigure(1, weight=1)

        right_col = ttk.Frame(main)
        right_col.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=0)
        right_col.grid_rowconfigure(1, weight=1)

        self._create_device_section(left_col)
        self._create_input_section(left_col)
        self._create_notes_section(right_col)
        self._create_arbitrary_section(right_col)

    def _create_device_section(self, parent):
        """Секция выбора устройства"""
        card = Card(parent, title="выбор устройства")
        card.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        parent.grid_columnconfigure(0, weight=1)

        options = [
            ("🔹 МР-801", "MR_801"),
            ("🔹 RET-521 (ОПОРА ВН)", "RET_521_HV"),
            ("🔹 RET-521 (ОПОРА НН)", "RET_521_LV"),
            ("🔹 RET-670 (ОПОРА ВН)", "RET_670_HV"),
            ("🔹 RET-670 (ОПОРА НН)", "RET_670_LV")
        ]

        for text, value in options:
            rb = ttk.Radiobutton(
                card.content,
                text=text,
                variable=self.selected_device,
                value=value,
                style='Modern.TRadiobutton',
                command=self._on_device_change
            )
            rb.pack(anchor=W, pady=4, fill=X)

    def _create_input_section(self, parent):
        """Секция ввода параметров с сеткой 2 колонки"""
        card = Card(parent, title="параметры защиты")
        card.grid(row=1, column=0, sticky='nsew')
        parent.grid_rowconfigure(1, weight=1)

        grid_container = ttk.Frame(card.content)
        grid_container.pack(fill=BOTH, expand=True)
        grid_container.grid_columnconfigure(0, weight=1, uniform="col")
        grid_container.grid_columnconfigure(1, weight=1, uniform="col")

        scroll = ScrollableFrame(grid_container)
        scroll.pack(fill=BOTH, expand=True)

        self.inputs_container = ttk.Frame(scroll.scrollable_frame)
        self.inputs_container.pack(fill=BOTH, expand=True)
        self.inputs_container.grid_columnconfigure(0, weight=1, uniform="col")
        self.inputs_container.grid_columnconfigure(1, weight=1, uniform="col")

        btn_frame = ttk.Frame(card.content)
        btn_frame.pack(fill=X, pady=(15, 0))

        Button(btn_frame, text="📊 Показать результаты",
               variant="primary",
               command=self._on_show_results).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        Button(btn_frame, text="🔄 Сбросить",
               variant="danger",
               command=self._on_reset_values).pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

        self._create_input_fields()

    def _create_input_fields(self):
        """Создание полей ввода"""
        for widget in self.inputs_container.winfo_children():
            widget.destroy()

        device_type = self.selected_device.get()
        params = self.controller.get_default_params(device_type)
        labels = DeviceConstants.PARAM_LABELS_BY_DEVICE.get(device_type, DeviceConstants.BASE_PARAM_LABELS)

        self.entries = {}
        available_params = [p for p in params.keys() if p in labels and p != 'I_arbitrary']

        row, col = 0, 0
        for param in available_params:
            field = InputField(self.inputs_container, label=labels[param])
            field.grid(row=row, column=col, sticky='ew', padx=5, pady=6)
            field.set(str(params[param]))
            field.entry.bind('<KeyRelease>', lambda e, p=param: self._on_param_change(p))
            self.entries[param] = field

            col += 1
            if col >= 2:
                col = 0
                row += 1

        if col == 1:
            placeholder = ttk.Frame(self.inputs_container)
            placeholder.grid(row=row, column=1, sticky='ew', padx=5, pady=6)

    def _create_notes_section(self, parent):
        """Секция заметок"""
        card = Card(parent, title="памятка")
        card.pack(fill=BOTH, expand=True, pady=(0, 20))

        text_frame = ttk.Frame(card.content)
        text_frame.pack(fill=BOTH, expand=True)

        text = Text(text_frame,
                   wrap=WORD,
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_SM),
                   bg=AppStyles.SURFACE_VARIANT,
                   fg=AppStyles.TEXT_PRIMARY,
                   padx=15,
                   pady=15,
                   relief='flat',
                   borderwidth=0,
                   highlightthickness=0)
        text.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.configure(yscrollcommand=scrollbar.set)

        self.notes_text = text
        self._update_notes()

    def _create_arbitrary_section(self, parent):
        """Секция для ввода произвольной точки"""
        card = Card(parent, title="произвольная точка")
        card.pack(fill=BOTH, expand=True)

        desc_label = ttk.Label(
            card.content,
            text="Введите значение тормозного тока для расчета произвольной точки на характеристике:",
            font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_SM),
            wraplength=800,
            justify=LEFT
        )
        desc_label.pack(fill=X, pady=(0, 10))

        self.arbitrary_field = InputField(card.content, label="Ток торможения I_brake, о.е.")
        self.arbitrary_field.pack(fill=X)
        self.arbitrary_field.set("2.5")

    def _update_notes(self):
        """Обновление заметок"""
        device_type = self.selected_device.get()
        notes = DeviceConstants.NOTES.get(device_type, "")

        self.notes_text.configure(state='normal')
        self.notes_text.delete(1.0, END)
        self.notes_text.insert(1.0, notes)
        self.notes_text.configure(state='disabled')

    def _on_param_change(self, param):
        """Обработчик изменения параметра"""
        try:
            if param in self.entries:
                value = float(self.entries[param].get())
                self.controller.update_device_params(
                    self.selected_device.get(),
                    {param: value}
                )
        except ValueError:
            pass

    def _on_device_change(self):
        """Обработчик смены устройства"""
        try:
            device_type = self.selected_device.get()
            self.controller.set_device(device_type)
            self._create_input_fields()
            if hasattr(self, 'arbitrary_field'):
                self.arbitrary_field.set("2.5")
            self._update_notes()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_show_results(self):
        """Показать результаты"""
        try:
            params = self._get_current_params()
            device_type = self.selected_device.get()
            self.controller.show_results(params, device_type)
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def _on_reset_values(self):
        """Сброс значений"""
        device_type = self.selected_device.get()
        params = self.controller.get_default_params(device_type)

        for param, field in self.entries.items():
            if param in params:
                field.set(str(params[param]))
                self.controller.update_device_params(device_type, {param: params[param]})

        if hasattr(self, 'arbitrary_field'):
            self.arbitrary_field.set("2.5")

    def _get_current_params(self):
        """Получение текущих параметров"""
        params = {}
        for param, field in self.entries.items():
            value = field.get().strip()
            if value:
                try:
                    params[param] = float(value.replace(',', '.'))
                except ValueError:
                    raise ValueError(f"Некорректное значение: {param}")

        if hasattr(self, 'arbitrary_field') and self.arbitrary_field.get().strip():
            try:
                params['I_arbitrary'] = float(self.arbitrary_field.get().replace(',', '.'))
            except ValueError:
                pass

        return params