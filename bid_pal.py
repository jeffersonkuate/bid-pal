import re
import os
import math
import json
from display import Display

PROMPT_ROUND_START = "Enter q to quit, i for info, and enter to start: "
PROMPT_YES_NO = "Enter Y or N: "
PROMPT_NUMERIC = "Enter a number: "
PROMPT_ENTER = "Press Enter to Continue: "

INVALID = "INPUT INVALID!"

REGEX_QUIT = 'q$|quit$'
REGEX_INFO = 'i$|info$'
REGEX_START = 'q$|i$|quit$|info$|$'
REGEX_BLANK = '$'
REGEX_YES = 'y$|yes$'
REGEX_NO = 'n$|no$'
REGEX_YES_NO = 'y$|n$|yes$|no%'
REGEX_NUMERIC = '[0-9]*$'
REGEX_ALL = '.*'

# TODO: add Windows OS filesystem support
CONFIG = json.load(open(os.getcwd() + '/config.json'))
START_BALANCE = CONFIG['startBalance']
INITIAL_DRAFTS = CONFIG['initialDrafts']
BID_MULTIPLIER = CONFIG['bidMultiplier']
ASSET_USES = CONFIG['assetUses']
ASSET_NAMES = CONFIG['assetSets'][CONFIG['assetSet']]


# Container for all information of a game's current state
class Game:
    def __init__(self, start_balance, initial_drafts, bid_multiplier, asset_uses, asset_names):
        self.start_balance = start_balance
        self.initial_drafts = initial_drafts
        self.bid_multiplier = bid_multiplier
        self.drafted = []
        self.assets = []
        self.players = []

        for name in asset_names:
            self.assets.append(Asset(name, asset_uses))

    # Adds a player to a Game
    def add_player(self, name):
        self.players.append(Player(name, self.start_balance))

    # Assigns a asset to a player
    def draft_asset(self, asset, player):
        self.assets.remove(asset)
        self.drafted.append(asset)
        player.assets.append(asset)

    def __str__(self):
        string = ""

        player_number = 1
        for player in self.players:
            string += "(" + str(player_number) + ") " + player.name + ": "

            asset_number = 1
            for asset in player.assets:
                string += str(asset_number) + ". " + asset.name
                if asset_number < len(player.assets):
                    string += ", "
                asset_number += 1

            string += "\n"
            player_number += 1

        return string


# Container for the state of a player and assets assigned to the player
class Player:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.assets = []
        self.next_player = None

    def debit(self, amount):
        self.balance -= amount

    def credit(self, amount):
        self.balance += amount


# Represents a asset with their name and the amount of uses they have left
class Asset:
    def __init__(self, name, uses):
        self.name = name
        self.uses = uses


# Polls p1 for a asset name until a valid name is entered, initiates a bid between p1 and p2 for the asset,
# assigns the asset to the winning bidder and updates the game state accordingly
def draft(game, display, rounds):
    for round in range(rounds):
        i = round % len(game.players)
        while True:
            asset_name = display.input("Enter " + game.players[i].name + "'s selection: ")
            asset = find_asset(asset_name, game.assets)

            if asset is None:
                display.input("Could not find " + asset_name, PROMPT_ENTER)
            else:
                break

        winner = bid(game, display, i, asset)
        game.draft_asset(asset, winner)


def bid(game, display, starting_player, asset):
    participants = game.players.copy()
    cur_player = starting_player
    leader = None
    bid_num = 0
    last_bid = 0
    next_bid = 0
    while len(participants) > 1:
        if cur_player >= len(participants):
            cur_player = 0
        bidder = participants[cur_player]
        if bidder.balance <= 0:
            participants.remove(bidder)
            continue

        if bid_num == 0:
            display_string = (bidder.name + " has a balance of " + str(bidder.balance)
                              + ".\nPlace an initial bid for " + asset.name)
            last_bid = int(checked_input(display, display_string, PROMPT_NUMERIC, REGEX_NUMERIC))
            next_bid = math.ceil(last_bid * BID_MULTIPLIER)

            if last_bid > bidder.balance or last_bid == 0:
                display_invalid(display)
                continue
            else:
                leader = bidder
                bid_num += 1
                cur_player += 1
                continue

        if next_bid < bidder.balance:
            display_string = (bidder.name +
                              " has a balance of " + str(bidder.balance) + ". Would you like to bid "
                              + str(next_bid) + " for " + asset.name)

            user_response = checked_input(display, display_string, PROMPT_YES_NO, REGEX_YES_NO)

            if match(REGEX_YES, user_response):
                leader = bidder
                last_bid = next_bid
                next_bid = math.ceil(last_bid * BID_MULTIPLIER)
                cur_player += 1
                continue

        participants.remove(bidder)

    leader.debit(last_bid)
    display.input(leader.name + " has won the bid. They have a current balance of "
                  + str(leader.balance),
                  PROMPT_ENTER)
    return leader


def find_asset(asset_name, asset_list):
    asset_obj = None
    for asset in asset_list:
        if match(asset_name, asset.name):
            if asset_obj is not None:
                return None
            else:
                asset_obj = asset

    return asset_obj


def checked_input(display, string='', prompt='', reg=REGEX_ALL):
    user_input = display.input(string, prompt)
    while not match(reg, user_input):
        display_invalid(display)
        user_input = display.input(string, prompt)
    return user_input


def display_invalid(display):
    display.input(INVALID, PROMPT_ENTER)


def search(reg, string):
    return not (re.search(reg.lower(), string.lower()) is None)


def match(reg, string):
    return not (re.match(reg.lower(), string.lower()) is None)


def play_round(game):
    pass


def main():
    # -------------------
    # INITIATION
    # -------------------
    game = Game(START_BALANCE, INITIAL_DRAFTS, BID_MULTIPLIER, ASSET_USES, ASSET_NAMES)
    display = Display()

    turn = 1
    player_number = 1

    while True:
        prompt = "Enter Player " + str(player_number) + "'s name"
        prompt += " (press Enter to skip)" if player_number > 2 else ""
        name = display.input(prompt)

        if name == '':
            if player_number <= 2:
                display_invalid(display)
                continue
            else:
                break
        elif any(player.name.lower() == name.lower() for player in game.players):
            display.input(name + " has already been chosen!", PROMPT_ENTER)
            continue

        game.add_player(name)
        player_number += 1

    # ---------------
    # DRAFT
    # ---------------
    draft(game, display, INITIAL_DRAFTS)

    # -----------------
    # ACTUAL GAME
    # -----------------
    while True:
        user_input = checked_input(display, "It is currently round " + str(turn), PROMPT_ROUND_START, REGEX_START)

        if match(REGEX_QUIT, user_input):
            quit(1)
        elif match(REGEX_INFO, user_input):
            display.input(str(game) + "\n Press Enter to continue")
        else:
            play_round(game)
            turn += 1


if __name__ == '__main__':
    main()
