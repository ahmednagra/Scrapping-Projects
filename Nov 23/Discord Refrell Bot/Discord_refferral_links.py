import csv
import glob
from datetime import datetime

import discord
from discord.ext import commands

from googleapiclient.discovery import build, logger
from oauth2client.service_account import ServiceAccountCredentials

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='&', intents=intents)


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('input/mine_credentials.json', scope)

invites = {}


@bot.event
async def on_ready():
    for guild in bot.guilds:
        invites[guild.id] = await guild.invites()
        print('Waiting For Member Joining')


def find_invite_by_code(invites, code):
    for invite in invites:
        if invite.code == code:
            return invite

    return None


@bot.event
async def on_member_join(member):
    # Getting the invites before the user joins from our cache for this specific guild
    invites_before_join = invites[member.guild.id]

    # Getting the invites after the user joins,  we can compare them with the first ones
    invites_after_join = await member.guild.invites()

    for invite in invites_before_join:
        new_invite = find_invite_by_code(invites_after_join, invite.code)

        if new_invite is not None and invite.uses < new_invite.uses:
            # Now that we found which link was used, we will print the details
            entry = {
                "profile_name": member.display_name,
                "name": member.name,
                "referral_link": invite.code,
                "inviter_username": invite.inviter,
                "inviter_profile_name": invite.inviter.display_name
            }

            # Update our cache for the next user who joins the guild
            invites[member.guild.id] = invites_after_join
            update_google_sheet(entry)

            return


def update_google_sheet(entry):
    current_datetime = datetime.now()
    date_time = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
    inviter_username = entry['inviter_username'].name if entry.get('inviter_username') else ''
    rows_values = [
        [entry['profile_name'], entry['name'], entry['referral_link'], inviter_username, entry['inviter_profile_name'],
         date_time]]

    spreadsheet_id = read_config_inputfile().get('googlesheet_id', '')
    tab_sheet_name = read_config_inputfile().get(f'tab_name')

    service = build('sheets', 'v4', credentials=creds)
    sheet_range = tab_sheet_name

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=sheet_range,
        body={
            "majorDimension": "ROWS",
            "values": rows_values  # representing each row values as list. So it contains as list of lists
        },
        valueInputOption="USER_ENTERED"
    ).execute()

    logger.debug(f'Google Sheet "{tab_sheet_name}" has been updated\n\n')


def read_config_inputfile():
    file_path = ''.join(glob.glob('input/config.txt'))
    config = {}
    try:
        with open(file_path, mode='r') as txt_file:
            for line in txt_file:
                line = line.strip()
                if line and '==' in line:
                    key, value = line.split('==', 1)
                    config[key.strip()] = value.strip()

        return config

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []


if __name__ == '__main__':
    print('PyCharm')
    bot_token = read_config_inputfile().get('bot_token', '')
    if bot_token:
        bot.run(bot_token)
    else:
        print("Bot token not found in the configuration file.")
