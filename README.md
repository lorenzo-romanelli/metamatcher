# Metamatcher

Metamatcher is a prototype web app for interactive metadata matching of sound recordings. It consists of a SPA and an API to load,
compare, and choose which recordings match other recordings, according to their metadata (artist name, song title, 
[ISRC](http://isrc.ifpi.org/en/), duration).

It uses Django for the backend and Vue.js for the frontend.

## Setup
### Prerequisites

For the app to work, you should have the `postgresql` and `virtualenv` packages installed on your machine. If you don't,
in Ubuntu you can do so from the terminal by using `apt-get` (or any other package manager of your choice):
``` bash
$ sudo apt-get install postgresql virtualenv
```

### Creating the database
Before installing the app, you have to create the PostgreSQL database on your local machine.

Log in to PostgreSQL:
``` bash
$ psql -U <username> -h localhost
```
where `<username>` is the name of your PostgreSQL user. PostgreSQL should ask you to type in your password. If not, add
the `-W` flag to the same previous command.

Once you are logged in, you can create the database directly from the `psql` shell by copy-pasting the following command:
``` sql
CREATE DATABASE metamatcher;
```

If the command fails, make sure that your PostgreSQL user has the right permissions to create the database.

### Installation
To install the app, move into the root directory of the project. Then, run the following commands to create 
and activate a virtual environment, as well as for installing the required Python packages:
```
$ virtualenv .
$ source bin/activate
$ pip install -r requirements.txt
```

One last step! We need to tell Django which are the credentials for accessing the database. To do so, open the file
`settings.py` (you will find it in the directory `/app/metamatcher`), and go to lines 80 to 89:
``` python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'HOST': 'localhost',
    'NAME': 'metamatcher',
    'USER': '',
    'PASSWORD': '',
    'PORT': 5432,
  }
}
```
Here, change the values of `'USER'` and `'PASSWORD'` to your PostgreSQL credentials (the same you used when creating the
database).

That's it! The app is ready to be used.

## Initializing the database
The script contained into the file `/app/init_db.py` takes care of creating the required tables in the database,
and of populating them with the metadata contained into some input reports. Such reports are stored into `/app/reports/`.
The script also calculates and stores the matching values for the recordings.

To run it, refer to the following commands (make sure your virtual environment is active!):
``` bash
$ cd app
$ python init_db.py
```

If everything went good, you should see some output messages on your terminal indicating that the imports were succesful.

## Using the app
In order to use the application from your browser, start Django's own development
server with your virtual environment activated:
``` bash
$ cd fullstack-developer-test/app
$ python manage.py runserver
```

Now open your browser and navigate to `http://localhost:8000`, where you will be presented with the UI of
the application.

On the left column, you have the list of the input reports. Select one of them, and on the right you'll see the candidates found
in the database that are the most similar to the one you selected.
The colored dot next to each to each result indicates the similarity between that recording and the one you selected (green =
very similar, yellow = similar enough, red = not so similar). If you hover on the dot with the mouse, it will also show you the
similarity percentage.

Once you have chosen the right candidate (if any), the button at the bottom will be activated and you can submit your choice.
The input recording will be also removed from the list.
