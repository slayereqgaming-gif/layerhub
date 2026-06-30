import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Nazwa pliku tekstowego, który będzie trzymał konta na dysku
DB_FILE = "users.txt"

def load_users():
    """Wczytuje wszystkich użytkowników z pliku tekstowego."""
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
    """Dopisuje nowego użytkownika na koniec pliku tekstowego."""
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nickname}:{password}\n")

# Naprawione ścieżki: teraz telefon wejdzie bez błędu 404
@app.route('/')
@app.route('/index')
def home():
    error_msg = request.args.get('error')
    return render_template('index.html', error=error_msg)

@app.route('/register', methods=['POST'])
def register():
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    
    if nickname and password:
        nickname = nickname.strip().replace(":", "")
        uzytkownicy = load_users()
        
        if nickname in uzytkownicy:
            return redirect(url_for('home', error="This nickname is already taken!"))
            
        save_user(nickname, password)
        return redirect(url_for('community', user=nickname))
        
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    
    uzytkownicy = load_users()
    
    if nickname in uzytkownicy and uzytkownicy[nickname] == password:
        return redirect(url_for('community', user=nickname))
    else:
        return redirect(url_for('home', error="Invalid nickname or password!"))

@app.route('/community')
def community():
    nazwa_uzytkownika = request.args.get('user', 'Gość')
    return render_template('community.html', user=nazwa_uzytkownika)

if __name__ == '__main__':
    app.run(debug=True)
