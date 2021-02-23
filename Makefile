up:
	docker-compose up

manage:
	docker-compose run --rm api python manage.py ${c}

makemigrations:
	docker-compose run --rm api python manage.py makemigrations

migrate:
	docker-compose run --rm api python manage.py migrate

tox:
	docker-compose run --rm api tox ${c}

loaddata:
	docker-compose run --rm api python manage.py loaddata initial_data.json