from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    # Pobieramy aktualną godzinę z systemu
    teraz = datetime.now().strftime("%H:%M:%S")

    # Przekazujemy zmienne bezpośrednio do szablonu HTML
    return render_template(
        "index.html",
        tekst_z_pythona="Ten komunikat został wygenerowany przez skrypt Pythona!",
        czas=teraz,
    )


if __name__ == "__main__":
    app.run(debug=True)
