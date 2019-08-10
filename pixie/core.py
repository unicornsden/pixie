# discord bot - main application
import discord
import subprocess
import os
import sys
import traceback
from . import commands
from . import messages
from . import data
from .messages import MessageWrapper

client = discord.Client()

def run_bot(token=None):

    data.init()

    if token is not None:
        data.TOKEN = token.strip()
    if len(sys.argv) >= 2:
        data.TOKEN = sys.argv[1].strip()
    elif os.path.isfile('./bot-token'):
        with open('./bot-token', 'r') as f:
            data.TOKEN = f.read().strip()
    else:
        sys.exit("No TOKEN supplied")

    client.run(data.TOKEN)


@client.event
async def on_message(message):
    """
    Called whenever a message is read by the bot.
    :param message: The discord.Message
    :return: None
    """

    # Don't react to bot itself
    if message.author == client.user:
        return

    command = messages.get_command(message, data.CMDCHAR)

    # Don't do anything if there was no valid command.
    if command is None:
        return

    # Wrap message to allow additional attributes to be passed along
    message = MessageWrapper(message)
    message.command = command

    # Get args (all strings after the command separated by ' ')
    args = messages.get_args(message)
    message.args = args

    # noinspection PyBroadException
    # catch exceptions
    try:
        msg = commands.handle_commands(message)
    except Exception as e:
        print('Exception thrown: ' + str(e) + '\n')
        traceback.print_exc()
        msg = '''\
Something went wrong.
This is so sad. Alexa, play Despacito!'''

    if not msg or isinstance(msg, int):
        return

    await message.channel.send(msg)


@client.event
async def on_ready():
    if os.path.exists(data.DATAPATH):
        print('data already exists')
    else:
        if not os.path.isfile('create_env.sh'):
            return
        subprocess.run(['bash', 'create_env.sh'])
        print('data created')
