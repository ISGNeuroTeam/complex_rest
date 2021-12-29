cd `dirname "${BASH_SOURCE[0]}"`/../../complex_rest/
celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler > logs/celery_beat.log 2>&1 &
celery -A core worker --loglevel=INFO > logs/celery.log 2>&1 &