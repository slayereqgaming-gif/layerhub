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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    nickname = request.form.get('nickname')
    password = request.form.get('password')
    
    if nickname and password:
        # Usuwamy spacje i dwukropki z nicku dla bezpieczeństwa zapisu w pliku
        nickname = nickname.strip().replace(":", "")
        
        # Sprawdzamy, czy login nie jest już zajęty
        uzytkownicy = load_users()
        if nickname in uzytkownicy:
            # Jeśli zajęty, wracamy na stronę główną (możesz dodać komunikat o błędzie)
            return redirect(url_for('home'))
            
        # Zapisujemy konto na stałe w pliku users.txt
        save_user(nickname, password)
        
        # Przekierowujemy użytkownika prosto do strefy Community
        return redirect(url_for('community', user=nickname))
        
    return redirect(url_for('home'))

@app.route('/community')
def community():
    # Pobieramy nick z adresu URL, żeby spersonalizować powitanie
    nazwa_uzytkownika = request.args.get('user', 'Gość')
    return render_template('community.html', user=nazwa_uzytkownika)

if __name__ == '__main__':
    app.run(debug=True)
