# --- receiver.py ---

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
        self.fp = open(file_name, 'wb')

    def write(self, data):
        self.fp.write(data)

    def __del__(self):
        self.fp.close()

class Connection():
    def __init__(self):
        self.s = socket(AF_INET, SOCK_DGRAM)
        host = "0.0.0.0"
        port = 9999
        self.buf = 1024
        self.addr = (host, port)

        self.s.bind(self.addr)

    def receive_packet(self):
        data,addr = self.s.recvfrom(self.buf)
        return data

    def __del__(self):
        self.s.close()

def receive_filename(con):
    file_name = con.receive_packet()
    print "Receiving %s" % file_name
    file_name = file_name.split('/')[-1] # Avoid /boot/initramfs to be rewritten for exe
    return file_name

def print_files_checksums(con, file_name):
    original_sha = con.receive_packet()
    print "Original SHA-256: %s" % original_sha
    received_sha = sha256_file_checksum(file_name)
    print "Received SHA-256: %s" % received_sha

def receive_file(con, file_name):
    f = File(file_name)

    data = con.receive_packet()
    while not data=='EOF':
        checksum = con.receive_packet()
        if checksum == sha256(data):
            f.write(data)
            sys.stdout.write('Checksum OK. Write data to file.\n')
        elif len(checksum) == 1024:
            sys.stdout.write('Checksum not received. ')
            f.write(data)
            f.write(checksum)
            sys.stdout.write('Write data and recovered data to file.\n')
        elif len(checksum) == 64:
            raise SystemExit('Checksums do not match')
        else:
            raise SystemExit('Checksum is neither 64 nor 1024 bytes')
        data = con.receive_packet()

    sys.stdout.flush()

def main():
    con = Connection()

    file_name = receive_filename(con)

    top = time.time()
    receive_file(con, file_name)
    print 'File received in %ds' % (time.time() - top)

    print_files_checksums(con, file_name)

if __name__=='__main__':
    main()