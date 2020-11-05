USER CONFIGURATION CONTROL
=============
project to upload and save configuration files from user.

Requirements
-----------
* Python 3.6
* requests
* pytest
* pytest-asyncio
* aiohttp
* pyyaml
* pymongo
* aiomongodel
* motor
* mongo


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

