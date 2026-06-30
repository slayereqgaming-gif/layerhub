import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "layerhub_klucz_szyfrujacy_produkcje_2026"
DB_FILE = "users.txt"

def load_users():
    users = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    u, p = line.strip().split(":", 1)
                    users[u] = p
    return users

@app.route('/')
def home():
    return render_template('index.html', current_user=session.get('user'), error=request.args.get('error'))

@app.route('/register', methods=['POST'])
def register():
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    if nickname and password:
        with open(DB_FILE, "a", encoding="utf-8") as f:
            f.write(f"{nickname}:{password}\n")
        session['user'] = nickname
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    users = load_users()
    if request.form.get('nickname') in users and users[request.form.get('nickname')] == request.form.get('password'):
        session['user'] = request.form.get('nickname')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
