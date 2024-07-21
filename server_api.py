from network_classes import *
class ServerTransport:

    mail_boxes = []

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = socket.gethostbyname(socket.gethostname())
        self.server.bind((self.address, NetworkConfigs.PORT))
        return
    
    def __get_mailbox(self, address):
        # Ensure box does not already exist
        for box in self.mail_boxes:
            if box.address == address:
                return box
        return None

    def __register_client(self, address):
        # Ensure box does not already exist
        box = self.__get_mailbox(address)
        if box:
            return
        # Add client to list of active clients by creating a mailbox
        server_address = self.address
        self.mail_boxes.append(MailBox(server_address, address))
        return

    def __deregister_client(self, address):
        # Remove mail box
        box = self.__get_mailbox(address)
        if box:
            self.mail_boxes.remove(box)
        return
    
    def __get_active_clients(self):
        client_ips = []
        for box in self.mail_boxes:
            client_ips.append(box.address)
        return client_ips

    def __handle_client_proto(self, conn, addr):
        client_address = addr[0]
        print(f"[NEW CONNECTION] {addr} connected.")

        self.__register_client(client_address)
    
        connected = True
        while connected:
            # Get Client Message
            client_message = conn.recv(NetworkConfigs.MAX_PACKET_LENGTH_BYTES)

            # Client Sent a Message
            if client_message:
                client_message_parcel : MailParcel = MailParcel.from_dict(json.loads(client_message))

                if DISCONNECT_MESSAGE == client_message_parcel.purpose:
                    print(f"[DISCONNECTED] {addr}")
                    connected = False
                    break
                elif NEXT_PARCEL == client_message_parcel.purpose:
                    # Send Client its mail if requested
                    box = self.__get_mailbox(client_address)
                    next_parcel_for_client = box.get_next_parcel()
                    if next_parcel_for_client.purpose != EMPTY_PARCEL:
                        print(f"[Sending Next Parcel of Mail to {client_address}] {next_parcel_for_client}")
                    send_proto(conn, next_parcel_for_client)
                elif GET_ACTIVE_CLIENTS == client_message_parcel.purpose:
                    self.send_to_client(GET_ACTIVE_CLIENTS_RESPONSE, self.address, client_address, str(self.__get_active_clients()))
                else:
                    cmp = client_message_parcel
                    self.send_to_client(cmp.purpose, cmp.from_address, cmp.to_address, cmp.message)
                    
                print(f"[{client_address}] {client_message}")

                # Server reacts to client
                if self.handle_client != None:
                    self.handle_client(client_message)
        
        self.__deregister_client(client_address)
        conn.close()
        print(f"[CLOSED / DEREGISTERED] {addr}")

    def start(self):
        print("[STARTING] server is starting...")
        self.server.listen()

        print(f"[LISTENING] Server is listening on {self.address}")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.__handle_client_proto, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    
    def send_to_client(self, ID, from_address, to_address, msg):
        box = self.__get_mailbox(to_address)

        if not box:
            return

        # Split mail into partial parcels if needed
        parcel = MailParcel(ID, from_address, to_address, msg)
        partial_parcels = parcel.split()

        # Add all of the generated partial parcels to target mailbox
        for partial_parcel in partial_parcels:
            box.add_parcel(partial_parcel)

        return