import sqlite3
import discord
from github import Github


#Connects to db
conn = sqlite3.connect('data.db')
c = conn.cursor()
#Checks if table exists, creates one if it doesnt.
c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='data'")
if c.fetchone()[0] == 1:
    pass
else:
    c.execute("CREATE TABLE data (user TEXT, pets INTEGER)")
    conn.commit()

intents = discord.Intents.all() #inits new discord Intents system
client = discord.Client(intents=intents)

g = Github("token") #Add personal access token, or ("username", "password")
repo = g.get_repo("dragomagol/snitch-bot")

@client.event
async def on_ready():
    """Shows that bot and database have started successfully."""
    print("Database connected.") #database has connected
    print('Logged on. ({0.user})'.format(client)) #bot is ready

@client.event
async def on_message(message):
    """On message, handles commands."""
    if message.author == client.user: #avoids responding to itself
        return

    if message.content.startswith('.'): #if starts with '.'
        msg = message.content #shortens string var to make easier to concat
        msg = msg.split('.', 1)[1] #removes the '.'

        if msg.split(" ", 1)[0] in commands: #if msg in commands
            #accessess the dictionary with the name of the command,
            #turns it into a callable function
            to_send = commands[msg.split(" ", 1)[0]]
            await message.channel.send(to_send(message))
        elif "_" + msg.split(" ", 1)[0] in commands:
            #same thing only without an argument, the _ indicates that it doesnt require an arg.
            to_send = commands[("_" + msg.split(" ", 1)[0])]
            await message.channel.send(to_send())

#COMMANDS

def pet(message):
    """Pets user."""
    arg = get_args(message)
    if arg == "noarg": #If no argument is returned, don't run command.
        return "Invalid argument."
    in_guild = is_in_guild(message) #If user provided is in the server.

    if in_guild:
        user_in_db = False
        for user in c.execute("SELECT user FROM data"): #Checks if user is in database
            if user[0] == arg:
                user_in_db = True

        if user_in_db: #If user is already in the database
            c.execute("SELECT pets FROM data WHERE user = ?", (arg,))
            current_pets = c.fetchone()[0]
            #Adds one to pets :)
            c.execute("UPDATE data SET pets = ? WHERE user = ?", (current_pets + 1, arg))
        else:
            c.execute("INSERT INTO data VALUES (?,?)", (arg, 1)) #else create a new entry

        conn.commit()
        return "*Pets " + arg + "*" #Takes the argument of the command (mentioning a user)
    else:
        return "Invalid user provided!"

def hi_():
    """Returns a greeting!"""
    return "*chirp!*"

def stats(message):
    """Gets amount of times someone has been pet"""
    arg = get_args(message)

    if arg == "noarg": #If no argument is given
        return "Invalid argument."
    for user in c.execute("SELECT * FROM data WHERE user = ?", (arg,)):
        #Tells us how many times they've been pet
        return user[0] + " has been pet " + str(user[1]) + " times!"

def _help():
    """Returns a help statement."""
    ret = """
    .pet %username    —— Pets the person you mention. :) \n
    .stats %username —— Gets how many times the user you mention has been pet. :) \n
    .hi                              —— chirp \n.
    help                          —— Shows this message.
    """
    return ret

def pull_request():
    """Gets current PR information."""
    pulls = repo.get_pulls(state='open', sort='created', base='master')

    for pull in pulls:

        ret = "PR: #%s | %s | By: %s\nSee here: http://github.com/dragomagol/snitch-bot/pull/%s"
        return ret.format(str(pull.number), pull.title, pull.user.name, str(pull.number))

#END OF COMMANDS

def get_args(message):
    """Returns just argument of the message."""
    try:
        msg = message.content
        arg = msg.split(" ", 1)[1]
        #PC discord sends mentions with <@!id>, mobile sends it with <@id>
        #This checks if the ! is missing, and adds it to remove discrepancies.
        if arg[2] != '!':
            return arg[:2] + "!" + arg[2:]
        return arg
#If the function fails due to no argument provided, it will catch the error and return "noarg"
    except IndexError:
        return "noarg"

def is_in_guild(message): #Checks if the argument contains a valid user.
    """Checks if user is in guild."""
    try:
        arg = get_args(message)
        usr_id = arg[3:-1] #Removes <! > from the mention to isolate the user ID.
        guild = client.get_guild(message.guild.id) #gets the server
        if guild.get_member(int(usr_id)) is not None: #If the user is in the server
            return True
        return False
    except IndexError:
        return False

commands = {
    "pet": pet,
    "_hi": hi_,
    "stats": stats,
    "_help": _help,
    "_pr": pull_request
}
#inits commands
#Keeps commands in a dict, allows the func to be callable instead of using eval()

client.run('token') #Add token here.
