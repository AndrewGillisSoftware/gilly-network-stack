import pytest
from network_classes import *

def test_large_mail_parcel_split():
    NetworkConfigs.MAX_PACKET_LENGTH_BYTES = 15
    largeMailParcel = LargeMailParcel("Frog", "1.1.1.1", "2.2.2.2", "This frog jumps over the big blue moon")

    mail = largeMailParcel.split()
    print(mail)
    assert False

def test_large_mail_parcel_pull_from_mail():
    assert False