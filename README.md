
## planet-rolodex

Demo for running simple REST service for users and groups
illustrating one-to-many relationships

### Requirements/Installation

* Python:

```
pip install flask
pip install psycopg2
pip install pytest
```

* Postgres (assumes localhost:5432)

 - create demo [super]user `planet:planet`; this will prompt for pass:

```
    createuser planet -s -d -w -h localhost -P
```

 - optionally, verify user & perms with a login and run `\du`

```
    $> psql -U planet -h localhost -d postgres -W
```

 - run the migrate:
```
    (planet@localhost:5432) [postgres] > \i sql/migrate-01.sql
    (planet@localhost:5432) [postgres] >  COMMIT;
```

 - optionally, add some demo-data:

```
    (planet@localhost:5432) [postgres] > \i sql/demo-data.sql
    (planet@localhost:5432) [postgres] >  COMMIT;
```

### Running the app

```
python rolodex.py
```

This will start an HTTP server on default port 5000.
If the demo data was loaded, basic queries should already work:

```
    curl -si localhost:5000/users/alice
    curl -si localhost:5000/groups/admin
```


### Testing

```
    py.test
```

### Ceveats

Warts 'n all here.  Due to timeboxing (and rat holeing!), a few issues and ruminations:

* lots of exceptions not handled, but fully recognized

* the use of `res = {}` throughout endpoints is left as scaffold (ie. sloppy).
  imho, ideally, with a bit more time, there should be an object returned like:

    `{ "meta":{ "rc":"ok"}, "data": [...]}`

 or

    `{ "meta":{ "rc":"err", "errors":["missing arg"]}, "data": []}`

* use of a single DB for test / prod is considered OK for this PoC here & now

* solution as NoSQL was first round.  That was easily 3x the code.

* tried to use ArangoDB, but as a n0ob, too much time to get up to speed 
  (various issues with Python client did not help....)


