#!/usr/bin/env python3
import os
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flag', methods=['GET', 'POST'])
def ping():
    if request.method == 'POST':
        host = request.form.get('host')
        cmd = f'{host}'
        if not cmd:
             return render_template('ping_result.html', data='Hello')
        try:
            output = os.system(f'ping -c 4 {cmd}')
            return render_template('ping_result.html', data="DeadSecCTF2024")
        except subprocess.CalledProcessError:
            return render_template('ping_result.html', data=f'error when executing command')
        except subprocess.TimeoutExpired:
            return render_template('ping_result.html', data='Command timed out')

    return render_template('ping.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
