import discord, asyncio, random
from discord.ext import commands
from discord import app_commands, Intents, ButtonStyle, ui
from discord.ui import Button, View
from tinydb import TinyDB, Query

intents = Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

db = TinyDB('data.json')
users = Query()


@bot.event
async def on_ready():
    print("Winter System")
    await bot.change_presence(activity=discord.Game(name="Winter Scripts"))
    try:
        synced = await bot.tree.sync()
        print("Synced " + str(len(synced)) + " commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="coins", description="View someones's coins amount")
@app_commands.describe(user="Who ?")
async def coins(interaction:discord.Interaction, user:discord.Member=None):
    if user == None:
        user = interaction.user
        try:
            data = db.search(users.user == user.id)[0]
            coins_amount = data.get('coins')
            await interaction.response.send_message("**:coin: "+user.name+", your coins amount is $"+str(coins_amount)+".**")
        except IndexError:
            db.insert({'user':user.id, 'coins':0})
            await interaction.response.send_message("**:coin: "+user.name+", your coins amount is $0.**")
    else:
        try:
            data = db.search(users.user == user.id)[0]
            coins_amount = data.get('coins')
            await interaction.response.send_message("**:coin: "+user.name+" coins amount is $"+str(coins_amount)+".**")
        except IndexError:
            db.insert({'user':user.id, 'coins':0})
            await interaction.response.send_message("**:coin: "+user.name+" coins amount is $0.**")

@bot.tree.command(name="transfer", description="Transfer coins to another user")
@app_commands.describe(user="Who ?", amount="How many ?")
async def transfer(interaction:discord.Interaction, user:discord.Member, amount:int):
    try:
        transferrer_data = db.search(users.user == interaction.user.id)[0]
        transferrer_coins = transferrer_data.get("coins")
        try:
            receiver_data = db.search(users.user == user.id)[0]
            receiver_coins = receiver_data.get("coins")
        except IndexError:
            db.insert({'user':user.id, 'coins':0})
        if int(transferrer_coins) > amount:
            new_transferrer_coins = int(transferrer_coins) - amount
            db.remove(users.user == interaction.user.id)
            db.insert({'user':interaction.user.id, 'coins':new_transferrer_coins})

            new_receiver_coins = int(receiver_coins) + amount
            db.remove(users.user == user.id)
            db.insert({'user':user.id, 'coins':new_receiver_coins})
            await interaction.response.send_message("**🏦 "+interaction.user.name+" successfully transferred $"+str(amount)+" to "+user.mention+"**")
        elif int(transferrer_coins) < amount:
            await interaction.response.send_message("**You haven't this coins amount, you can't transfer it.**")
    except IndexError:
        db.insert({'user': interaction.user.id, 'coins': 0})
        await interaction.response.send_message("**You haven't this coins amount, you can't transfer it.**")

@bot.tree.command(name="give_coins", description="Add coins to someone's account")
@app_commands.describe(user="Who ?", amount="How many?")
async def give_coins(interaction:discord.Interaction, user:discord.Member, amount:int):
    if interaction.user.guild_permissions.administrator:
        try:
            data = db.search(users.user == user.id)[0]
            old_coins = data.get('coins')
            new_coins = old_coins + amount
            db.remove(users.user == user.id)
            db.insert({'user':user.id, 'coins':new_coins})
        except IndexError:
            db.insert({'user':user.id, 'coins':amount})
        await interaction.response.send_message("**You successfully added "+str(amount)+" to "+user.name+"'s account **")

@bot.tree.command(name="remove_coins", description="Remove coins from someone's account")
@app_commands.describe(user="Who ?", amount="How many?")
async def remove_coins(interaction:discord.Interaction, user:discord.Member, amount:int):
    if interaction.user.guild_permissions.administrator:
        try:
            data = db.search(users.user == user.id)[0]
            old_coins = data.get('coins')
            if amount <= old_coins:
                new_coins = old_coins - amount
                db.remove(users.user == user.id)
                db.insert({'user':user.id, 'coins':new_coins})
            else:
                await interaction.response.send_message("**"+user.name+"'s doesn't have this coins amount**")
        except IndexError:
            await interaction.response.send_message("**" + user.name + "'s doesn't have this coins amount**")
        await interaction.response.send_message("**You successfully removed "+str(amount)+" from "+user.name+"'s account **")

@bot.tree.command(name="delete_coins", description="Set someone's coins amount to 0")
@app_commands.describe(user="Who ?")
async def delete_coins(interaction:discord.Interaction, user:discord.Member):
    if interaction.user.guild_permissions.administrator:
        try:
            data = db.search(users.user == user.id)[0]
            db.remove(users.user == user.id)
            db.insert({'user': user.id, 'coins': 0})
        except:
            db.insert({'user': user.id, 'coins': 0})
        await interaction.response.send_message("**You successfully set "+user.name+"'s coins amount to 0**")


bot.run("token")
