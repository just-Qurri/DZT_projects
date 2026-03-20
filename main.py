"""
Главный модуль программы для расчета характеристик дифференциальных защит трансформаторов.
"""

import tkinter as tk  # Добавьте эту строку
from tkinter import messagebox
import matplotlib.pyplot as plt

from config.constants import AppStyles
from views.theme import setup_theme
from controllers.app_controller import AppController


def main():
    """Точка входа в программу"""
    # Настройка стилей matplotlib
    AppStyles.configure_styles()

    # Создание главного окна
    root = tk.Tk()  # Теперь tk определен

    # Применение современной темы
    setup_theme(root)

    # Установка иконки (если есть)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass

    # Настройка заголовка
    root.title("📊 Расчет характеристик дифференциальных защит")

    # Создание контроллера приложения
    app = AppController(root)

    # Настройка обработчика закрытия окна
    def on_closing():
        if messagebox.askokcancel("Выход", "Закрыть программу?"):
            plt.close('all')
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()