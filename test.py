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
        reaction_to_message_chance = 20
        reply_chance = 40
        reaction_in_message_chance = 20
        ping_chance = 20
        random_message_chance = 10
        delay = round(random.random()*5+5)

        for i in User.check_channels:
            if last_message["channel_id"] in User.check_channels[i]: guild_id = int(i); break
        if (round(random.random()*100) < reaction_to_message_chance) and (len(User.emojis[guild_id]) > 0):
            rand = round(random.random()*(len(User.emojis[guild_id])-1)) 
            User.createReaction(last_message["channel_id"], last_message["id"], User.emojis[guild_id][rand]["name"]+":"+User.emojis[guild_id][rand]["id"])
        for i in rep:
            if (len(re.findall(re.compile(i), last_message["content"].lower())) > 0):
                if (round(random.random()*100) < reply_chance):
                    time.sleep(30)
                    rand = round(random.random()*(len(User.emojis[guild_id])-1)) 
                    reaction = "" if round(random.random()*100) > reaction_in_message_chance or len(User.emojis[guild_id]) <= 0 else f'<:{User.emojis[guild_id][rand]["name"]}:{User.emojis[guild_id][rand]["id"]}>'
                    ping = "" if round(random.random()*100) > ping_chance else f'{User.ping(last_message)},'
                    User.send(f"{rep[i][round(random.random()*(len(rep[i])-1))]} {reaction}", last_message["channel_id"], reply={"message_id":str(last_message["id"]),"channel_id":last_message["channel_id"],"guild_id":str(guild_id), "fail_if_not_exists":True}, delay=delay)
                break
        if (round(random.random()*100) < random_message_chance):
            time.sleep(30)
            User.send(f"{ran[round(random.random()*(len(ran)-1))]}", last_message["channel_id"], delay=delay)
        print(f'\n[{last_message["timestamp"]}]  <{guild_id} -> {last_message["channel_id"]}>\n{last_message["author"]["username"]}#{last_message["author"]["discriminator"]} : {last_message["content"]}')
        
        # Log messages
        # with open("log.txt", "a") as f:
        #    f.write(last_message["content"]+"\n")


    await asyncio.wait([asyncio.create_task(User.run())])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
