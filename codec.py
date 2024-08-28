import json

def crc16_valid(data : bytes) -> bool:
    # Data Field Length	
    data_part_length_crc = int(data[8:16], 16)
    # From Codec ID to Number Of Data 2 then convert it to bytes
    data_part_for_crc = bytes.fromhex(data[16 : 16 + 2 * data_part_length_crc])
    
    crc16_arc_from_record = data[16 + len(data_part_for_crc.hex()) : 24 + len(data_part_for_crc.hex())]

    crc = 0

    for byte in data_part_for_crc:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1

    if crc16_arc_from_record.upper() == crc.to_bytes(4, byteorder="big").hex().upper():
        return True
    else:
        return False

def get_codec_id(data:bytes):
    return data[16:18].decode()

class Codec8ExtendedParser:
    CODEC_ID = b'0x8E'
    def __init__(self, raw_data : bytes) -> None:
        self.data = raw_data.decode()
        self.byte_index = 0
        self.parsed = {}
        # Get Preamble
        self.dequeue_bytes(4)

        # Get Data Field Length	
        self.parsed['data_field_length'] = int(self.dequeue_bytes(4), 16)

        # Get Codec ID
        self.parsed['codec_id'] = self.dequeue_bytes(1)
        
        # If codec id not match with Codec8 Extended Codec ID, raise Exception
        if int(self.parsed['codec_id'], 16) != int(Codec8ExtendedParser.CODEC_ID, 16):
            raise Exception(f'Codec ID is not match with Codec8 Extended Codec ID (Given: {self.parsed['codec_id']})')
        
        if not crc16_valid(self.data):
            raise Exception('CRC 16 Validation Failed')
        
        # Get Number of Data 1
        self.parsed['number_of_data_1'] = int(self.dequeue_bytes(1), 16)
        self.parsed['avl_records'] = []
        for _ in range(self.parsed['number_of_data_1']):
            avl_record = {}
            avl_record['timestamp'] = float.fromhex(self.dequeue_bytes(8))
            avl_record['priority'] = int(self.dequeue_bytes(1))
            avl_record['longitude'] = float.fromhex(self.dequeue_bytes(4))
            avl_record['latitude'] = float.fromhex(self.dequeue_bytes(4))
            avl_record['altitude'] = float.fromhex(self.dequeue_bytes(2))
            avl_record['angle'] = float.fromhex(self.dequeue_bytes(2))
            avl_record['satellites'] = float.fromhex(self.dequeue_bytes(1))
            avl_record['speed'] = float.fromhex(self.dequeue_bytes(2))
            
            avl_record['event_io_id'] = self.dequeue_bytes(2)
            avl_record['number_of_total_id'] = int(self.dequeue_bytes(2), 16)
            
            avl_record['elements'] = []
            avl_record['elements'].append(self.parse_n_byte_elements(1))
            avl_record['elements'].append(self.parse_n_byte_elements(2))
            avl_record['elements'].append(self.parse_n_byte_elements(4))
            avl_record['elements'].append(self.parse_n_byte_elements(8))
            
            number_of_x_byte_elements = int(self.dequeue_bytes(2), 16)
            
            for __ in range(number_of_x_byte_elements):
                avl_record['elements'].append(self.parse_x_byte_element())
            
            self.parsed['avl_records'].append(avl_record)
        
        
        self.dequeue_bytes(1) #self.parsed['number_of_data_2'] = int(self.dequeue_bytes(1), 16)
        self.dequeue_bytes(4) # self.parsed['crc_16'] = self.dequeue_bytes(4)
        print(json.dumps(self.parsed))
        
    def dequeue_bytes(self, bytes : int):
        data = self.data[self.byte_index * 2 : self.byte_index * 2 + bytes * 2]
        self.byte_index += bytes
        return data    
    
    def parse_n_byte_elements(self, n : int):
        number_of_elements = int(self.dequeue_bytes(2), 16)
        elements = []
        for _ in range(number_of_elements):
            elements.append({
                'io_id': self.dequeue_bytes(2),
                'io_value': self.dequeue_bytes(n)
            })
        return elements
    
    def parse_x_byte_element(self):
        io_id = self.dequeue_bytes(2)
        io_length = self.dequeue_bytes(2)
        io_value = self.dequeue_bytes(io_length)
        return {'io_id': io_id, 'io_length': io_length, 'io_value': io_value}

