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
            try:
                client_message = conn.recv(NetworkConfigs.MAX_PACKET_LENGTH_BYTES)
            except:
                # Client Force Closed
                print(f"[FORCE DISCONNECTED] {addr}")
                self.__deregister_client(addr)
                return

            # Client Sent a Message
            if client_message:
                client_message = client_message.decode(NetworkConfigs.ENCODING_FORMAT)
                client_message = (client_message.split("}")[0] + "}").encode(NetworkConfigs.ENCODING_FORMAT)

                try:
                    client_message_parcel : PartialMailParcel = PartialMailParcel.from_dict(json.loads(client_message))
                except:
                    print(f"[DROPPING PACKET] {client_message_parcel}")

                if NetworkConfigs.DISCONNECT == client_message_parcel.ID:
                    print(f"[DISCONNECTED] {addr}")
                    connected = False
                    break
                elif NetworkConfigs.ACTIVE_CLIENTS == client_message_parcel.ID:
                    self.send_to_client(NetworkConfigs.ACTIVE_CLIENTS, self.address, client_address, str(self.__get_active_clients()))
                else:
                    cmp = client_message_parcel
                    self.send_to_client(cmp.ID, cmp.from_address, cmp.to_address, cmp.message)
                    
                print(f"[{client_address}] {client_message}")

                # Send all of the mail for the client
                box = self.__get_mailbox(client_address)

                current_parcel = box.get_next_parcel()
                while current_parcel:
                     # Add padding to parcel
                    partial_parcel_str = str(current_parcel)
                    remaining_bytes = NetworkConfigs.MAX_PACKET_LENGTH_BYTES - len(partial_parcel_str)
                    padded_partial_parcel = partial_parcel_str + ('0' * remaining_bytes)
                    conn.send(padded_partial_parcel.encode(NetworkConfigs.ENCODING_FORMAT))
                    current_parcel = box.get_next_parcel()
        
        self.__deregister_client(client_address)
        conn.close()

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
        partial_parcels = parcel.slice()

        # Add all of the generated partial parcels to target mailbox
        for partial_parcel in partial_parcels:
            box.add_parcel(partial_parcel)

        return