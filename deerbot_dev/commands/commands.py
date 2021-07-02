import json

class Commands:
    """Class commands, commands can use server id to sort data"""
    def __init__(self, data):
        self.data_folder = data

    def _server_db(self, server):
        server_db = self.data_folder.joinpath(str(server) + ".json")

        if not server_db.is_file():
            with open(server_db, "w") as sdb: 
                json.dump({"id": server}, sdb)

        server_json = None

        with open(server_db, "r") as sd: 
            server_json = json.load(sd)

        return server_json

    def _save_server_db(self, server, db):
        server_db = self.data_folder.joinpath(str(server) + ".json")

        with open(server_db, "w") as sdb: 
            json.dump(db, sdb)

    # commands

    def test(self, server, params):
        return "server id: " + str(server) + ", server database: " + str(self._server_db(server))

    def test_add_data(self, server, params):
        db = self._server_db(server)
        if "test_array" not in db:
            db["test_array"] = []
        db["test_array"].append(params)
        self._save_server_db(server, db)
        return "added '" + params + "' to test database!"

    _commandlist = [
        {
            "name": "test",
            "alias": ["testing", "moretesting"],
            "function": test
        },
        {
            "name": "testadd",
            "alias": [],
            "function": test_add_data
        },
        {
            "name": "source",
            "alias": ["github", "sourcecode"],
            "function": lambda a,b,c: "Source code: https://github.com/Savestate2A03/deerbot-dev/"
        },        
    ]

    def decode(self, server, user_command, params):
        user_command = user_command.lower()
        for command in self._commandlist:
            if user_command == command["name"] or user_command in command["alias"]:
                return command["function"](self, server, params)
        return None