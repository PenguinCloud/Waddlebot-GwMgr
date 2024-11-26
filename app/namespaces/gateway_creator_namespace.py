# Import the twitch message sender class

from flask import Flask, request, make_response, jsonify, send_file, render_template
from flask_restx import Resource, Api, fields, reqparse, abort, Namespace
import logging
import json
import os
from datetime import datetime
import base64
import sys
import requests
import uuid
# from app.test.test import test

from dotenv import load_dotenv
from message_sender.twitch_msg import Twitch_Message_Sender
from message_sender.discord_msg import Discord_Message_Sender

# Set the logging level to INFO
logging.basicConfig(level=logging.INFO)

# This scripts handles the creation of a gateway in the application, as a namespace

gateway_creator_namespace = Namespace('gateway-creator', description='Gateway Creator operations')

gateway_creator_model = gateway_creator_namespace.model('Gateway Creator', {
    # 'account_name': fields.String(required=True, description='The account name'),
    'gateway_type_name': fields.String(required=True, description='The gateway type name'),
    'channel_id': fields.String(required=True, description='The channel id')})

# Check if the .env file exists
# if not os.path.exists('.env'):
#     raise Exception('.env file not found')

load_dotenv()

# Check if the gateway creation URL is set in the environment
if 'GATEWAY_CREATION_URL' not in os.environ:
    raise Exception('GATEWAY_CREATION_URL environment variable not set')

# Check if the gateway deletion URL is set in the environment
if 'GATEWAY_DELETION_URL' not in os.environ:
    raise Exception('GATEWAY_DELETION_URL environment variable not set')

# Check if the gateway server get URL is set in the environment
if 'GATEWAY_SERVER_GET_URL' not in os.environ:
    raise Exception('GATEWAY_SERVER_GET_URL environment variable not set')

# Check if gateway server create URL is set in the environment
if 'GATEWAY_SERVER_CREATE_URL' not in os.environ:
    raise Exception('GATEWAY_SERVER_CREATE_URL environment variable not set')

# Check if the gateway server deletion URL is set in the environment
if 'GATEWAY_SERVER_DELETE_URL' not in os.environ:
    raise Exception('GATEWAY_SERVER_DELETE_URL environment variable not set')

# Get the gateway creation URL from the environment
gateway_creation_url = os.getenv('GATEWAY_CREATION_URL')
gateway_deletion_url = os.getenv('GATEWAY_DELETION_URL')
gateway_server_get_url = os.getenv('GATEWAY_SERVER_GET_URL')
gateway_server_create_url = os.getenv('GATEWAY_SERVER_CREATE_URL')
gateway_server_delete_url = os.getenv('GATEWAY_SERVER_DELETE_URL')

# Check if the twitch host, port and pass are set in the environment
if 'TWITCH_HOST' not in os.environ:
    raise Exception('TWITCH_HOST environment variable not set')
if 'TWITCH_PORT' not in os.environ:
    raise Exception('TWITCH_PORT environment variable not set')
if 'TWITCH_PASS' not in os.environ:
    raise Exception('TWITCH_PASS environment variable not set')
if 'TWITCH_NICK' not in os.environ:
    raise Exception('TWITCH_NICK environment variable not set')

# Get the twitch host, port and pass from the environment
twitch_host = os.getenv('TWITCH_HOST')
twitch_port = os.getenv('TWITCH_PORT')
twitch_pass = os.getenv('TWITCH_PASS')
twitch_nick = os.getenv('TWITCH_NICK')

# Check if the twitch auth url, client id, redirect uri, response type and scope are set in the environment
if 'TWITCH_AUTH_URL' not in os.environ:
    raise Exception('TWITCH_AUTH_URL environment variable not set')
if 'TWITCH_AUTH_CLIENT_ID' not in os.environ:
    raise Exception('TWITCH_AUTH_CLIENT_ID environment variable not set')
if 'TWITCH_AUTH_REDIRECT_URI' not in os.environ:
    raise Exception('TWITCH_AUTH_REDIRECT_URI environment variable not set')
if 'TWITCH_AUTH_RESPONSE_TYPE' not in os.environ:
    raise Exception('TWITCH_AUTH_RESPONSE_TYPE environment variable not set')
if 'TWITCH_AUTH_SCOPE' not in os.environ:
    raise Exception('TWITCH_AUTH_SCOPE environment variable not set')

