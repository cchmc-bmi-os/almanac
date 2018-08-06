# LPDR Data Almanac

The LPDR Data Almanac, written with Ember.js for the frontend and Django REST Framework JSON API for the backend API server.

## Requirements
* Node
* NPM
* Bower
* Ember CLI
* Python 3

## Directories
* backend/ - Django REST Framework App
* frontend/ - Ember CLI app

## Installation
* Clone the repository
    * `git clone <repository-url> <app-directory>`
* Update npm and bower components
    * `npm install`
    * `bower install`
    * `ember build --production`
* This will install all of the dependencies to build the frontend ember project.  The dist/ directory is where the final files are generated.  Using the --production flag will minifiy all of the assests.
* Create a virtual environment to run the Django REST API
    * `cd backend`
    * `virtualenv -p <path to python3> <directory>`
    * `source <directory>/bin/activate`
    * `pip install -r requirements.txt`
    * `pg_restore -Fc -j 8 -O -d <database> -U <db_user> -h <db_host> almanac/fixtures/latest.dump`
## Serving
* TBD

## BACKUP
 `pg_dump -U <db_user> -h <db_host> -Fc -O -x -Z 9 --file=almanac/fixtures/<name>.dump <database>`
