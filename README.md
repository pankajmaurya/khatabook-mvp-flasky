# khatabook-mvp based on Flask

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

## Things to do when going live with something like this

* Figure out how to make this mobile devices friendly (DONE)
* Do a security assessment
* Establish data governance (take backup periodically)
* Write a runbook for debugging issues like internal server errors (where are logs? Will there be any metrics?)
* Perhaps restructure this into blueprints and add manage.py to allow running a shell and doing db operations. Will improve support ability to fix things.

## Testing locally
The db is already pushed with one test account : <8800.....9> / foo

## Tools
https://www.easyhindityping.com/
