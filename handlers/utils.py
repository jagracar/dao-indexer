
def hex_to_utf8(hex_string):
    return bytes.fromhex(hex_string).decode("utf-8", errors="replace")

def first_key(dictionary):
    return list(dictionary.keys())[0]

def first_value(dictionary):
    return list(dictionary.values())[0]