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



class Person(ABC):
    """Абстрактный класс человека."""

    people_count = 0

    def __init__(self, first_name, last_name, email):
        if not first_name or not last_name:
            raise InvalidEmployeeDataError("Имя и фамилия не могут быть пустыми.")

        if "@" not in email:
            raise InvalidEmployeeDataError("Некорректный адрес электронной почты.")

        self.first_name = first_name
        self.last_name = last_name
        self.email = email

        Person.people_count += 1

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @abstractmethod
    def get_info(self):
        """Возвращает информацию о человеке."""
        pass

    @classmethod
    def get_people_count(cls):
        """Возвращает количество созданных объектов людей."""
        return Person.people_count


# =========================
# Класс Employee
# =========================

class Employee(Person):
    """Класс сотрудника компании."""

    def __init__(
        self, first_name, last_name, email,
        position, salary, hire_date
    ):
        super().__init__(first_name, last_name, email)

        if salary <= 0:
            raise InvalidEmployeeDataError("Зарплата должна быть больше нуля.")

        if not position:
            raise InvalidEmployeeDataError("Должность не может быть пустой.")

        self.position = position
        self.salary = salary
        self.hire_date = hire_date

    def calc_salary(self):
        """Рассчитывает выплату после условного удержания 13%."""
        return self.salary * 0.87

    def get_info(self):
        return (
            f"Сотрудник: {self.get_full_name()}, "
            f"должность: {self.position}, "
            f"зарплата после удержания: {self.calc_salary():.2f}"
        )

    def to_dict(self):
        """Преобразует сотрудника в словарь для JSON."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "position": self.position,
            "salary": self.salary,
            "hire_date": self.hire_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """Создаёт сотрудника из словаря."""
        try:
            return cls(
                data["first_name"],
                data["last_name"],
                data["email"],
                data["position"],
                float(data["salary"]),
                date.fromisoformat(data["hire_date"])
            )
        except (KeyError, TypeError, ValueError) as error:
            raise InvalidEmployeeDataError(f"Некорректные данные сотрудника: {error}") from error


# =========================
# Класс Manager
# =========================

class Manager(Employee):
    """Класс менеджера компании."""

    def __init__(
        self, first_name, last_name, email, position, salary,
        hire_date, bonus_percent, team_size
    ):
        if not 0 <= bonus_percent <= 100:
            raise InvalidEmployeeDataError("Процент премии должен быть от 0 до 100.")

        if team_size < 0:
            raise InvalidEmployeeDataError("Размер команды не может быть отрицательным.")

        super().__init__(
            first_name, last_name, email,
            position, salary, hire_date
        )

        self.bonus_percent = bonus_percent
        self.team_size = team_size

    def calc_salary(self):
        """Рассчитывает выплату менеджера с учётом премии."""
        return self.salary * (
            1 + self.bonus_percent / 100
        ) * 0.87

    def get_info(self):
        return (
            f"Менеджер: {self.get_full_name()}, "
            f"должность: {self.position}, "
            f"подчинённых: {self.team_size}, "
            f"зарплата с бонусом после удержания: "
            f"{self.calc_salary():.2f}"
        )


# =========================
# Класс Department
# =========================

class Department:
    """Класс отдела компании."""

    def __init__(self, dept_id, dept_name, manager=None):
        self.dept_id = dept_id
        self.dept_name = dept_name
        self.manager = manager
        self.employees = []

    def add_employee(self, employee):
        if not isinstance(employee, Employee):
            raise InvalidEmployeeDataError("В отдел можно добавлять только сотрудников.")

        self.employees.append(employee)

    def get_info(self):
        if self.manager:
            manager_name = self.manager.get_full_name()
        else:
            manager_name = "не назначен"

        return (
            f"Отдел {self.dept_name}; "
            f"руководитель: {manager_name}; "
            f"сотрудников: {len(self.employees)}"
        )


# =========================
# Класс Company
# =========================

class Company:
    """Класс компании."""

    def __init__(self, name):
        self.name = name
        self.employees = []
        self.managers = []
        self.departments = []

    def hire_employee(self, employee):
        if not isinstance(employee, Employee) or isinstance(
            employee, Manager
        ):
            raise InvalidEmployeeDataError("Ожидается объект Employee, не являющийся Manager.")

        self.employees.append(employee)

    def hire_manager(self, manager):
        if not isinstance(manager, Manager):
            raise InvalidEmployeeDataError("Ожидается объект класса Manager.")

        self.managers.append(manager)

    def find_by_email(self, email):
        for person in self.employees + self.managers:
            if person.email == email:
                return person

        raise EmployeeNotFoundError(f"Сотрудник с email {email} не найден.")

    def fire(self, email):
        person = self.find_by_email(email)

        if person in self.employees:
            self.employees.remove(person)
        elif person in self.managers:
            self.managers.remove(person)

        for department in self.departments:
            if person in department.employees:
                department.employees.remove(person)

            if department.manager == person:
                department.manager = None

    def add_department(self, department):
        if not isinstance(department, Department):
            raise InvalidEmployeeDataError("Ожидается объект класса Department.")

        self.departments.append(department)

    def save_employees_json(self, filename="employees.json"):
        data = [
            employee.to_dict()
            for employee in self.employees
        ]

        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(
                    data, file,
                    ensure_ascii=False,
                    indent=4
                )
        except (OSError, TypeError, ValueError) as error:
            raise DataFileError(f"Не удалось сохранить сотрудников в JSON: {error}") from error

    def load_employees_json(self, filename="employees.json"):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise DataFileError("JSON должен содержать список сотрудников.")

            loaded_employees = [
                Employee.from_dict(item) for item in data
            ]

            self.employees = loaded_employees

        except DataFileError:
            raise
        except (
            OSError, json.JSONDecodeError,
            TypeError, ValueError
        ) as error:
            raise DataFileError(f"Не удалось загрузить сотрудников из JSON: {error}") from error

    def save_managers_xml(self, filename="managers.xml"):
        root = ET.Element("managers")

        for manager in self.managers:
            element = ET.SubElement(root, "manager")

            ET.SubElement(
                element, "first_name"
            ).text = manager.first_name

            ET.SubElement(
                element, "last_name"
            ).text = manager.last_name

            ET.SubElement(
                element, "email"
            ).text = manager.email

            ET.SubElement(
                element, "position"
            ).text = manager.position

            ET.SubElement(
                element, "salary"
            ).text = str(manager.salary)

            ET.SubElement(
                element, "hire_date"
            ).text = manager.hire_date.isoformat()

            ET.SubElement(
                element, "bonus_percent"
            ).text = str(manager.bonus_percent)

            ET.SubElement(
                element, "team_size"
            ).text = str(manager.team_size)

        try:
            tree = ET.ElementTree(root)
            ET.indent(tree, space="    ")
            tree.write(
                filename,
                encoding="utf-8",
                xml_declaration=True
            )
        except (OSError, TypeError, ValueError) as error:
            raise DataFileError(f"Не удалось сохранить менеджеров в XML: {error}") from error

    def load_managers_xml(self, filename="managers.xml"):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            loaded_managers = []

            for element in root.findall("manager"):
                manager = Manager(
                    element.findtext("first_name"),
                    element.findtext("last_name"),
                    element.findtext("email"),
                    element.findtext("position"),
                    float(element.findtext("salary")),
                    date.fromisoformat(
                        element.findtext("hire_date")
                    ),
                    float(element.findtext("bonus_percent")),
                    int(element.findtext("team_size"))
                )

                loaded_managers.append(manager)

            self.managers = loaded_managers

        except DataFileError:
            raise
        except (
            OSError, ET.ParseError, TypeError,
            ValueError, InvalidEmployeeDataError
        ) as error:
            raise DataFileError(f"Не удалось загрузить менеджеров из XML: {error}") from error

    def show(self):
        print("\nКомпания:", self.name)

        print("\nСотрудники:")
        for employee in self.employees:
            print(employee.get_info())

        print("\nМенеджеры:")
        for manager in self.managers:
            print(manager.get_info())

        print("\nОтделы:")
        for department in self.departments:
            print(department.get_info())

