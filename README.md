# math-problems-platform
Written in Python using Django. Tomasz Nowak, Michał Staniewski.

## Example setup

Start off by creating the database, initializing the example setup
``` sh
python manage.py migrate
python manage.py shell < testing/init_db.py
```

Now you can run the server.
``` sh
python manage.py runserver localhost:8000
```

Go to `localhost:8000` in your browser, and login onto your Google account.

You may quit the server with ctrl + c. After creating your user, you can make yourself staff by
``` sh
python manage.py shell < testing/make_staff.py
```

Restart the server, and test it :)
