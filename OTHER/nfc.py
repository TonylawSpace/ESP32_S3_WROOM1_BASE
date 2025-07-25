# ref https://github.com/marshmll/nfc-esp32-micropython/blob/main/nfc.py
# MFRC522

from machine import Pin, SoftSPI

class NFC:
    """
    A class to interface with the MFRC522 NFC reader.

    This class provides methods to interact with NFC tags using the MFRC522 module.
    It supports reading and writing data to Mifare Classic tags, as well as basic
    tag detection and authentication.

    Attributes:
        OK (int): Operation successful.
        NOTAGERR (int): No tag detected.
        ERR (int): General error.
        COLLERR (int): Collision error.
        SLCTERR (int): Tag selection error.
        AUTHERR (int): Authentication error.
        WRITERR (int): Write error.
        REQIDL (int): Request idle command.
        REQALL (int): Request all command.
        AUTHENT1A (int): Authentication type A.
        AUTHENT1B (int): Authentication type B.
        MIFARE_KEY (list): Default Mifare key (6 bytes).
    """

    OK       = 0
    NOTAGERR = 1
    ERR      = 2
    COLLERR  = 3
    SLCTERR  = 4
    AUTHERR  = 5
    WRITERR  = 6

    REQIDL    = 0x26
    REQALL    = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    MIFARE_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]  # Mifare standard key

    def __init__(self, sda_pin, sck_pin, mosi_pin, miso_pin, baudrate=100000):
        """
        Initialize the NFC reader.

        Args:
            sda_pin (int): Pin number for SDA (chip select).
            sck_pin (int): Pin number for SCK (clock).
            mosi_pin (int): Pin number for MOSI (master out, slave in).
            miso_pin (int): Pin number for MISO (master in, slave out).
            baudrate (int): SPI baud rate (default: 100000).
        """
        self.sck = Pin(sck_pin, Pin.OUT)
        self.mosi = Pin(mosi_pin, Pin.OUT)
        self.miso = Pin(miso_pin, Pin.OUT)
        self.spi = SoftSPI(baudrate=baudrate, polarity=0, phase=0, sck=self.sck, mosi=self.mosi, miso=self.miso)
        self.sda = Pin(sda_pin, Pin.OUT)
        self.sda.value(1)
        self.spi.init()
        self.init()

    def _write_register(self, reg, value):
        """
        Write a value to a register.

        Args:
            reg (int): Register address.
            value (int): Value to write.
        """
        self.sda.value(0)
        self.spi.write(bytes([(reg << 1) & 0x7E]))
        self.spi.write(bytes([value & 0xFF]))
        self.sda.value(1)

    def _read_register(self, reg):
        """
        Read a value from a register.

        Args:
            reg (int): Register address.

        Returns:
            int: Value read from the register.
        """
        self.sda.value(0)
        self.spi.write(bytes([((reg << 1) & 0x7E) | 0x80]))
        value = self.spi.read(1)
        self.sda.value(1)
        return value[0]

    def _set_register_flags(self, reg, mask):
        """
        Set specific bits in a register.

        Args:
            reg (int): Register address.
            mask (int): Bitmask to set.
        """
        self._write_register(reg, self._read_register(reg) | mask)

    def _clear_register_flags(self, reg, mask):
        """
        Clear specific bits in a register.

        Args:
            reg (int): Register address.
            mask (int): Bitmask to clear.
        """
        self._write_register(reg, self._read_register(reg) & (~mask))

    def _communicate_with_card(self, command, data):
        """
        Communicate with the NFC card.

        Args:
            command (int): Command to send.
            data (list): Data to send.

        Returns:
            tuple: (status, received_data, bits)
        """
        recv = []
        bits = irq_en = wait_irq = 0
        status = self.ERR

        if command == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        elif command == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30

        self._write_register(0x02, irq_en | 0x80)
        self._clear_register_flags(0x04, 0x80)
        self._set_register_flags(0x0A, 0x80)
        self._write_register(0x01, 0x00)

        for byte in data:
            self._write_register(0x09, byte)
        self._write_register(0x01, command)

        if command == 0x0C:
            self._set_register_flags(0x0D, 0x80)

        timeout = 2000
        while timeout > 0:
            n = self._read_register(0x04)
            timeout -= 1
            if not ((timeout != 0) and not (n & 0x01) and not (n & wait_irq)):
                break

        self._clear_register_flags(0x0D, 0x80)

        if timeout:
            if (self._read_register(0x06) & 0x1B) == 0x00:
                status = self.OK

                if n & irq_en & 0x01:
                    status = self.NOTAGERR
                elif command == 0x0C:
                    n = self._read_register(0x0A)
                    lbits = self._read_register(0x0C) & 0x07
                    bits = (n - 1) * 8 + lbits if lbits else n * 8

                    n = 1 if n == 0 else 16 if n > 16 else n
                    recv = [self._read_register(0x09) for _ in range(n)]
            else:
                status = self.ERR

        return status, recv, bits

    def _calculate_crc(self, data):
        """
        Calculate CRC for the given data.

        Args:
            data (list): Data to calculate CRC for.

        Returns:
            list: CRC bytes.
        """
        self._clear_register_flags(0x05, 0x04)
        self._set_register_flags(0x0A, 0x80)

        for byte in data:
            self._write_register(0x09, byte)

        self._write_register(0x01, 0x03)

        timeout = 0xFF
        while timeout > 0:
            n = self._read_register(0x05)
            timeout -= 1
            if not ((timeout != 0) and not (n & 0x04)):
                break

        return [self._read_register(0x22), self._read_register(0x21)]

    def init(self):
        """Initialize the MFRC522 module."""
        self.reset()
        self._write_register(0x2A, 0x8D)
        self._write_register(0x2B, 0x3E)
        self._write_register(0x2D, 30)
        self._write_register(0x2C, 0)
        self._write_register(0x15, 0x40)
        self._write_register(0x11, 0x3D)
        self.antenna_on()

    def reset(self):
        """Reset the MFRC522 module."""
        self._write_register(0x01, 0x0F)

    def antenna_on(self, on=True):
        """
        Turn the antenna on or off.

        Args:
            on (bool): Whether to turn the antenna on (default: True).
        """
        if on and not (self._read_register(0x14) & 0x03):
            self._set_register_flags(0x14, 0x03)
        else:
            self._clear_register_flags(0x14, 0x03)

    def request(self, mode):
        """
        Request communication with a tag.

        Args:
            mode (int): Request mode (e.g., REQIDL, REQALL).

        Returns:
            tuple: (status, bits)
        """
        self._write_register(0x0D, 0x07)
        status, recv, bits = self._communicate_with_card(0x0C, [mode])
        return (status, bits) if (status == self.OK and bits == 0x10) else (self.ERR, 0)

    def anticoll(self):
        """
        Perform anti-collision to get the tag's UID.

        Returns:
            tuple: (status, UID)
        """
        ser_chk = 0
        ser = [0x93, 0x20]

        self._write_register(0x0D, 0x00)
        status, recv, _ = self._communicate_with_card(0x0C, ser)

        if status == self.OK and len(recv) == 5:
            ser_chk = recv[0] ^ recv[1] ^ recv[2] ^ recv[3]
            if ser_chk != recv[4]:
                status = self.ERR
        else:
            status = self.ERR

        return status, recv

    def select_tag(self, uid):
        """
        Select a tag by its UID.

        Args:
            uid (list): UID of the tag.

        Returns:
            int: Status (OK or ERR).
        """
        buf = [0x93, 0x70] + uid[:5]
        buf += self._calculate_crc(buf)
        status, recv, bits = self._communicate_with_card(0x0C, buf)
        return self.OK if (status == self.OK and bits == 0x18) else self.ERR

    def authenticate(self, mode, block, key, uid):
        """
        Authenticate a tag.

        Args:
            mode (int): Authentication mode (e.g., AUTHENT1A, AUTHENT1B).
            block (int): Block to authenticate.
            key (list): Key for authentication.
            uid (list): UID of the tag.

        Returns:
            int: Status (OK or ERR).
        """
        return self._communicate_with_card(0x0E, [mode, block] + key + uid[:4])[0]

    def stop_crypto(self):
        """Stop crypto operations."""
        self._clear_register_flags(0x08, 0x08)

    def read_block(self, block):
        """
        Read data from a block.

        Args:
            block (int): Block to read.

        Returns:
            tuple: (status, tag_type, UID, data)
        """
        self.init()
        status, tag_type = self.request(self.REQIDL)
        if status != self.OK:
            return self.NOTAGERR, None, None, None

        status, uid = self.anticoll()
        if status != self.OK:
            return self.COLLERR, None, None, None

        if self.select_tag(uid) != self.OK:
            return self.SLCTERR, None, None, None

        if self.authenticate(self.AUTHENT1A, block, self.MIFARE_KEY, uid) != self.OK:
            return self.AUTHERR, None, None, None

        data = self._read_block(block)
        return self.OK, tag_type, uid, data

    def write_block(self, block, data):
        """
        Write data to a block.

        Args:
            block (int): Block to write.
            data (list): Data to write (16 bytes).

        Returns:
            tuple: (status, tag_type, UID)
        """
        self.init()
        status, tag_type = self.request(self.REQIDL)
        if status != self.OK:
            return self.NOTAGERR, None, None

        status, uid = self.anticoll()
        if status != self.OK:
            return self.COLLERR, None, None

        if self.select_tag(uid) != self.OK:
            return self.SLCTERR, None, None

        if self.authenticate(self.AUTHENT1A, block, self.MIFARE_KEY, uid) != self.OK:
            return self.AUTHERR, None, None

        status = self._write_block(block, data)
        self.stop_crypto()
        return (self.OK, tag_type, uid) if status == self.OK else (self.WRITERR, None, None)

    def is_card_present(self):
        """
        Check if a card is present.

        Returns:
            bool: True if a card is present, False otherwise.
        """
        self.init()
        status, _ = self.request(self.REQIDL)
        return status == self.OK

    def _read_block(self, block):
        """
        Read data from a block (internal method).

        Args:
            block (int): Block to read.

        Returns:
            list: Data read from the block.
        """
        data = [0x30, block]
        data += self._calculate_crc(data)
        status, recv, _ = self._communicate_with_card(0x0C, data)
        return recv if status == self.OK else None

    def _write_block(self, block, data):
        """
        Write data to a block (internal method).

        Args:
            block (int): Block to write.
            data (list): Data to write (16 bytes).

        Returns:
            int: Status (OK or ERR).
        """
        buf = [0xA0, block]
        buf += self._calculate_crc(buf)
        status, recv, bits = self._communicate_with_card(0x0C, buf)

        if status == self.OK and bits == 4 and (recv[0] & 0x0F) == 0x0A:
            buf = data[:16]
            buf += self._calculate_crc(buf)
            status, recv, bits = self._communicate_with_card(0x0C, buf)
            if status == self.OK and bits == 4 and (recv[0] & 0x0F) == 0x0A:
                return self.OK

        return self.ERR