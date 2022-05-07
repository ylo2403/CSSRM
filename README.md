# Bloxlink
:bangbang: | Bloxlink is currently undergoing a [full rewrite](https://github.com/bloxlink/bloxlink-http); please do not contribute large features to this codebase as I do not intend on changing it too much.
:---: | :---

Roblox Verification made easy! Features everything you need to integrate your Discord server with Roblox.

## Dependencies
  - Python 3.8+
  - [MongoDB](https://www.mongodb.com/)
  - [Redis](https://redis.io)
  - [Requirements file](https://github.com/bloxlink/Bloxlink/blob/master/requirements.txt)

## Configuration
  ### Configuration files
  First, rename [config.py.example](https://github.com/bloxlink/Bloxlink/blob/master/src/config.py.example) to `config.py`.
  Edit the config.py file. Some values, the "secrets" or "tokens", can be optionally saved as environmental variables instead.
  Valid secrets which can be saved as environmental variables are found in the [secrets.py](https://github.com/bloxlink/Bloxlink/blob/master/src/resources/secrets.py) file.

  Environmental variables have priority over the config file!

  ### Constants
  Some options which aren't required to be changed are in the [constants.py](https://github.com/bloxlink/Bloxlink/blob/master/src/resources/constants.py) file.

  ### Image Server
  The [Bloxlink Image Server](https://github.com/bloxlink/image-server) is required to run in order for some of Bloxlink's functionality to work. Run the instance, then put your server URL (could just be `localhost`) in the config.py file. Make sure the auth used for the Image Server is the same as in your config file. These values can also be environmental variables.

## Intents
The **Members Privileged Intent** is required for the bot to function. This can be toggled on your [Developer Dashboard](https://discord.com/developers/applications) unless your bot reached over 100 servers.

## Setup
```sh
$ git clone https://github.com/bloxlink/Bloxlink
$ cd Bloxlink
[run image server]
[change the configuration]
$ python3.8 -m pip install -r requirements.txt
$ python3.8 src/bot.py
```

## Disclaimer
We do not provide support for self-hosting! This package has been made open-source to aid with contributions, not so you can run your own Bloxlink for private use. If something breaks or there's a vulnerability in a version you use, then you're on your own.

For this reason, we recommend using the official hosted bot at https://blox.link which is given regular updates.

Also, keep in mind that we use the AGPL-3.0 License, which means you're required to keep your local version open-source and state all changes that you have made to it.