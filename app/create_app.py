from flask import Flask, abort
import json
from datetime import datetime, timedelta
import atexit
import os
from apscheduler.schedulers.background import BackgroundScheduler

from steamicons.updateicons import update_game_icons


GAME_ICONS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/game_icons.json')


def new_games():
    update_game_icons(check_new_games=True, recheck_unreviewed_games=False)


def update_all_games():
    update_game_icons(check_new_games=True, recheck_unreviewed_games=True)


class IconData:
    def __init__(self):
        self.game_icons = None
        self.last_update = None
        self.load_icon_file()

    def reload_if_outdated(self):
        if self.last_update < datetime.now() - timedelta(days=2):
            self.load_icon_file()

    def load_icon_file(self):
        try:
            with open(GAME_ICONS_JSON_PATH, 'r') as fp:
                self.game_icons = json.load(fp)
                self.last_update = datetime.now(tz=None)
        except FileNotFoundError:
            exit(1)


def create_app():
    app = Flask(__name__)
    icon_data = IconData()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=new_games, trigger="interval", days=2)
    scheduler.add_job(func=update_all_games, trigger="interval", days=7)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    @app.route('/')
    def all_icons():
        icon_data.reload_if_outdated()
        return icon_data.game_icons

    @app.route('/<id>')
    def icon(id):
        icon_data.reload_if_outdated()
        if str(id) not in icon_data.game_icons.keys():
            abort(404)
        return f"https://media.steampowered.com/steamcommunity/public/images/apps/{id}/{icon_data.game_icons[id]}.jpg"

    return app


if __name__ == "__main__":
    create_app().run()
