import socketserver
import threading
import codec
from typing_extensions import Literal

IMEI_RECIEVE_SIZE = 256
CODEC_RECIEVE_SIZE = 1024

class TeltonikaRequestHandler(socketserver.BaseRequestHandler):
    
    
    def handle(self) -> None:
        try:
            # Get IMEI first
            imei_data = self.request.recv(IMEI_RECIEVE_SIZE).hex()
            
            if not TeltonikaRequestHandler.is_imei(imei_data):
                return
            
            imei = TeltonikaRequestHandler.get_imei(imei_data)
            print(f"Server: IMEI {imei}")
            # If IMEI valid then sent 1 to get CODEC data
            self.send_imei_response(1)
            
            
            # Device sends codec data after imei response 
            codec_data = self.request.recv(CODEC_RECIEVE_SIZE).hex().encode()
            parsed = codec.parse_codec(codec_data)
            print(f'SERVER: parsed {parsed}')
            self.send_codec_response(number_of_data=parsed['number_of_data_1'])
            
        except Exception as e:
            print(f'Error: {e}')
    
    def is_imei(data : str):
        imei_length = int(data[:4], 16)
        if imei_length != len(data[4:]) / 2:
            return False
        return True
    
    def get_imei(data : str):
        return bytes.fromhex(data[4:]).decode()
    
    def send_imei_response(self, status = Literal[0, 1]):
        reply = (status).to_bytes(1)
        self.request.sendall(reply)
    
    def send_codec_response(self, number_of_data : int):
        self.request.sendall((number_of_data).to_bytes(4))
    
class TeltonikaTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "localhost", 0
    server = TeltonikaTCPServer((HOST, PORT), TeltonikaRequestHandler)
    with server:
        try:
            ip, port = server.server_address
            print(f'Teltonika Server Started IP: {ip}, PORT: {port}')
            server.serve_forever()
        except:
            pass
    server.shutdown()
    print("Teltonika Server shut down") 

