from deerbot_dev.commandhandler import ch
import requests

class Command(ch.Command): 
    def __init__(self, commandhandler):
        commandlist = [
                {
                    "name": "leaderboards",
                    "alias": ["boards"],
                    "function": self.leaderboards
                },
                {
                    "name": "rank",
                    "alias": [],
                    "function": self.rank
                },
                {
                    "name": "rankadd",
                    "alias": [],
                    "function": self.rankadd
                },
                {
                    "name": "rankremove",
                    "alias": ["rankdelete"],
                    "function": self.rankremove
                },
        ]
        self.commandhandler = commandhandler
        super().__init__(commandlist)

    def _get_user(self, connect_code):
        graphql_connect_codes = ""
        for i in range(5):
            graphql_connect_codes += f"""
                item{i}: getConnectCode(code: $cc) {{
                    user {{
                        ...userRankedInfo
                        __typename
                    }}
                __typename
                }}
            """
        operation_name = "RankedSlippiQuery"
        query = """
            fragment userRankedInfo on User {
                displayName
                connectCode {
                    code
                    __typename
                }
                rankedNetplayProfile {
                    ratingOrdinal
                    wins
                    losses
                    __typename
                }
                __typename
            }

            query RankedSlippiQuery($cc: String!) {
        """ + graphql_connect_codes + """       
            }
        """
        variables = {
            "cc": connect_code
        }
        url = "https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql"
        headers = {
            "Host": "gql-gateway-dot-slippi.uc.r.appspot.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://slippi.gg/",
            "content-type": "application/json",
            "apollographql-client-name": "slippi-web",
            "Origin": "https://slippi.gg",
            "DNT": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "TE": "trailers"
        }

        response = requests.post(url=url, json={
            "operationName": operation_name,
            "query": query,
            "variables": variables
        })
        return f"```json\n{response.json()}```"

    def _check_and_generate_db(self, server):
        db = self.commandhandler._server_db(server)
        if "prefix" not in db:
            db["prefix"] = "!"
        if "players" not in db:
            db["players"] = []
        self.commandhandler._save_server_db(server, db)

    def leaderboards(self, server, params, message):
        self._check_and_generate_db(server)
        return self._get_user(params)

    def rank(self, server, params, message):
        self._check_and_generate_db(server)
        pass

    def rankadd(self, server, params, message):
        self._check_and_generate_db(server)
        db = self.commandhandler._server_db(server)
        params = params.upper()
        if params not in db["players"]:
            db["players"].append(params)
            self.commandhandler._save_server_db(server, db)
            return f"Connect code '{params}' added!"
        else:
            return f"Connect code '{params}' already exists in this server's leaderboard."

    def rankremove(self, server, params, message):
        self._check_and_generate_db(server)
        db = self.commandhandler._server_db(server)
        params = params.upper()
        if params in db["players"]:
            db["players"].remove(params)
            self.commandhandler._save_server_db(server, db)
            return f"Connect code '{params}' removed!"
        else:
            return f"Connect code '{params}' does not exist in this server's leaderboard."
