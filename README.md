# Flask Media Storage

The Media Storage Flask Application is a web-based tool that allows users to store images and videos on a server, edit them in size and watermark, and generate thumbnails for videos.

### Getting Started

To get started with the Media Storage Flask Application, follow these steps:

1. Clone the repository from GitHub using git clone `https://github.com/M4p4/flask-media-storage.git`
2. Install the necessary dependencies by running `pip install -r requirements.txt`.
3. Run the application using `FLASK_DEBUG=1 flask run -p 3000`.
4. Run background worker for image / video progressing with `celery -A app.celery worker --loglevel=info`.

### Config

In the `config.py` file in the root dir you can configurate image and video settings. You also need to set there an AUTH_KEY because every request needs the AUTH_KEY as param.

There tons of config options in the config file like sizes and quality.

### Add Video / Image

To add an Video or Image to the storage you call the `/media` (http://127.0.0.1:3000/media for local) route with a `POST` request.

The following params are needed

```
file - byte array - the file the user uploaded (can be empty)
url - string -  if file is empty and url is given, it downloads file from url
id - string - an id from backend
filename - string - filename from backend can be also a random genrated string
use_watermark - boolean - use watermark in image or video
media_type - string - "video" or "image"
auth - string - AUTH_KEY
```

As result you get an UID, that can be used to check the status on the `/status/<uid>` route.

### Delete Video / Image

Send a `DELETE` request to `/image/<uid>` or `/video/<uid>` route, with AUTH_KEY as param as `auth`. This will result in deleting all files related to the UID (Images, Videos and Thumbnails).
