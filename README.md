# Foodgram

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
