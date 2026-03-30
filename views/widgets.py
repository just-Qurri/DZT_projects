"""
Кастомные виджеты для пользовательского интерфейса.
"""

from tkinter import *
from tkinter import ttk
from config.constants import AppStyles


class Card(ttk.Frame):
    """
    Красивая карточка с закругленными углами и тенью.
    """

    def __init__(self, parent, title="", padding=AppStyles.PADDING_LG, **kwargs):
        super().__init__(parent, **kwargs)

        # Настраиваем стиль карточки
        self.configure(style='Card.TFrame')

        # Создаем внутренний контейнер
        inner = ttk.Frame(self, style='CardInner.TFrame')
        inner.pack(fill=BOTH, expand=True, padx=1, pady=1)

        # Заголовок с иконкой
        if title:
            header = ttk.Frame(inner, style='CardHeader.TFrame')
            header.pack(fill=X, padx=padding, pady=(padding, 0))

            # Иконка (простой символ)
            icon_map = {
                'параметры': '⚙️',
                'результаты': '📊',
                'устройство': '🔧',
                'памятка': '📝'
            }
            icon = '📌'
            for key, value in icon_map.items():
                if key in title.lower():
                    icon = value
                    break

            ttk.Label(header, text=icon, style='CardIcon.TLabel').pack(side=LEFT, padx=(0, 8))
            ttk.Label(header, text=title.upper(), style='CardTitle.TLabel').pack(side=LEFT)

        # Контейнер для содержимого
        self.content = ttk.Frame(inner, style='CardContent.TFrame')
        self.content.pack(fill=BOTH, expand=True, padx=padding, pady=padding)


class InputField(ttk.Frame):
    """
    Красивое поле ввода с плавающей подписью.
    """

    def __init__(self, parent, label="", **kwargs):
        super().__init__(parent, style='Input.TFrame')

        self.label = label
        self.value = StringVar()

        # Метка
        self.label_widget = ttk.Label(self, text=label, style='InputLabel.TLabel')
        self.label_widget.pack(anchor=W, padx=4, pady=(0, 2))

        # Контейнер для поля ввода
        entry_frame = ttk.Frame(self, style='InputEntry.TFrame')
        entry_frame.pack(fill=X)

        # Поле ввода
        self.entry = ttk.Entry(entry_frame,
                               textvariable=self.value,
                               style='Input.TEntry',
                               **kwargs)
        self.entry.pack(fill=X, padx=1, pady=1)

        # Индикатор фокуса
        self.focus_indicator = Frame(entry_frame, height=2, bg=AppStyles.BORDER)
        self.focus_indicator.pack(fill=X)

        # Привязка событий
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)

    def _on_focus_in(self, event):
        self.focus_indicator.configure(bg=AppStyles.PRIMARY)
        self.label_widget.configure(foreground=AppStyles.PRIMARY)

    def _on_focus_out(self, event):
        self.focus_indicator.configure(bg=AppStyles.BORDER)
        self.label_widget.configure(foreground=AppStyles.TEXT_SECONDARY)

    def get(self):
        return self.value.get()

    def set(self, value):
        self.value.set(value)


class Button(ttk.Button):
    """
    Красивая кнопка с эффектами.
    """

    def __init__(self, parent, text="", variant="primary", **kwargs):
        style = f'{variant.capitalize()}.TButton'
        super().__init__(parent, text=text, style=style, **kwargs)


class RadioGroup(ttk.Frame):
    """
    Стилизованная группа радио-кнопок.
    """

    def __init__(self, parent, options, **kwargs):
        super().__init__(parent, style='RadioGroup.TFrame', **kwargs)

        self._value_var = StringVar()
        self._value_var.set(options[0][1])  # Первое значение по умолчанию
        self.options = options
        self.buttons = []  # Сохраняем кнопки для возможного обновления

        for text, value in options:
            rb = ttk.Radiobutton(self,
                                text=text,
                                variable=self._value_var,
                                value=value,
                                style='Modern.TRadiobutton')
            rb.pack(anchor=W, pady=4)
            self.buttons.append(rb)

    @property
    def value(self):
        """Получить текущее значение"""
        return self._value_var.get()

    @value.setter
    def value(self, new_value):
        """Установить новое значение и обновить все кнопки"""
        if isinstance(new_value, StringVar):
            # Если передали StringVar, нужно перепривязать все кнопки
            self._value_var = new_value
            for rb in self.buttons:
                rb.configure(variable=self._value_var)
        else:
            # Если передали строковое значение
            self._value_var.set(new_value)

    def set(self, value):
        """Установить значение (альтернативный метод)"""
        self._value_var.set(value)

    def get(self):
        """Получить значение (альтернативный метод)"""
        return self._value_var.get()


class ScrollableFrame(ttk.Frame):
    """
    Красивый прокручиваемый фрейм.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Canvas
        self.canvas = Canvas(self,
                            highlightthickness=0,
                            bg=AppStyles.BACKGROUND)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self,
                                       orient=VERTICAL,
                                       command=self.canvas.yview)

        # Настраиваем canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Фрейм для содержимого
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0),
                                                      window=self.scrollable_frame,
                                                      anchor=NW)

        # Размещаем
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # События
        self.scrollable_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self._bind_mousewheel()

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _bind_mousewheel(self):
        def on_mousewheel(event):
            if event.delta:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        self.canvas.bind_all('<MouseWheel>', on_mousewheel)


# Для обратной совместимости
CardFrame = Card
ModernEntry = InputField