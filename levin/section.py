from time import time
import random
from io import BytesIO
from collections import OrderedDict

from levin.constants import *
from levin.ctypes import *


class Section:
    def __init__(self):
        self.entries = OrderedDict()

    def add(self, key: str, entry: object):
        self.entries[key] = entry

    def __len__(self):
        return len(self.entries.keys())

    @classmethod
    def from_byte_array(cls, buffer: BytesIO):
        from levin.reader import LevinReader
        x = LevinReader(buffer)
        section = x.read_payload()
        return section

    @classmethod
    def handshake_request(cls, my_port: int = 0, network_id: bytes = None, peer_id: bytes = None):
        if not network_id:
            network_id = bytes.fromhex("1ffffff111111ffffff11111a")  # mainnet
        if not peer_id:
            peer_id = random.getrandbits(64)

        section = cls()
        node_data = Section()
        # node_data.add("local_time", c_uint64(0x4141414141414141))
        node_data.add("local_time", c_uint64(int(time())))
        node_data.add("my_port", c_uint32(my_port))
        node_data.add("network_id", c_string(network_id))
        node_data.add("peer_id", c_uint64(peer_id))
        section.add("node_data", node_data)

        payload_data = Section()
        payload_data.add("cumulative_difficulty", c_uint64(1))
        payload_data.add("current_height", c_uint64(1))
        genesis_hash = bytes.fromhex("60077b4d5cd49a1278d448c58b6854993d127fcaedbdeab82acff7f7fd86e328")  # genesis
        payload_data.add("top_id", c_string(genesis_hash))
        payload_data.add("top_version", c_ubyte(1))
        section.add("payload_data", payload_data)
        return section

    @classmethod
    def create_flags_response(cls):
        section = cls()
        section.add("support_flags", P2P_SUPPORT_FLAGS)
        return section

    def __bytes__(self):
        from levin.writer import LevinWriter

        writer = LevinWriter()
        buffer = writer.write_payload(self)
        buffer.seek(0)
        return buffer.read()
