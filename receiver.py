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
        self.buf = 1024 + 64 + 8
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

def parse_block(block):
    data = block[:-64-8]
    checksum = block[-64-8:-8]
    number = block[-8:]
    numberd = int(number, 16)

    return data, checksum, numberd

def write_queue_to_file(queue, file):
    print 'Queue contains %s elements' % len(queue)
    if all(queue[i] <= queue[i+1] for i in xrange(len(queue)-1)):
        print 'No packets are unsorted'
    else:
        print 'Sorting queue'
        sorted(queue, key=lambda x: x[0])
    for data in [x[1] for x in queue]:
        file.write(data)

def receive_file(con, file_name):
    file = File(file_name)
    queue = list()

    block = con.receive_packet()
    while not block == 'EOF':
        data, checksum, numberd = parse_block(block)

        #print 'Block %d: %s' %(numberd,''.join([hex(ord(x))[2:] for x in data[:2]]))

        if sha256(data) == checksum:
            queue.append( (numberd, data) )
        else:
            print 'Checksums do not match'
            print 'Hoping for %s' % checksum
            print 'Got %s' % sha256(data)
            raise SystemExit()

        block = con.receive_packet()
    write_queue_to_file(queue, file)

def main():
    con = Connection()

    file_name = receive_filename(con)

    top = time.time()
    receive_file(con, file_name)
    print 'File received in %ds' % (time.time() - top)

    print_files_checksums(con, file_name)

if __name__=='__main__':
    main()