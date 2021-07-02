import discord
import requests
import shutil
import json
import re
from pathlib import Path

from deerbot_dev.commands import commands

class DeerbotDev(discord.Client):

    # data folder containing all bot data
    data = Path(Path(__file__).parent.resolve().joinpath("data"))

    # if we don't have data made, copy it from the sample data folder and prompt for required user input
    if not data.is_dir():
        sample_data = Path(Path(__file__).parent.resolve().joinpath("sample_data"))
        shutil.copytree(sample_data, data)
        info_dict = None

        with open(data.joinpath("info.json"), "r") as info: 
            info_dict = json.load(info)
            for setting in info_dict.keys():
                if info_dict[setting] is None:
                    user_input = input(setting + " -> ")
                    info_dict[setting] = user_input

        with open(data.joinpath("info.json"), "w") as info: 
            json.dump(info_dict, info, indent = 4)

    # load bot settings
    settings = None
    with open(data.joinpath("info.json"), "r") as info: 
        settings = json.load(info)

    # setup commands
    cmds = commands.Commands()

    def api_key(self):
        return self.settings["discord_api_key"]

    def prefix(self):
        return self.settings["prefix"]

    # async overrides

    async def on_ready(self):
        print('Logged in as {0.user}'.format(self))

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.strip().startswith(self.prefix()):
            try: 
                match = re.search(r'^\.(\S+)\s*(.*)$', message.content.strip())
            except:
                print("command detected, regex search failed: " + message.content.strip())
                return
            command_response = self.cmds.decode(message.guild.id, match.group(1), match.group(2))
            if command_response is not None:
                await message.channel.send(command_response)