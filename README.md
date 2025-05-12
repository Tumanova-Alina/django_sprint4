# Blogicum

---

## Описание
Социальная сеть для публикации блогов. Сайт, на котором пользователь может создать свою страницу, публиковать посты и оставлять комментарии.

---

## Функционал сайта
- Для каждого поста существует категория — например «путешествия», 
«здоровье» или «работа», а также опционально можно указать
локацию, с которой связан пост.

- Пользователь может перейти на страницу любой категории и 
увидеть все посты, которые к ней относятся.

- Пользователи могут заходить на чужие страницы, смотреть 
и комментировать посты.

- Для своей страницы автор может задать имя и уникальный адрес.

- Присутствует возможность восстановления пароля через почту.


---

## Технологии

![Python](https://img.shields.io/badge/Python-3.9.13-blue)
![Django](https://img.shields.io/badge/Django-3.2.16-green)
![HTML](https://img.shields.io/badge/HTML-5-orange)
![CSS](https://img.shields.io/badge/CSS-3-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-4-purple)
![Unittest](https://img.shields.io/badge/Unittest-tested-brightgreen)
![PythonAnywhere](https://img.shields.io/badge/Deployed-PythonAnywhere-red)
![pytest](https://img.shields.io/badge/pytest-7.1.3-yellow)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.11.2-lightgreen)
![Pillow](https://img.shields.io/badge/Pillow-9.3.0-pink)
![flake8](https://img.shields.io/badge/flake8-5.0.4-orange)


---

## Как запустить проект:

### 1. Клонировать репозиторий и перейти в него в командной строке:
```sh
git clone https://github.com/Tumanova-Alina/django_sprint4/
```
```sh
cd django_sprint4
```

---

### 2. В корневой директории проекта создайте виртуальное окружение:

- Для Windows:
```sh
python -m venv venv
```
- Для Linux/MacOS:
```sh
python3 -m venv venv
```

---

### 3. Активируйте виртуальное окружение, находясь в корневой директории:
- Для Windows:
```sh
source venv/Scripts/activate
```
- Для Linux/MacOS:
```sh
source venv/bin/activate
```

---

### 4. Обновите пакетный менеджер, находясь в корневой директории:
- Для Windows:
```sh
python -m pip install --upgrade pip
```
- Для Linux/MacOS:
```sh
python3 -m pip install --upgrade pip
```

---

### 5. Установите зависимости проекта командой, находясь в корневой директории:
```sh
pip install -r requirements.txt
```

---

### 6. Выполняем миграции. При активированном виртуальном окружении из директории с файлом manage.py выполните команду:
- Для Windows:
```sh
python manage.py migrate
```
- Для Linux/MacOS:
```sh
python3 manage.py migrate
```

---

### 7. Запустить проект:
- Для Windows:
```sh
python manage.py runserver
```
- Для Linux/MacOS:
```sh
python3 manage.py runserver
```