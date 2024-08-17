from flask import Flask, render_template, request
import re

class LexerException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class Token:
    EPSILON = 0
    UNIT = 1
    NUMBER = 2
    FUNCTION = 3
    DELIMITER = 4
    VALUE = 5
    STRING = 6

    def __init__(self, token, lexeme, pos):
        self.token = token
        self.lexeme = lexeme
        self.pos = pos

    def clone(self):
        return Token(self.token, self.lexeme, self.pos)

class TokenInfo:
    def __init__(self, regex, token):
        self.regex = regex
        self.token = token

class Tokenizer:
    def __init__(self):
        self.tokenInfos = []
        self.tokens = []

    def add(self, regex, token):
        self.tokenInfos.append(TokenInfo(re.compile(f"^{regex}"), token))

    def remove_comments(self, string):
        # Elimina todas las líneas que comiencen con #
        return re.sub(r"(?m)^\s*#.*\n?", "", string)

    def tokenize(self, string):
        # Primero eliminar los comentarios
        s = self.remove_comments(string).strip()
        totalLength = len(s)
        self.tokens.clear()
        while s != "":
            remaining = len(s)
            match = False
            for info in self.tokenInfos:
                m = info.regex.match(s)
                if m:
                    match = True
                    tok = m.group().strip()
                    s = s[m.end():].strip()
                    self.tokens.append(Token(info.token, tok, totalLength - remaining))
                    break
            if not match:
                raise LexerException(f"Unexpected character in input: {s}")

    def get_tokens(self):
        return self.tokens

# Flask app setup
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    file_content = ""
    tokens = []
    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            if file and file.filename.endswith(".txt"):
                file_content = file.read().decode("utf-8")
        elif "manual_text" in request.form:
            file_content = request.form["manual_text"]

        if file_content:

            tokenizer = Tokenizer()
            tokenizer.add("rutina|datos_personales|peso|altura|edad|actividad_semanal|objetivo|dieta", Token.FUNCTION)  
            tokenizer.add("años|kg|cm", Token.UNIT) 
            tokenizer.add(r"\{|\}", Token.DELIMITER)  
            tokenizer.add("definir|perder grasa|volumen|sedentario|activo|atleta", Token.VALUE)  
            tokenizer.add(r"[0-9]+", Token.NUMBER)  
            tokenizer.add(r'"[^"]*"|\'[^\']*\'', Token.STRING) 

            try:
                tokenizer.tokenize(file_content)
                tokens = tokenizer.get_tokens()
            except LexerException as e:
                return str(e), 400

    return render_template("index.html", file_content=file_content, tokens=tokens)

if __name__ == "__main__":
    app.run(debug=True)
