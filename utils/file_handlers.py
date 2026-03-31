"""
Утилиты для работы с файлами: сохранение и загрузка конфигураций.
"""

import json
import numpy as np
from tkinter import filedialog, messagebox
from datetime import datetime


class ConfigFileHandler:
    """Класс для работы с файлами конфигураций"""

    @staticmethod
    def save_config(params, device_type, filename=None):
        """
        Сохранение конфигурации в JSON файл.

        Args:
            params: Словарь с параметрами
            device_type: Тип устройства
            filename: Имя файла (если None, будет запрошено через диалог)

        Returns:
            bool: True если сохранение успешно, иначе False
        """
        if filename is None:
            # Формируем имя файла по умолчанию
            default_name = f"config_{device_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=default_name,
                title="Сохранить конфигурацию"
            )

        if not filename:
            return False

        try:
            config_data = {
                'device_type': device_type,
                'params': params,
                'saved_date': datetime.now().isoformat()
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)

            messagebox.showinfo("Успех", f"Конфигурация сохранена в файл:\n{filename}")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить конфигурацию:\n{str(e)}")
            return False

    @staticmethod
    def load_config():
        """
        Загрузка конфигурации из JSON файла.

        Returns:
            tuple: (device_type, params) или (None, None) если загрузка не удалась
        """
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить конфигурацию"
        )

        if not filename:
            return None, None

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            device_type = config_data.get('device_type')
            params = config_data.get('params')

            if not device_type or not params:
                messagebox.showerror("Ошибка", "Неверный формат файла конфигурации")
                return None, None

            messagebox.showinfo("Успех", f"Конфигурация загружена из файла:\n{filename}")
            return device_type, params

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить конфигурацию:\n{str(e)}")
            return None, None


