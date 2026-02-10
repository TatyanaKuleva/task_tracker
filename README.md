# Task Tracker API 

Система управления задачами с поддержкой иерархии (родительские задачи), зависимостей (блокировки) и аналитики нагрузки сотрудников.

## ✨ Основные возможности
- **Иерархия:** Создание подзадач любой вложенности.
- **Блокировки:** Отслеживание задач, выполнение которых зависит от других.
- **Умный подбор:** Эндпоинт для поиска наименее загруженного исполнителя или ответственного за родительскую задачу.
- **Аналитика:** Отчеты по критическим блокировщикам и важным задачам (Priority 1).
- **Документация:** Автогенерируемые схемы Swagger 

---

## 🛠 Технологический стек
- **Python 3.10+**
- **Django 4.2+ & Django REST Framework**
- **PostgreSQL** (в Docker)
- **drf-yasg** (OpenAPI 3.0)
- **Docker & Docker Compose**

---

## 📂 Структура проекта
```text
├── config/                # Настройки проекта (settings.py, urls.py)
├── tracker/               # Приложение управления задачами
│   ├── management/      # Кастомные команды (fill_tasks)
│   ├── models.py        # Модели Task и Employee
│   ├── serializers.py   # Логика валидации и форматирования
│   ├── views.py         # Эндпоинты и бизнес-логика
│   └── urls.py          # Маршрутизация API
├── users/               # Приложение управления задачами
│   ├── management/      # Кастомные команды (csu)
│   ├── models.py        # Модель USER
│   ├── serializers.py   # Логика валидации и форматирования
│   ├── views.py         # Эндпоинты и бизнес-логика
│   └── urls.py          # Маршрутизация API
├── docker-compose.yml   # Конфигурация контейнеров
├── Dockerfile           # Инструкции сборки образа
└── manage.py
```
# Быстрый запуск (Docker)

1. Клонируйте репозиторий
bash
    git clone https://github.com/TatyanaKuleva/task_tracker
    cd task-tracker

2. Запустите контейнеры
bash
    docker-compose up -d --build

3. Примените миграции
bash
    docker-compose exec web python manage.py migrate

4. Заполните базу тестовыми данными
bash
    docker-compose exec web python manage.py migrate

5. Создайте суперпользователя
bash
    docker-compose exec web python manage.py createsuperuser

Документация API
После запуска документация доступна по адресам:
ReDoc (Справочник): http://127.0.0.1
Swagger (Интерактив): http://127.0.0.1
Основные эндпоинты:
Метод	Эндпоинт	Описание
GET	/tracker/tasks/	Список всех задач
GET	/tracker/employees/workload/	Сотрудники, отсортированные по нагрузке
GET	/tracker/tasks/critical-blockers/	Задачи 'new', блокирующие работу других
GET	/tracker/tasks/priority-report/	Отчет по задачам Priority 1 в формате {Задача, Срок, ФИО}
GET	/trackertasks/{id}/suggest-assignee/	Рекомендация исполнителя для задачи


Валидация и логика
В системе реализованы следующие проверки:
    Self-dependency: Задача не может зависеть от самой себя.
    Parent-loop: Задача не может быть своим собственным родителем.
    Logic: При поиске исполнителя приоритет отдается сотруднику с минимальной нагрузкой или владельцу родительской задачи (если разница в нагрузке ≤ 2).
