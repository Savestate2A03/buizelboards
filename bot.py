from deerbot_dev import deerbot_dev

bot = deerbot_dev.DeerbotDev()
# api key is defined in data/info.json
bot.run(bot.api_key())