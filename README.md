# Проект спринта: покрытие тестами.

Написаны юнит-тесты для учебного django проекта соц.сети yatube.

## Технологии и запуск проекта

Проект написан на языке python, с использованием фреймворка django. 
Необходимые для работы проекта зависимости описаны в файле requirements.txt

Для запуска проекта:
- Клонируйте репозиторий
``` 
- git clone https://github.com/AVinAnd/api_yamdb.git 
```
- Активируйте виртуальное окружение 

```
python -m venv venv
source venv/scripts/activate
```
- Установите зависимости

``` 
pip install -r requirements.txt
```
- Выполните миграции 
```
python manage.py makemigrations
python manage.py migrate
```
- Запустите проект
```
python manage.py runserver
```

### Об авторе
Андрей Виноградов - python-developer, выпускник Яндекс Практикума по курсу Python-разработчик
