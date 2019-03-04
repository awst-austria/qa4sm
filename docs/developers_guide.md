# QA4SM webapp / Valentina developers' guide

## Minimum requirements

- Git client
- Miniconda (Python 3.6)

## Optional dependencies

- Redis (for Celery)
- RabbitMQ (for Celery)
- Postgres database (instead of SQlite default)

## How to set up development environment

Note: The environment setup is automated for the production environment in [environment/create_conda_env.sh]. This guide describes how to do a similar setup on your development machine. If you suspect this guide is not up to date, check the script and see if it has steps that may be missing here.

If you've got a Linux system, you can also try to run the `create_conda_env.sh` script on your system to create the conda environment. You've got to set 4 shell variables before running the script and point them to 4 directories on your system:

    export INSTALL_DIR="<install_dir>"
    export MINICONDA_PATH="<conda_dir>"
    export TOOL_DIR="<tools_dir>"
    export PYTHON_ENV_DIR="<pytenv_dir>"

Where `<install_dir>` is the place you want to put the webapp git sandbox, `<conda_dir>` is the place you want to install miniconda, `<tools_dir>` is the place you want to store the downloaded install packages of conda and basemap, and `<pytenv_dir>` is the place you want to put the conda environment for the webapp.

### Install required development tools

**Note:** If you don't install Redis and RabbitMQ, you've got to set the corresponding Celery config variable - see "Create webapp configuration file" below.

#### git
Ubuntu/Debian:

    sudo apt install git
SUSE:

    sudo zypper install git

#### Miniconda

Get latest Miniconda (Python 3) from <https://repo.continuum.io/miniconda/>. For 64bit Linux, use <https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh>.

Run installer, e.g.

    bash Miniconda3-latest-Linux-x86_64.sh -b -p <MINICONDA_INSTALL_PATH>

### Install optional tools

#### rabbitmq-server
Ubuntu/Debian:

    sudo apt install rabbitmq-server
SUSE:

    sudo zypper install rabbitmq-server

Logs are in `/var/log/rabbitmq`