class ResultsFileHandler:
    """Класс для работы с файлами результатов"""

    @staticmethod
    def save_results_to_file(params, currents, break_points, blocking_data, device_type, arbitrary_point=None):
        """
        Сохранение результатов в текстовый файл.

        Args:
            params: Параметры расчета
            currents: Токи для таблицы
            break_points: Точки излома (I_brake1, I_brake2, y1, y2, k1, k2)
            blocking_data: Данные блокировок
            device_type: Тип устройства
            arbitrary_point: Произвольная точка

        Returns:
            bool: True если сохранение успешно, иначе False
        """
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"results_{device_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            title="Сохранить результаты"
        )

        if not filename:
            return False

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Заголовок
                f.write("=" * 80 + "\n")
                f.write(f"РЕЗУЛЬТАТЫ РАСЧЕТА ХАРАКТЕРИСТИК ЗАЩИТЫ\n")
                f.write(f"Устройство: {device_type}\n")
                f.write(f"Дата расчета: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")

                # Исходные параметры
                f.write("1. ИСХОДНЫЕ ПАРАМЕТРЫ\n")
                f.write("-" * 80 + "\n")
                f.write(f"Номинальная мощность трансформатора: {params.get('S_nom', 'N/A')} МВА\n")
                f.write(f"Напряжение ВН: {params.get('U_hv', 'N/A')} кВ\n")
                f.write(f"Напряжение НН: {params.get('U_lv', 'N/A')} кВ\n")
                f.write(f"Коэффициент ТТ ВН: {params.get('CT_hv_perv', 'N/A')}/{params.get('CT_hv_sec', 'N/A')}\n")
                f.write(f"Коэффициент ТТ НН: {params.get('CT_lv_perv', 'N/A')}/{params.get('CT_lv_sec', 'N/A')}\n")
                f.write(f"Уставка дифференциального тока: {params.get('I_diff', 'N/A')} Iном\n")
                f.write(f"Блокировка по 2-й гармонике: {params.get('I2/I1', 'N/A')}%\n")
                f.write(f"Блокировка по 5-й гармонике: {params.get('I5/I1', 'N/A')}%\n")

                if 'I_brake1' in params:
                    f.write(f"1-я точка излома: {params.get('I_brake1', 'N/A')} Iном\n")
                if 'I_brake2' in params:
                    f.write(f"2-я точка излома: {params.get('I_brake2', 'N/A')} Iном\n")
                if 'k1' in params:
                    f.write(f"Наклон k1: {params.get('k1', 'N/A')}\n")
                if 'k2' in params:
                    f.write(f"Наклон k2: {params.get('k2', 'N/A')}\n")

                f.write("\n")

                # Основные параметры
                f.write("2. ОСНОВНЫЕ ПАРАМЕТРЫ\n")
                f.write("-" * 80 + "\n")
                f.write(f"Номинальный ток ВН: {currents.get('I_nom_hv', 'N/A')} А\n")
                f.write(f"Номинальный ток НН: {currents.get('I_nom_lv', 'N/A')} А\n")
                f.write(f"Вторичный ток ВН: {currents.get('I_sec_hv', 'N/A')} А\n")
                f.write(f"Вторичный ток НН: {currents.get('I_sec_lv', 'N/A')} А\n")
                f.write(f"Дифференциальный ток ВН: {currents.get('Id_hv', 'N/A')} А\n")
                f.write(f"Дифференциальный ток НН: {currents.get('Id_lv', 'N/A')} А\n\n")

                # Токи РЕТОМ
                f.write("3. ТОКИ РЕТОМ-61\n")
                f.write("-" * 80 + "\n")
                f.write(f"Точка 1 (ДЗТ) - ВН: {currents.get('retom_hv1', 'N/A')} А, НН: {currents.get('retom_lv1', 'N/A')} А\n")
                f.write(f"Точка 1 (сквозное КЗ) - ВН: {currents.get('retom_skvoz_hv1', 'N/A')} А, НН: {currents.get('retom_skvoz_lv1', 'N/A')} А\n")
                f.write(f"Точка 2 (ДЗТ) - ВН: {currents.get('retom_hv2', 'N/A')} А, НН: {currents.get('retom_lv2', 'N/A')} А\n")
                f.write(f"Точка 2 (сквозное КЗ) - ВН: {currents.get('retom_skvoz_hv2', 'N/A')} А, НН: {currents.get('retom_skvoz_lv2', 'N/A')} А\n\n")

                # Точки излома
                I_brake1, I_brake2, y1, y2, k1, k2 = break_points
                f.write("4. ТОЧКИ ИЗЛОМА ХАРАКТЕРИСТИКИ\n")
                f.write("-" * 80 + "\n")
                f.write(f"Точка 1: Iторм = {I_brake1:.2f} Iном, Iдиф = {y1:.2f} Iном\n")
                f.write(f"Точка 2: Iторм = {I_brake2:.2f} Iном, Iдиф = {y2:.2f} Iном\n")
                f.write(f"Наклон k1 = {k1:.2f} (tg φ = {k1:.2f}, α = {np.degrees(np.arctan(k1)):.2f}°)\n")
                f.write(f"Наклон k2 = {k2:.2f} (tg φ = {k2:.2f}, α = {np.degrees(np.arctan(k2)):.2f}°)\n\n")

                # Блокировки
                f.write("5. БЛОКИРОВКИ\n")
                f.write("-" * 80 + "\n")
                for row in blocking_data:
                    f.write(f"{row[0]}: {row[1]} А (уставка: {row[2]}%)\n")

                if arbitrary_point:
                    f.write("\n6. ПРОИЗВОЛЬНАЯ ТОЧКА\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"Ток торможения: {arbitrary_point['I_brake']:.2f} Iном\n")
                    f.write(f"Дифференциальный ток: {arbitrary_point['I_diff']:.2f} Iном\n")

                    # Получаем токи РЕТОМ для произвольной точки
                    # Сначала проверяем, есть ли уже рассчитанные значения в arbitrary_point
                    if 'retom_hv_arb' in arbitrary_point and 'retom_lv_arb' in arbitrary_point:
                        f.write(f"Ток РЕТОМ-61 ВН (ДЗТ): {arbitrary_point['retom_hv_arb']:.2f} А\n")
                        f.write(f"Ток РЕТОМ-61 НН (ДЗТ): {arbitrary_point['retom_lv_arb']:.2f} А\n")

                    # Если есть токи для сквозного КЗ
                    if 'retom_skvoz_arb_hv' in arbitrary_point and 'retom_skvoz_arb_lv' in arbitrary_point:
                        f.write(f"Ток РЕТОМ-61 ВН (сквозное КЗ): {arbitrary_point['retom_skvoz_arb_hv']:.2f} А\n")
                        f.write(f"Ток РЕТОМ-61 НН (сквозное КЗ): {arbitrary_point['retom_skvoz_arb_lv']:.2f} А\n")
                    elif 'retom_skvoz_arb' in arbitrary_point:
                        f.write(f"Ток РЕТОМ-61 сквозной: {arbitrary_point['retom_skvoz_arb']:.2f} А\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write("КОНЕЦ ОТЧЕТА\n")

            messagebox.showinfo("Успех", f"Результаты сохранены в файл:\n{filename}")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить результаты:\n{str(e)}")
            return False

    @staticmethod
    def save_figure(figure, filename=None):
        """
        Сохранение графика в файл.

        Args:
            figure: Объект Figure matplotlib
            filename: Имя файла (если None, будет запрошено через диалог)

        Returns:
            bool: True если сохранение успешно, иначе False
        """
        if filename is None:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                    ("All files", "*.*")
                ],
                initialfile=f"characteristic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                title="Сохранить график"
            )

        if not filename:
            return False

        try:
            figure.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Успех", f"График сохранен в файл:\n{filename}")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить график:\n{str(e)}")
            return False