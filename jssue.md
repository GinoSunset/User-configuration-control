Issue: 
- create an asynchronous application (python 3.5, aio http, aiomongodel), API
- API to get a list of available configurations for a specific user
- it is possible to get/download a specific configuration via the API
- it is possible to upload the configuration to the server via the API
- through the API, it is possible to link the user to a specific configuration

Terms and restrictions:
 - the Configuration is a text file (INI, XML, etc.), it is also possible to archive (ZIP, etc.)
 - The main focus is on working with configurations, the implementation of users is minimal, only to support working with configurations. Use MongoDB/PostgreSQL database. Use docker containers.