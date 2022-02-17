from deerbot_dev.commandhandler import ch
from datetime import date
import hashlib
import requests
from html import escape
from time import sleep

class Command(ch.Command): 
    def __init__(self, commandhandler):
        commandlist = [
                {
                    "name": "lunch",
                    "alias": [],
                    "function": self.lunch
                },
                {
                    "name": "lunchset",
                    "alias": [],
                    "function": self.lunch_set
                },
        ]
        self.commandhandler = commandhandler
        super().__init__(commandlist)

    def daily_offset(self, message): 
        today = date.today()
        date_string = today.strftime("%d-%m-%Y-" + str(message.author.id))
        hash_object = hashlib.md5(date_string.encode())
        hex_string = hash_object.hexdigest()
        hex_string = hex_string[:8]
        integer_from_hash = int(hex_string, 16)
        return integer_from_hash

    def lunch(self, server, params, message):
        info = self.commandhandler._server_db("info")
        db   = self.commandhandler._server_db(server)
        user = str(message.author.id)

        if "lunch" not in db:
            return "No lunch database! Use !lunchset"
        if user not in db["lunch"]:
            return "No user location set! Use !lunchset"

        places = db["lunch"][user]["places"]

        return places[self.daily_offset(message) % len(places)]["name"]
        
    def lunch_set(self, server, params, message):
        info = self.commandhandler._server_db("info")
        db   = self.commandhandler._server_db(server)
        user = str(message.author.id)

        if "lunch" not in db:
            db["lunch"] = {}
        if user not in db["lunch"]:
            db["lunch"][user] = {}
        user_db = db["lunch"][user]
        if "google_maps_api_key" not in info:
            return "No Google Maps API key!"

        key = info["google_maps_api_key"]
        url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={escape(params)}&key={key}'
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        address  = response.json()["results"][0]["formatted_address"]
        location = response.json()["results"][0]["geometry"]["location"]
        user_db["address"]  = address
        user_db["location"] = location

        results = []

        location = escape(f'{user_db["location"]["lat"]} {user_db["location"]["lng"]}')
        url      = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&key={key}&keyword=food&radius=1500&maxprice=2'

        while True:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.json()["status"] == "INVALID_REQUEST":
                continue
            results.extend(response.json()["results"])
            if "next_page_token" not in response.json():
                break
            url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&key={key}&pagetoken={response.json()["next_page_token"]}'
            sleep(0.5)

        user_db["places"] = results

        self.commandhandler._save_server_db(server, db)

        return f"User area set as: {address}. {len(results)} restaurants."

