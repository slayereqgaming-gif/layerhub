import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Stały, bezpieczny klucz sesji
app.secret_key = "layerhub_klucz_bezpieczenstwa_2026_xyz"

DB_FILE = "users.txt"
PROJECTS_FILE = "projects.jsonl"
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"stl"}
PROVISION_RATE = 0.20  # 20% prowizji serwisu od każdej transakcji

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def load_users():
    """Bezpieczne wczytywanie użytkowników z automatycznym tworzeniem pliku."""
    users = {}
    if not os.path.exists(DB_FILE):
        # Jeśli plik nie istnieje, tworzymy go pustego, żeby uniknąć błędów
        with open(DB_FILE, "w", encoding="utf-8") as f:
            pass
        return users

    with open(DB_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and ":" in line:
                nickname, password = line.split(":", 1)
                users[nickname] = password
    return users


def save_user(nickname, password):
    """Zapis nowego użytkownika na końcu pliku."""
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nickname}:{password}\n")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_projects():
    """Wczytuje wszystkie projekty community z pliku JSONL (najnowsze pierwsze)."""
    projects = []
    if not os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            pass
        return projects

    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    projects.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    projects.reverse()  # najnowsze na górze
    return projects


def save_project(project):
    """Dopisuje jeden projekt (jako linia JSON) do pliku."""
    with open(PROJECTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(project, ensure_ascii=False) + "\n")


@app.route('/')
@app.route('/index')
def home():
    error_msg = request.args.get('error')
    zalogowany_jako = session.get('user')
    projects = load_projects()
    return render_template(
        'index.html',
        error=error_msg,
        current_user=zalogowany_jako,
        projects=projects,
        provision_percent=int(PROVISION_RATE * 100)
    )


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
        return redirect(url_for('home'))

    return redirect(url_for('home', error="Wprowadź poprawne dane rejestracji!"))


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


@app.route('/add_project', methods=['POST'])
def add_project():
    # Tylko zalogowani użytkownicy mogą dodawać projekty
    current_user = session.get('user')
    if not current_user:
        return redirect(url_for('home', error="Musisz się zalogować, aby dodać projekt!"))

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    price_raw = request.form.get('price', '').strip()
    model_file = request.files.get('model_file')

    if not title or not description or not price_raw:
        return redirect(url_for('home', error="Uzupełnij wszystkie pola formularza projektu!"))

    try:
        price = round(float(price_raw), 2)
        if price < 0:
            raise ValueError
    except ValueError:
        return redirect(url_for('home', error="Podaj poprawną cenę projektu!"))

    if not model_file or model_file.filename == '':
        return redirect(url_for('home', error="Wybierz plik .stl do wgrania!"))

    if not allowed_file(model_file.filename):
        return redirect(url_for('home', error="Dozwolone są tylko pliki z rozszerzeniem .stl!"))

    # Unikalna nazwa pliku na dysku, żeby uniknąć nadpisywania cudzych plików
    original_filename = secure_filename(model_file.filename)
    stored_filename = f"{uuid.uuid4().hex}_{original_filename}"
    model_file.save(os.path.join(UPLOAD_FOLDER, stored_filename))

    project = {
        "id": uuid.uuid4().hex,
        "title": title,
        "description": description,
        "price": price,
        "author": current_user,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
    }
    save_project(project)

    return redirect(url_for('home') + '#projekty')


if __name__ == '__main__':
    app.run(debug=True)
