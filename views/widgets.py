"""
Кастомные виджеты для пользовательского интерфейса.
Содержит стилизованные элементы управления.
"""

from tkinter import *
from tkinter import ttk
from config.constants import AppStyles


class CardFrame(ttk.Frame):
    """
    Стилизованный фрейм-карточка с тенью для группировки элементов интерфейса.
    Может содержать заголовок и имеет оформленные границы.
    """

    def __init__(self, parent, title="", padding=15, *args, **kwargs):
        """
        Инициализация карточки.

        Args:
            parent: Родительский виджет
            title: Заголовок карточки
            padding: Внутренние отступы
        """
        super().__init__(parent, *args, **kwargs)
        self._create_card(title, padding)

    def _create_card(self, title, padding):
        """Внутренний метод для создания содержимого карточки"""
        self.config(style='Card.TFrame')
        if title:
            self.label = ttk.Label(self, text=title, style='CardTitle.TLabel')
            self.label.pack(side=TOP, fill=X, padx=5, pady=(0, 10))

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))


class ModernEntry(ttk.Frame):
    """
    Современное поле ввода с улучшенным дизайном.
    Поддерживает стилизацию и различные состояния.
    """

    def __init__(self, parent, *args, **kwargs):
        """Инициализация поля ввода"""
        width = kwargs.pop('width', 20)
        super().__init__(parent, *args, **kwargs)
        self._setup_style()
        self._create_widgets(width)

    def _setup_style(self):
        """Настройка стилей для поля ввода"""
        self.style = ttk.Style()
        self.style.configure('Modern.TEntry',
                             fieldbackground=AppStyles.ENTRY_BG,
                             foreground=AppStyles.DARK_TEXT,
                             borderwidth=1,
                             relief='solid',
                             padding=(5, 3),
                             font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_REGULAR))

        self.style.map('Modern.TEntry',
                       fieldbackground=[('focus', AppStyles.ENTRY_BG)],
                       foreground=[('focus', AppStyles.DARK_TEXT)],
                       bordercolor=[('focus', AppStyles.ENTRY_BORDER_FOCUS)])

    def _create_widgets(self, width):
        """Создание виджетов поля ввода"""
        self.entry_var = StringVar()
        self.entry = ttk.Entry(
            self,
            textvariable=self.entry_var,
            style='Modern.TEntry',
            width=width
        )
        self.entry.pack(fill=BOTH, expand=True, padx=1, pady=1)

    def get(self):
        """Получение текущего значения поля ввода"""
        return self.entry_var.get()

    def insert(self, index, string):
        """Вставка значения в поле ввода"""
        self.entry_var.set(string)


class ScrollableFrame(ttk.Frame):
    """
    Прокручиваемый фрейм с автоматической прокруткой.
    Позволяет размещать большое количество виджетов в ограниченном пространстве.
    """

    def __init__(self, container, *args, **kwargs):
        """Инициализация прокручиваемого фрейма"""
        super().__init__(container, *args, **kwargs)
        self._setup_widgets()
        self._bind_events()

    def _setup_widgets(self):
        """Настройка виджетов для прокрутки"""
        self.canvas = Canvas(self, highlightthickness=0, bg=AppStyles.LIGHT_BG)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.content_frame = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.content_frame, anchor=NW)

    def _bind_events(self):
        """Привязка обработчиков событий"""
        self.content_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel()

    def _on_frame_configure(self, event):
        """Обработчик изменения размеров фрейма"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Обработчик изменения размеров canvas"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _bind_mousewheel(self):
        """Привязка обработчиков колеса мыши"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Обработчик прокрутки колесом мыши"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")