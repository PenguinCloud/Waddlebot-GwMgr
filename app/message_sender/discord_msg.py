import requests
import logging

# Set the loggimg level to DEBUG

class Discord_Message_Sender:
    def __init__(self, token, server_id, message):
        self.token = token
        self.server_id = server_id
        self.message = message

        self.user_id = self.get_owner_id(server_id)
        self.channel_id = self.create_dm_channel()

    def send_message(self):
        logging.info(f"Sending message to channel {self.channel_id}")

        url = 'https://discord.com/api/v10/channels/{}/messages'.format(self.channel_id)
        data = {"content": self.message}
        header = {"Authorization": f"Bot {self.token}"}

        r = requests.post(url, data=data, headers=header)
        
        logging.info(f"Status code: {r.status_code}")

    def create_dm_channel(self):
        if(self.user_id == None):
            logging.error("User id not found")
            return None
        
        logging.info(f"Creating DM channel with user {self.user_id}")

        data = {"recipient_id": self.user_id}
        headers = {"Authorization": f"Bot {self.token}"}

        r = requests.post(f'https://discord.com/api/v10/users/@me/channels', json=data, headers=headers)

        logging.info(f"Status code: {r.status_code}")

        channel_id = r.json()['id']

        return channel_id
    
    # A function that uses a given server name to retrieve the owner id of the server
    def get_owner_id(self, server_name):
        logging.info(f"Getting owner id of server {server_name}")

        url = f'https://discord.com/api/v10/guilds/{server_name}'
        headers = {"Authorization": f"Bot {self.token}"}
        r = requests.get(url, headers=headers)
        
        if r.status_code == 200:
            logging.info(f"Server {server_name} found. Getting owner.")

            data = r.json()
            # The key 'owner_id' is the owner of the server. Check if this key is in the data
            if 'owner_id' in data:
                return data['owner_id']
            else:
                logging.error(f"Owner id not found in server {server_name}")
                return None
        else:
            logging.error(f"Server {server_name} not found. Status code: {r.status_code}")

        return None
    


# def sendMessage(token, channel_id, message):
#     url = 'https://discord.com/api/v8/channels/{}/messages'.format(channel_id)
#     data = {"content": message}
#     header = {"authorization": token}
 
#     r = requests.post(url, data=data, headers=header)
#     logging.info(r.status_code)
 
 
# def createDmChannel(token, user_id):
#     data = {"recipient_id": user_id}
#     headers = {"authorization": token}
 
#     r = requests.post(f'https://discord.com/api/v9/users/@me/channels', json=data, headers=headers)
#     logging.info(r.status_code)
 
#     channel_id = r.json()['id']
 
#     return channel_id
 
 
# #Change these variables
# token = ''
# user_id = ''
# message = ''
 
# channel_id = createDmChannel(token, user_id)
# sendMessage(token, channel_id, message)