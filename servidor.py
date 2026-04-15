from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="catif"
    )

@app.route("/")
def home():
    return "Flask está funcionando!"

@app.route("/teste")
def teste():
    return "Rota de teste OK!"

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/vagas")
def vagas():
    return render_template("vagas.html")

@app.route("/estagio")
def estagio():
    return render_template("estagio.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        confirmar = request.form["confirmar_senha"]

        if senha != confirmar:
            return "As senhas não são iguais!"

        conexao = conectar_db()
        cursor = conexao.cursor()

        query = "SELECT * FROM usuarios WHERE email = %s"
        cursor.execute(query, (email,))

        result = cursor.fetchone() 

        if result:
            return("O email já existe")
        
        else:

            sql = "INSERT INTO usuarios (email, senha) VALUES (%s, %s)"
            dados = (email, senha)

            cursor.execute(sql, dados)
            conexao.commit()

            cursor.close()
            conexao.close()

            return render_template("perfilAluno.html")
    
    return render_template("cadastro.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/perfilAluno")
def perfilAluno():
    return render_template("perfilAluno.html")

if __name__ == "__main__":
    app.run(debug=True)

