import socket, pickle, json, threading
from dbconnect import client
import yaml
import ssl, traceback

with open("config.yaml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

HOST = cfg['socket']['ip']
PORT = cfg['socket']['port']

db = client[cfg['mongodb']['db']]
col = db[cfg['mongodb']['collection']]

ssl_version = ssl.PROTOCOL_SSLv23
certfile = "ssl/ca.cert"
keyfile = "ssl/canew.key"
ciphers = None
option_test_switch = 1 # to test, change to 1

if option_test_switch == 1:
    print("ver=", ssl_version, "ciphers=",ciphers, "certfile=", certfile, \
            "keyfile=", keyfile, "HOST=", HOST, "PORT=", PORT)


def ssl_wrap_socket(sock, ssl_version=None, keyfile=None, certfile=None, ciphers=None):

    # create a new SSL context with specified TLS version
    sslContext = ssl.SSLContext(ssl_version)
    if option_test_switch == 1:
        print("ssl_version loaded!! =", ssl_version)
    else:
            # if not specified, default
        sslContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    if ciphers is not None:
        # if specified, set certain ciphersuite
        sslContext.set_ciphers(ciphers)
        if option_test_switch == 1:
            print("ciphers loaded!! =", ciphers)

    # server-side must load certfile and keyfile, so no if-else

    sslContext.load_cert_chain(certfile, keyfile)
    print("ssl loaded!! certfile=", certfile, "keyfile=", keyfile)

    try:
        return sslContext.wrap_socket(sock, server_side=True)

    except ssl.SSLError as e:
        print
        "wrap socket failed!"
        print
        traceback.format_exc()


print("Creating socket...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket succesfully created")
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Trying to bind...")
s.bind((HOST, PORT))
print("Succesfully bound to, ", (HOST, PORT))
s.listen(1)
print("Listening for connection...")

while True:
    conn, addr = s.accept()
    print('Connected by', addr)
    connectionSocket = ssl_wrap_socket(conn, ssl_version, keyfile, certfile, ciphers)

    if not connectionSocket:
        continue

    data = connectionSocket.recv(8192)
    if not data: break
    data_variable = pickle.loads(data)
    conn.close()
   # print(data_variable)

    newjson = json.dumps(data_variable)
    # Access the information by doing data_variable.process_id or data_variable.task_id etc..,
    #print(newjson)

    print('Data received from client and inserted in db')
    db = client[cfg['mongodb']['db']]
    col = db[cfg['mongodb']['collection']]
    col.insert(data_variable)



