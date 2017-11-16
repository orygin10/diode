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

def sha256_data_checksum(raw_data):
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

    def sec_send_packet(self, packet_data):
        self.send_packet(packet_data)
        self.send_packet(sha256_data_checksum(packet_data))
        time.sleep(0.00001)

    def send_file(self, file_name):
        file = File(file_name)
        data = file.read(self.buf)
        while (data):
            print "sending ..."
            self.sec_send_packet(data)
            data = file.read(self.buf)

    def __del__(self):
        self.s.close()

def main():
    file_name = sys.argv[2]
    host = sys.argv[1]

    con = Connection(host)

    con.send_packet(file_name)
    con.send_file(file_name)
    con.send_packet('EOF')

    con.send_packet(sha256_file_checksum(file_name))

if __name__=='__main__':
    main()