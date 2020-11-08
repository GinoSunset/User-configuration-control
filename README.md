USER CONFIGURATION CONTROL
=============
project to upload and save configuration files from user.

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
only auth user may request api. User token create ony via db.

API:
* `GET /api/v1/files/` - returns a list of files for the authorized user
* `POST /api/v1/files/ ` data =`files={"configuration": ("filename", "binar data"}` - save configuration for the authorized user. Data is Multipart/form-data file. If file saved return 201 status code and  list of files for the authorized user. Example: 
    ```python
    import requests
    requests.post(
                "http://localhost:8000/api/v1/files/",
                files={"configuration": ("MyConf.conf", "[Main]\nEntryPoint=entry.py".encode())},
                headers={"Authorization": f"Token MySercretToken"},
            )
    ```
* `GET /api/v1/files/<name_file_to_download>` - return file for the authorized user is exists

How to run
----------
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