#import json
import socket
import msgspec

# Convenience functions for sending data to a Plotjuggler instance

class PlotJugglerUDPClient:
    def __init__(self, addr: str, port: int, block: bool = False, serialization: str = 'json'):
        self.addr = addr
        self.port = port
        self.serialization=serialization
        if serialization != 'json':
            raise ValueError("Only 'json' serialization is currently supported")

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setblocking(block)
        print(f"Plotjuggler Client Streaming to {self.addr} on port {self.port}")


    def send(self, data: dict|str):
        if isinstance(data, dict): 
            data_to_send = msgspec.json.encode(data)
        elif isinstance(data, str): 
            data_to_send = data.encode('UTF-8')
        else:
            raise TypeError("Data sent to Plotjuggler must be either of type str or dict")
        try:
            self.s.sendto(data_to_send, (self.addr, self.port))
        except BlockingIOError as e:
            pass

if __name__ == "__main__":
    import sys
    import time
    import math
    addr = sys.argv[1]
    pj_client = PlotJugglerUDPClient(addr=addr, port=5556)
    test_data = {
        'example_data': {
            'sine': math.sin(time.time()),
            'cosine': math.cos(time.time())
        },
        'timestamp': time.time()
    }
    while True:
        time.sleep(0.033)
        test_data = {
            'example_data': {
                'sine': math.sin(time.time()),
                'cosine': math.cos(time.time())
            },
            'timestamp': time.time()
        }
        pj_client.send(test_data)


