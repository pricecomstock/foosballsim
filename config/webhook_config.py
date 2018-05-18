import requests
from config.secrets import slack_webhook_url

def eternal_season_slack_game_notifier(game):
    # accepts a game and sends it to slack
    payload = game.slack_report()
    # requests.post(slack_webhook_url, json=payload)

def eternal_season_slack_league_notifier(league):
    # accepts a game and sends it to slack
    payload = league.slack_report()
    # requests.post(slack_webhook_url, json=payload)

# An array of dictionaries.
#   function: a function that the game object should be passed to. It should notify or send something.
#   leagues: an array of leagues that 
NOTIFIERS = [
    {
        'leagues': ['the-eternal-season'],
        'game_notifier': eternal_season_slack_game_notifier,
        'league_notifier': eternal_season_slack_league_notifier
    }
]