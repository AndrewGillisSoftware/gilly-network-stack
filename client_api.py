from network_classes import *

class ClientTransport:
    def __init__(self):
        self.mail_box = []
        self.connected = False
        self.server_address = None
        self.client_address = socket.gethostbyname(socket.gethostname())
        self.client = None
        return
    
    def connect(self, server_address):
        self.server_address = server_address
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_address, PORT))
        self.connected = True
        return

    # If IP is server the message is for the server
    def send_parcel(self, purpose, to_address, string_message) -> PartialMailParcel:
        # Create Parcel
        parcel = PartialMailParcel(purpose, self.client_address, to_address, string_message)
        send_proto(self.client, parcel)
        return
    
    def get_next_parcel(self) -> PartialMailParcel:
        # Create Parcel
        parcel = PartialMailParcel(NEXT_PARCEL, self.client_address, self.server_address, "")
        send_proto(self.client, parcel)

        return PartialMailParcel.from_dict(json.loads(recv_proto(self.client)))

    def disconnect(self):
        self.send_parcel(self.server_address, DISCONNECT_MESSAGE)
        self.connect = False
        return