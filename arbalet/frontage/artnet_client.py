import socket
import struct
import sys

from time import sleep
from numpy import array
from artnet import dmx


__all__ = ['ArtnetClient']


def print_flush(s):
    print(s)
    sys.stdout.flush()


class ArtnetClient(object):
    def __init__(self, row=4, col=19, port=33460):
        self.width = col
        self.height = row
        self.closed = False

         # row, column -> (DMX universe, DMX address)
        self.mapping = array([[[ 7, 18],
                                [ 7, 21],
                                [ 7, 24],
                                [ 7, 27],
                                [ 7, 30],
                                [ 7, 33],
                                [ 7, 36],
                                [ 7, 39],
                                [ 6, 51],
                                [ 6, 48],
                                [ 6, 45],
                                [ 6, 42],
                                [ 6, 39],
                                [ 6, 36],
                                [ 6, 33],
                                [ 6, 30],
                                [ 6, 27],
                                [ 6, 24],
                                [ 6, 21]],
                               [[ 5, 18],
                                [ 5, 21],
                                [ 5, 24],
                                [ 5, 27],
                                [ 5, 30],
                                [ 5, 33],
                                [ 5, 36],
                                [ 5, 39],
                                [ 4, 51],
                                [ 4, 48],
                                [ 4, 45],
                                [ 4, 42],
                                [ 4, 39],
                                [ 4, 36],
                                [ 4, 33],
                                [ 4, 30],
                                [ 4, 27],
                                [ 4, 24],
                                [ 4, 21]],
                               [[ 2, 18],
                                [ 2, 21],
                                [ 2, 24],
                                [ 2, 27],
                                [ 2, 30],
                                [ 2, 33],
                                [ 2, 36],
                                [ 2, 39],
                                [ 2, 42],
                                [ 3, 48],
                                [ 3, 45],
                                [ 3, 42],
                                [ 3, 39],
                                [ 3, 36],
                                [ 3, 33],
                                [ 3, 30],
                                [ 3, 27],
                                [ 3, 24],
                                [ 3, 21]],
                               [[ 0, 18],
                                [ 0, 21],
                                [ 0, 24],
                                [ 0, 27],
                                [ 0, 30],
                                [ 0, 33],
                                [ 0, 36],
                                [ 0, 39],
                                [ 0, 42],
                                [ 1, 48],
                                [ 1, 45],
                                [ 1, 42],
                                [ 1, 39],
                                [ 1, 36],
                                [ 1, 33],
                                [ 1, 30],
                                [ 1, 27],
                                [ 1, 24],
                                [ 1, 21]]])
        
        self.num_pixels = row*col
        self.num_universes = 8
        self.dmx = None
        self.data = [[0]*512]*self.num_universes  # self.data[universe][dmx_address] = dmx_value 

        while not self.start_socket(port):
            print('Next connection try in 3 sec')
            sleep(3)

    def start_dmx(self):
        if self.dmx is None:
            # Broadcasting on all Arnet nodes network 2.0.0.0/8
            self.dmx = dmx.Controller("2.255.255.255", universes=self.num_universes)
            self.dmx.start()

    def stop_dmx(self):
        if self.dmx is not None:
            self.dmx.close_socket()
            self.dmx = None

    def start_socket(self, port):
        print('->Start Connecting...')
        print('Port: ' + str(port))
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(("127.0.0.1", port))
            self.client.settimeout(0.05)
        except socket.error as e:
            print(str(e))
            return False
        print('->Connected')
        return True

    def update(self, raw):
        if not self.closed and self.dmx is not None:
            i = 0
            for row in range(self.height):
                for col in range(self.width):
                    universe, address = self.mapping[row, col]
                    r, g, b = raw[i], raw[i+1], raw[i+2]
                    self.data[universe][address] = r
                    self.data[universe][address+1] = g
                    self.data[universe][address+2] = b
                    #if row==0 and col==0: print(universe, address, r, g, b)
                i += 3

            for universe in range(len(self.data)):
                self.dmx.add(iter([self.data[universe]]), universe)

    def run(self):
        self.start_dmx()
        while not self.closed:
            try:
                resp = self.client.recv(self.width*self.height*3)
            except socket.timeout:
                pass
            else:
                if resp != "":
                    # print_flush(resp)
                    # print_flush("*****")
                    raw = struct.unpack("!{}B".format(self.width*self.height*3), resp)
                    self.update(raw)
        self.close_dmx()

    def close_socket(self):
        self.closed = True


if __name__ == '__main__':
    artnet = ArtnetClient()
    artnet.run()

