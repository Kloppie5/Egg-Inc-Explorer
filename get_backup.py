import base64
import json
import os
import requests
import struct
import time

def get_backup ( ) :
    data = bytearray()

    ei_user_id = "EI6338173869490176"
    data += struct.pack(f"!BB{len(ei_user_id)}s", ( 4 << 3 ) | 2, len(ei_user_id), ei_user_id.encode())
    
    bot_name = "EggIncExplorer"
    data += struct.pack(f"!BB{len(bot_name)}s", ( 5 << 3 ) | 2, len(bot_name), bot_name.encode() )

    print(f"Requesting backup for {ei_user_id}, using request data: {base64.b64encode(data)}")
    
    url = 'https://www.auxbrain.com/ei/bot_first_contact'
    headers = {
        'User-Agent': 'EggIncExplorer/1.0.0',
    }
    response = requests.post(url, headers=headers, data={'data':base64.b64encode(data)})
    if response.status_code != 200:
        print(f"Failed to get backup: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    backup = response.content
    return backup

if __name__ == "__main__":
    backup = get_backup()
    if backup is None:
        print("Failed to get backup")
        exit(1)
    print(f"Got backup: {backup}")
    print(f"Decoded backup: {base64.b64decode(backup)}")
