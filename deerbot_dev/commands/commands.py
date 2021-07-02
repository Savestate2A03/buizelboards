import json

class Commands:
    """Class commands, commands can use server id to sort data"""
    def __init__(self, data):
        # use the bot's data folder that's passed in.
        # server json files will be stored here!
        self.data_folder = data
        self._commandlist = [
            {
                "name": "test",
                "alias": ["testing", "moretesting"],
                "function": self.test
            },
            {
                "name": "testadd",
                "alias": [],
                "function": self.test_add_data
            },
            {
                "name": "testclear",
                "alias": [],
                "function": self.test_clear
            },
            {
                "name": "source",
                "alias": ["github", "sourcecode"],
                "function": lambda a,b: "Source code: https://github.com/Savestate2A03/deerbot-dev/"
            },
        ]

    # this just gets the server.json and returns it as a dict
    def _server_db(self, server):
        server_db = self.data_folder.joinpath(str(server) + ".json")

        # create essentially empty server json if not found
        if not server_db.is_file():
            with open(server_db, "w") as sdb: 
                json.dump({"id": server}, sdb)

        # return the json as a dict using json.load
        with open(server_db, "r") as sd: 
            return json.load(sd)

    # pass in a server id and a dict to save it as the server database
    def _save_server_db(self, server, db):
        server_db = self.data_folder.joinpath(str(server) + ".json")

        with open(server_db, "w") as sdb: 
            json.dump(db, sdb)

    # testing commands
    def test(self, server, params):
        return "server id: " + str(server) + ", server database: " + str(self._server_db(server))

    def test_add_data(self, server, params):
        db = self._server_db(server)
        if "test_array" not in db:
            db["test_array"] = []
        db["test_array"].append(params)
        self._save_server_db(server, db)
        return "added '" + params + "' to test database!"

    def test_clear(self, server, params):
        db = self._server_db(server)
        db["test_array"] = []
        self._save_server_db(server, db)
        return "cleared test database!"

    def decode(self, server, user_command, params):
        # lower the user command for consistency
        user_command = user_command.lower()
        # search through the _commandlist array for one that matches our command
        for command in self._commandlist:
            if user_command == command["name"] or user_command in command["alias"]:
                return command["function"](server, params)
        # if no command is found, return None
        return None