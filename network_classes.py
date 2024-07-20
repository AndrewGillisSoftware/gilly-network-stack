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

class MailParcel:
    def __init__(self, id:str, segment_id:int, segment_count:int, from_address:str, to_address:str, message:str, time_stamp=None):
        self.id = id
        self.segment_id = segment_id
        self.segment_count = segment_count
        self.time_stamp = time_stamp if time_stamp else str(time.time())
        self.from_address = from_address
        self.to_address = to_address
        self.message = message
        return
    
    def to_dict(self) -> dict:
        return {
            'id' : self.id,
            'segment_id': self.segment_id,
            'segment_count': self.segment_count,
            'time_stamp': self.time_stamp,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'message': self.message
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
        self.box:MailParcel = []
        return

    def add_parcel(self, parcel:MailParcel):
        self.box.append(parcel)
        return

    def get_next_parcel(self) -> MailParcel:
        if len(self.box) == 0:
            return None

        return self.box.pop()

class LargeMailParcel:
    def __init__(self, id:str, from_address:str = "", to_address:str = "", message:str = "") -> None:
        self.id = id
        self.from_address = from_address
        self.to_address = to_address
        self.message = message
        return
    
    def split(self) -> list[MailParcel]:
        mail_parcels:list[MailParcel] = []

        segment_id:int = 0
        message_bytes = list(self.message)

        while len(message_bytes) > 0:
            current_parcel = MailParcel(id, segment_id, 0, self.from_address, self.to_address, "") 
            parcel_header_len:int = len(str(current_parcel).encode(NetworkConfigs.ENCODING_FORMAT))

            parcel_bytes_remaining:int = NetworkConfigs.MAX_PACKET_LENGTH_BYTES - parcel_header_len

            while parcel_bytes_remaining:
                current_parcel.message += message_bytes.pop(0)

            mail_parcels.append(current_parcel)
            segment_id += 1
        
        for parcel in mail_parcels:
            parcel.segment_count = len(mail_parcels)
        
        return mail_parcels
    
    def __list_mail_with_id(self, mail_parcels:list[MailParcel]) -> list[MailParcel]:
        mail_parcels_with_id:list[MailParcel] = []

        for mail in mail_parcels:
            if mail.id == self.id:
                mail_parcels_with_id.append(mail)

        return mail_parcels_with_id
    
    def pull_from_mail(self, mail_parcels:list[MailParcel]) -> bool:
        relevant_mail_parcels:MailParcel = self.__list_mail_with_id(self, mail_parcels)

        if len(relevant_mail_parcels) == 0:
            return False
        
        if len(relevant_mail_parcels) != relevant_mail_parcels[0].segment_count:
            return False

        # Sort Segments
        relevant_mail_parcels.sort(key=lambda mail: mail.segment)