# Get the twitch auth url, client id, redirect uri, response type and scope from the environment
twitch_auth_url = os.getenv('TWITCH_AUTH_URL')
twitch_auth_client_id = os.getenv('TWITCH_AUTH_CLIENT_ID')
twitch_auth_redirect_uri = os.getenv('TWITCH_AUTH_REDIRECT_URI')
twitch_auth_response_type = os.getenv('TWITCH_AUTH_RESPONSE_TYPE')
twitch_auth_scope = os.getenv('TWITCH_AUTH_SCOPE')

# Check if the discord token and bot invite URL is included in the environment
if 'DISCORD_TOKEN' not in os.environ:
    raise Exception('DISCORD_TOKEN environment variable not set')
if 'DISCORD_BOT_INVITE_URL' not in os.environ:
    raise Exception('DISCORD_BOT_INVITE_URL environment variable not set')

# Get the discord token and invite URL from the environment
discord_token = os.getenv('DISCORD_TOKEN')
discord_bot_invite_url = os.getenv('DISCORD_BOT_INVITE_URL')

# Function route to get the default account for a given account type
# def get_default_account(account_type):
#     try:
#         response = requests.get(gateway_default_account_get_url, json={'account_type_name': account_type})
#         response_payload = response.json()
#         if 'data' not in response_payload and len(response_payload['data']) == 0:
#             return make_response(jsonify({'msg': 'Something went wrong while getting the default account. Please try again later, or contact a technician for further assistance'}), 500)

#         response_data = response_payload['data']
#         if 'account_name' not in response_data[0]:
#             return make_response(jsonify({'msg': 'Something went wrong while getting the default account. Please try again later, or contact a technician for further assistance'}), 500)

#         account_name = response_data[0]['account_name']
#         return account_name
#     except Exception as e:
#         return make_response(jsonify({'msg': str(e)}), 500)

# Function to get the list of gateway servers from the gateway server service and return the list
def get_gateway_servers():
    try:
        response = requests.get(gateway_server_get_url)
        response_payload = response.json()
        if 'data' not in response_payload and len(response_payload['data']) == 0:
            return make_response(jsonify({'msg': 'Something went wrong while getting the gateway servers. Please try again later, or contact a technician for further assistance'}), 500)

        response_data = response_payload['data']
        return response_data
    except Exception as e:
        return make_response(jsonify({'msg': str(e)}), 500)
    
# Function to generate a uuid
def generate_uuid():
    return str(uuid.uuid4())

# Function to build the twitch auth url
def build_twitch_auth_url(activation_code):
    return f'{twitch_auth_url}?client_id={twitch_auth_client_id}&redirect_uri={twitch_auth_redirect_uri}&response_type={twitch_auth_response_type}&scope={twitch_auth_scope}&force_verify=true&state={activation_code}'

