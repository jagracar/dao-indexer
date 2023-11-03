import json
from contextlib import suppress

def clean_null_bytes(string: str) -> str:
    if string is None:
        return ''
    if type(string) is dict:
        return json.dumps(string)
    else:
        return ''.join(string.split('\x00'))


def hex_to_utf8(hexbytes: str) -> str:
    string = None
    with suppress(Exception):
        try:
            string = bytes.fromhex(hexbytes).decode()
        except Exception:
            string = bytes.fromhex(hexbytes).decode('latin-1')
    return clean_null_bytes(string or '')

def hex_to_utf8_old(hex_string):
    return bytes.fromhex(hex_string).decode("utf-8", errors="replace")

def first_key(dictionary):
    return list(dictionary.keys())[0]

def first_value(dictionary):
    return list(dictionary.values())[0]