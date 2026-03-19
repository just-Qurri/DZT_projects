"""
Главное окно приложения.
Содержит элементы управления для ввода параметров и выбора устройства.
"""

from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
from tkinter import WORD
from config.constants import AppStyles, DeviceConstants
from views.widgets import CardFrame, ModernEntry, ScrollableFrame


class MainWindow:
    """
    Главное окно приложения.
    Управляет отображением интерфейса и взаимодействием с пользователем.
    """

    def __init__(self, root, controller):
        """
        Инициализация главного окна.

        Args:
            root: Корневой элемент Tkinter
            controller: Контроллер приложения
        """
        self.root = root
        self.controller = controller
        self.selected_device = StringVar(value="MR_801")
        self.entries = {}
        self.use_html = False
        self.notes_html = None
        self.notes_text = None
        self.current_params = {}  # Добавляем атрибут для текущих параметров
        self.scrollable_input = None
        self.input_frame = None

        self._setup_window()
        self._setup_ui()

        # Привязываем событие изменения выбранного устройства
        self.selected_device.trace_add('write', lambda *args: self._on_device_change())

    def _setup_window(self):
        """Настройка параметров главного окна"""
        self.root.title("Расчет характеристик дифференциальных защит")
        self.root.state('zoomed')
        self.root.configure(bg=AppStyles.LIGHT_BG)

        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

    def _setup_ui(self):
        """Создание пользовательского интерфейса"""
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill=BOTH, expand=True)

        content_container = ttk.Frame(main_container)
        content_container.pack(fill=BOTH, expand=True)

        # Левая панель
        left_panel = ttk.Frame(content_container)
        left_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 15))

        # Правая панель
        right_panel = ttk.Frame(content_container, width=400)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=False)

        self._create_device_selection(left_panel)
        self._create_input_frame(left_panel)
        self._create_button_frame(left_panel)
        self._create_notes_frame(right_panel)

        # Обновляем заметки
        self._update_notes()

    def after(self, ms, func):
        """Обертка для метода after корневого окна"""
        return self.root.after(ms, func)

    def _create_device_selection(self, parent):
        """Создание блока выбора устройства"""
        device_frame = CardFrame(parent, title="Выбор устройства")
        device_frame.pack(fill=X, pady=(0, 15))

        devices = [
            ("МР-801", "MR_801"),
            ("RET-521 (ОПОРА ВН)", "RET_521_HV"),
            ("RET-521 (ОПОРА НН)", "RET_521_LV")
        ]

        for text, mode in devices:
            rb = ttk.Radiobutton(
                device_frame.content_frame,
                text=text,
                variable=self.selected_device,
                value=mode,
                style='TRadiobutton'
            )
            rb.pack(anchor=W, pady=5, padx=5)

    def _create_input_frame(self, parent):
        """Создание блока ввода параметров"""
        self.input_frame = CardFrame(parent, title="Параметры защиты")
        self.input_frame.pack(fill=BOTH, expand=True)

        self.scrollable_input = ScrollableFrame(self.input_frame.content_frame)
        self.scrollable_input.pack(fill=BOTH, expand=True)

    def _create_input_fields(self):
        """Создание полей ввода параметров"""
        if not self.scrollable_input or not hasattr(self.scrollable_input, 'content_frame'):
            return

        # Очистка предыдущих полей
        for widget in self.scrollable_input.content_frame.winfo_children():
            widget.destroy()

        device_type = self.selected_device.get()
        params = self.controller.get_default_params(device_type)

        # Сохраняем текущие параметры
        self.current_params = params.copy()
        self.entries = {}

        grid_frame = ttk.Frame(self.scrollable_input.content_frame)
        grid_frame.pack(fill=BOTH, expand=True, pady=(5, 0))

        grid_frame.columnconfigure(0, weight=3, pad=10)
        grid_frame.columnconfigure(1, weight=1, pad=10)

        row = 0
        for param, default_value in params.items():
            # Пропускаем I_brake1 для RET-521 (кроме MR-801)
            if param == 'I_brake1' and device_type != "MR_801":
                continue

            # Проверяем, есть ли подпись для параметра
            if param not in DeviceConstants.PARAM_LABELS:
                continue

            label = ttk.Label(
                grid_frame,
                text=DeviceConstants.PARAM_LABELS[param],
                anchor='w',
                style='TLabel'
            )
            label.grid(row=row, column=0, sticky='ew', pady=5)

            entry_frame = ModernEntry(grid_frame, width=15)
            entry_frame.grid(row=row, column=1, sticky='ew', pady=5, padx=(0, 10))
            entry_frame.insert(0, str(default_value))

            # Привязываем обработчик изменения
            entry_frame.entry.bind('<KeyRelease>', lambda e, p=param: self._on_param_change(p))

            self.entries[param] = entry_frame
            row += 1

    def _on_param_change(self, param):
        """Обработчик изменения значения параметра"""
        try:
            if param in self.entries:
                value = float(self.entries[param].get())
                self.current_params[param] = value
                # Обновляем параметры в контроллере
                self.controller.update_device_params(self.selected_device.get(), self.current_params)
        except ValueError:
            pass  # Игнорируем некорректные значения во время ввода

    def _create_button_frame(self, parent):
        """Создание панели с кнопками"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=X, pady=10)

        buttons = [
            ("Показать результаты", self._on_show_results, 'Primary.TButton'),
            ("Сбросить значения", self._on_reset_values, 'Danger.TButton')
        ]

        for col, (text, command, style) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, style=style)
            btn.grid(row=0, column=col, padx=5, sticky='ew')
            button_frame.columnconfigure(col, weight=1)

    def _create_notes_frame(self, parent):
        """Создание блока с памяткой"""
        self.notes_frame = CardFrame(parent, title="Памятка")
        self.notes_frame.pack(fill=BOTH, expand=True)

        try:
            from tkinterweb import HtmlFrame
            self.notes_html = HtmlFrame(
                self.notes_frame.content_frame,
                messages_enabled=False
            )
            self.notes_html.pack(fill=BOTH, expand=True)
            self.use_html = True
        except ImportError:
            self.notes_text = scrolledtext.ScrolledText(
                self.notes_frame.content_frame,
                wrap=WORD,
                font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_REGULAR),
                padx=10,
                pady=10
            )
            self.notes_text.pack(fill=BOTH, expand=True)
            self.use_html = False

    def _update_notes(self):
        """Обновление текста памятки"""
        device_type = self.selected_device.get()
        notes = DeviceConstants.NOTES.get(device_type, "Нет заметок для выбранного устройства")

        if self.use_html and self.notes_html:
            html = f"""
            <div style='text-align: justify; padding: 10px;
                        font-family: {AppStyles.FONT_FAMILY};
                        font-size: {AppStyles.FONT_SIZE_REGULAR}pt;'>
                {notes.replace(chr(10), "<br>")}
            </div>
            """
            self.notes_html.load_html(html)
        elif self.notes_text:
            self.notes_text.configure(state='normal')
            self.notes_text.delete(1.0, END)
            self.notes_text.insert(END, notes)
            self.notes_text.configure(state='disabled')

    def _on_device_change(self):
        """Обработчик изменения выбранного устройства"""
        try:
            device_type = self.selected_device.get()
            self.controller.set_device(device_type)
            self._create_input_fields()
            self._update_notes()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при изменении устройства:\n{str(e)}")

    def _on_show_results(self):
        """Обработчик кнопки показа результатов"""
        try:
            params = self._get_current_params()
            self.controller.show_results(params, self.selected_device.get())
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Проверьте правильность введенных данных:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")

    def _on_reset_values(self):
        """Обработчик кнопки сброса значений"""
        device_type = self.selected_device.get()
        params = self.controller.get_default_params(device_type)

        self.current_params = params.copy()

        for param, entry in self.entries.items():
            if param in params:
                entry.entry.delete(0, END)
                entry.entry.insert(0, str(params[param]))

    def _get_current_params(self):
        """Получение текущих параметров из полей ввода"""
        params = {}
        for param, entry in self.entries.items():
            try:
                value = entry.get().strip()
                if value:
                    params[param] = float(value.replace(',', '.'))
                else:
                    raise ValueError(f"Параметр {param} не может быть пустым")
            except ValueError as e:
                raise ValueError(f"Некорректное значение для параметра {param}: {entry.get()}")
        return params