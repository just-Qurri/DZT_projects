"""
Главный модуль программы для расчета характеристик дифференциальных защит трансформаторов.
Программа позволяет моделировать и анализировать работу защитных устройств MR-801, RET-521, RET-670.
"""

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

from config.constants import AppStyles
from controllers.app_controller import AppController


def main():
    """Точка входа в программу"""
    # Настройка стилей
    AppStyles.configure_styles()

    # Создание главного окна
    root = tk.Tk()

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