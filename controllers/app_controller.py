"""
Контроллер приложения.
Управляет взаимодействием между моделями и представлениями.
"""

from tkinter import messagebox
import numpy as np
import copy

from models.mr801 import MR801Device
from models.ret521 import RET521Device
from models.ret670 import RET670Device
from config.constants import DeviceConstants
from views.main_window import MainWindow
from views.results_window import ResultsWindow


class AppController:

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

        self.devices['MR_801'] = MR801Device(
            device_type='MR_801',
            default_params=copy.deepcopy(DeviceConstants.MR801_DEFAULTS)
        )

        self.devices['RET_521_HV'] = RET521Device(
            device_type='RET_521_HV',
            default_params=copy.deepcopy(DeviceConstants.RET521_HV_DEFAULTS)
        )

        self.devices['RET_521_LV'] = RET521Device(
            device_type='RET_521_LV',
            default_params=copy.deepcopy(DeviceConstants.RET521_LV_DEFAULTS)
        )

        self.devices['RET_670_HV'] = RET670Device(
            device_type='RET_670_HV',
            default_params=copy.deepcopy(DeviceConstants.RET670_HV_DEFAULTS)
        )

        self.devices['RET_670_LV'] = RET670Device(
            device_type='RET_670_LV',
            default_params=copy.deepcopy(DeviceConstants.RET670_LV_DEFAULTS)
        )

        self.current_device = self.devices['MR_801']

    def _prepare_device(self, device_type, params):
        """Подготовка устройства: получение, конвертация параметров, обновление"""
        device = self.devices[device_type]
        numeric_params = device.numeric_params(params)
        device.update_params(numeric_params)
        return device, numeric_params

    def _init_main_window(self):
        """Инициализация главного окна"""
        self.main_window = MainWindow(self.root, self)
        self.root.after(100, self.main_window._create_input_fields)

    def set_device(self, device_type):
        """
        Установка текущего устройства.
        """
        if device_type in self.devices:
            self.current_device = self.devices[device_type]

            # Обновляем параметры текущего устройства в главном окне
            if hasattr(self, 'main_window'):
                self.main_window.current_params = self.current_device.current_params.copy()


    def get_default_params(self, device_type):
        """
        Получение параметров по умолчанию для устройства.
        """
        return self.devices[device_type].default_params.copy()


    def update_device_params(self, device_type, params):
        """
        Обновление параметров устройства.
        """
        self.devices[device_type].update_params(params)

    def calculate_currents_full(self, params, device_type):
        """
        Расчет токов для таблицы результатов.
        """
        device = self.devices[device_type]
        numeric_params = device.numeric_params(params)
        return device.calculate_currents_full(numeric_params)

    def calculate_characteristic_full(self, I_brake, params, device_type):
        device, _ = self._prepare_device(device_type, params)
        return device.calculate_characteristic_full(I_brake)

    def get_break_points(self, params, device_type):
        device, numeric_params = self._prepare_device(device_type, params)
        return device.get_break_points(numeric_params)

    def calculate_arbitrary_point_full(self, I_brake, params, device_type):
        """
        Расчет произвольной точки по току торможения.
        Дифференциальный ток рассчитывается по характеристике устройства.
        """
        device, numeric_params = self._prepare_device(device_type, params)

        # Рассчитываем дифференциальный ток по характеристике
        I_brake_array = np.array([float(I_brake)])
        I_diff = device.calculate_characteristic_full(I_brake_array)[0]

        # Получаем базовые параметры
        base = device._get_base_params(numeric_params)

        # Рассчитываем токи ретома
        arbitrary_result = device._calculate_arbitrary_retom(base, float(I_brake), I_diff)

        # Добавляем исходные значения
        arbitrary_result['I_brake'] = float(I_brake)
        arbitrary_result['I_diff'] = I_diff

        return arbitrary_result

    def get_blocking_currents(self, params, device_type, arbitrary_point=None):
        device, _ = self._prepare_device(device_type, params)
        numeric_params = device.numeric_params(params)
        currents = self.calculate_currents_full(params, device_type)
        return device.calculate_blocking_currents(currents, numeric_params, arbitrary_point)

    def show_results(self, params, device_type):
        """
        Отображение окна с результатами.
        """

        # Сохраняем параметры в устройство
        self.update_device_params(device_type, params)
        self.arbitrary_point = self.calculate_arbitrary_point_full(
            params['I_arbitrary'],
            params,
            device_type
        )

        # Проверяем, существует ли окно результатов
        if self.results_window and hasattr(self.results_window, 'window') and self.results_window.window:
            try:
                if self.results_window.window.winfo_exists():
                    self.results_window.update_results(params, device_type, self.arbitrary_point)
                    self.results_window.window.lift()
                    self.results_window.window.focus_force()
                    return
            except:
                pass

        # Создаем новое окно
        self.results_window = ResultsWindow(self.root, self)
        self.results_window.show(params, device_type, self.arbitrary_point)