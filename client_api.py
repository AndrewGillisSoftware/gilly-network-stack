from network_classes import *

class ClientTransport:
    def __init__(self):
        self._partial_mail_box = []
        self.mail_box = []

        self.connected = False
        self.server_address = None
        self.client_address = socket.gethostbyname(socket.gethostname())
        self.client = None
        self.server_active_clients = []
        return
    
    def connect(self, server_address):
        self.server_address = server_address
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_address, NetworkConfigs.PORT))
        self.connected = True
        return
    
    def request_active_clients(self):
        self.send_parcel(NetworkConfigs.ACTIVE_CLIENTS, self.server_address, "")

    def disconnect(self):
        self.send_parcel(NetworkConfigs.DISCONNECT, self.server_address, "")
        self.connect = False
        return
    
    # If IP is server the message is for the server
    def send_parcel(self, ID, to_address, string_message) -> PartialMailParcel:
        # Create Parcel
        parcel = MailParcel(ID, self.client_address, to_address, string_message)

        # If parcel is large split it up into multiple
        partial_parcels = parcel.slice()

        # Send all segments of the parcel
        for partial_parcel in partial_parcels:
            self.client.send(partial_parcel)

        return
    
    def __save_server_active_clients_if_present(self, mail):
        if mail.ID == NetworkConfigs.ACTIVE_CLIENTS:
            mail_response = mail.message
            self.server_active_clients.clear()
            self.server_active_clients.extend(eval(mail_response))
            self.mail_box.remove(mail)
    
    def listen(self):
        partial_parcel = self.client.recv(NetworkConfigs.MAX_PACKET_LENGTH_BYTES).decode(NetworkConfigs.ENCODING_FORMAT)
        partial_parcel = PartialMailParcel.from_dict(json.loads(partial_parcel))

        # Add to the partial mailbox
        self._partial_mail_box.append(partial_parcel)

        # Find full parcels, combine them and remove from the partial box and move to full box
        for partial_parcel in self._partial_mail_box:
            possible_parcel = MailParcel()
            full_parcel, relevant_mail_parcels = possible_parcel.pull_from_mail(partial_parcel, self._partial_mail_box)

            if full_parcel:
                # Remove mail parcels that are partials of the full parcel
                self._partial_mail_box = [x for x in self._partial_mail_box if (x not in relevant_mail_parcels)]
                # Add Full Parcel
                self.mail_box.append(possible_parcel)
        
        # Check if it was a server message
        for mail in self.mail_box:
            self.__save_server_active_clients_if_present(mail)

        return
    
    def next_parcel(self):
        if len(self.mail_box) == 0:
            return None

        return self.mail_box.pop(0)
    