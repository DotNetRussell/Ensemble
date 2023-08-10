#!/usr/bin/python3

import ensemble_logging

from cryptography.fernet import Fernet

_key = None
_FERNET = None

def initialize(app_config):

	KEY_EXISTS =  "EncryptionKey" in app_config 
	ensemble_logging.log_message(f"Encryption key exists {KEY_EXISTS}")
	if(bool(KEY_EXISTS) == False):
		ensemble_logging.log_message("Generating new encryption key")
		key = Fernet.generate_key()
		decodedKey = key.decode('utf-8')
		app_config["EncryptionKey"] = decodedKey		
	else:
		ensemble_logging.log_message("Loading encryption key from config")
		key = app_config["EncryptionKey"]

	set_encryption_key(key)
	return app_config

def set_encryption_key(key):
	global _key
	global _FERNET

	_key = key
	_FERNET = Fernet(key)

def encrypt_string(payload):
	return _FERNET.encrypt(bytes(payload.encode('utf-8')))

def decrypt_string(payload):
	return _FERNET.decrypt(payload).decode('utf-8')

def get_agent_connection_string(hostIp, port):

	ensemble_logging.log_message("Building connection string for agent")
	decodedKey = _key
	agent_connection_string = f'"HOST":"{hostIp}","PORT":"{port}","ENCRYPTION_KEY":"{decodedKey}"'
	agent_connection_string = "{"+agent_connection_string.strip()+"}"

	#print("AGENT CONNECTION STRING ~~~ DO NOT SHARE")
	#print(f"'{agent_connection_string}'")
	return agent_connection_string

