from client_api import *

ct = ClientTransport()

def listen_to_server(ct):
    while True:
        time.sleep(0.5)
        if ct.connected:
            ct.listen()

def handle_mail(ct):
    while True:
        parcel = ct.next_parcel()

        if parcel:
            print(str(parcel))
        if len(ct.server_active_clients) > 0:
            print(ct.server_active_clients)

def start_client():
    # Start Checking for mail
    listen_to_server_thread = threading.Thread(target=listen_to_server, args=(ct,))
    listen_to_server_thread.start()

    handle_mail_thread = threading.Thread(target=handle_mail, args=(ct,))
    handle_mail_thread.start()

    while True:
        command = input("'ID' 'to_address' 'message'")
        segments = command.split(' ')
        ct.send_parcel(segments[0], segments[1], segments[2])

print("[STARTING CLIENT]")
server_ip = input("IP:")
ct.connect(server_ip)
start_client()