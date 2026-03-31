"""
Настройка темы оформления.
"""

from tkinter import ttk
from config.constants import AppStyles


def setup_theme(root):
    """Настройка современной темы"""

    style = ttk.Style()
    style.theme_use('clam')

    # --- Базовые цвета ---
    style.configure('.',
                   background=AppStyles.BACKGROUND,
                   foreground=AppStyles.TEXT_PRIMARY,
                   fieldbackground=AppStyles.SURFACE,
                   selectbackground=AppStyles.PRIMARY,
                   selectforeground='white',
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD))

    # --- Карточки ---
    style.configure('Card.TFrame',
                   background=AppStyles.SURFACE,
                   relief='flat',
                   borderwidth=0)

    style.configure('CardInner.TFrame',
                   background=AppStyles.SURFACE,
                   relief='solid',
                   borderwidth=1,
                   bordercolor=AppStyles.BORDER)

    style.configure('CardHeader.TFrame',
                   background=AppStyles.SURFACE)

    style.configure('CardTitle.TLabel',
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_LG, 'bold'),
                   background=AppStyles.SURFACE,
                   foreground=AppStyles.TEXT_PRIMARY)

    style.configure('CardIcon.TLabel',
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_LG),
                   background=AppStyles.SURFACE,
                   foreground=AppStyles.PRIMARY)

    style.configure('CardContent.TFrame',
                   background=AppStyles.SURFACE)

    # --- Поля ввода ---
    style.configure('Input.TFrame',
                   background=AppStyles.BACKGROUND)

    style.configure('InputLabel.TLabel',
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_SM),
                   background=AppStyles.BACKGROUND,
                   foreground=AppStyles.TEXT_SECONDARY)

    style.configure('InputEntry.TFrame',
                   background=AppStyles.BORDER,
                   relief='flat')

    style.configure('Input.TEntry',
                   fieldbackground=AppStyles.SURFACE,
                   foreground=AppStyles.TEXT_PRIMARY,
                   insertcolor=AppStyles.PRIMARY,
                   insertwidth=2,
                   borderwidth=0,
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD),
                   padding=(AppStyles.PADDING_SM, AppStyles.PADDING_SM))

    # --- Кнопки ---
    style.configure('Primary.TButton',
                   background=AppStyles.PRIMARY,
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD, 'bold'),
                   padding=(AppStyles.PADDING_LG, AppStyles.PADDING_SM))

    style.map('Primary.TButton',
             background=[('active', AppStyles.PRIMARY_DARK),
                        ('pressed', AppStyles.PRIMARY_DARK)],
             relief=[('pressed', 'sunken')])

    style.configure('Secondary.TButton',
                   background=AppStyles.SECONDARY,
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD, 'bold'),
                   padding=(AppStyles.PADDING_LG, AppStyles.PADDING_SM))

    style.map('Secondary.TButton',
             background=[('active', AppStyles.SECONDARY_DARK),
                        ('pressed', AppStyles.SECONDARY_DARK)])

    style.configure('Danger.TButton',
                    background='#dc3545',  # Красный цвет
                    foreground='white',
                    borderwidth=0,
                    focuscolor='none',
                    font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD, 'bold'),
                    padding=(AppStyles.PADDING_LG, AppStyles.PADDING_SM))

    style.map('Danger.TButton',
              background=[('active', '#c82333'),
                          ('pressed', '#bd2130')],
              relief=[('pressed', 'sunken')])

    # --- Радио-кнопки ---
    style.configure('Modern.TRadiobutton',
                    background=AppStyles.BACKGROUND,
                    foreground=AppStyles.TEXT_PRIMARY,
                    font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD),
                    indicatorcolor=AppStyles.PRIMARY,
                    indicatorrelief='flat',  # Убираем рельеф
                    borderwidth=0,  # Убираем границу
                    focuscolor='none',  # Убираем цвет фокуса
                    focusthickness=0)  # Убираем толщину фокуса

    style.map('Modern.TRadiobutton',
              background=[('active', AppStyles.BACKGROUND),
                          ('pressed', AppStyles.BACKGROUND)],
              indicatorcolor=[('selected', AppStyles.PRIMARY),
                              ('active', AppStyles.PRIMARY_LIGHT)],
              relief=[('pressed', 'flat')])  # Убираем изменение рельефа при нажатии

    # --- Таблицы ---
    style.configure('Treeview',
                   background=AppStyles.SURFACE,
                   foreground=AppStyles.TEXT_PRIMARY,
                   fieldbackground=AppStyles.SURFACE,
                   borderwidth=0,
                   rowheight=30,
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD))

    style.configure('Treeview.Heading',
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD, 'bold'),
                   background=AppStyles.SURFACE_VARIANT,
                   foreground=AppStyles.TEXT_PRIMARY,
                   borderwidth=0,
                   relief='flat')

    style.map('Treeview.Heading',
             background=[('active', AppStyles.BORDER)])

    style.map('Treeview',
             background=[('selected', AppStyles.PRIMARY + '20')],
             foreground=[('selected', AppStyles.TEXT_PRIMARY)])

    # --- LabelFrame ---
    style.configure('TLabelframe',
                   background=AppStyles.BACKGROUND,
                   bordercolor=AppStyles.BORDER,
                   relief='solid',
                   borderwidth=1)

    style.configure('TLabelframe.Label',
                   font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD, 'bold'),
                   foreground=AppStyles.TEXT_PRIMARY,
                   background=AppStyles.BACKGROUND)

    style.configure('Modern.TCombobox',
                    fieldbackground=AppStyles.SURFACE,
                    background=AppStyles.SURFACE,
                    foreground=AppStyles.TEXT_PRIMARY,
                    selectbackground=AppStyles.PRIMARY,
                    selectforeground='white',
                    borderwidth=1,
                    relief='solid',
                    bordercolor=AppStyles.BORDER,
                    arrowsize=15,
                    font=(AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD))

    style.map('Modern.TCombobox',
              fieldbackground=[('readonly', AppStyles.SURFACE),
                               ('focus', AppStyles.SURFACE)],
              foreground=[('readonly', AppStyles.TEXT_PRIMARY),
                          ('focus', AppStyles.TEXT_PRIMARY)],
              selectbackground=[('focus', AppStyles.PRIMARY)],
              selectforeground=[('focus', 'white')],
              bordercolor=[('focus', AppStyles.PRIMARY)],
              lightcolor=[('focus', AppStyles.PRIMARY)],
              darkcolor=[('focus', AppStyles.PRIMARY)])

    # Стиль для стрелки Combobox
    style.configure('TCombobox.arrow',
                    background=AppStyles.SURFACE_VARIANT,
                    foreground=AppStyles.TEXT_SECONDARY)

    style.map('TCombobox.arrow',
              background=[('pressed', AppStyles.PRIMARY_LIGHT),
                          ('active', AppStyles.PRIMARY_LIGHT)],
              foreground=[('pressed', AppStyles.PRIMARY),
                          ('active', AppStyles.PRIMARY)])

    # Стиль для выпадающего списка
    root.option_add('*TCombobox*Listbox.font',
                    (AppStyles.FONT_FAMILY, AppStyles.FONT_SIZE_MD))
    root.option_add('*TCombobox*Listbox.background', AppStyles.SURFACE)
    root.option_add('*TCombobox*Listbox.foreground', AppStyles.TEXT_PRIMARY)
    root.option_add('*TCombobox*Listbox.selectBackground', AppStyles.PRIMARY)
    root.option_add('*TCombobox*Listbox.selectForeground', 'white')
    root.option_add('*TCombobox*Listbox.borderWidth', 0)
    root.option_add('*TCombobox*Listbox.relief', 'flat')

    # Убираем фокус с Combobox
    style.layout('Modern.TCombobox',
                 [('Combobox.field',
                   {'children':
                        [('Combobox.downarrow', {'side': 'right', 'sticky': 'ns'}),
                         ('Combobox.padding',
                          {'expand': '1', 'sticky': 'nswe',
                           'children':
                               [('Combobox.textarea', {'sticky': 'nswe'})]})],
                    'sticky': 'nswe'})])

    return style