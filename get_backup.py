import base64
import json
import os
import requests
import struct
import time

def serialize_protobuf ( obj ) :
    result = bytearray()
    for field, value in obj.items ( ) :
        if isinstance(value, str) :
            result.append(int(field) << 3 | 2)
            length = len(value)
            while length > 0x7F :
                result.append((length & 0x7F) | 0x80)
                length >>= 7
            result.append(length)
            result.extend(value.encode())
        else :
            print(f"Unknown type for key {field}: {type(value)}")
            exit(1)
    return result

def read_varint ( data, debug = False ) :
    value = 0
    shift = 0
    while True :
        byte, = struct.unpack("!B", data[0:1])
        if debug :
            print(f"Read varint: {byte:08b} | {shift}")
        value |= (byte & 0x7F) << shift
        shift += 7
        data = data[1:]
        if byte & 0x80 == 0 :
            break
    return value, data

def deserialize_protobuf ( data, debug = False ) :
    if debug:
        print(f"Total length: {len(data)}")
    result = {}
    while len(data) > 0 :
        wire_tag, data = read_varint(data, debug)
        if debug :
            print(f"Wire tag: {wire_tag:b}")
        field_tag = str(wire_tag >> 3)
        field_type = wire_tag & 0x7
        
        if field_type == 0 : # Varint
            value, data = read_varint(data, debug)
            if debug :
                print(f"{field_tag}: {value}")
        elif field_type == 1 : # i64
            value, = struct.unpack("!Q", data[0:8])
            data = data[8:]
            if debug :
                print(f"{field_tag}: {value}")
        elif field_type == 2 : # Length-delimited string
            length, data = read_varint(data, debug)
            value, = struct.unpack(f"!{length}s", data[0:length])
            data = data[length:]
            if debug :
                print(f"{field_tag} | {length} length-delimited string: {value[0:10]}...")
        else:
            print(f"Unknown field type {field_type}: {field_tag} | {data[0:10]}...")
            exit(1)
        if field_tag in result:
            if not isinstance(result[field_tag], list):
                result[field_tag] = [result[field_tag]]
            result[field_tag].append(value)
        else:
          result[field_tag] = value
    return result



def get_backup ( ) :
    data = {
        "4" : "EI6338173869490176", # EI User ID
        "5" : "EggIncExplorer" # Bot Name
    }
    
    url = 'https://www.auxbrain.com/ei/bot_first_contact'
    headers = {
        'User-Agent': 'EggIncExplorer/1.0.0',
    }
    response = requests.post(url, headers=headers, data={'data':base64.b64encode(serialize_protobuf(data))})
    if response.status_code != 200:
        print(f"Failed to get backup: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    response_object = deserialize_protobuf(base64.b64decode(response.content))
    backup = deserialize_protobuf(response_object["1"])
    return backup

if __name__ == "__main__":
    backup = get_backup()
    if backup is None:
        print("Failed to get backup")
        exit(1)

    print(f"Backup: {backup.keys()}")
