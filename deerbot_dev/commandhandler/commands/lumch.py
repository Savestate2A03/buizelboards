from deerbot_dev.commandhandler import ch
from datetime import date
import hashlib

class Command(ch.Command): 
    def __init__(self, commandhandler):
        commandlist = [
                {
                    "name": "lumch",
                    "alias": [],
                    "function": self.lumch
                },
                {
                    "name": "lumchadd",
                    "alias": [],
                    "function": self.lumch_add
                },
                {
                    "name": "lumchremove",
                    "alias": [],
                    "function": self.lumch_remove
                },
                {
                    "name": "lumchlist",
                    "alias": [],
                    "function": self.lumch_list
                },
        ]
        self.commandhandler = commandhandler
        super().__init__(commandlist)

    def lumch(self, server, params, message):
        db = self.commandhandler._server_db(server)
        if "lumch" not in db:
            return "No lumch database!"
        if len(db["lumch"]) <= 0:
            return "No lumches!"
        today = date.today()
        date_string = today.strftime("%d-%m-%Y-" + str(message.author.id))
        hash_object = hashlib.md5(date_string.encode())
        hex_string = hash_object.hexdigest()
        hex_string = hex_string[:8]
        integer_from_hash = int(hex_string, 16)
        return db["lumch"][integer_from_hash % len(db["lumch"])]

    def lumch_add(self, server, params, message):
        db = self.commandhandler._server_db(server)
        if "lumch" not in db:
            db["lumch"] = []
        if params.lower() in [x.lower() for x in db["lumch"]]:
            return "Lumch already exists!"
        db["lumch"].append(params)
        self.commandhandler._save_server_db(server, db)
        return "Added '" + params + "' to lumch!"

    def lumch_remove(self, server, params, message):
        db = self.commandhandler._server_db(server)
        if "lumch" not in db:
            db["lumch"] = []
        if params.lower() not in [x.lower() for x in db["lumch"]]:
            return "Lumch to remove doesn't exist!"
        db["lumch"] = [x for x in db["lumch"] if x.lower() != params.lower()]
        self.commandhandler._save_server_db(server, db)
        return "Removed '" + params + "' from lumch!"

    def lumch_list(self, server, params, message):
        db = self.commandhandler._server_db(server)
        if "lumch" not in db:
            return "No lumch database!"
        if len(db["lumch"]) <= 0:
            return "No lumches!"
        return "Lumches: " + ", ".join(db["lumch"])