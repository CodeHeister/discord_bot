import user, asyncio, random, re, time
from cfg import *
from msg import *

async def main():
    User = user.MyBot(TOKEN)
    User.guilds = guilds
    User.drop_limit = 15

    @User.on_start
    def starter():
        print(f'Logged as {User.username}#{User.discriminator}!')
        User.check_channels = check_channels 


    @User.on_message
    def message(last_message):
        print(last_message)

    def greet(update):
        update.send(f"Hi, {User.ping(last_message)}", update["channel_id"])

    User.on_commant(command="greeting", func=greet)

    await asyncio.wait([asyncio.create_task(User.run())])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
