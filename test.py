import socket
def connection():
    ServerIP = '122.51.26.166'
    ServerPort = 14290
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ServerSocket.connect(('122.51.26.166', 14290))
    ServerSocket.send(b'are you ok')

if __name__ == "__main__":
    connection()