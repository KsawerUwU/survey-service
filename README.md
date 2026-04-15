# Сервис опросов (анкет) с GraphQL API (Strawberry + Django)

Учебный проект по дисциплине «Программирование и разработка web-приложений».

## Возможности

- создание опросов, вопросов и вариантов ответа;
- поддержка типов вопросов:
  - `single_choice`;
  - `multiple_choice`;
  - `text`;
  - `number`;
  - `boolean`;
- приём пользовательских ответов через GraphQL;
- прохождение анкет через обычный веб-интерфейс;
- получение списка опросов и структуры конкретной анкеты;
- сбор статистики по результатам прохождения;
- администрирование через стандартную панель Django Admin;
- демонстрационное заполнение базы тестовыми данными.

## Стек

- Python 3.11+ 
- Django
- Strawberry GraphQL
- SQLite по умолчанию
- HTML / CSS / JavaScript для пользовательского интерфейса

## Структура проекта

```text
survey_service/
├─ config/                  # настройки Django и маршруты
├─ api/
│  ├─ graphql/              # GraphQL schema, типы, inputs, queries, mutations
│  ├─ services/             # бизнес-логика обработки ответов и статистики
│  ├─ management/commands/  # команда seed_demo
│  ├─ templates/api/        # HTML-шаблоны главной и формы анкеты
│  ├─ static/api/           # CSS-оформление интерфейса
│  ├─ views.py              # страницы сайта
│  ├─ models.py             # модели данных
│  ├─ admin.py              # регистрация в админ-панели
│  └─ tests/                # примеры тестов
├─ docs/                    # примеры запросов GraphQL
├─ manage.py
└─ requirements.txt
```

## Быстрый запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

После запуска доступны страницы:

- Главная страница: `http://127.0.0.1:8000/`
- Прохождение анкет: `http://127.0.0.1:8000/surveys/<slug>/`
- GraphQL endpoint / GraphiQL: `http://127.0.0.1:8000/graphql/`
- Django Admin: `http://127.0.0.1:8000/admin/`

## Сценарий работы администратора

1. Создать суперпользователя: `python manage.py createsuperuser`
2. Открыть `http://127.0.0.1:8000/admin/`
3. Войти под логином администратора
4. Создать объект **Опрос**
5. Добавить к нему вопросы
6. Для вопросов типа `single_choice` и `multiple_choice` добавить варианты ответа
7. Убедиться, что у опроса установлен флаг `is_active = True`
8. Передать пользователю ссылку вида `http://127.0.0.1:8000/surveys/<slug>/`
9. После прохождения анкеты смотреть результаты в разделах **Прохождения опросов**, **Ответы** и через GraphQL статистику

## Сценарий работы обычного пользователя

1. Открыть `http://127.0.0.1:8000/`
2. Выбрать нужную анкету из списка
3. Перейти на страницу опроса
4. При необходимости заполнить имя и email
5. Ответить на вопросы
6. Нажать кнопку **Отправить ответы**
7. Получить страницу подтверждения успешной отправки

## Пример GraphQL-запроса

```graphql
query GetSurvey {
  surveyBySlug(slug: "customer-satisfaction") {
    id
    title
    description
    isActive
    questions {
      id
      title
      questionType
      isRequired
      choices {
        id
        text
        value
      }
    }
  }
}
```

## Пример мутации отправки ответов

```graphql
mutation SubmitSurvey {
  submitSurvey(
    data: {
      surveySlug: "customer-satisfaction"
      respondentName: "Valeriya"
      respondentEmail: "test@example.com"
      metadata: { source: "web" }
      answers: [
        { questionId: "1", choiceIds: ["1"] }
        { questionId: "2", choiceIds: ["4", "5"] }
        { questionId: "3", textValue: "Интерфейс удобный" }
        { questionId: "4", numberValue: 9.5 }
        { questionId: "5", booleanValue: true }
      ]
    }
  ) {
    ok
    message
    submission {
      id
      respondentName
      submittedAt
    }
  }
}
```

## Развертывание в GitHub

1. Создать новый пустой репозиторий.
2. Инициализировать Git локально:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
   git push -u origin main
   ```
3. Скопировать ссылку на репозиторий и вставить её в приложение курсовой работы.

## Примечание

Проект ориентирован на учебную демонстрацию проектирования БД и GraphQL API. По умолчанию используется SQLite, однако модели и слой доступа к данным спроектированы так, чтобы проект можно было перенести на PostgreSQL без изменения GraphQL-контракта.
