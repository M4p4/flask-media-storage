# Flask Media Storage

TODO

#### To run FMS locally use the following command:

```
1 - FLASK_DEBUG=1 flask run -p 3000
2 - celery -A app.celery worker --loglevel=info
```

```
celery -A app.celery purge -f
```
