from deerbot_dev.commandhandler import ch
import requests
import discord
import re

class Command(ch.Command): 
    def __init__(self, commandhandler):
        commandlist = [
                {
                    "name": "leaderboard",
                    "alias": ["boards", "leaderboards", "board"],
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

    def _check_and_generate_db(self, server):
        db = self.commandhandler._server_db(server)
        if "prefix" not in db:
            db["prefix"] = "!"
        if "players" not in db:
            db["players"] = []
        self.commandhandler._save_server_db(server, db)

    def _get_users(self, connect_codes):

        graphql_connect_codes = ""

        for i in range(len(connect_codes)):
            graphql_connect_codes += f"""
                item{i}: getConnectCode(code: "{connect_codes[i]}") {{
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

            query RankedSlippiQuery {
        """ + graphql_connect_codes + """       
            }
        """
        url = "https://gql-gateway-dot-slippi.uc.r.appspot.com/graphql"
        response = requests.post(url=url, json={
            "operationName": operation_name,
            "query": query,
        })
        return response.json()

    def _prune_list(self, slippi_players, players):
        prune = []
        for i in range(len(players)):
            if not slippi_players["data"][f"item{i}"]:
                prune.append({"player": players[i], "exists": False})
                continue
            profile = slippi_players["data"][f"item{i}"]["user"]["rankedNetplayProfile"]
            if not profile["wins"] and not profile["losses"]:
                prune.append({"player": players[i], "exists": True})
        return prune

    def _format_players(self, slippi_players):
        players = slippi_players["data"]
        formatted_players = []
        for player in players:
            if not players[player]:
                continue
            profile = players[player]["user"]["rankedNetplayProfile"]
            if not profile["wins"] and not profile["losses"]:
                continue
            formatted_players.append({
                "tag": players[player]["user"]["displayName"],
                "connect_code": players[player]["user"]["connectCode"]["code"],
                "rating": players[player]["user"]["rankedNetplayProfile"]["ratingOrdinal"]
            })
        formatted_players.sort(key=lambda p: p["rating"], reverse=True)
        return formatted_players

    def _get_all_rankings(self, server):
        self._check_and_generate_db(server)
        db = self.commandhandler._server_db(server)
        if not db["players"]:
            return None
        slippi_players = self._get_users(db["players"])
        pruned = self._prune_list(slippi_players, db["players"])
        for prune in pruned:
            if not prune["exists"]:
                db["players"].remove(player)
        self.commandhandler._save_server_db(server, db)
        return {
            "players": self._format_players(slippi_players),
            "pruned": pruned
        }

    def _does_player_exist(self, players, connect_code):
        for player in players:
            if player["connect_code"] == connect_code.upper():
                return True
        return False

    def _top(self, players, server_name):
        limit = 15
        leaderboard = ""
        rank = 1
        for player in players:
            if rank == limit + 1:
                leaderboard += f"...\n{len(players)-limit} players not shown"
                break
            if rank == 1:
                leaderboard += "🥇 "
            elif rank == 2:
                leaderboard += "🥈 "
            elif rank == 3:
                leaderboard += "🥉 "
            else:
                leaderboard += f"{rank}. "
            leaderboard += f"**{discord.utils.escape_markdown(player['tag'])}** ({player['connect_code']}) - {'{:.2f}'.format(round(player['rating'], 2))}\n"
            rank += 1
        embed=discord.Embed(title="🏆 Slippi Leaderboard", description=f"{server_name}'s leaderboard", color=0x18f334)
        embed.add_field(name="", value=leaderboard, inline=False)
        return embed

    def _specific_rank(self, players, connect_code, server_name):
        limit = 4
        leaderboard = ""
        rank = 1
        player_rank = 1
        for player in players:
            if player["connect_code"] == connect_code.upper():
                break
            player_rank += 1
        start_players_at = 1 if player_rank-limit < 1 else player_rank-limit
        end_players_at = len(players) if player_rank+limit > len(players) else player_rank+limit
        if player_rank-limit < 1:
            end_players_at += limit - (player_rank + 1)
        if player_rank+limit > len(players):
            start_players_at -= limit - (len(players) - player_rank)
        start_dots = False
        end_dots = False
        for player in players:
            if rank < start_players_at:
                if not start_dots:
                    leaderboard += f"...\n"
                    start_dots = True
                rank += 1
                continue
            if rank > end_players_at:
                if not end_dots:
                    leaderboard += f"...\n"
                    end_dots = True
                rank += 1
                break
            if player["connect_code"] == connect_code.upper():
                leaderboard += " --> "
            if rank == 1:
                leaderboard += "🥇 "
            elif rank == 2:
                leaderboard += "🥈 "
            elif rank == 3:
                leaderboard += "🥉 "
            else:
                leaderboard += f"{rank}. "
            leaderboard += f"**{discord.utils.escape_markdown(player['tag'])}** ({player['connect_code']}) - {'{:.2f}'.format(round(player['rating'], 2))}\n"
            rank += 1
        embed=discord.Embed(title="🏆 Slippi Leaderboard", description=f"{server_name}'s leaderboard", color=0x18f334)
        embed.add_field(name="", value=leaderboard, inline=False)
        return embed

    def _finalize(self, embed, rankings):
        if rankings["pruned"]:
            unranked = []
            removed = []
            for prune in rankings["pruned"]:
                if prune["exists"]:
                    unranked.append(prune["player"])
                else:
                    removed.append(prune["player"])
            msg = ""
            if unranked:
                joined = [('`' + player + '`') for player in unranked]
                msg += f"\nUnranked not included: {', '.join(unranked)}"
            if removed:
                joined = [('`' + player + '`') for player in removed]
                msg += f"\nPlayers removed for not existing: {', '.join(removed)}"
            return {
                "msg": msg,
                "embed": embed
            }
        else:
            return embed

    def leaderboards(self, server, params, message):
        rankings = self._get_all_rankings(server)
        if not rankings:
            return "No players in server database! Add them with !rankadd"
        embed = self._top(rankings["players"], message.guild.name)
        return self._finalize(embed, rankings)

    def rank(self, server, params, message):
        rankings = self._get_all_rankings(server)
        if not rankings:
            return "No players in server database! Add them with !rankadd"
        if not self._does_player_exist(rankings["players"], params):
            return "Player not found in server database!"
        embed = self._specific_rank(rankings["players"], params, message.guild.name)
        return self._finalize(embed, rankings)

    def rankadd(self, server, params, message):
        self._check_and_generate_db(server)
        db = self.commandhandler._server_db(server)
        params = params.upper()
        code_check = re.compile(r"^[A-Z0-9]{1,6}#[0-9]{1,3}$")
        if not code_check.search(params):
            return f"Not a valid connect code! Please check your formatting."
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
