from bootstrap.app import setup_app
from telegram import Update

if __name__ == '__main__':
    app = setup_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES,)
