import discord

#COMMANDS
def pet(msg):
    return "*Pets " + msg.split(" ", 1)[1] + "*" #Takes the argument of the command (mentioning a user)

def hi(msg):
    return "*chirp*"

#END OF COMMANDS

client = discord.Client()
commands = ["pet", "hi"] #inits commands
@client.event
async def on_ready():
    print('Logged on. ({0.user})'.format(client)) #bot is ready
    
@client.event
async def on_message(message):
    if message.author == client.user: #avoids responding to itself
        return
        
    if message.content.startswith('.'): #if starts with '.'
        msg = message.content #shortens string var to make easier to concat
        msg = msg.split('.', 1)[1] #removes the '.'
        for x in commands: #loops through commands
            if msg.split(" ", 1)[0] == x: #ignores args
                #Takes input, removes the arguments sent by user, executes the func, and sends the original message.
                #This saves having an if statement for every command.
                to_send = eval(msg.split(" ", 1)[0] + "(msg)") 
                await message.channel.send(to_send) #Sends the returned string.

client.run('token')
