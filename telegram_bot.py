import logging
import telegram
import urllib

def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    bot = telegram.Bot('136940855:AAGaZVK07Mocwz4NVabKysOuWEvJwGvEpT0')  # Telegram Bot Authorization Token

    LAST_UPDATE_ID = bot.getUpdates()[-1].update_id  # Get lastest update
    while True:
        for update in bot.getUpdates(offset=LAST_UPDATE_ID, timeout=10):
            text = update.message.text
            chat_id = update.message.chat.id
            update_id = update.update_id

            if text:
                roboed = ed(text)  # Ask something to Robô Ed
                bot.sendMessage(chat_id=chat_id, text=roboed)
                LAST_UPDATE_ID = update_id + 1


def ed(text):
    # Do something with it
    return text

if __name__ == '__main__':
    main()