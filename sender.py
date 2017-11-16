# --- sender.py ---

#!/usr/bin/env python

from socket import *
import sys
import hashlib
import time

def sha256_file_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def sha256(raw_data):
    sha256 = hashlib.sha256()
    sha256.update(raw_data)
    return sha256.hexdigest()

class File():
    def __init__(self, file_name):
        self.fp = open(file_name, 'rb')

    def read(self, buffer):
        return self.fp.read(buffer)

    def __del__(self):
        self.fp.close()

class Connection():
    def __init__(self, _host):
        self.s = socket(AF_INET, SOCK_DGRAM)
        host = _host
        port = 9999
        self.buf = 1024
        self.addr = (host, port)

    def send_packet(self, packet_data):
        self.s.sendto(packet_data, self.addr)
        time.sleep(1.0/100000.0)

    def __del__(self):
        self.s.close()

def send_file(con, file_name):
    file = File(file_name)

    print 'Sending...'
    block = file.read(con.buf)
    while (block):
        data = block + sha256(block)
        con.send_packet(data)
        block = file.read(con.buf)

def main():
    file_name = sys.argv[2]
    host = sys.argv[1]

    con = Connection(host)

    con.send_packet(file_name)
    send_file(con, file_name)
    con.send_packet('EOF')

    con.send_packet(sha256_file_checksum(file_name))

if __name__=='__main__':
    main()