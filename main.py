import discord
import sqlite3

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
commands = ["pet", "_hi", "stats", "_help"] #inits commands
#commands with _ in front tell the argument handler that the command doesn't require an argument.

@client.event
async def on_ready():
    print("Database connected.") #database has connected
    print('Logged on. ({0.user})'.format(client)) #bot is ready
    
@client.event
async def on_message(message):
    if message.author == client.user: #avoids responding to itself
        return
        
    if message.content.startswith('.'): #if starts with '.'
        msg = message.content #shortens string var to make easier to concat
        msg = msg.split('.', 1)[1] #removes the '.'
        for command in commands: #loops through commands
            if msg.split(" ", 1)[0] == command: #ignores args
                #Takes input, removes the arguments sent by user, executes the func, and sends the original message.
                #This saves having an if statement for every command.
                to_send = eval(msg.split(" ", 1)[0] + "(message)") 
                await message.channel.send(to_send) #Sends the returned string.
            elif ("_" + msg.split(" ", 1)[0]) == command: #Checks to see if the command is available with a _ in front.
                #This will run the function without an argument, as it's not needed.
                to_send = eval(msg.split(" ", 1)[0] + "()") 
                await message.channel.send(to_send)

#COMMANDS

def pet(message):
    arg = get_args(message)
    if (arg == "noarg"): #If no argument is returned, don't run command.
        return "Invalid argument."
    else:
        in_guild = is_in_guild(message) #If user provided is in the server.

        if in_guild:
            user_in_db = False
            for user in c.execute("SELECT user FROM data"): #Checks if user is in database
                if user[0] == arg:
                    user_in_db = True 

            if user_in_db: #If user is already in the database
                c.execute("SELECT pets FROM data WHERE user = ?", (arg,))
                current_pets = c.fetchone()[0]
                c.execute("UPDATE data SET pets = ? WHERE user = ?", (current_pets + 1, arg)) #Adds one to pets :)
            else:
                c.execute("INSERT INTO data VALUES (?,?)", (arg, 1)) #else create a new entry
        
            conn.commit()
            return "*Pets " + arg + "*" #Takes the argument of the command (mentioning a user)
        else:
            return "Invalid user provided!"

def hi():
    return "*chirp!*"
  
def stats(message):
    arg = get_args(message)

    if (arg == "noarg"): #If no argument is given
        return "Invalid argument."
    else:
        for user in c.execute("SELECT * FROM data WHERE user = ?", (arg,)):
            return user[0] + " has been pet " + str(user[1]) + " times!" #Tells us how many times they've been pet

def help():
    return ".pet %username    —— Pets the person you mention. :) \n.stats %username —— Gets how many times the user you mention has been pet. :) \n.hi                              —— chirp \n.help                          —— Shows this message."

#END OF COMMANDS

def get_args(message): #Returns just argument of the message
    try:
        msg = message.content
        arg = msg.split(" ", 1)[1]
        #PC discord sends mentions with <@!id>, mobile sends it with <@id>
        #This checks if the ! is missing, and adds it to remove discrepancies. 
        if arg[2] != '!':
          return arg[:2] + "!" + arg[2:]
        else:
          return arg
    except: #If the function fails due to no argument provided, it will catch the error and return "noarg"
        return "noarg"

def is_in_guild(message): #Checks if the argument contains a valid user.
    try:
        arg = get_args(message)
        usr_id = arg[3:-1] #Removes <! > from the mention to isolate the user ID.
        guild = client.get_guild(message.guild.id) #gets the server
        if guild.get_member(int(usr_id)) is not None: #If the user is in the server
            return True
        else:
            return False
    except:
        return False

client.run('token') #Add token here.
