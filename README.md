# triabot
tripulse's own Discord bot which serves a lot of unique features that other bots fail to deliver.

---

## Programmers
As you may have probably guessed, this is written in Python 3 for doing the work with Discord it uses the
 sophisticated Discord.py API. You're assumed to have a little of experience with MongoDB.

### Installation
- clone the repository
- type in TTY `pip3 install -r requirements.txt`
- setup a MongoDB database by following the instructions found on the internet.
  - retrieve the connection URI from the cluster then put it inside the `DBOT_DATASTORE` enviroment variable.
  - make collections in the database: `prefixes` and `configuration`.
  - navigate to `configurations` and insert a document, put this where the data should be (excluding the comments),
  replace values as needed:
    ```json5
    {
      "default_prefix": ".",  // prefix to use when not configured for a guild.
      "discord_token": "",  // token for the Bot to use the API.
      
      // for using the Reddit for the Memery category.
      "reddit_clid": "",  // reddit application: client id.
      "reddit_clsecret": ""  // client secret.
    }
    ```

Optionally, to configure the log-level in the console, set `DBOT_LOGLEVEL` to any of [these values][1], by default it's
set to `INFO` level (the most *acceptable* verbosity). 

### Contribution
To contribute to this project you should follow the idioms described below, if not then core developers might have to
do extra effort cleaning up the code to match the idioms, sometimes not even accepting the PR.

#### Navigation
- `cogs` folder has all the command modules in it, each module is separated based on its usage.
    - `__init__.py` loads all command modules and handles their exceptions.
- `requirements.txt` is where all the required external dependencies stored in the `pip freeze` format.

#### Idioms
Moving to `cogs/` you'll see a lot of Python modules, each one has multiple categories referred to as so called "cogs
" in the Discord.py convention.

Categories are always that inherit from `Cog`. The syntax is somewhat like this:
```py
class MyCategory(Cog):
    ...
```

Free floating commands are not supported, they should be wrapped in a `Cog`. A command is a coroutine (aka. async
 function). Decorated with `command` and must accept a positional argument.
```py
class MyCategory(Cog):
    @command
    async def dosomething(ctx):
        ...
```

To export these classes to be picked up and be loaded, append a `__cogexport__` at the end all the class definitions
. It could be any iterable object that yields classes inherited from `Cog`, if not then the class is discarded.
```py
__cogexport__ = [MyCategory, SomeCategory]
```

For accessing bot-metadata, there's a property `metadata` in the `Bot` object (which can be accessed with `ctx.bot`),
which is a [`pymongo.Database`][0] object. There's also a `config` in `Bot` which is an alias to `metadata.config`.

[0]: https://api.mongodb.com/python/current/api/pymongo/database.html?highlight=database#pymongo.database.Database
[1]: https://docs.python.org/3.8/library/logging.html#logging-levels