import pigpio
import time
import struct

from nrf24 import *

pi = pigpio.pi("127.0.0.1", 8888)

if not pi.connected:
	print("Couldn't connect to Raspberry Pi daemon, exiting...")
	exit()

USB_ADDR = b'\xAA\x44\x33\x22\x11'
LASER_ADDR = b'\x00\x00\x00\x00\x00'

SELF_ADDR = b'\x99\x88\x77\x66\x55'

nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=52, data_rate=RF24_DATA_RATE.RATE_2MBPS, pa_level=RF24_PA.MAX)

nrf.set_address_bytes(len(LASER_ADDR))
nrf.set_retransmission(15, 15)

nrf.open_reading_pipe(RF24_RX_ADDR.P2,SELF_ADDR)

nrf.reset_packages_lost()

nrf._nrf_write_reg(NRF24.DYNPD, 0x3F)
nrf._nrf_write_reg(NRF24.FEATURE, 0x4)

nrf.show_registers()

while True:
	if nrf.data_ready():
		print("Data ready!")
		nrf.show_registers()
		print(str(nrf.get_payload()))
