import requests, json, sys, time, re, random, asyncio

class MyBot():
    def __init__(self, token):
        self.count = False
        self.token = token
        self.prefix = "$"
        self.base_link = "https://discord.com/api/v9"
        self.drop_limit = 10

        self.retry_after = {}

        self.command_name = {}
        self.message = []
        self.command = []
        self.start = self.default
        self.stop = self.default

        self.check_channels = {}

        self.emojis = {}

        self.roles = {}

        self.count_list = {}

        self.verify = False
        self.verify_list = {}
        self.verify_funcs = []

        self.guilds = []


    def check(self):
        me = self.getMe()
        self.username = me["username"]
        self.discriminator = me["discriminator"]
        self.id = me["id"]
        if (len(self.guilds) == 0):
            self.guilds = [i["id"] for i in self.allGuilds()]
        channels = {}
        emojis = {}
        roles = {}
        for i in self.guilds:
            channels[i] = self.getGuildChannels(int(i))
            emojis[i] = self.getGuildEmojis(int(i))
            roles[i] = self.getGuildRoles(int(i))
        for g in channels:
            self.check_channels[g] = []
            for i in channels[g]:
                if i["type"] == 0:
                    self.check_channels[g].append(i["id"])
        for g in emojis:
            self.emojis[g] = []
            for i in emojis[g]:
                if i["animated"] == False:
                    self.emojis[g].append({"name":i["name"], "id":i["id"]})
        for g in roles:
            self.roles[g] = []
            for i in roles[g]:
                if not "tags" in i:
                    self.roles[g].append({"name":i["name"], "id":i["id"]})


    def default(self): 
        pass


    async def messageVerify(self):
        funcs = []
        for i in self.verify_list:
            funcs.append(self.verifier(int(i), self.verify_list[i][0], self.verify_list[i][1]))
        await asyncio.wait([asyncio.create_task(i) for i in funcs])


    async def verifier(self, channel_id, message_id, emoji):
        self.createReaction(channel_id, message_id, emoji).text
        print("Verifier ready!")
        while True:
            await asyncio.sleep(0.1)
            if self.verify:
                reactions = self.getReactions(channel_id, message_id,emoji)
                if len(reactions) > 1:
                    for i in reactions:
                        if i["id"] != self.id:
                            for j in self.check_channels:
                                if str(channel_id) in self.check_channels[j]: i["guild_id"] = j; i["channel_id"] = channel_id; break
                            for func in self.verify_funcs:
                                func(i)
                            self.deleteUserReaction(channel_id, message_id, emoji, i["id"])


    async def countMembers(self):
        funcs = []
        for i in self.count_list:
            funcs.append(self.counter(int(i), self.count_list[i]))
        await asyncio.wait([asyncio.create_task(i) for i in funcs])


    async def counter(self, guild_id, channel_id):
        print("Counter ready!")
        self.retry_after[str(guild_id)] = 0
        while True:
            if self.retry_after[str(guild_id)] > 0:
                self.retry_after[str(guild_id)] -= 1
            else:
                r = self.renameVoiceChannel(channel_id, "CLOWNS: "+str(len(self.getGuildMembers(guild_id, 1000))))
                try:
                    self.retry_after[str(guild_id)] = r["retry_after"]
                except:
                    pass
            await asyncio.sleep(1)



    async def run(self):
        self.check()
        self.start()
        funcs = [self.runner()]
        if self.count: funcs.append(self.countMembers())
        if self.verify: funcs.append(self.messageVerify())
        await asyncio.wait([asyncio.create_task(i) for i in funcs])



    async def runner(self):
        self.last_msg_id = {}
        print(f"Servers: {len(self.guilds)} detected\nLoading...")
        for j in self.check_channels:
            for i in self.check_channels[j]:
                self.last_msg_id[i] = self.getLastMessage(int(i))["id"]
        print(f"Text Channels: {len(self.last_msg_id)} detected\nReady! Starting listener loop.")
        funcs = []
        for j in self.check_channels:
            for i in self.check_channels[j]:
                funcs.append(self.checkChannel(i))
        await asyncio.wait([asyncio.create_task(i) for i in funcs])


    async def checkChannel(self, id):
        while True:
            await asyncio.sleep(1)
            last_messages = self.getLastMessages(id)
            for last_msg in last_messages[::-1]:
                if self.id != last_msg["author"]["id"]:
                    if len(re.findall("^\\{0}".format(self.prefix), last_msg["content"])) > 0:
                        for func in self.command:
                            func(last_msg)
                        command = last_msg["content"][len(self.prefix):].split(" ")[0]
                        for word in self.command_name:
                            if word == command:
                                self.command_name[word](last_msg)
                    else:
                        for func in self.message:
                            func(last_msg)
                self.last_msg_id[id] = last_msg["id"]


    def on_start(self, func):
        self.start = func


    def on_stop(self, func):
        self.stop = func


    def on_message(self, func):
        self.message.append(func)
        def wraper(update):
            func(update)
        return wraper

    def on_verify(self, func):
        self.verify_funcs.append(func)
        def wraper(update):
            func(update)
        return wraper


    def on_command(self, func, command=""):
        if command == "":
            self.command.append(func)
            def wraper(update):
                func(update)
            return wraper
        else:
            self.command_name[command] = func


    def getDate(self):
        date = time.localtime(time.time())
        time_array = [date.tm_hour, date.tm_min, date.tm_mday, date.tm_mon, date.tm_year]
        i = 0
        while i < len(time_array):
            if len(str(time_array[i])) < 2:
                time_array[i] = "0" + str(time_array[i])
            else:
                i += 1
        return "UTC: {1}:{0[1]} {0[2]}.{0[3]}.{0[4]}".format(time_array, time_array[0]-3)


    def getLastMessage(self, id):
        headers = {
            "Authorization" : self.token
        }

        r = json.loads(requests.get(f"{self.base_link}/channels/{id}/messages", headers=headers).text)
        return r[0] if len(r) > 0 and type(r) == type([]) else {"id":"0"}

    
    def getLastMessages(self, id):
        headers = {
            "Authorization" : self.token
        }

        r = json.loads(requests.get(f"{self.base_link}/channels/{id}/messages?after"+str(self.last_msg_id[id]), headers=headers).text)
        '''try:
            i = 0
            while r[i]["id"] != self.last_msg_id[id]:
                i+=1
            return r[0:i]
        except:
            print(f"[KERNEL]: Last messages error\n\n{r}\n")
            return []'''
        return r if len(r) < self.drop_limit else r[:self.drop_limit]


    def getChannelMessages(self, id):
        headers = {
            "Authorization" : self.token
        }

        r = json.loads(requests.get(f"{self.base_link}/channels/{id}/messages", headers=headers).text)
        return r


    def type(self, id, sec):
        times = sec//9
        last = sec-times*9
        for i in range(0, times):
            headers = {
                "Authorization" : self.token
            }

            r = requests.post(f"{self.base_link}/channels/{id}/typing", headers=headers)
            time.sleep(9)
        headers = {
            "Authorization" : self.token
        }

        r = requests.post(f"{self.base_link}/channels/{id}/typing", headers=headers)
        time.sleep(last)


    def send(self, content, id, reply="", delay=0):
        self.type(id, delay)
        headers = {
            "Authorization" : self.token,
            "Content-Type" : "application/json",
            "Accept" :"application/json"
        }

        payload = {
            "content": content
        }
        if reply != "": payload["message_reference"] = reply

        r = requests.post(f"{self.base_link}/channels/{id}/messages", data=json.dumps(payload), headers=headers)
        return json.loads(r.text)


    def getGuildMembers(self, id, limit=1):
        headers = {
            "Authorization" : self.token,
            "Content-Type" : "application/json",
            "Accept" :"application/json"
        }

        r = requests.get(f"{self.base_link}/guilds/{id}/members?limit={limit}", headers=headers)
        return json.loads(r.text)


    def renameVoiceChannel(self, id, name):
        headers = {
            "Authorization" : self.token,
            "Content-Type": "application/json"
        }

        payload = {
            "name": f"{name}",
            "position": 0,
            "user_limit" : 0,
            "permission_overwrites" : [
                {
                        "id": "908404207340625960",
                    "type": 0,
                    "allow": "0",
                    "deny": "1049600"
                },
                {
                    "id": "908420813957509201",
                    "type": 0,
                    "allow": "1024",
                    "deny": "1048576"
                }
            ],
            "bitrate" : 64000,
            "rtc_region": "europe",
            "video_quality_mode":1
        }

        r = requests.patch(f"{self.base_link}/channels/{id}", data=json.dumps(payload), headers=headers)
        return json.loads(r.text)


    def getMe(self):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.get(f"{self.base_link}/users/@me", headers=headers)
        return json.loads(r.text)


    def ping(self, message):
        return f'<@{message["author"]["id"]}>'


    def allGuilds(self):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.get(f"{self.base_link}/users/@me/guilds", headers=headers)
        return json.loads(r.text)


    def getGuild(self, id):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.get(f"{self.base_link}/guilds/{id}?with_counts=true", headers=headers)
        return json.loads(r.text)


    def getGuildChannels(self, id):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.get(f"{self.base_link}/guilds/{id}/channels", headers=headers)
        return json.loads(r.text)


    def getGuildEmojis(self, id):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.get(f"{self.base_link}/guilds/{id}/emojis", headers=headers)
        return json.loads(r.text)


    def createReaction(self, channel_id, message_id, emoji):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.put(f"{self.base_link}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me", headers=headers)
        return r


    def getReactions(self, channel_id, message_id, emoji):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.get(f"{self.base_link}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}", headers=headers)
        return json.loads(r.text)


    def getChannelMessage(self, channel_id, message_id):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.get(f"{self.base_link}/channels/{channel_id}/messages/{message_id}", headers=headers)
        return json.loads(r.text)


    def deleteUserReaction(self, channel_id, message_id, emoji, user_id):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.delete(f"{self.base_link}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}", headers=headers)
        return r


    def modifyGuildMember(self, guild_id, user_id, nick="", roles="", mute=False, deaf=False, voice_channel_id=""):
        headers = {
            "Authorization" : self.token,
            "Content-Type" : "application/json",
            "Accept" :"application/json"
        }

        payload = {
            
        }

        if mute: payload["mute"] = mute
        if deaf: payload["deaf"] = deaf
        if roles != "": payload["roles"] = roles
        if nick != "": payload["nick"] = nick
        if voice_channel_id != "": payload["channel_id"] = voice_channel_id

        r = requests.patch(f"{self.base_link}/guilds/{guild_id}/members/{user_id}", data=json.dumps(payload), headers=headers)
        return json.loads(r.text)

    def getGuildRoles(self, guild_id):
        headers = {
            "Authorization" : self.token,
        }

        r = requests.get(f"{self.base_link}/guilds/{guild_id}/roles", headers=headers)
        return json.loads(r.text)


    def status(self, status):
        headers = {
            "Authorization" : self.token,
            "Content-Type" : "application/json",
            "Accept" :"application/json"
        }

        payload = {
            "status" : status
        }

        r = requests.patch(f"{self.base_link}/users/@me/settings", data=json.dumps(payload), headers=headers)
        return r