You may have to edit `/etc/hosts` and add you hostname as an alias for 127.0.0.1 like this ([see also](https://serverfault.com/questions/235669/how-do-i-make-rabbitmq-listen-only-to-localhost)):

    127.0.0.1	qa4sm

Start RabbitMQ, e.g. with:

    sudo rcrabbitmq-server start

#### redis

Ubuntu/Debian:

    sudo apt install redis

SUSE:

    sudo zypper install redis

Follow instructions in `/usr/share/doc/packages/redis/README.SUSE`.
In order to check the redis log, use

    journalctl --since today

Start redis, e.g. with:

    sudo systemctl restart redis.target

#### Postgresql server

Ubuntu/Debian:

    sudo apt postgresql postgresql-contrib

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

In the qsql shell, run the commands from `[gitrepos]/valentina/sql/create_postgres_db.txt`

    CREATE DATABASE valentina;
    CREATE USER django WITH PASSWORD 's3cr3t';
    ALTER ROLE django SET client_encoding TO 'utf8';
    ALTER ROLE django SET default_transaction_isolation TO 'read committed';
    ALTER ROLE django SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE valentina TO django;

### Create conda Python virtual environment

    conda create --yes -n valentina -c conda-forge python=3.6 numpy scipy pandas cython pytest pip matplotlib pyproj django pyresample pygrib
    source activate valentina

Download [matplotlib basemap](https://github.com/matplotlib/basemap/releases) and install:

    curl -Lo mpl_basemap.tar.gz https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz
    pip install mpl_basemap.tar.gz

Install other dependencies into Python environment with pip:

    pip install pynetcf
    pip install ascat
    pip install ismn
    pip install pybufr-ecmwf
    pip install c3s_sm
    pip install coverage
    pip install pygeogrids
    pip install pytest-django
    pip install django-widget-tweaks
    pip install psycopg2-binary
    pip install pytest-cov
    pip install pytest-mpl
    pip install celery==4.1.1
    pip install celery[redis]
    pip install gldas
    pip install smap-io
    pip install django-countries
    pip install cartopy
    pip install --upgrade --force-reinstall netcdf4

Install dependencies that are not available via pip (e.g. unreleased TU libraries). Use a temporary directory to check out the source and install it.

    export TMP_DIR="/tmp/valentina_lib_install"
    mkdir -p $TMPDIR

    # install latest pytesmo trunk
    git clone -b master --single-branch https://github.com/TUW-GEO/pytesmo.git
    cd pytesmo
    rm requirements.txt # ignore requirements
    touch requirements.txt
    python setup.py install
    cd $TMP_DIR
    rm -rf pytesmo

### Get source code

Check out the QA4SM source code from [GitHub](https://github.com/awst-austria/qa4sm) to create your sandbox:

    git clone git@github.com:awst-austria/qa4sm.git

### Create webapp configuration file

    cd valentina
    ./init_config.sh dev

This should create `valentina/settings_conf.py` from the template in `settings_example_conf.py`.

If the `init_conig.sh` doesn't work for you, copy `settings_example_conf.py` into the `valentina` subfolder yourself and set the variables appropriately.

Adapt the `valentina/settings_conf.py` to match your local configuration:

- Set `DATA_FOLDER` to the folder where you keep the (geo)data, see the datasets folder section for more info.
- If you didn't set up your own Redis and RabbitMQ, add below the other CELERY settings: `CELERY_TASK_ALWAYS_EAGER = True`. This means that Celery jobs will be processed sequentially (not in parallel) - but you don't have to set up the services.
- Use `DBSM = 'postgresql'` and `DB_PASSWORD = ...` if you've set up a local postgresql database. The rest of the database configuration is in `valentina/valentina/settings.py` and ideally should be left unchanged.
- Set `EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'` to tell Django to log emails to files instead of trying to send them. Use `EMAIL_FILE_PATH = ...` to tell Django where to put the email files.

### Datasets folder

Your datasets folder should have the following structure so that the webapp can find the data:

    ASCAT/ASCAT_H113
        data/xxxx.nc
        grid
        static_layer

    C3S/C3S_V201706/TCDR/063_images_to_ts/combined-daily

    GLDAS/GLDAS_NOAH025_3H_2_1
    GLDAS/GLDAS_TEST

    ISMN/ISMN_V20180712_MINI
    ISMN/ISMN_V20180712_TEST
    ISMN/ISMN_V20180830_GLOBAL

    SMAP/SMAP_V5_PM

The folders are used in `validator.validation.readers.create_reader` to create the necessary data readers. The general folder structure is `<dataset_name>/<version_name>`, using the names in the webapp database. As always, capitalisation makes a difference ;-)

### Init Django

Go to webapp folder (if you haven't done so already):

    cd valentina

Set up Django app:

    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic

Create admin user for webapp:

    python manage.py createsuperuser

Keep note of the username and password you enter here, you'll need it to log into the webapp later.

### Start necessary servers

If you haven't set up Postgres, Redis, and RabbitMQ, skip to the next section.

If you've installed those services on your machine, you can (re)start them with:

    sudo rcrabbitmq-server start
    sudo systemctl restart redis.target
    sudo rcpostgresql restart

Start a celery worker with the shell script:

`valentina/start_celery_worker`

### Run Django development server

    python manage.py runserver

Check the output of this command for the URL to point your browser to - e.g. <http://127.0.0.1:8000/>.

Now you should be able to see the landing page. You can log in with the admin user you created in section "Init Django".

You can access the webapp's admin panel you appending "admin/" to the URL, e.g. <http://127.0.0.1:8000/admin/>. There you can create more users by clicking "Add" next to the "Users" row.

Depending the `LOG_FILE` in your `settings_conf.py` file, the webapp's logfile should be written to `valentina/valentina.log`. If you encounter problems, check this log and the command line output of the Django server.

### Integrated Development Envionment

It's up you which Python IDE you want to use for development.

We use Eclipse with PyDev. Since Django templates consist of HTML and JavaScript, the [Eclipse IDE for JavaScript and Web Developers](https://www.eclipse.org/downloads/packages/release/2018-09/r/eclipse-ide-javascript-and-web-developers) can be helpful. If you want to use Eclipse, you should probably check what the latest version is and use that.

To install PyDev, use Eclipse's `Help > Install New Software...` menu and the PyDev update URL `http://www.pydev.org/updates`. [PyDev install manual](http://www.pydev.org/manual_101_install.html).

To add the webapp project to Eclipse, use `File > Import > General > Existing Projects into Workspace` and set the root directory to `valentina` folder.

In case you don't want to use Eclipse, one alternative is [PyCharm](https://www.jetbrains.com/pycharm/).

### Webapp walkthrough

The code for the webapp lives in two submodules of the `valentina` folder: `valentina` and `validator`. The first contains the Django "project", the second the Django "app" - [see here for the Django tutorial that explains projects and apps.](https://docs.djangoproject.com/en/2.1/intro/tutorial01/)

The `valentina` module exists to conform to the Django structure. It contains mainly configuration in `settings.py`, `settings_conf.py`, `celery.py`. Most of the interesting stuff is happening in the `validator` module.

#### Contents of the validator module

Module|Functionality
--- | ---
admin|Customisations of the webapp’s admin pages, e.g. controls to activate new users.
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
metrics.py|Contains the EssentialMetrics class that defines the metrics to be produced by the webapp on validation. 
urls.py|Django specific file containing the mapping of URLs to views.

### How to run integration / unit tests

Go to `valentina` and run

    pytest

Congratulations, your development environment is now set up and you can develop ;-)

## Tips and Tricks

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
6. Look at `my_project_visualized.png`.

For further hints see <https://django-extensions.readthedocs.io/en/latest/graph_models.html>.


