import asyncio
import socket
import json
import time

class NetworkConfigs:
    PORT:int = 5051
    ENCODING_FORMAT:str = 'utf-8'
    MAX_PACKET_LENGTH_BYTES:int = 0xFFFF
    ACK:str = "G_N_S_ACK"
    ACTIVE_CLIENTS:str = "G_N_S_ACTIVE_CLIENTS"
    DISCONNECT:str = "G_N_S_DISCONNECT"

class PartialMailParcel:
    def __init__(self, ID:str, segment_ID:int, segment_count:int, from_address:str, to_address:str, message:str, time_stamp:str=None):
        self.ID = ID
        self.segment_ID = segment_ID
        self.segment_count = segment_count
        self.time_stamp = time_stamp if time_stamp else str(time.time())
        self.from_address = from_address
        self.to_address = to_address
        self.message = message
        return
    
    def to_dict(self) -> dict:
        return {
            'ID' : self.ID,
            'segment_ID': self.segment_ID,
            'segment_count': self.segment_count,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'message': self.message,
            'time_stamp': self.time_stamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def __repr__(self) -> str:
        return json.dumps(self.to_dict())

class MailBox:
    def __init__(self, server_address:str, address:str):
        self.server_address = server_address
        self.address = address
        self.box:PartialMailParcel = []
        return

    def add_parcel(self, parcel:PartialMailParcel):
        self.box.append(parcel)
        return

    def get_next_parcel(self) -> PartialMailParcel:
        if len(self.box) == 0:
            return None

        return self.box.pop()

class MailParcel:
    def __init__(self, ID:str, from_address:str = "", to_address:str = "", message:str = "") -> None:
        self.ID = ID
        self.from_address = from_address
        self.to_address = to_address
        self.message = message
        return
    
    def split(self) -> list[PartialMailParcel]:
        parcel_time = str(time.time())
        mail_parcels:list[PartialMailParcel] = []

        segment_ID:int = 0
        message_bytes = list(self.message)

        while len(message_bytes) > 0:
            current_parcel = PartialMailParcel(self.ID, segment_ID, 0, self.from_address, self.to_address, "", parcel_time)
            encoded_parcel = str(current_parcel).encode(NetworkConfigs.ENCODING_FORMAT)
            parcel_header_len:int = len(encoded_parcel)

            parcel_bytes_remaining:int = NetworkConfigs.MAX_PACKET_LENGTH_BYTES - parcel_header_len

            while parcel_bytes_remaining:
                if len(message_bytes) > 0:
                    current_parcel.message += message_bytes.pop(0)
                parcel_bytes_remaining -= 1

            mail_parcels.append(current_parcel)
            segment_ID += 1
        
        for parcel in mail_parcels:
            parcel.segment_count = len(mail_parcels)
        
        return mail_parcels
    
    def __list_mail_with_ID(self, mail_parcels:list[PartialMailParcel]) -> list[PartialMailParcel]:
        mail_parcels_with_ID:list[PartialMailParcel] = []

        for mail in mail_parcels:
            if mail.ID == self.ID:
                mail_parcels_with_ID.append(mail)

        return mail_parcels_with_ID
    
    def pull_from_mail(self, mail_parcels:list[PartialMailParcel]) -> bool:
        relevant_mail_parcels:PartialMailParcel = self.__list_mail_with_ID(self, mail_parcels)

        if len(relevant_mail_parcels) == 0:
            return False
        
        if len(relevant_mail_parcels) != relevant_mail_parcels[0].segment_count:
            return False

        # Sort Segments
        relevant_mail_parcels.sort(key=lambda mail: mail.segment)


NetworkConfigs.MAX_PACKET_LENGTH_BYTES = 160
largeMailParcel = MailParcel("Frog", "1.1.1.1", "2.2.2.2", "This frog jumps over the big blue moon. 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21")

mail = largeMailParcel.split()
print(mail)