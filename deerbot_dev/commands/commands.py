class Commands:
    """Class commands, commands can use server id to sort data"""
    def __init__(self, data):
        self.data = data

    def _get_server_data(server):
        pass

    def _write_server_data(server, data):
        pass

    def test(self, server, params):
        return "test command return"

    _commandlist = [
        {
            "name": "test",
            "alias": ["testing", "moretesting"],
            "function": test
        }
    ]

    def decode(self, server, user_command, params):
        user_command = user_command.lower()
        for command in self._commandlist:
            if user_command == command["name"] or user_command in command["alias"]:
                return command["function"](self, server, params)
        return None