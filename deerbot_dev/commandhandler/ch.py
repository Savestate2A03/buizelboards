import json
import importlib
from pathlib import Path

class Command:
    def __init__(self, commandlist):
        self.commandlist = commandlist

class CommandHandler:
    """Class commands, commands can use server id to sort data"""
    def __init__(self, data):
        # use the bot's data folder that's passed in.
        # server json files will be stored here!
        self.data_folder = data
        self._commandlist = [
            {
                "module": "base",
                "name": "source",
                "alias": ["github", "sourcecode"],
                "function": lambda a,b,c: "Source code: https://github.com/Savestate2A03/buizelboards"
            },
            {
                "module": "base",
                "name": "setprefix",
                "alias": [],
                "function": self._set_server_prefix
            },
            {
                "module": "base",
                "name": "help",
                "alias": [],
                "function": self._help
            }
        ]

        # import modules based on name (in the commands directory)
        added_modules = ["buizelboards"]
        for module in added_modules:
            imported_module = importlib.import_module("." + module, package="deerbot_dev.commandhandler.commands")
            commands = imported_module.Command(self)
            for c in commands.commandlist:
                c["module"] = module # document what module the command is from
            self._commandlist.extend(commands.commandlist)

    def _help(self, server, params, message):
        prefix = self.get_server_prefix(server)
        return f"""
`{prefix}setprefix`
Sets the bot prefix (defaults to `!`)

`{prefix}leaderboard` / `{prefix}leaderboard X`
List the top 15 players in the server by
default, but will display a specific page
in the leaderboards if provided.
**Aliases**: `{prefix}boards`, `{prefix}leaderboards`, `{prefix}board`, `{prefix}lb`

`{prefix}rank ABC#123`
Get the rank of a connect code

`{prefix}rankadd ABC#123`
Add a connect code to the server

`{prefix}rankremove ABC#123`
Remove a connect code from the server
**Aliases**: `{prefix}rankdelete`
        """

    def _set_server_prefix(self, server, params, message):
        if not params:
            return "No prefix provided!"
        db = self._server_db(server)
        db["prefix"] = params[0]
        self._save_server_db(server, db)
        return f"Server prefix set to: `{params[0]}`"

    # this just gets the server.json and returns it as a dict
    def _server_db(self, server):
        server_db = self.data_folder.joinpath(str(server) + ".json")

        # create essentially empty server json if not found
        if not server_db.is_file():
            with open(server_db, "w") as sdb: 
                json.dump({"id": server, "prefix": "!"}, sdb)

        # return the json as a dict using json.load
        with open(server_db, "r") as sd: 
            return json.load(sd)

    # pass in a server id and a dict to save it as the server database
    def _save_server_db(self, server, db):
        server_db = self.data_folder.joinpath(str(server) + ".json")

        with open(server_db, "w") as sdb: 
            json.dump(db, sdb)

    def get_server_prefix(self, server):
        db = self._server_db(server)
        return db["prefix"]

    def set_server_prefix(self, server, prefix):
        db = self._server_db(server)
        db["prefix"] = prefix
        self._save_server_db(server, db)

    def decode(self, server, user_command, params, message):
        # lower the user command for consistency
        user_command = user_command.lower()
        # search through the _commandlist array for one that matches our command
        for command in self._commandlist:
            if user_command == command["name"] or user_command in command["alias"]:
                return command["function"](server, params, message)
        # if no command is found, return None
        return None