# Compfest Definitely Safe Safe Program Writeup

### Source Code

Pada challenge kali ini diberikan kode sebagai berikut

```python
"""
Welcome to my first Python program!!!

This program will be able to execute most Python
statements just like the REPL, but I have made sure
to sanitize the input so you won't be able to hack
my computer!!!

But... if you somehow managed to hack my computer
here is a gift from me COMPFEST16{PART1_
"""

__file__ = "Nothing here..."

def safe(s):
    blacklist = ["os", "system", "\\", "(", ")", "io", "subprocess", "Popen", "=", "0", "1", "2", "+", "3", "4", "5", "PART2}","6", "7", "8", "9", "import", "-", "globals", "locals", "vars"]
    return not any(c in s for c in blacklist)


if __name__ == "__main__":
    while True:
        cmd = ascii(input(">>> "))
        print(cmd)
        if not safe(cmd):
            print("Not Allowed!!!")
            continue
            
        result = eval(eval(cmd))
        print(str(result)[:25])


```
Pada comment section dijelaskan bahwa program ini mirip seperti `REPL` python,  mungkin kita bisa melakukan beberapa command yang bisa membuat kita untuk mendapatkan flag. 

walaupun kode ini di desain seperti `REPL` python, banyak kata kata yang di blacklist seperti `os`, `(`, `)`, `import`, `subprocess`, dan masih banyak lagi, hampir terbilang tidak mungkin untuk melakukan `RCE` pada program ini.

namun kita bisa memanfaatkan python dunder dan code object untuk mendapatkan flag, berikut merupakan article yang menarik seputar dunder dan code object:

https://www.codeguage.com/courses/python/functions-code-objects

https://stackoverflow.com/questions/7791574/how-can-i-print-a-python-files-docstring-when-executing-it

### Flag Part 1

Untuk membaca flag part 1 terbilang cukup simpel, dengan menggunakan command `__doc__` kita bisa membaca isi dari comment section, atau isi dari docs pada document, namun program hanya menampilkan 25 karakter saja, ini menjadi tantangan untuk kita.

kita bisa melakukan command seperti `__doc__[281:]` untuk melakukan print comment  dari karakter ke 281 sampai akhir, ini akan memberikan kita flag part 1, namun masalahnya kita tidak bisa menginputkan angka karena semua angka ada di dalam blacklist.

untuk menulis angka pada `__doc__[<angka>:]` kita bisa memanfaatkan fungsi dunder code objects yang melakukan return angka, berikut merupakan contohnya:

```python
>>> safe.__code__.co_argcount
1
>>> safe.__code__.co_firstlineno
15
>>> safe.__code__.co_stacksize
4
>>> safe.__code__.co_flags
3
```
kita tahu bahwa flag berada pada karakter ke 281 jadi, kita bisa memanfaatkan return angka diatas untuk menulis angka 281 pada `__doc__` untuk mendapatkan flag part 1 berikut contohnya:
```python
>>> safe.__code__.co_stacksize*safe.__code__.co_flags
12
>>> __doc__[safe.__code__.co_firstlineno**safe.__code__.co_flags//result:]
COMPFEST16{fake_flag_:v
```

kode diatas akan melakukan print doc dimulai dari karakter ke 281 sampai akhir ini akan memberikan kita flag part 1.

### Flag part 2
Untuk mendapatkan flag part 2 kita harus melihat isi dari list blacklist, dan flag berada pada array ke 17, untuk melihat flag kita bisa memanfaatkan python code objects untuk mendapatkan flag, berikut contohnya:

```python
# untuk mendapatkan flag kita harus melakukan command safe.__code__.co_varnames[1][17]
# kita bisa memanfaatkan kode objek yang mereturn angka untuk mendapatkan flag
>>> safe.__code__.co_consts[safe.__code__.co_argcount][safe.__code__.co_stacksize*safe.__code__.co_stacksize]
th1s_1s_f4k3_fl4gg783s9dD
```












