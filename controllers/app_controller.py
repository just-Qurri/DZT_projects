"""
Контроллер приложения.
Управляет взаимодействием между моделями и представлениями.
"""

from tkinter import messagebox
import numpy as np

from models.mr801 import MR801Device
from models.ret521 import RET521Device
from models.ret670 import RET670Device
from config.constants import DeviceConstants
from views.main_window import MainWindow
from views.results_window import ResultsWindow


class AppController:
    """
    Контроллер приложения.
    Координирует работу моделей и представлений.
    """

    def __init__(self, root):
        """
        Инициализация контроллера.
        """

        self.root = root
        self.devices = {}
        self.current_device = None
        self.results_window = None
        self.arbitrary_point = None

        # Сначала инициализируем устройства
        self._init_devices()

        # Потом создаем главное окно
        self._init_main_window()

    def _init_devices(self):
        """Инициализация всех устройств"""
        # Создаем копии словарей, чтобы не изменять оригиналы
        import copy
        self.devices['MR_801'] = MR801Device(copy.deepcopy(DeviceConstants.MR801_DEFAULTS))
        self.devices['RET_521_HV'] = RET521Device('RET_521_HV', copy.deepcopy(DeviceConstants.RET521_HV_DEFAULTS))
        self.devices['RET_521_LV'] = RET521Device('RET_521_LV', copy.deepcopy(DeviceConstants.RET521_LV_DEFAULTS))
        self.devices['RET_670_HV'] = RET670Device('RET_670_HV', copy.deepcopy(DeviceConstants.RET670_HV_DEFAULTS))
        self.devices['RET_670_LV'] = RET670Device('RET_670_LV', copy.deepcopy(DeviceConstants.RET670_LV_DEFAULTS))
        self.current_device = self.devices['MR_801']

    def _init_main_window(self):
        """Инициализация главного окна"""
        self.main_window = MainWindow(self.root, self)
        # После создания окна, сразу создаем поля ввода
        self.main_window.after(100, self.main_window._create_input_fields)

    def set_device(self, device_type):
        """
        Установка текущего устройства.
        device_type: Тип устройства
        """
        if device_type in self.devices:
            self.current_device = self.devices[device_type]
            # Обновляем параметры текущего устройства в главном окне
            self.main_window.current_params = self.current_device.current_params.copy()

    def get_default_params(self, device_type):
        """
        Получение параметров по умолчанию для устройства.

        Args:
            device_type: Тип устройства

        Returns:
            Словарь с параметрами по умолчанию
        """
        return self.devices[device_type].default_params.copy()


    def update_device_params(self, device_type, params):
        """
        Обновление параметров устройства.

        Args:
            device_type: Тип устройства
            params: Новые параметры
        """
        self.devices[device_type].update_params(params)

    def calculate_currents_full(self, params, device_type):
        """
        Расчет токов для таблицы результатов.

        Args:
            params: Параметры для расчета
            device_type: Тип устройства

        Returns:
            Словарь с рассчитанными токами
        """
        device = self.devices[device_type]
        numeric_params = device.numeric_params(params)
        is_valid, error = device.validate_params(numeric_params)

        if not is_valid:
            messagebox.showerror('Ошибка ввода данных', error)
            return {}

        return device.calculate_currents_full(numeric_params)

    def calculate_characteristic_full(self, I_brake, params, device_type):
        """
        Расчет характеристики срабатывания.

        Args:
            I_brake: Массив тормозных токов
            params: Параметры для расчета
            device_type: Тип устройства

        Returns:
            Массив дифференциальных токов
        """
        device = self.devices[device_type]
        numeric_params = device.numeric_params(params)
        device.update_params(numeric_params)
        return device.calculate_characteristic_full(I_brake)

    def get_break_points(self, params, device_type):
        """
        Получение точек излома характеристики.

        Args:
            params: Параметры для расчета
            device_type: Тип устройства

        Returns:
            Кортеж (I_brake1, I_brake2, y1, y2)
        """
        device = self.devices[device_type]
        numeric_params = device.numeric_params(params)
        return device.get_break_points(numeric_params)

    def calculate_arbitrary_point_full(self, I_brake, params, device_type):
        """
        Расчет произвольной точки характеристики.

        Args:
            I_brake: Тормозной ток в произвольной точке
            params: Параметры для расчета
            device_type: Тип устройства

        Returns:
            Кортеж (I_brake, I_diff)
        """
        device = self.devices[device_type]
        numeric_params = device.numeric_params(params)
        device.update_params(numeric_params)

        I_brake_array = np.array([I_brake])
        I_diff = device.calculate_characteristic_full(I_brake_array)[0]

        return {
            'I_brake': I_brake,
            'I_diff': I_diff
        }

    def get_blocking_currents(self, params, device_type, arbitrary_point=None):
        """Получение данных блокировок через конкретное устройство"""
        device = self.devices[device_type]
        numeric_params = device.numeric_params(params)

        # Сначала получаем токи для расчетов
        currents = self.calculate_currents_full(params, device_type)

        # Вызываем специфичный для устройства метод расчета блокировок
        return device.calculate_blocking_currents(currents, numeric_params, arbitrary_point)

    def show_results(self, params, device_type):
        """
        Отображение окна с результатами.

        Args:
            params: Параметры для расчета
            device_type: Тип устройства
        """
        # Сохраняем параметры в устройство
        self.update_device_params(device_type, params)

        # Рассчитываем произвольную точку, если есть I_arbitrary
        if 'I_arbitrary' in params:
            self.arbitrary_point = self.calculate_arbitrary_point_full(
                params['I_arbitrary'], params, device_type
            )

        # Создаем или показываем окно результатов
        if not self.results_window or not hasattr(self.results_window, 'window') or not self.results_window.window:
            self.results_window = ResultsWindow(self.root, self)

        self.results_window.show(params, device_type, self.arbitrary_point)