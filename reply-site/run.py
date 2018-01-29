from decouple import config

from app import create_app

config_name = config('APP_SETTINGS', cast=str, default="development").lower()
app = create_app()

if __name__ == '__main__':
    app.run()
