from flask import Flask, render_template, request, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for



app = Flask(__name__)
app.secret_key = "chave_secreta"

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="catif" #banco de dados, tem q mudar para o 'catif' #
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

@app.route("/vaga/<int:id>")
def vaga_detalhes(id):

    conexao = conectar_db()
    cursor = conexao.cursor(dictionary=True)

    sql = "SELECT * FROM vaga WHERE id_vaga = %s"
    cursor.execute(sql, (id,))

    vaga = cursor.fetchone()

    cursor.close()
    conexao.close()

    return render_template("detalhes_vaga.html", vaga=vaga)


@app.route("/estagio")
def estagio():
    return render_template("estagio.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    # Se apenas abriu a página
    if request.method == "GET":
        return render_template("cadastro.html")

    # Se clicou em cadastrar
    if request.method == "POST":

        email = request.form["email"]
        senha_1 = request.form["senha"]
        senha_2 = request.form["confirmar_senha"]
        tipo = request.form["tipo"]
        cnpj = request.form["cnpj"]
        cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")

        # Verifica se as senhas são iguais
        if senha_1 != senha_2:
            return render_template(
                "cadastro.html",
                erro="As senhas não coincidem"
            )

        # Criptografa a senha
        senha_hash = generate_password_hash(senha_1)

        # Conexão com o banco
        conexao = conectar_db()
        cursor = conexao.cursor()

        # Verifica se o email já existe
        sql = "SELECT * FROM usuarios WHERE email = %s"
        cursor.execute(sql, (email,))

        resultados = cursor.fetchall()

        if len(resultados) > 0:
            cursor.close()
            conexao.close()

            return render_template(
                "cadastro.html",
                erro="Email já cadastrado"
            )
        
        if tipo == "empresa" and cnpj == "":
            return render_template(
        "cadastro.html",
        erro="Empresas precisam informar o CNPJ"
    )

        # Insere o usuário
        sql = """
        INSERT INTO usuarios (email, senha, tipo, cnpj)
        VALUES (%s, %s, %s, %s)
        """

        valores = (email, senha_hash, tipo, cnpj)

        cursor.execute(sql, valores)

        # Salva no banco
        conexao.commit()

        # Fecha conexão
        cursor.close()
        conexao.close()

        return """
        <p>Cadastro realizado com sucesso!</p>

        <a href="/login">
            <button>Ir para Login</button>
        </a>
        """

@app.route("/login", methods=["GET", "POST"])
def login():

    # Apenas abriu a página
    if request.method == "GET":
        return render_template("login.html")

    # Enviou o formulário
    email = request.form["email"]
    senha = request.form["senha"]

    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="catif"
    )

    cursor = conexao.cursor()

    sql = "SELECT * FROM usuarios WHERE email = %s AND tipo = %s"
    valores = (email, tipo)
    cursor.execute(sql, valores)

    usuario = cursor.fetchone()

    cursor.close()
    conexao.close()

    if usuario:

        # usuario[3] = senha hash no banco
        if check_password_hash(usuario[3], senha):
            session['usuario_id'] = usuario[0]
            session["tipo"] = usuario[4]

            if session['tipo'] == 'aluno':
                return redirect(url_for('perfilAluno'))

            if session['tipo'] == 'empresa':
                return redirect(url_for('perfil_empresa'))

           # return redirect(url_for('home'))

            #return render_template("perfilAluno.html")

        else:
            return render_template(
                "login.html",
                erro="Senha incorreta"
            )

    else:
        return render_template(
            "login.html",
            erro="Usuário não encontrado"
        )







@app.route("/perfil_aluno")
def perfilAluno():

    if session.get('tipo') != 'aluno':
        return redirect(url_for('login'))

    return render_template('perfilAluno.html')

if __name__ == "__main__":
    app.run(debug=True)

