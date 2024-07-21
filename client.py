from client_api import *

ct = ClientTransport()

def listen_to_server(ct):
    while True:
        time.sleep(0.5)
        if ct.connected:
            ct.listen()

def handle_client_to_client(ct):
    parcel = ct.next_parcel

    if parcel:
        print(parcel)

def start_client():
    # Start Checking for mail
    listen_to_server_thread = threading.Thread(target=listen_to_server, args=(ct,))
    listen_to_server_thread.start()

    while True:
        pass

print("[STARTING CLIENT]")
ct.connect("127.0.0.1")
start_client()