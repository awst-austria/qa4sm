# QA4SM webapp / Valentina developers' guide

## Get source code

Check out the QA4SM source code from [GitHub](https://github.com/awst-austria/qa4sm).

- Use the following command for anonymous checkout:

        git clone https://github.com/awst-austria/qa4sm.git

- Use the following command if you have your ssh key set up in GitHub already:

        git clone git@github.com:awst-austria/qa4sm.git

This creates the qa4sm folder. Within this are the webapp folders:

    valentina
    validator

If you want to work on QA4SM releases, be sure to use the git hooks in the `hooks` folder (for remembering to tag correctly). Either copy the scripts in that folder to `.git/hooks/` or [set your custom hooks directory to 'hooks'](https://stackoverflow.com/questions/427207/can-git-hook-scripts-be-managed-along-with-the-repository/37861972#37861972).

To fetch the test data necessary for the unit tests into the `testdata` folder:

    git submodule init
    git submodule update

## Minimum requirements

- Git client
- Miniconda (Python 3.6)

## Optional dependencies

- Redis (for Celery)
- RabbitMQ (for Celery)
- Postgres database (instead of SQlite default)

## Integrated Development Envionment

It's up you which Python IDE you want to use for development.

We use Eclipse with PyDev. Since Django templates consist of HTML and JavaScript, the [Eclipse IDE for JavaScript and Web Developers](https://www.eclipse.org/downloads/packages/release/2018-09/r/eclipse-ide-javascript-and-web-developers) can be helpful. If you want to use Eclipse, you should probably check what the latest version is and use that.

To install PyDev, use Eclipse's `Help > Install New Software...` menu and the PyDev update URL `http://www.pydev.org/updates`. [PyDev install manual](http://www.pydev.org/manual_101_install.html).

To add the webapp project to Eclipse, use `File > Import > General > Existing Projects into Workspace` and set the root directory to your qa4sm folder.

In case you don't want to use Eclipse, one alternative is [PyCharm](https://www.jetbrains.com/pycharm/).

## How to set up development environment

TLDR: download and install Miniconda and use the official environment file to create a conda environment. Optionally set up the backend services - if you want to work on the parallelisation part of the webapp or test with the 'real' database system. If you don't, you don't need to install any services, only conda. You can also start with the easy installation and add the services later on.

## Install required development tools

### git
Ubuntu/Debian:

    sudo apt install git
SUSE:

    sudo zypper install git

### Miniconda

Get latest Miniconda (Python 3) from <https://repo.continuum.io/miniconda/>. For 64bit Linux, use <https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh>.

Run installer, e.g.

    bash Miniconda3-latest-Linux-x86_64.sh -b -p <MINICONDA_INSTALL_PATH>

## Install optional tools

**Note:** If you don't install Redis and RabbitMQ, you've got to set the corresponding Celery config variable - see "Create webapp configuration file" below.

### rabbitmq-server
Ubuntu/Debian:

    sudo apt install rabbitmq-server
SUSE:

    sudo zypper install rabbitmq-server

Logs are in `/var/log/rabbitmq`

You may have to edit `/etc/hosts` and add you hostname as an alias for 127.0.0.1 like this ([see also](https://serverfault.com/questions/235669/how-do-i-make-rabbitmq-listen-only-to-localhost)):

    127.0.0.1	qa4sm

Start RabbitMQ, e.g. with:

    sudo rcrabbitmq-server start

### redis

Ubuntu/Debian:

    sudo apt install redis

SUSE:

    sudo zypper install redis

Follow instructions in `/usr/share/doc/packages/redis/README.SUSE`.
In order to check the redis log, use

    journalctl --since today

Start redis, e.g. with:

    sudo systemctl restart redis.target

### Postgresql server

Ubuntu/Debian:

    sudo apt install postgresql postgresql-contrib

Start with:

    sudo service postgresql restart

SUSE:

    sudo zypper postgresql-server postgresql

Edit `postgresql.conf` and `pg_hba.conf` in `/var/lib/pgsql/data`:

- `postgresql.conf`: comment in `listen_addresses`, `port`, set `log_directory` to `/var/log/postgresql/` (create that directory and give it to postgres user), comment in `log_filename`, `log_rotation_size`, and `log_file_mode`.
- `pg_hba.conf`: Set method to `trust` for `127.0.0.1/32`, `::1/128`, and `local`.

(Re)start postgres server with:

    sudo rcpostgresql restart

Set password for database root user:

    su - postgres
    psql
    \password postgres

Create webapp database and user:

In the qsql shell, run the commands from `[gitrepos]/sql/create_postgres_db.txt`

    CREATE DATABASE valentina;
    CREATE USER django WITH PASSWORD 's3cr3t';
    ALTER ROLE django SET client_encoding TO 'utf8';
    ALTER ROLE django SET default_transaction_isolation TO 'read committed';
    ALTER ROLE django SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE valentina TO django;

## Create conda Python virtual environment

Change into your cloned qa4sm directory and create an environment with:

    conda env create -f environment/qa4sm_env.yml -n valentina

Then activate it with:

    conda activate valentina

## Create webapp configuration file

In your cloned qa4sm directory run:

    ./init_config.sh dev

This should create `valentina/settings_conf.py` from the template in `settings_example_conf.py`.

If the `init_conig.sh` doesn't work for you, copy `settings_example_conf.py` into the `valentina` subfolder yourself and set the variables appropriately.

Adapt the `valentina/settings_conf.py` to match your local configuration:

- If you didn't set up your own Redis and RabbitMQ, add below the other CELERY settings: `CELERY_TASK_ALWAYS_EAGER = True` and `CELERY_TASK_EAGER_PROPAGATES = True`. This means that Celery jobs will be processed sequentially (not in parallel) - but you don't have to set up the services.
- Use `DBSM = 'postgresql'` and `DB_PASSWORD = ...` if you've set up a local postgresql database. The rest of the database configuration is in `valentina/settings.py` and ideally should be left unchanged.
- Set `EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'` to tell Django to log emails to files instead of trying to send them. Use `EMAIL_FILE_PATH = ...` to tell Django where to put the email files.
- Set the `LOG_FILE` location to where you want the log files to be written to.
- If you want to publish to the Zenodo sandbox (test environment) with your installation, set the `DOI_ACCESS_TOKEN_ENV` variable to a valid Zenodo sandbox token. To get a token, register an [account with Zenodo sandbox](https://sandbox.zenodo.org/) and [create a token](https://sandbox.zenodo.org/account/settings/applications/tokens/new/).

Make sure the `LOG_FILE` folder defined in your settings exist in your system, otherwise, the `Init Django` section of this guide will throw an error.

## Init Django

Go to your qa4sm folder and init the database and the static files:

    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic

The first of these will prepare the migration, the second will apply it (and should result in a list of things applied with OK at the end of each line), the third will result in copying of files.

Create admin user for webapp:

    python manage.py createsuperuser

Keep note of the username, email, and password you enter here, you'll need it to log into the webapp later. This should result in the message "Superuser created successfully."

Populate the database with information about the datasets:

    python manage.py loaddata versions variables filters datasets networks

This should result in the message "Installed x object(s) from y fixture(s)".

### Start necessary servers

If you haven't set up Postgres, Redis, and RabbitMQ, skip to the next section.

If you've installed those services on your machine, you can (re)start them with:

    sudo rcrabbitmq-server start
    sudo systemctl restart redis.target
    sudo rcpostgresql restart

Start a celery worker with the shell script:

`./start_celery_worker.sh`

### Run Django development server

Run the following:

    python manage.py runserver

Check the output of this command for the URL to point your browser to - e.g. <http://127.0.0.1:8000/>.

Now you should be able to see the landing page. You can log in with the admin user you created in section "Init Django".

You can access the webapp's admin panel by appending "admin/" to the URL, e.g. <http://127.0.0.1:8000/admin/>. There you can create more users by clicking "Add" next to the "Users" row.

Depending on the `LOG_FILE` setting in your `settings_conf.py` file, the webapp's logfile should be written to `valentina.log`. If you encounter problems, check this log and the command line output of the Django server.

If, when you try to log in, you get a verification failed error, try going to `valentina/settings.py` and commenting out the `CSRF_COOKIE_SECURE` setting. Then log in again.

## Specifying location of datasets

If you want to try out or host QA4SM beyond running the integration tests, you can use your own data if you make the data locations known to the app. There's an interactive Django command that will prompt you for the data locations:

    python manage.py setdatasetpaths

With it, you can change all dataset paths or just the datasets that don't have a path set yet. You can optionally give a parent data folder from which the dataset subfolder names will be guessed and suggested. If you don't give a parent data folder, the suggestion will be the currently set path (if one is set) - this is useful if you want to change only a few of the paths and just skip over the others.

The folders are used in `validator.validation.readers.create_reader` to create the necessary data readers. The general folder structure is `<dataset_name>/<version_name>`, using the names in the webapp database. As always, capitalisation makes a difference ;-)

## Webapp walkthrough

The code for the webapp lives in two submodules of the your qa4sm folder: `valentina` and `validator`. The first contains the Django "project", the second the Django "app" - [see here for the Django tutorial that explains projects and apps.](https://docs.djangoproject.com/en/2.1/intro/tutorial01/)

The `valentina` module exists to conform to the Django structure. It contains mainly configuration in `settings.py`, `settings_conf.py`, `celery.py`. Most of the interesting stuff is happening in the `validator` module.

### Contents of the validator module

Module|Functionality
--- | ---
admin|Customisations of the webapp’s admin pages, e.g. controls to activate new users.
fixtures|Settings relating to the datasets used in the webapp.
formats|Changes to date formats so that most international date formats are accepted by webapp.
forms|Python representations of the forms used by the main webapp (not admin forms, those are in admin). HTML templates are in templates, see below.
management| Customised Django commands that can be passed to `manage.py` on the command line, similar to the standard `runserver` or `makemigration`.
migrations|Django migrations that create and update the app’s database. If you want to learn about migrations, [see here](https://docs.djangoproject.com/en/2.1/topics/migrations/).
models|Domain objects of the app. Django will automatically create database tables and rows for these classes and instances (if used correctly).
static|Static files the webapp delivers to the client as they are, such as JavaScript, CSS, fonts, and image files.
templates|Django templates – HTML files with special Django tags that can be used somewhat like a programming language. If you want to learn about Django templates, [see here](https://docs.djangoproject.com/en/2.1/topics/templates/).
tests|Unit and integration tests for the webapp, based on pydev and Django tests.
validation|Business logic of the app – code that sets up, runs, and stores pytesmo validations with Celery and produces plots afterwards.
views|Django views for the webapp. They define the behaviour of the app’s (sub)URLs: what happens if a specific subURL is accessed. Includes filling the templates with values. If you want to learn about Django views, [see here](https://docs.djangoproject.com/en/2.1/topics/http/views/).
|
apps.py|Django specific file that currently defines the name of the app.
hacks.py|Bin for hacks we have to use but rather wouldn’t. If you can, avoid creating those ;-)
mailer.py|Email functionality, including (for now) wording of the automatic emails sent by the app.
urls.py|Django specific file containing the mapping of URLs to views.

## How to run integration / unit tests

Go to to your qa4sm folder and run:

    pytest

## Set up front-end environment

Go to UI folder -> developers-guide.md

Congratulations, your development environment is now set up and you can develop ;-)

## Tips and Tricks

### Setting up cronjob for autocleanup

To have the `autocleanupvalidations` command called regularly, it's recommended to have a wrapper script that activates the conda environment and call it with cron. The default installation script installs a script to `/var/lib/qa4sm-web-val/valentina/run_autocleanup.sh`. If the paths in the script don't fit your installation, you'll have to edit them.

You can set up a cronjob for the user that runs the webapp as root like this:

    crontab -e -u www-data

    15 2 * * * /var/lib/qa4sm-web-val/valentina/run_autocleanup.sh

### Creating new environment file

If you need to create a new environment file with the latest dependencies, look at `environment/recreate_environment_file.sh`, edit it to include dependencies you want to add/update. Then run it - output should be an updated `environment/qa4sm_env.yml` file.

### Cartopy doesn't want to install

1. Make sure proj development files are installed with something like

        zypper install libproj-devel

    or

        apt-get install libproj-dev

1. If pip complains about PEP, add a parameter to ignore it

        pip install --no-use-pep517 cartopy

1. If the compiler complains about `ACCEPT_USE_OF_DEPRECATED_PROJ_API`, define this shell environment variable before running pip. Note that this is also included in the instructions above and in the installation script.

        export CFLAGS="-DACCEPT_USE_OF_DEPRECATED_PROJ_API_H=1"

    then run pip as above.

### Django migration tricks

To convert database content or fill the database with default entries, you can write your own data migrations, see [data migrations](https://docs.djangoproject.com/en/2.1/topics/migrations/#data-migrations).

In short:
Create an empty migration as a template to use

    python manage.py makemigrations --empty validator

and then add your data manipulation code into that file. You can also rename the file to make it more clear to other devs what's happening in it.

Example migration:


    from django.db import migrations

    def fill_progress(apps, schema_editor):
        ValidationRun = apps.get_model('validator', 'ValidationRun')

        for run in ValidationRun.objects.all():
            if (run.progress == 0) and (run.end_time is not None):
                run.progress = 100
                run.save()

    class Migration(migrations.Migration):

        dependencies = [
            ('validator', '0010_auto_20181030_1158'),
        ]

        operations = [
            migrations.RunPython(fill_progress),
        ]

#### Reset migrations

To recreate migrations from scratch:

Delete database?

Delete `validator/migrations`.

    python manage.py makemigrations validator

You should now have a new migration: `validator/migrations/0001_initial.py`

#### Squash migrations

Combine all migrations up to migration `x`:

    python manage.py squashmigrations validator x

The resulting `validator/migrations/0001_squashed_...` file contains a list `replaces = [...]` in the `Migration` class that details the other migrations it replaces. If you want to use a "from-scratch" migration (see above), you can copy the `replaces` list into that and it should be treated like a squashed migration.

#### Dump ops db

And omit stuff that creates problems on import:

    python manage.py dumpdata --exclude=auth --exclude=contenttypes > ~/dbdump.json


### Postgres tricks

Connect to Postgres database with command line client:

    psql -U postgres valentina

List all tables:

    \dt

Delete the contents of a list of tables (but not the tables themselves) and all other rows that depend on the deleted rows:

    TRUNCATE TABLE validator_dataset, validator_dataset_filters, validator_dataset_variables, validator_dataset_versions, validator_datasetversion, validator_datavariable CASCADE;

Delete tables and all other tables that depend on them:

    DROP TABLE validator_dataset, validator_dataset_filters, validator_dataset_variables, validator_dataset_versions, validator_datasetversion, validator_datavariable CASCADE;

Quit connection:

    \q

### Data model visualisation tricks

Django will create pretty graphs visualising your data models if you ask nicely:

1. Install `graphviz-devel` package in your operating system (and graphviz, of course, if it isn't already installed).
1. `pip install pygraphviz`
1. `pip install django-extensions`
1. Add `'django_extensions'` to `INSTALLED_APPS` in `settings.py`.
1. Run `python manage.py graph_models -a -g -o my_project_visualized.png`
1. Look at `my_project_visualized.png`.

To get a graph of the valiator app excluding some admin classes:

    python manage.py graph_models -g -X "Settings,User,AbstractUser" -o validator.png validator

To get an editable dot file of the above graph:

    python manage.py graph_models -g -X "Settings,User,AbstractUser" validator > validator.dot

To get from the dot file to a png file (presumably after editing):

    dot -Tpng validator.dot -o validator.png

Possible changes to the diagram:

- Removing arrowheads: `arrowhead=none arrowtail=none` [in the `// Relations` section at the end of the dot file]
- Change lines: edit `splines  = ...` [at the top of the file]. For options see `man dot`; least ugly results with `splines = polyline` or `splines = true`.
- Add labels to start/end of lines: edit label to add `[label="ref_filters" headlabel="start" taillabel="end"]`

For further hints see <https://django-extensions.readthedocs.io/en/latest/graph_models.html>.


### Fixtures

#### Create fixtures

[Fixtures documentation](https://docs.djangoproject.com/en/2.1/howto/initial-data/#providing-data-with-fixtures).

Dump database contents into separate files for readability:

    python manage.py dumpdata validator.DataVariable > variables.json
    python manage.py dumpdata validator.DatasetVersion > versions.json
    python manage.py dumpdata validator.DataFilter > filters.json
    python manage.py dumpdata validator.Dataset > datasets.json

Put json files into `validator/fixtures/` (and pretty-print them with an editor for better readability).

#### Apply fixtures

Set up database contents with the fixtures:

    python manage.py loaddata versions variables filters datasets

### Database bulk changes

To assign validation runs to a specific user in bulk:

    python manage.py shell

    from validator.models import ValidationRun
    from validator.models import User
    myuser = User.objects.get(username='admin')
    for run in ValidationRun.objects.all():
        run.user = myuser
        run.save()

### Secrets / tokens in continuous builds

#### In Jenkins

Use the `Credentials` menu entry to add a new credential and select `Secret text` as type. Put your token into the `Secret` field and name / describe it as you wish. You can then use it in your build job's configuration page by going to `Build Environment` and checking `Use secret text(s) or file(s)`. This allows you to bind your secret text to an environment variable. Jenkins will set that env variable before running the build and you can use it inside your scripts.

For example, to keep the Zenodo access token secret, put it into Jenkins and bind the secret text to variable `DOI_ACCESS_TOKEN_ENV`. The `init_config.sh` script will inject it into the django config.

#### In Travis

Similar to Jenkins - see [Defining Variables in Repository Settings](https://docs.travis-ci.com/user/environment-variables/#defining-variables-in-repository-settings) and [go to the settings page](https://travis-ci.com/github/awst-austria/qa4sm/settings) to set environment variables. Then use in your script as an environment variable.

You could also try [Defining encrypted variables in .travis.yml](https://docs.travis-ci.com/user/environment-variables/#defining-encrypted-variables-in-travisyml) but I never managed to get it to work.

#### Don't leak the secrets!

Travis docs have general [Recommendations on how to avoid leaking secrets to build logs](https://docs.travis-ci.com/user/best-practices-security/#recommendations-on-how-to-avoid-leaking-secrets-to-build-logs).
If you accidentally leak a secret, repair the leak and generate a new secret, e.g. a new API token for Zenodo.

### Debugging unit tests
Coverage report is enabled by default for tests which makes it impossible to debug unit tests. In case you need to debug a unit test update the `pytest.ini` file with the followings:
`addopts = --tb=short --verbose --junitxml=junit.xml -m "not long_running and not needs_advanced_setup"`
