celery -A project_name worker -l info
celery -A project_name beat -l info
flower -A project_name