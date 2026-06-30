```python
import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "layerhub_klucz_bezpieczenstwa_2026_xyz"
DB_FILE = "users.txt"

def load_users():
    users = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and ":" in line:
                    nickname, password = line.split(":", 1)
                    users[nickname] = password
    return users

def save_user(nickname, password):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nickname}:{password}\n")

@app.route('/')
@app.route('/index')
def home():
    error_msg = request.args.get('error')
    zalogowany_jako = session.get('user')
    return render_template('index.html', error=error_msg, current_user=zalogowany_jako)

@app.route('/register', methods=['POST'])
def register():
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    
    if nickname and password:
        nickname = nickname.strip().replace(":", "")
        uzytkownicy = load_users()
        
        if nickname in uzytkownicy:
            return redirect(url_for('home', error="Ta nazwa użytkownika jest już zajęta!"))
            
        save_user(nickname, password)
        session['user'] = nickname  # Automatyczne logowanie po rejestracji
        return redirect(url_for('home')) # Przekierowanie z powrotem na stronę z projektami
        
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    uzytkownicy = load_users()
    
    if nickname in uzytkownicy and uzytkownicy[nickname] == password:
        session['user'] = nickname
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home', error="Błędny login lub hasło!"))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
