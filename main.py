"""
Лабораторная работа № 1
Тема: Объектно-ориентированное программирование.
Предметная область: управление сотрудниками компании.
Технологии: Python, UML, JSON, XML.

Реализованы:
- абстрактный класс и абстрактный метод;
- наследование и полиморфизм;
- методы класса (@classmethod);
- пользовательские исключения;
- чтение и запись данных в JSON и XML.
"""

import json
import xml.etree.ElementTree as ET
from datetime import date
from abc import ABC, abstractmethod


# =========================
# Классы пользовательских исключений
# =========================

class CompanyError(Exception):
    """Базовое исключение программы."""
    pass


class InvalidEmployeeDataError(CompanyError):
    """Ошибка в данных сотрудника или менеджера."""
    pass


class EmployeeNotFoundError(CompanyError):
    """Сотрудник не найден."""
    pass


class DataFileError(CompanyError):
    """Ошибка при работе с файлами."""
    pass
