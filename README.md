Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

Сервер доступен по адресу http://84.201.152.190

Администратор
Почта: makskol43@gmail.com
Пароль:qwerty

## Установка

### Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:heydolono/foodgram.git
```
```
cd foodgram
```
### Запустить Docker Compose и заполнить данные:
```
docker compose up -d
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py load_data ingredients.csv
```
## Примеры запросов к API и ответов
### Доступно на http://localhost/api/docs/