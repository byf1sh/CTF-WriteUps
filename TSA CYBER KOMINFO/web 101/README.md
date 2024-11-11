# TSA CYBER KOMINFO - Web 101 - Writeup
Pada challenge kali ini diberikan sebuah web yang terdapat fitur ping ke suatu ip dan juga fitur upload untuk melakukan upload suatu image. terdapat kerentanan file upload disini, kita bisa mengupload image dengean menyisipkan comment `php rce syntax `pada image tersebut, dan mendapatkan RCE.

upload image dengan command rce, lalu upload image, kemudian rce bisa dialkuakn seperti url berikut, 
```bash!
https://<url>/uploads/image.jpg&cmd=ls
```