"""
Главное окно приложения.
"""

from tkinter import *
from tkinter import ttk, messagebox, font
from config.constants import AppStyles, DeviceConstants
from views.widgets import Card, InputField, Button, RadioGroup, ScrollableFrame
from views.theme import setup_theme


class MainWindow:
    """
    Главное окно приложения.
    """

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.selected_device = StringVar(value="MR_801")
        self.entries = {}
        self.current_params = {}

        # Настройка темы
        self.style = setup_theme(root)

        self._setup_window()
        self._create_ui()

        # Привязка событий
        self.selected_device.trace_add('write', lambda *args: self._on_device_change())

    def _setup_window(self):
        """Настройка окна"""
        self.root.title("🔧 Расчет характеристик дифференциальных защит")
        self.root.state('zoomed')
        self.root.configure(bg=AppStyles.BACKGROUND)

        # Убираем стандартные отступы
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def _create_ui(self):
        """Создание интерфейса"""
        # Главный контейнер
        main = ttk.Frame(self.root, style='Card.TFrame')
        main.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # Левая колонка
        left_col = ttk.Frame(main)
        left_col.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_col.grid_rowconfigure(1, weight=1)

        # Правая колонка
        right_col = ttk.Frame(main, width=400)
        right_col.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        right_col.grid_propagate(False)

        # Блок выбора устройства
        self._create_device_section(left_col)

        # Блок ввода параметров
        self._create_input_section(left_col)

        # Блок заметок
        self._create_notes_section(right_col)

    def _create_device_section(self, parent):
        """Секция выбора устройства"""
        card = Card(parent, title="выбор устройства")
        card.grid(row=0, column=0, sticky='ew', pady=(0, 20))

        options = [
            ("🔹 МР-801", "MR_801"),
            ("🔸 RET-521 (ОПОРА ВН)", "RET_521_HV"),
            ("🔸 RET-521 (ОПОРА НН)", "RET_521_LV"),
            ("💠 RET-670 (ОПОРА ВН)", "RET_670_HV"),
            ("💠 RET-670 (ОПОРА НН)", "RET_670_LV")
        ]

        radio_group = RadioGroup(card.content, options)
        radio_group.value = self.selected_device
        radio_group.pack(fill=X)

    def _create_input_section(self, parent):
        """Секция ввода параметров"""
        card = Card(parent, title="параметры защиты")
        card.grid(row=1, column=0, sticky='nsew')

        # Прокручиваемая область
        scroll = ScrollableFrame(card.content)
        scroll.pack(fill=BOTH, expand=True)

        # Контейнер для полей ввода
        self.input_container = ttk.Frame(scroll.scrollable_frame)
        self.input_container.pack(fill=BOTH, expand=True)

        # Кнопки
        btn_frame = ttk.Frame(card.content)
        btn_frame.pack(fill=X, pady=(15, 0))

        Button(btn_frame, text="📊 Показать результаты",
               variant="primary",
               command=self._on_show_results).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        Button(btn_frame, text="🔄 Сбросить",
               variant="outline",
               command=self._on_reset_values).pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

        # Создаем поля ввода
        self._create_input_fields()

    def _create_input_fields(self):
        """Создание полей ввода"""
        # Очистка
        for widget in self.input_container.winfo_children():
            widget.destroy()

        device_type = self.selected_device.get()
        params = self.controller.get_default_params(device_type)
        labels = DeviceConstants.PARAM_LABELS_BY_DEVICE.get(
            device_type, DeviceConstants.BASE_PARAM_LABELS
        )

        self.current_params = params.copy()
        self.entries = {}

        # Создаем поля
        for i, (param, default) in enumerate(params.items()):
            # Пропускаем лишние параметры
            if param in ['I_brake1', 'I_brake2'] and 'RET_521' in device_type:
                continue
            if param not in labels:
                continue

            # Поле ввода
            field = InputField(self.input_container, label=labels[param])
            field.pack(fill=X, pady=6)
            field.set(str(default))

            # Привязка событий
            field.entry.bind('<KeyRelease>',
                           lambda e, p=param: self._on_param_change(p))

            self.entries[param] = field

    def _create_notes_section(self, parent):
        """Секция заметок"""
        card = Card(parent, title="памятка")
        card.pack(fill=BOTH, expand=True)

        # Текстовое поле с прокруткой
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

        # Скроллбар
        scrollbar = ttk.Scrollbar(text_frame, command=text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.configure(yscrollcommand=scrollbar.set)

        self.notes_text = text
        self._update_notes()

    def _update_notes(self):
        """Обновление заметок"""
        device_type = self.selected_device.get()
        notes = DeviceConstants.NOTES.get(device_type, "")

        self.notes_text.delete(1.0, END)
        self.notes_text.insert(1.0, notes)
        self.notes_text.configure(state='disabled')

    def _on_param_change(self, param):
        """Обработчик изменения параметра"""
        try:
            if param in self.entries:
                value = float(self.entries[param].get())
                self.current_params[param] = value
                self.controller.update_device_params(
                    self.selected_device.get(), self.current_params
                )
        except ValueError:
            pass

    def _on_device_change(self):
        """Обработчик смены устройства"""
        try:
            device_type = self.selected_device.get()
            self.controller.set_device(device_type)
            self._create_input_fields()
            self._update_notes()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_show_results(self):
        """Показать результаты"""
        try:
            params = self._get_current_params()
            self.controller.show_results(params, self.selected_device.get())
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def _on_reset_values(self):
        """Сброс значений"""
        device_type = self.selected_device.get()
        params = self.controller.get_default_params(device_type)

        for param, field in self.entries.items():
            if param in params:
                field.set(str(params[param]))

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
        return params