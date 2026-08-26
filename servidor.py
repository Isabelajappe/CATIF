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

@app.route("/inicio")
def index():
    return render_template("inicio.html")

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

    # Dados enviados pelo formulário
    login_usuario = request.form["login"]
    senha = request.form["senha"]
    tipo = request.form["tipo"]

    # Conecta ao banco
    conexao = conectar_db()
    cursor = conexao.cursor()

    # ALUNO -> entra usando EMAIL
    if tipo == "aluno":

        sql = "SELECT * FROM usuarios WHERE email = %s"
        valores = (login_usuario,)

        cursor.execute(sql, valores)

    # EMPRESA -> entra usando CNPJ
    elif tipo == "empresa":

        # Remove pontos, barra e hífen do CNPJ
        cnpj = login_usuario.replace(".", "")
        cnpj = cnpj.replace("/", "")
        cnpj = cnpj.replace("-", "")

        sql = "SELECT * FROM usuarios WHERE cnpj = %s"
        valores = (cnpj,)

        cursor.execute(sql, valores)

    # Tipo inválido
    else:

        cursor.close()
        conexao.close()

        return render_template(
            "login.html",
            erro="Selecione o tipo de usuário"
        )

    # Procura o usuário
    usuario = cursor.fetchone()

    cursor.close()
    conexao.close()


    # Usuário encontrado
    if usuario:

        # Verifica a senha
        if check_password_hash(usuario[3], senha):

            # Salva o ID do usuário
            session["usuario_id"] = usuario[0]

            # Salva o tipo do usuário
            session["tipo"] = usuario[4]


            # Se for aluno
            if session["tipo"] == "aluno":

                return redirect(
                    url_for("perfilAluno")
                )


            # Se for empresa
            if session["tipo"] == "empresa":

                return redirect(
                    url_for("Perfil_Empresa")
                )


            # Caso o tipo não seja reconhecido
            return render_template(
                "login.html",
                erro="Tipo de usuário inválido"
            )


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

    return render_template('PerfilAluno.html')

@app.route("/perfil_empresa")
def Perfil_Empresa():

    # Verifica se é uma empresa
    if session.get("tipo") != "empresa":
        return redirect(url_for("login"))

    # Pega o ID da empresa logada
    id_empresa = session.get("usuario_id")

    # Conecta ao banco
    conexao = conectar_db()
    cursor = conexao.cursor(dictionary=True)

    # Busca somente as vagas dessa empresa
    sql = """
        SELECT *
        FROM vagas
        WHERE id_empresa = %s
        ORDER BY id_vaga DESC
    """

    cursor.execute(sql, (id_empresa,))

    vagas = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        "Perfil_Empresa.html",
        vagas=vagas
    )

@app.route("/cadastrar-vaga", methods=["POST"])
def cadastrar_vaga():

    # Verifica se existe uma empresa logada
    if session.get("tipo") != "empresa":
        return redirect(url_for("login"))

    # Pega o ID da empresa logada
    id_empresa = session.get("usuario_id")

    # Pega os dados do formulário
    nome_vaga = request.form["nome_vaga"]
    curso = request.form["curso"]
    cidade = request.form["cidade"]
    descricao = request.form["descricao"]
    requisitos = request.form["requisitos"]

    # Conecta ao banco
    conexao = conectar_db()
    cursor = conexao.cursor()

    # Salva a vaga
    sql = """
        INSERT INTO vagas
        (id_empresa, nome_vaga, curso, cidade, descricao, requisitos)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    valores = (
        id_empresa,
        nome_vaga,
        curso,
        cidade,
        descricao,
        requisitos
    )

    cursor.execute(sql, valores)

    conexao.commit()

    cursor.close()
    conexao.close()

    # Volta para o perfil da empresa
    return redirect(url_for("Perfil_Empresa"))

if __name__ == "__main__":
    app.run(debug=True)
