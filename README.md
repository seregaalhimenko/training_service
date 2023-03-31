[Посмотреть Api](https://seregaalhimenko.github.io/training-service_swager/)
# Training service
Реализован обучающий сервис. В общем виде выглядит, как список тем, где каждая тема содержит теоретический отрывок и тест. Тест состоит из нескольких вопросов. Каждый вопрос состоит из утверждения и нескольких вариантов ответов. Правильных ответов может быть несколько. На каждый вопрос пользователь отвечает последовательно, и после каждого ответа получает результат: правильно он ответил или нет. Если ответил неправильно, также получает комментарий.

После прохождения всего теста пользователь получает общую статистику: на сколько вопросов ответил правильно и сколько неправильно. Один и тот же тест можно проходить только 1 раз. После прохождения теста пользователю на email отправляется письмо с результатом.
## Запуск
сборка

`docker-compose build`

после запуск

`docker-compose up`

или собрать и запустить сразу

`docker-compose up --build`

Для настройки нужно изменить файл `project/project/settings.py `  

```python
#Секретный ключ для конкретной установки Django. 
#Используется для предоставления криптографической подписи
#и должно быть установлено уникальное, непредсказуемое значение.
SECRET_KEY = os.environ.get("SECRET_KEY")

#Логическое значение, которое включает/выключает режим отладки.
DEBUG = True

#Имена хостов/доменов, которые может обслуживать этот сайт Django
ALLOWED_HOSTS = []

#Модель, используемая для представления пользователя
AUTH_USER_MODEL = "users.User"

#Список строк, обозначающих все приложения, включенные в этой установке Django
INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"users.apps.UsersConfig",
	"rest_framework",
	"rest_framework.authtoken",
	"djoser",
	"training_service",
	"drf_spectacular",
]

#Настройки DRF 
REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.TokenAuthentication",),
	"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
	"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
	"PAGE_SIZE": 10,
}

#Настройки для drf-spectacular
SPECTACULAR_SETTINGS = {
	"TITLE": "Training service API",
	"DESCRIPTION": "Your project description",
	"VERSION": "1.0.0",
	"SERVE_INCLUDE_SCHEMA": False,
}

#Список промежуточного программного обеспечения для использования
MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

#Строка, представляющая полный путь импорта Python к вашей корневой конфигурации URL
ROOT_URLCONF = "project.urls"

#Список, содержащий настройки для всех механизмов шаблонов, 
#которые будут использоваться с Django. 
#Каждый элемент списка представляет собой словарь, 
#содержащий параметры для отдельного движка.
TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.debug",
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
			],
		},
	},
]
#Полный путь Python к объекту приложения WSGI, 
#который будут использовать встроенные серверы Django
WSGI_APPLICATION = "project.wsgi.application"

#Настройки базы данных 
DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.postgresql",
		"NAME": os.environ.get("POSTGRES_NAME"),
		"USER": os.environ.get("POSTGRES_USER"),
		"PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
		"HOST": os.environ.get("POSTGRES_HOST", "localhost"),
		"PORT": os.environ.get("POSTGRES_PORT", "5432"),
	}
}

#Список валидаторов, которые используются для проверки надежности паролей пользователей
AUTH_PASSWORD_VALIDATORS = [
	{
		"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
	},
]

#Строка, представляющая код языка для этой установки
LANGUAGE_CODE = "en-us"

#Строка, представляющая часовой пояс для этой установки
TIME_ZONE = "UTC"

#Логическое значение, указывающее, 
#следует ли включить систему перевода Django. 
#Это дает возможность отключить его для повышения производительности. 
#Если установлено значение `False`, 
#Django выполнит некоторые оптимизации, чтобы не загружать механизм перевода.
USE_I18N = True

#Логическое значение, указывающее, будет ли datetime учитывать часовой пояс по умолчанию или нет
USE_TZ = True

#URL-адрес для использования при обращении к статическим файлам, 
#расположенным в `STATIC_ROOT`.
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
#Настройки smtp
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

*Если используете Docker не забудьте изменить и файлы **Dockerfile, docker-compose.yml***
## Немного о приложении
**Функциональные части сервиса:**

-   **Регистрация пользователей через email;**
   
-   **Аутентификация пользователей;**
    
-   **Список тем, выбор темы, изучение материала, тестирование, результат;**
    
-   **Отправка на почту результата тестирования;**
    
-   **Админка. Стандартная админка Django. Разделы:**
    -   **Раздел информации о пользователях (+ кривая  статистика).**
    -   **Раздел создания вопросов:**
        -   **Возможность создавать темы, тесты, вопросы с вариантами ответов (+указание правильных ответов);**
        -   **Валидация вопросов на внесение минимум одного правильного ответа.**
        -   **Удаление вопросов;**
        -   **Редактирование вопросов (редактирование текста вопроса, количества ответов и количество верных ответов);**
    -   **Раздел с результатами;**
   
-   **Стек реализации: Python, Django, REST API, Postgres,Poetry;**
-   **Документация API  в Swagger (/docs/schema/swagger-ui/) или Redoc (/docs/schema/redoc/) ;**
-   **Список всех зависимостей  храниться в pyproject.toml;**