class Codec8Parser:
    CODEC_ID = b'0x08'
    def __init__(self, raw_data : bytes) -> None:
        self.data = raw_data.decode()
        self.byte_index = 0
        self.parsed = {}
        # Get Preamble
        self.dequeue_bytes(4)

        # Get Data Field Length	
        self.parsed['data_field_length'] = int(self.dequeue_bytes(4), 16)

        # Get Codec ID
        self.parsed['codec_id'] = self.dequeue_bytes(1)
        
        # If codec id not match with Codec8 Extended Codec ID, raise Exception
        if int(self.parsed['codec_id'], 16) != int(Codec8Parser.CODEC_ID, 16):
            raise Exception(f'Codec ID is not match with Codec8 Extended Codec ID (Given: {self.parsed['codec_id']})')
        
        if not crc16_valid(self.data):
            raise Exception('CRC 16 Validation Failed')
        
        # Get Number of Data 1
        self.parsed['number_of_data_1'] = int(self.dequeue_bytes(1), 16)
        self.parsed['avl_records'] = []
        for _ in range(self.parsed['number_of_data_1']):
            avl_record = {}
            avl_record['timestamp'] = float.fromhex(self.dequeue_bytes(8))
            avl_record['priority'] = int(self.dequeue_bytes(1))
            # TODO: Lat Long negatiflik durumuna bak
            avl_record['longitude'] = float.fromhex(self.dequeue_bytes(4))
            avl_record['latitude'] = float.fromhex(self.dequeue_bytes(4))
            avl_record['altitude'] = float.fromhex(self.dequeue_bytes(2))
            avl_record['angle'] = float.fromhex(self.dequeue_bytes(2))
            avl_record['satellites'] = float.fromhex(self.dequeue_bytes(1))
            avl_record['speed'] = float.fromhex(self.dequeue_bytes(2))
            
            avl_record['event_io_id'] = self.dequeue_bytes(1)
            avl_record['number_of_total_id'] = int(self.dequeue_bytes(1), 16)
            
            avl_record['elements'] = [] 
            avl_record['elements'].append((self.parse_n_byte_elements(1)))
            avl_record['elements'].append((self.parse_n_byte_elements(2)))
            avl_record['elements'].append((self.parse_n_byte_elements(4)))
            avl_record['elements'].append((self.parse_n_byte_elements(8)))
            
            
            self.parsed['avl_records'].append(avl_record)
        
        
        self.dequeue_bytes(1) #self.parsed['number_of_data_2'] = int(self.dequeue_bytes(1), 16)
        self.dequeue_bytes(4) # self.parsed['crc_16'] = self.dequeue_bytes(4)
        print(json.dumps(self.parsed))
        
    def dequeue_bytes(self, bytes : int):
        data = self.data[self.byte_index * 2 : self.byte_index * 2 + bytes * 2]
        self.byte_index += bytes
        return data    
    
    def parse_n_byte_elements(self, n : int):
        number_of_elements = int(self.dequeue_bytes(1), 16)
        elements = []
        for i in range(number_of_elements):
            elements.append({
                'io_id': self.dequeue_bytes(1),
                'io_value': self.dequeue_bytes(n)
            })
        return elements

def parse_codec(data : bytes):
    codec_id = get_codec_id(data)
    if int(codec_id, 16) == int(Codec8ExtendedParser.CODEC_ID, 16):
        return Codec8ExtendedParser(data).parsed
    elif int(codec_id, 16) == int(Codec8Parser.CODEC_ID, 16):
        return Codec8Parser(data).parsed
    else:
        raise Exception("Codec ID is not valid")

if __name__ == '__main__':
    # Codec 8 Extended Data
    data = b'000000000000004A8E010000016B412CEE000100000000000000000000000000000000010005000100010100010011001D00010010015E2C880002000B000000003544C87A000E000000001DD7E06A00000100002994'
    # Codec 8 Data
    #data = b'000000000000011f0804000001919970d3d00015bf987e15e1316701210033120000ef0e05ef01f0001504c800450107b50008b60006426249430f97440051190bce56005002f100006fb910026024f300000001919970e7580015bf987e15e1316701210033120000ef0e05ef00f0001504c800450107b50008b60006421afe430f8244002a190bce56005002f100006fb910026024f300000001919970ef280015bf987e15e1316701210033120000ef0e05ef01f0011504c800450107b50008b600064265d4430fac44006f190bce56005002f100006fb910026024f300000001919970f3100015bf987e15e1316701210033120000f00e05ef01f0011504c800450107b50008b600064265d4430fac44006f190bce56005002f100006fb910026024f30004000095a2'
    parse_codec(data)
    