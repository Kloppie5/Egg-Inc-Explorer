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
    # 2: name
    # 3: timestamp
    # 4: Settings
    # 5: Tutorial
    # 6: Stats
    # 7: Game
    #   1: progress
    #   2: golden eggs earned
    #   3: golden eggs spent
    #   5: 0?
    #   6: very large number
    #   7: piggybank
    #   8: 1?
    #   9: EpicResearch[]
    #   10: timestamp?
    #   11: News[]
    #   12: timestamp?
    #   13: 64?
    #   14: timestamp?
    #   15: Achievement[]
    #   16: 0?
    #   18: ?[]
    #   19: trophy[]?
    #   20: ?
    #   22: 0?
    #   23: 1?
    #   24: 0?
    #   25: 1?
    #   26: ?
    #   27: ?
    #   28: daily gift progress
    #   29: 0?
    #   30: Boost[]
    #   31: 1?
    #   32: 0?
    #   33: 0?
    #   34: big number?
    #   35: 0?
    #   36: 0?
    #   37: 0?
    #   38: 27?
    #   39: 0?
    #   40: 0?
    # 9: ?
    #   3: ?[]
    # 10: ?
    #   1: 1?
    #   2: 1?
    #   3: big number?
    #   4: big number?
    #   5: meh number?
    #   6: 1?
    #   7: 1?
    #   8: meh number?
    #   9: meh number?
    #   11: 1?
    #   12: 1?
    #   13: 1?
    #   14: 1?
    #   15: 1?
    #   16: 1?
    #   17: 1?
    #   18: 1?
    #   19: 0?
    #   20: 0?
    # 12: Farm[]
    #   1: egg type
    #   2: cash earned
    #   3: cash spent
    #   4: 0?
    #   5: timestamp?
    #   6: chickens
    #   7: 0?
    #   8: 0?
    #   9: eggs laid
    #   10: eggs.... eeeh, something
    #   11: silos
    #   12: habitat[]
    #   13: habitat ?[]
    #   14: habitat 0[]?
    #   15: habitat pop[]?
    #   16: ?
    #   17: vehicle[]
    #   18: Research[]
    #   19: 2?
    #   20: name?
    #   21: 1[5]?
    #   22: Boost[]
    #   23: 0?
    #   24: 0?
    #   25: 0?
    #   26: 0?
    #   27: 0?
    #   28: 0?
    #   29: timestamp?
    #   30: eggs shipped
    #   31: 0?
    # 13: Contracts
    contracts = deserialize_protobuf(backup["13"])
    #   1: Contract[] << active
    active_contracts = [ deserialize_protobuf(contract) for contract in contracts["1"] ]
    print(f"Active contracts: {len(active_contracts)}")
    #for contract in active_contracts:
    #    print(f"{contract}")
    #     1: ?
    #       1: contract id
    #       2: egg type
    #       3: Goal[]
    #       4: 1?
    #       5: max players
    #       6: timestamp?
    #       7: meh number
    #       9: proper name
    #       10: description
    #       11: 0?
    #       12: 0?
    #       13: 0?
    #       14: 44? << same as top layer value, maybe some version check?
    #       15: ?
    #       16: Goal[] again?
    #       17: timestamp?
    #       18: ?
    #       19: 1?
    #     2: coop code
    #     3: timestamp?
    #     5: timestamp?
    #     6: timestamp?
    #     7: 1?
    #     9: timestamp?
    #     10: 0?
    #     11: timestamp?
    #     13: user id
    #     14: goals completed
    #     15: 0?
    #     17: 1?
    #   2: Contract[] << old
    #   3: name[]
    #   4: CurrentContractStatus[]
    #     1: contract id
    #     2: progress
    #     3: coop code
    #     4: Contributor[]
    #       1: base64 encoded something
    #       2: user name
    #       3: contribution double
    #       4: 1?
    #       5: 2?
    #       6: contribution rate
    #       7: 0?
    #       11: soul power
    #       12: boost tokens
    #       14: boost tokens spent
    #       15: ?
    #         1: chickens
    #         2: capacity
    #         3: ?
    #         4: ?
    #         5: ?
    #         6: ?
    #       16: 0?
    #       17: 0?
    #       18: FarmInfo?
    #         1: soul eggs
    #         2: prophecy eggs
    #         3: 1?
    #         4: 1?
    #         5: trophy[]
    #         6: EpicResearch[]
    #         7: egg type
    #         8: cash
    #         9: habitat[]
    #         10: habitat pop[]
    #         11: vehicle[]
    #         12: train length[]
    #         13: silos
    #         14: Research[]
    #         15: Boost[]
    #         16: boost tokens
    #         17: Artifact[]
    #         18: ?
    #         19: FarmAppearance[]
    #         20: version again
    #         21: habitat capacity[]
    #         22: timestamp?
    #       19: contract id
    #       20: timestamp?
    #     5: timestamp?
    #     6: 0?
    #     7: timestamp?
    #     8: 0?
    #     9: user id creator
    #     10: 0?
    #     12: timestamp?
    # 14: Rocket platform?
    #   6: timestamp?
    #   7: 1?
    #   9: 4?
    #   10: big number?
    #   11: 1?
    #   12: 1?
    #   14: 0?
    #   15: 1?
    #   16: fuel level[]
    #   17: meh number?
    # 15: ?
    #   1: ?[]
    #   2: 30?
    #   4: ?[]
    #   5: ?[]
    #   11: ?[]
    #   12: ?[]
    # 16: Game id
    # 17: Device id
    # 18: User id
    # 20: 0?
    # 21: 44 << version?
    # 22: 0?
    # 23: seasonal event string[]?
    # 24: ?
    #   3: ?[]
    #   6: seasonal store string[]?
    #   7: empty string?
    # 25: ?
    #   1: 1?
    #   2: 1?
    #   3: [0,0,0]?
    # 100: probably a checksum