# Function route to create a gateway
@gateway_creator_namespace.route('/')
class GatewayCreator(Resource):
    @gateway_creator_namespace.expect(gateway_creator_model)
    def post(self):
        try:
            # account_name = request.json['account_name']
            gateway_type_name = request.json['gateway_type_name']
            channel_id = request.json['channel_id']

            gateway_type_name = gateway_type_name.capitalize()

            # Check if all the payload parameters are set
            if not gateway_type_name:
                return make_response(jsonify({'msg': 'Gateway type name not set'}), 400)
            if not channel_id:
                return make_response(jsonify({'msg': 'Channel id not set'}), 400)
            
            # Get the default account
            # account_name = get_default_account(gateway_type_name)

            # Get the gateway servers
            gateway_servers = get_gateway_servers()

            # if not account_name:
            #     return make_response(jsonify({'msg': 'Default gateway account could not be found.'}), 400)

            default_twitch_server = None

            # Get the default twitch server
            for server in gateway_servers:
                if server['server_type'] == 'Twitch':
                    default_twitch_server = server['name']
                    break

            # Check that the gateway type is "Twitch" or "Discord", because only twitch and discord is currently supported
            if gateway_type_name != 'Twitch' and gateway_type_name != 'Discord':
                return make_response(jsonify({'msg': 'Gateway type not supported. Only Twitch is currently available for support.'}), 400)
            elif gateway_type_name == 'Twitch' and default_twitch_server is not None:
                # Generate an activation code
                activation_code = generate_uuid()
                response = requests.post(gateway_creation_url, json={'gateway_server_name': default_twitch_server, 'gateway_type_name': gateway_type_name, 'channel_id': channel_id, 'activation_key': activation_code})

                # The response payload should be a JSON object and contain a key 'msg'
                response_payload = response.json()
                if 'msg' not in response_payload:
                    return make_response(jsonify({'msg': 'Something went wrong while creating the gateway. Please try again later, or contact a technician for further assistance'}), 500)

                # Return the response payload msg value from the gateway creation service
                msg = response_payload['msg']

                # Check if a status key is present in the response payload. Return a 500 error if it is not present
                if 'status' not in response_payload:
                    return make_response(jsonify({'msg': 'Something went wrong while creating the gateway. Please try again later, or contact a technician for further assistance'}), 500)
                    
                status = response_payload['status']

                # If the gateway was created successfully, send a message to the twitch channel
                if status == 201:
                    # Create the twitch message sender object
                    twitch_message_sender = Twitch_Message_Sender(twitch_host, int(twitch_port), twitch_nick, twitch_pass, channel_id)
                    # Build the twitch auth url
                    twitch_auth_url = build_twitch_auth_url(activation_code)
                    # twitch_auth_url = "TEST"
                    # Send the message to the twitch channel
                    twitch_msg = f"Welcome to WaddleBot, {channel_id}! First of all, please mod WaddleBot on your channel. Then, click on the following link to authenticate your account: {twitch_auth_url}."
                    # twitch_msg = f"{twitch_auth_url}"
                    twitch_message_sender.send_message(twitch_msg)

                    return make_response(jsonify({'msg': msg}), 200)
                else:
                    return make_response(jsonify({'msg': msg}), 500)
                

            # If the gateway type is Discord, create a new gateway server and then create the gateway
            elif gateway_type_name == 'Discord':
                # Currently, the call only has 2 parameters. We are going to assume that the server name is the same as the channel id for now for discord. TODO: Make this more elegant
                server_name = request.json['channel_id']

                # Create a new gateway server
                response = requests.post(gateway_server_create_url, json={'name': server_name, 'server_type_name': 'Discord', 'server_id': server_name, 'server_nick': 'waddlebot'})

                # The response payload should be a JSON object and contain a key 'msg'
                response_payload = response.json()
                if 'msg' not in response_payload:
                    return make_response(jsonify({'msg': 'Something went wrong while creating the gateway. Please try again later, or contact a technician for further assistance'}), 500)
                
                logging.info(response_payload)
                # If the server creation process was successful, create the gateway route
                if response_payload['status'] == 201:
                    logging.info(f"Server {server_name} created successfully. Creating gateway now.")

                    # Generate an activation code
                    activation_code = generate_uuid()
                    response = requests.post(gateway_creation_url, json={'gateway_server_name': server_name, 'gateway_type_name': gateway_type_name, 'channel_id': "general", 'activation_key': activation_code})

                    logging.info(f"Got a response from the gateway creation service")

                    # The response payload should be a JSON object and contain a key 'msg'
                    response_payload = response.json()
                    if 'msg' not in response_payload:
                        return make_response(jsonify({'msg': 'Something went wrong while creating the gateway. Please try again later, or contact a technician for further assistance'}), 500)

                    logging.info(f"Got a message from the gateway creation service")

                    # Return the response payload msg value from the gateway creation service
                    msg = response_payload['msg']

                    # Check if a status key is present in the response payload. Return a 500 error if it is not present
                    if 'status' not in response_payload:
                        return make_response(jsonify({'msg': 'Something went wrong while creating the gateway. Please try again later, or contact a technician for further assistance'}), 500)
                        
                    status = response_payload['status']

                    logging.info(f"Got a status of {status}")

                    # If the gateway was created successfully, send a message to the discord channel
                    if status == 201:
                        logging.info(f"Starting the discord message sending process")

                        # Create a message to send to the discord channel
                        discord_msg = f"Welcome to WaddleBot, {server_name}! Please follow the following link to add the bot to your server: {discord_bot_invite_url}. Afterwards, your set up is complete! Enjoy using WaddleBot!"

                        # Create the discord message sender object
                        logging.info(f"Creating discord message sender object")
                        discord_message_sender = Discord_Message_Sender(discord_token, server_name, discord_msg)


                        # Send the message to the discord channel
                        logging.info(f"Sending message to discord channel {server_name}")
                        discord_message_sender.send_message()

                        return make_response(jsonify({'msg': msg}), 200)
                    else:
                        return make_response(jsonify({'msg': msg}), 500)
                else:
                    logging.info("AN ERROR OCURRED")
                    if 'msg' in response_payload:
                        return make_response(jsonify({'msg': response_payload['msg']}), 500)
                    return make_response(jsonify({'msg': 'Something went wrong while creating the gateway. Please try again later, or contact a technician for further assistance.'}), 500)
            else:
                return make_response(jsonify({'msg': 'Gateway type not supported. Only Twitch and Discord is currently available for support.'}), 400)

            # return make_response(jsonify({'msg': msg}), 200)
        except Exception as e:
            return make_response(jsonify({'msg': str(e)}), 500)
        
    # Function route to delete a gateway
    @gateway_creator_namespace.expect(gateway_creator_model)
    def delete(self):
        try:
            # account_name = request.json['account_name']
            gateway_type_name = request.json['gateway_type_name']
            channel_id = request.json['channel_id']

            # Check if all the payload parameters are set
            if not gateway_type_name:
                return make_response(jsonify({'msg': 'Gateway type name not set'}), 400)
            if not channel_id:
                return make_response(jsonify({'msg': 'Channel id not set'}), 400)
            
            # Check that the gateway type is "Twitch" or "Discord", because only twitch and discord is currently supported
            if gateway_type_name != 'Twitch' and gateway_type_name != 'Discord':
                return make_response(jsonify({'msg': 'Gateway type not supported. Only Twitch is currently available for support.'}), 400)
            elif gateway_type_name == 'Twitch':
                response = requests.delete(gateway_deletion_url, json={'gateway_type_name': gateway_type_name, 'channel_id': channel_id})

                # The response payload should be a JSON object and contain a key 'msg'
                response_payload = response.json()
                if 'msg' not in response_payload:
                    return make_response(jsonify({'msg': 'ERROR IN WADDLEBOT DB DELETION'}), 500)

                # Return the response payload msg value from the gateway creation service
                msg = response_payload['msg']

                # Check if a status key is present in the response payload. Return a 500 error if it is not present
                if 'status' not in response_payload:
                    return make_response(jsonify({'msg': 'Something went wrong while deleting the gateway. Please try again later, or contact a technician for further assistance'}), 500)
                    
                status = response_payload['status']

                # If the gateway was deleted successfully, send a message to the twitch channel
                if status == 200:
                    # Create the twitch message sender object
                    twitch_message_sender = Twitch_Message_Sender(twitch_host, int(twitch_port), twitch_nick, twitch_pass, channel_id)
                    # Send the message to the twitch channel
                    twitch_msg = f"Hi there! Your gateway has been deleted successfully. Thank you for using WaddleBot!"
                    twitch_message_sender.send_message(twitch_msg)

                    return make_response(jsonify({'msg': msg}), 200)
                else:
                    return make_response(jsonify({'msg': msg}), 500)
                
            elif gateway_type_name == 'Discord':
                # Currently, the call only has 2 parameters. We are going to assume that the server name is the same as the channel id for now for discord. TODO: Make this more elegant
                server_name = request.json['channel_id']

                response = requests.delete(gateway_server_delete_url + f'{server_name}')

                # The response payload should be a JSON object and contain a key 'msg'
                response_payload = response.json()
                if 'msg' not in response_payload:
                    return make_response(jsonify({'msg': 'An error occurred while deleting the gateway server. Please try again later, or contact a technician for further assistance'}), 500)

                # After the server was successfully deleted, delete the gateway
                response = requests.delete(gateway_deletion_url, json={'gateway_type_name': gateway_type_name, 'channel_id': channel_id})

                # Return the response payload msg value from the gateway creation service
                msg = response_payload['msg']

                # Check if a status key is present in the response payload. Return a 500 error if it is not present
                if 'status' not in response_payload:
                    return make_response(jsonify({'msg': 'Something went wrong while deleting the gateway. Please try again later, or contact a technician for further assistance'}), 500)
                    
                status = response_payload['status']

                # If the gateway was deleted successfully, send a message to the discord channel
                if status == 200:
                    return make_response(jsonify({'msg': msg}), 200)
                else:
                    return make_response(jsonify({'msg': msg}), 500)
            else:
                return make_response(jsonify({'msg': 'Gateway type not supported. Only Twitch and Discord is currently available for support.'}), 400)

            # return make_response(jsonify({'msg': msg}), 200)
        except Exception as e:
            return make_response(jsonify({'msg': str(e)}), 500)
            