USER CONFIGURATION CONTROL
=============
project to upload and save configuration files. Associate conf with user. 

Requirements
-----------
* Python 3.6
* requests
* aiohttp
* pyyaml
* pymongo
* aiomongodel
* motor
* mongo

API
-----------

* `POST /api/v1/users/` - data = `'name=12345'` create user and generate api token. Return User model: json  Username and Token. Example:
    ```console:
        curl --location --request POST 'http://localhost:8000/api/v1/users/' \
        --form 'name=12345'
    ```
* `GET /api/v1/users/<user_id>/configurations/` - search in the database in the collection of configurations that the user is a member
* `GET /api/v1/configuration/` - returns a list of all configuration 
* `POST /api/v1/configuration/ ` data =`files={"configuration": ("filename", "binar data"}` - save configuration with empty list users. Data is Multipart/form-data file. If file saved return 201 status code. Example: 
    ```python
    import requests
    requests.post(
                "http://localhost:8000/api/v1/files/",
                files={"configuration": ("MyConf.conf", "[Main]\nEntryPoint=entry.py".encode())},
                headers={"Authorization": f"Token MySercretToken"},
            )
    ```
* `GET /api/v1/files/<id_configuration>/download` - download conf file by id
* `PUT /api/v1/files/<id_configuration>/users/<user_id>}` - add user to list **users** in configuration. Example:
    ```cmd
    curl --location --request PUT 'http://localhost:8000/api/v1/configurations/5fce7c5e84fc379b2b23f275/users/5fce7bf684fc379b2b23f274' \
    --header 'Authorization: Token 6a4fc8ec-3930-1334-a333-640b8454e2e1'
    ```



How to run
----------
1. Up docker-compose 
    ```bash
    docker-compose up
    ```
or: 


1. Run mongo (you may use docker for this):
    ```console
    docker run --rm -p 27017:27017 -d mongo
    ```
1. Run server:
    ```console
    python entry.py
    ```

Configuration
----------

#### Args:
|param|default|description|
|-----|-------|-----------|
| `--host` | Host to listen |   0.0.0.0 |
| `--port`|  Port to accept connections |8000|
| `--reload` | Autoreload code on change"| |
| `-c`, `--config`|  Path to configuration file |


#### Settings:
configuration file has yaml format: 
- `site_name` - site name by defalt is "Control configure site"
- `database_uri` - url format path to db by default  mongodb://localhost:27017
- `media_dir` - folder to save users file by defalt is  __media__ in project folder
- `hash_method` - used hash function from hashlib. By default **sha1**


Testing
------------
install via pip:
* pytest
* pytest-asyncio
```console
pip install pytest pytest-asyncio
```
in project dir run pytest:
```console
python -m pytest
```
