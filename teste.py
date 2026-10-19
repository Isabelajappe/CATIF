import mysql.connector

# Conexão
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="catif"
)

# Criar cursor
cursor = conexao.cursor()

n=1
while(n!=0):
    n = int(input("opção:1-Selecionar\n2-Inserir"))
    if(n==1):# --- SELECT ---
        cursor.execute("SELECT * FROM aluno")
        resultado = cursor.fetchall()

        print(resultado)
       

    elif(n==2):
        nome=input("Digite o nome:")
        email=input("digite a email:")
        senha=input("Digite a senha:")
        curso=input("Digite a curso:")
        semestre=input("Digite a semestre:")

        sql = "INSERT INTO aluno (nome, email, senha, curso, semestre) VALUES (%s, %s, %s, %s, %s)"
        valores = (nome, email, senha, curso, semestre)
        
        cursor.execute(sql, valores)
        conexao.commit()
        
        print("Aluno inserido!")



# Fechar cursor e conexão
cursor.close()
conexao.close()