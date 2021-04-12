import pigpio
import time
import struct

from nrf24 import *

pi = pigpio.pi("127.0.0.1", 8888)

if not pi.connected:
	print("Couldn't connect to Raspberry Pi daemon, exiting...")
	exit()

send_address = b'RPI'

nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.MAX, channel=0x31, data_rate=RF24_DATA_RATE.RATE_2MBPS, pa_level=RF24_PA.MAX)

nrf.set_address_bytes(len(send_address))
nrf.set_retransmission(15, 15)

nrf.open_writing_pipe(send_address)

time.sleep(1)

nrf.show_registers()

payload = b'hello'
nrf.reset_packages_lost()
nrf.send(payload)

pi.stop()


input()