## Steamicons API

Currently, Valve's official Steam Web API does not offer an easy way to retreive app icons for steam games (the little logo that can optionally be displayed in your library) by appid, as the links to the images include a SHA-1 hash of the JPEG (This [SO Post](https://stackoverflow.com/questions/53963328/how-do-i-get-a-hash-for-a-picture-form-a-steam-game) mentions the problem).
However, when checking the owned games of any public steam account, these hashes are exposed by valve. 

This API caches these hashes and offers them via a separate REST endpoint, where they can be requested by appid (The API occasionally queries all logo hashes of games that are either owned by the top game owners listed on https://steamladder.com/ or have been reviewed by at least one public account). 

I am hosting a version of this API at `https://steamicons.adriansteffan.com/<app_id>`. If you want to host this yourself, you will need to use your own steam api key in order to collect a list of hashes with the provided scripts.


## Setup

These steps are needed for both deployment and development.

* Clone the repository
* Create a [Steam-Web-API-Key](http://steamcommunity.com/dev/apikey) at 
* Create a [Steam-Ladder-Key](https://steamladder.com/user/settings/api/)
* Rename `steamicons/steam_config.py.template` to `steamicons/steam_config.py` and enter the keys you created.


### Deployment

For the deployment on your Linux machine, you will need both [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

To build the docker image, run 

```
docker-compose build
```

in the root directory. As this will build the list of hashes while respecting Valve's rate limits, this might take a few hours.

After completing the setup, start the container with

```
docker-compose up -d
```

Stop the server with

```
docker-compose down
```


To make the api reachable from the internet, refer to [these instructions](https://gist.github.com/adriansteffan/48c9bda7237a8a7fcc5bb6987c8e1790) on how to set up your apache reverse proxy. Depending on your setup, you might want to change the ip mapping in [docker-compose.yml](docker-compose.yml).

### Development

For development, you will need a [Python3](https://www.python.org/downloads/) installation (the setup script assumes python3.7).

If you are using python3.7 and do not want to use a venv, simply run 

```
./setup.sh
```

in the root directory (As this will build the list of hashes while respecting Valve's rate limits, this might take a few hours).

Otherwise, just look at `setup.sh` and execute the commands with a different python command and/or venv.



## Authors

* **Adrian Steffan** - [adriansteffan](https://github.com/adriansteffan) [website](https://adriansteffan.com/)
