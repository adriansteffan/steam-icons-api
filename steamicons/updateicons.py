import requests
import json
import time
import argparse
import os

if __name__ != "__main__":
    import steamicons.steam_config as steam_config

GAME_ICONS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/game_icons.json')
IDS_WITH_MISSING_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/missing_data_ids.txt')


def update_game_icons(check_new_games, recheck_unreviewed_games):
    try:
        with open(GAME_ICONS_JSON_PATH, 'r') as fp:
            game_icons = json.load(fp)
            icon_file_exists = True
    except FileNotFoundError:
        # id : icon-url
        game_icons = dict()
        icon_file_exists = False

    # Check the accounts of the people that own the most games as a starting point
    if not icon_file_exists or check_new_games:

        steam_ids = [76561198039144984]  # include my own steam id because why not
        regions = ['europe', 'north_america', 'south_america', 'asia', 'oceania']
        for region in regions:
            print(f" Fetching top game owners from {region}")
            r = requests.get(f'https://steamladder.com/api/v1/ladder/games/{region}', headers={'Authorization': f'Token {steam_config.STEAM_LADDER_KEY}'})
            steam_ids += [elem['steam_user']['steam_id'] for elem in r.json()['ladder']]

        for i, steam_id in enumerate(steam_ids):
            print(f"Getting img_icon_url, {i/len(steam_ids)*100}% of top accounts searched")
            res = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_config.STEAM_KEY}&steamid={steam_id}&format=json&include_played_free_games=1&include_appinfo=1&skip_unvetted_apps=false&include_free_sub").json()['response']
            if 'games' not in res:
                print("failed")
                continue
            for game in res['games']:
                game_icons[str(game['appid'])] = game['img_icon_url']

        with open(GAME_ICONS_JSON_PATH, 'w') as fp:
            json.dump(game_icons, fp)

    if not icon_file_exists or check_new_games or recheck_unreviewed_games:
        # look up all steam games
        # then get remaining game icons by searching the GamesOwned of people that have reviewed the games
        # id : name
        steam_games = dict()

        try:
            with open(IDS_WITH_MISSING_DATA_PATH, 'r') as file:
                ids_missing_data = file.read().splitlines()
        except FileNotFoundError:
            ids_missing_data = []

        games_per_request = 50000
        queried_all_games = False
        last_app_id = 0

        print("Fetching all steam games...")
        while not queried_all_games:

            games = requests.get(
                f"https://api.steampowered.com/IStoreService/GetAppList/v1/?key={steam_config.STEAM_KEY}&include_games=true&include_dlc=false&include_software=false&include_videos=false&include_hardware=false&last_appid={last_app_id}&max_results={games_per_request}").json()['response']['apps']
            if len(games) < games_per_request:
                queried_all_games = True

            last_app_id = games[-1]['appid']
            for game in games:
                steam_games[str(game['appid'])] = game['name']

        missing_game_icon_ids = list(set(steam_games.keys()) - set(game_icons.keys()))

        print(f"Starting to search the missing {len(missing_game_icon_ids)} icons")
        found_icon_ids = []  # if person reviewing missing game x also has missing game y
        for i, game_id in enumerate(missing_game_icon_ids):
            game_id = str(game_id)
            if game_id in found_icon_ids or (game_id in ids_missing_data and not recheck_unreviewed_games):
                continue

            print(f"Getting missing icons via reviewing accounts, {i / len(missing_game_icon_ids) * 100}% of games checked")

            icon_found = False
            time.sleep(1.5)  # hacky way to prevent ip blocks by valve
            reviews = requests.get(f"http://store.steampowered.com/appreviews/{game_id}?json=1").json()['reviews']
            print(f"Number of reviews: {len(reviews)}")
            reviewers = [review['author']['steamid'] for review in reviews]

            for reviewer_id in reviewers:
                time.sleep(1.5)  # hacky way to prevent ip blocks by valve
                res = requests.get(
                    f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_config.STEAM_KEY}&steamid={reviewer_id}&format=json&include_played_free_games=1&include_appinfo=1&skip_unvetted_apps=false&include_free_sub").json()[
                    'response']

                if 'games' in res:
                    for game in res['games']:
                        game_icons[game['appid']] = game['img_icon_url']
                        found_icon_ids.append(game['appid'])  # collect all icon urls to potentially save requests

                        if str(game['appid']) == str(game_id):  # continue searching if the reviewer does not own the game anymore
                            print("icon found")
                            icon_found = True
                    with open(GAME_ICONS_JSON_PATH, 'w') as fp:
                        json.dump(game_icons, fp)
                    if icon_found:
                        continue

        ids_missing_data = list(set(steam_games.keys()) - set(game_icons.keys()))
        with open(IDS_WITH_MISSING_DATA_PATH, 'w') as f:
            for item in ids_missing_data:
                f.write("%s\n" % item)

    with open(GAME_ICONS_JSON_PATH, 'w') as fp:
        json.dump(game_icons, fp)


if __name__ == "__main__":
    import steam_config
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-new-games', dest="check_new_games", action='store_true')
    parser.add_argument('--recheck-unreviewed-games', dest="recheck_unreviewed_games", action='store_true')
    args = parser.parse_args()

    update_game_icons(args.check_new_games, args.recheck_unreviewed_games)