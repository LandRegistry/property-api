# property-api

This repository contains a Python3-based Flask application structured in the way that all
Land Registry Flask APIs should be structured going forwards.

## Available routes

|Route|What it does|
|---|---|
|**GET** /health|Returns some basic information about the app (JSON)|
|**GET** /health/cascade/\<depth\>|Returns the app's health information as above but also the health information of any database and HTTP dependencies, down to the specified depth (JSON)|
|**GET** /v1/properties/\<uprn\>|Returns a summary of what is availble for the given UPRN|
|**GET** /v1/properties/\<uprn\>/deeds|Returns a list of all deeds for the UPRN, in JSON format|
|**GET** /v1/properties/\<uprn\>/deeds/\<deed_id\>|Returns a specific deed, in JSON format|
|**GET** /v1/properties/\<uprn\>/landregisters|Returns a list of Registers for the given UPRN, in JSON format|
|**GET** /v1/properties/\<uprn\>/con29|Returns a CON29 search for the given UPRN, in JSON format|

## Data

Sample data is required but not provided here.
Data should be placed in `property_api/data` and should be structured as shown:
```
/data
  properties.json (maps UPRNs to addresses, lists of Title Numbers and Deed IDs)
  /title-number1
    title-number1.json (register)
    /deeds
      deed_id1.json
      deed_id2.json
  /title-number2
    title-number2.json (register)
    /deeds
      deed_id3.json
  /CON29
    con29_id1.json
    con29_id2.json
(etc.)
```

## Quick start


### Docker

This app supports the HM Land Registry universal dev-env, if using this adding the following to your dev-env config file is enough:

```YAML
  property-api:
    repo: git@github.com:LandRegistry/property-api.git
    branch: develop
```

The Docker image it creates (and runs) will install all necessary requirements and set all environment variables for you.

### Standalone

#### Environment variables to set

* PYTHONUNBUFFERED *(suggested value: yes)*
* PORT
* LOG_LEVEL
* COMMIT
* APP_NAME

##### When not using gunicorn

* FLASK_APP *(suggested value: property_api/main.py)*
* FLASK_DEBUG *(suggested value: 1)*

#### Running (when not using gunicorn)

(The third party libraries are defined in requirements.txt and can be installed using pip)

```shell
python3 -m flask run
or
flask run
or
make run
```

## Testing

### Unit tests

The unit tests are contained in the unit_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for unit testing. To run the tests use the following command:

```bash
make unittest
(or just py.test)
```

To run them and output a coverage report and a junit xml file run:

```bash
make report="true" unittest
```

These files get added to a test-output folder. The test-output folder is created if doesn't exist.

You can run these commands in the app's running container via `docker-compose exec property-api <command>` or `exec property-api <command>`. There is also an alias: `unit-test property-api` and `unit-test property-api -r` will run tests and generate reports respectively.

### Integration tests

The integration tests are contained in the integration_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for integration testing. To run the tests and output a junit xml use the following command:

```shell
make integrationtest
(or py.test integration_tests)
```

This file gets added to the test-output folder. The test-output folder is created if doesn't exist.

To run the integration tests if you are using the common dev-env you can run `docker-compose exec property-api make integrationtest` or, using the alias, `integration-test property-api`.

## Application Framework implementation

### Universal Development Envionment support

Provided via `configuration.yml`, `Dockerfile` and `fragments/docker-compose-fragment.yml`.

`configuration.yml` lists the commodities the dev env needs to spin up e.g. postgres. The ELK stack is spun up when "logging" is present.

The `docker-compose-fragment.yml` contains the service definiton, including the external port to map to, sharing the app source folder so the files don't need to be baked into the image, and redirection of the stdout logs to logstash via syslog.

The `Dockerfile` simply sets the APP_NAME environment variable and installs the third party library requirements. Any further app-specific variables or commands can be added here.

### Logging in a consistent format (JSON) with consistent content

Flask-LogConfig is used as the logging implementation. It is registered in a custom extension called `enhanced_logging`. There is also a filter that adds the current trace id into each log record from g, and a formatter that puts the log message into a standard JSON format. The message can then be correctly interpreted by both the dev-env and webops ELK stacks. The configuration that tells Python logging to use those formatters and the filter is also set up in `enhanced_logging`.

### Consistent way to run the application

`main.py` imports from `app.py` in order to trigger the setup of the app and it's extensions. It also provides the app object to `manage.py`.

`manage.py` contains the app object which is what should be given to a WSGI container such as gunicorn. It is also where Alembic database migration code is to be placed.

All Flask extensions (enhanced logging, SQLAlchemy, socketIO etc) shoud be registered in `extensions.py`. First they are created empty, then introduced to the app in the `register_extensions()` method (which is then called by `main.py` during initialisation).

### A Makefile with specific commands to run unit tests and integrations tests

`Makefile` - This provides generic language-independent functions to run unit and integration tests  (useful for the build pipeline).

### Consistent Unit test and integration test file structure

Provided via `unit_test` and `integration_test` directories. These locations do not have an `__init__.py` so the tests cannot be accidentally imported into other areas of the app. This links in with the management script as it expects the tests to be in these locations. The file `setup.cfg` also contains the default test entry point and coverage settings.

### An X-API-Version HTTP header returned in all responses detailing the semantic version of the interface

Provided by the `after_request()` method in `app.py`. The exact version of the API interface spec is returned, in case clients need to know (the URL will only contain the major version as per the API manual).

### An X-Trace-ID HTTP header received/generated and then propagated

Provided by the `before_request()` method in `main.py` in the enhanced_logging custom extension. If a header of that name is passed in, it extracts it and places it into g for logging (see next section) and also creates a requests Session object with it preset as a header. This allows the same value to propagate throughout the lifetime of a request regardless of how many UIs/APIs it passes through - making debugging and tracing of log messages much easier.

Note that for the propagation to work, g.requests must be used for making calls to other APIs rather than just requests.

### Consistent error response structure (but not content)

In `exceptions.py` there is a custom exception class ApplicationError defined, which can be raised by applications that need to send back details of an error to the client. There is a handler method defined that converts it into a consistent response, with JSON fields and the requested http status code.

There is also a handler method for any other types of exception that manage to escape the route methods. These are always http code 500.

Both handlers are registered in the `register_exception_handlers()` method, which is called by main.py in a similar way to registering  blueprints.

### Consistent environment variable names

All config variables the app uses are created in `config.py`. It is a plain python module (not a dict or object) and no region-specific code. The mandatory variables are `FLASK_LOG_LEVEL` (read by Flask automatically), `COMMIT` and `APP_NAME` (both used in the health route).

This should be the only place environment variables are read from the underlying OS. It is effectively the gateway into the app for them.

### Consistent implementation of health and cascading health endpoints

Routes are logically segregated into separate files within `/views`. By default a `general.py` is provided that creates the health routes (see table above) that returns a standardised set of JSON fields. Note how the app name is retrieved using the APP_NAME config variable (which in turn comes from the environment).

Blueprints are registered in the `register_blueprints` method in `blueprints.py` (which is then called by `main.py` during initialisation).
