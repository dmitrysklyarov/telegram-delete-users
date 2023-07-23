import os
import pandas as pd
import telethon as T
from telethon.sync import TelegramClient
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.channels import InviteToChannelRequest

import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the contents of the file
config.read('secret.conf')

# Access the values using the section and key names
api_id = config.getint('MAIN', 'api_id')
api_hash = config.get('MAIN', 'api_hash')
phone = config.get('MAIN', 'phone')

client = TelegramClient(phone, api_id, api_hash)
client.connect()

def _isbot(object_of_dialog):
    i = object_of_dialog
    try:
        return i.entity.bot
    except:
        return False
    
def _is_chat_chanel_user(object_of_dialog):
    i = object_of_dialog
    if isinstance (i.message.peer_id, T.tl.types.PeerUser):
        return "user"
    elif isinstance (i.message.peer_id, T.tl.types.PeerChannel):
        return "Chnannel or SuperGroup or MegaGroup"
    elif isinstance (i.message.peer_id, T.tl.types.PeerChat):
        return "General Group"
    else:
        return ""

def _is_megagroup(ids):
    d = client.get_dialogs()
    for i in d:
        typ = i.message.peer_id
        if ids == i.id:
            return _is_chat_chanel_user(i)

def group_participant(target_group):
    all_participants = client.get_participants(target_group, aggressive=True)
    fullname = []
    uname = []
    user_id = []
    user_phone = []
    access_hash = []
    for i in all_participants:
        fname = ""
        lname = ""
        user_id.append(i.id)
        user_phone.append(i.phone)
        access_hash.append(i.access_hash)
        if i.last_name is not None:
            lanme = i.last_name
        if i.first_name is not None:
            fname = i.first_name
        fullname.append(fname + " " + lname)
        if uname is not None:
            uname.append(i.username)
    else:
        return fullname, uname, user_phone, user_id, access_hash

def get_id_by_name(user_or_group_name):
    d = client.get_dialogs()
    for i in d:
        titl = i.name
        if titl.lower() == user_or_group_name.lower():
           return i.id
        
def get_name_by_id(user_or_group_id):
    d = client.get_dialogs()
    for i in d:
        if user_or_group_id == i.id:
            x = str(i.name) + "-" + str(i.username) + "-" + str(i.first_name)
            print(x)

def add_user_in_group(group_id,user_id):
    try:
        user_to_add = client.get_input_entity(user_id)
        group_to_add = client.get_input_entity(group_id)
        client(InviteToChannelRequest(group_to_add,[user_to_add]))
        nm = get_name_by_id(user_id)
        print("user - ", nm, " successfully add ")
    except:
        typ = _is_megagroup(group_id)
        print("user id: ",user_id," argument id type is : ", typ, " failed to add")

async def kick_user_from_group(group_id_or_name,user_id_name):
    user = await client.get_input_entity(user_id_name)
    chat = await client.get_input_entity(group_id_or_name)
    try:
        msg = await client.kick_participant(chat, user)
        print(msg)
        await msg.delete()
        print('user removed')
    except Exception as ex:
        print(f"Error: {ex}")
        print('failed removing')

def get_details_by_id(user_or_group_id=False):
    d = client.get_dialogs()
    for i in d:
        nm = i.title
        isbot = _isbot(i)
        typ = i.message.peer_id
        if user_or_group_id != True:
            if i.id == user_or_group_id:
                print("name= ",nm," bot= ",isbot,"id_type= ",_is_chat_chanel_user(i))
            else:
                pass
        else:
            print("name=",nm," bot=",isbot,"id_type=",_is_chat_chanel_user(i))

def kick_all_from_group(group_name):
    dclow = get_id_by_name(group_name)
    fullname, uname, user_phone, user_id, access_hash =  group_participant(group_name)
    for i in user_id:
        kick_user_from_group(dclow, i)

def clone_group_users(group_mother,group_chlid):
    fullname, uname, user_phone, user_id, access_hash =  group_participant(get_id_by_name(group_mother))
    fullname_c, uname_c, user_phone_c, user_id_c, access_hash_c =  group_participant(get_id_by_name(group_chlid))
    for i in user_id:
        if i not in user_id_c:
            add_user_in_group(get_id_by_name(group_chlid),i)
        else:
            print(get_name_by_id(i), " already exist")

def group_participant_into_csv(group_name_or_id, csv_save_path= os.getcwd()):
    if csv_save_path == False:
        csv_save_path = os.getcwd()
    fullname, uname, user_phone, user_id, access_hash =  group_participant(group_name_or_id)
    df = pd.DataFrame (list(zip(fullname, uname, user_phone, user_id)),columns =['fullname', 'username', 'phone', 'id'])
    try:
        print(csv_save_path + "\\" + str(group_name_or_id) + ".csv")
        df.to_csv(csv_save_path + "\\" + str(group_name_or_id) + ".csv")
    except:
        print("invalid path: " + csv_save_path)