import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# KLUCZ SZYFRUJĄCY SESJĘ (Niezbędny do zapamiętania zalogowanego konta)
app.secret_key = "super_tajny_klucz_layerhub_2026!"

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

@app.route('/')
@app.route('/index')
def home():
    error_msg = request.args.get('error')
    # Sprawdzamy, czy w przeglądarce jest aktywna sesja zalogowanego użytkownika
    zalogowany_uzytkownik = session.get('user')
    return render_template('index.html', error=error_msg, current_user=zalogowany_uzytkownik)

@app.route('/register', methods=['POST'])
def register():
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    
    if nickname and password:
        nickname = nickname.strip().replace(":", "")
        uzytkownicy = load_users()
        
        if nickname in uzytkownicy:
            return redirect(url_for('home', error="Ta nazwa użytkownika jest już zajęta!"))
            
        # Zapisujemy konto do pliku users.txt
        save_user(nickname, password)
        
        # Logujemy automatycznie do sesji i przenosimy na stronę główną
        session['user'] = nickname
        return redirect(url_for('home'))
        
    return redirect(url_for('home', error="Uzupełnij wszystkie pola!"))

@app.route('/login', methods=['POST'])
def login():
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    
    uzytkownicy = load_users()
    
    if nickname in uzytkownicy and uzytkownicy[nickname] == password:
        session['user'] = nickname
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home', error="Nieprawidłowa nazwa użytkownika lub hasło!"))

@app.route('/logout')
def logout():
    """Wylogowanie użytkownika."""
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
