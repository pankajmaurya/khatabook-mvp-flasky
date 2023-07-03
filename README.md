# khatabook-mvp-flasky

To wipe off previous db:
```
rm -rf instance/ migrations/ __pycache__/
```

To reinit the db and start dev server
```
flask db init
flask db migrate -m "init db"
flask db upgrade
flask --app app run
```