import tele
import os
import asyncio
from telethon.tl.custom.dialog import Dialog
from telethon.tl.types import ChannelAdminLogEventActionChangeAbout
from telethon.tl.types import ChatParticipantCreator, ChatParticipantAdmin
import telethon
import data


os.system("clear")
print("starting...")

def print_all_groups_where_i_am_admin():
    for group_id in data.all_groups:
        channel:telethon.tl.types.Channel = tele.client.get_entity(group_id)
        participants = tele.client.get_participants(channel)
        user:telethon.tl.types.User
        for user in participants:
            if user.is_self and (type(user.participant) == telethon.tl.types.ChannelParticipantAdmin or type(user.participant) == telethon.tl.types.ChannelParticipantCreator):
                print(f"{group_id}: \'{data.all_groups[group_id]}\',")
#print_all_groups_where_i_am_admin()

def delete_users():
    for group_id in data.admin_groups:
        channel:telethon.tl.types.Channel = tele.client.get_entity(group_id)
        participants = tele.client.get_participants(channel)
        for user in participants:
            if user.id in data.members_to_delete:
                try:
                    tele.client.kick_participant(channel, user.id)
                    print("user - ", data.members_to_delete[user.id], "is deleted from ", data.all_groups[group_id])
                except Exception as ex:
                    print("Error: ", ex)
                    print("user - ", data.members_to_delete[user.id], "is NOT deleted from ", data.all_groups[group_id])
#delete_users()

def print_list_not_deleted_group_with_admins():
    for group_id in data.all_groups:
        try:
            channel:telethon.tl.types.Channel = tele.client.get_entity(group_id)
            participants = tele.client.get_participants(channel)
            for user in participants:
                if user.id in data.members_to_delete:
                    admin:telethon.tl.types.User = None
                    for u in participants:
                        if type(u.participant) == telethon.tl.types.ChannelParticipantCreator:
                            admin = u
                            break
                    if admin is None:
                        for u in participants:
                            if type(u.participant) == telethon.tl.types.ChannelParticipantAdmin:
                                admin = u
                                break
                    if admin is None:
                        break
                    else:
                        print(f"{group_id}: {admin.id},")
        except Exception as ex:
            print("Error:", ex)
            print("Problem with:", data.all_groups[group_id])
#print_list_not_deleted_group_with_admins()

def create_message_for_admin():
    messages = {}
    for group_id in data.groups_with_admins:
        channel:telethon.tl.types.Channel = tele.client.get_entity(group_id)
        participants = tele.client.get_participants(channel)
        participants_to_delete = []
        for user in participants:
            if user.id in data.members_to_delete:
                participants_to_delete.append(user.username)
        if len(participants_to_delete) == 0: continue
        if data.groups_with_admins[group_id] in messages:
            messages[data.groups_with_admins[group_id]].append({channel.title: participants_to_delete})
        else:
            messages[data.groups_with_admins[group_id]] = [{channel.title: participants_to_delete}]
    for user, message in messages.items():
        name = tele.client.get_entity(user).username
        text = f"Добрый день, @{name}!\n"
        text += "Удали(те), пожалуйста, из групп(ы) следующего(их) пользователя(ей):"
        for group in message:
            for group_name, users in group.items():
                text += f"\n - Группа: \"{group_name}\". Необходимо удалить пользователя(ей): "
                for u in users:
                    text += f"\"{u}\", "
        text += "\n"
        text += "Или сделай(те), пожалуйста, меня админом в указанных группах, я удалю этих пользователей самостоятельно\n"
        
        #be carefull when uncomment the line below
        #tele.client.send_message(user, text)
#create_message_for_admin()

tele.client.disconnect()
print("finished")
