from gilly_network_stack.utils import *
import threading
import asyncio
import socket
import json
import time

class NetworkConfigs:
    PORT:int = 5049
    ENCODING_FORMAT:str = 'utf-8'
    MAX_PACKET_LENGTH_BYTES:int = 1028
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

        return self.box.pop(0)

class MailParcel:
    def __init__(self, ID:str = "", from_address:str = "", to_address:str = "", message:str = "", time_stamp:str=None) -> None:
        self.ID = ID
        self.from_address = from_address
        self.to_address = to_address
        self.message = message
        self.timestamp = time_stamp if time_stamp else str(time.time())
        return
    
    def slice(self) -> list[PartialMailParcel]:
        mail_parcels:list[PartialMailParcel] = []

        segment_ID:int = 0
        message_bytes = list(self.message)

        while len(message_bytes) > 0:
            current_parcel = PartialMailParcel(self.ID, segment_ID, 0, self.from_address, self.to_address, "", self.timestamp)
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
    
    def __list_mail_with_ID(self, partial_mail_parcel:PartialMailParcel, mail_parcels:list[PartialMailParcel]) -> list[PartialMailParcel]:
        mail_parcels_with_ID:list[PartialMailParcel] = []

        for mail in mail_parcels:
            if mail.ID == partial_mail_parcel.ID and mail.time_stamp == partial_mail_parcel.time_stamp:
                mail_parcels_with_ID.append(mail)

        return mail_parcels_with_ID
    
    def pull_from_mail(self, partial_mail_parcel:PartialMailParcel, mail_parcels:list[PartialMailParcel]) -> bool:
        self.ID = partial_mail_parcel.ID
        self.from_address = partial_mail_parcel.from_address
        self.to_address = partial_mail_parcel.to_address
        self.message = ""
        self.time_stamp = partial_mail_parcel.time_stamp

        relevant_mail_parcels:PartialMailParcel = self.__list_mail_with_ID(partial_mail_parcel, mail_parcels)

        if len(relevant_mail_parcels) == 0:
            return False, relevant_mail_parcels
        
        if len(relevant_mail_parcels) != relevant_mail_parcels[0].segment_count:
            return False, relevant_mail_parcels

        # Sort Segments
        relevant_mail_parcels.sort(key=lambda mail: mail.segment_ID)

        # Concatenate Messages
        for mail in relevant_mail_parcels:
            self.message += mail.message

        return True, relevant_mail_parcels
    
    def to_dict(self) -> dict:
        return {
            'ID' : self.ID,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'message': self.message,
            'time_stamp': self.time_stamp
        }
    
    def __repr__(self) -> str:
        return json.dumps(self.to_dict())
    