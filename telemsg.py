from telegram import Bot
import asyncio, sys

async  def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot = Bot(token='6857151769:AAFf1IZpyVlqKIYDH3CeueCeDDiVuzkyR6s')
    
    # Replace 'CHANNEL_ID' with your channel id
    channel_id = -4018430964
    
    # Replace 'Your message here' with your actual message
    message = open(sys.argv[1], 'r').read()
    print("sending message ", message);
    # Send the message
    await bot.send_message(chat_id=channel_id, text=message[:256])

if __name__ == "__main__":
    asyncio.run(main())
