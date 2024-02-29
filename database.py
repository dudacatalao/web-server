# antes, executar
# pip install mysql-connector-python
import mysql.connector

#conecta ao servidor MySQL
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="senai"
)

#cria um cursor para executar comandos SQL
cursor = conexao.cursor()

#cria um banco de dados chamado 'teste' se ele ainda não existir
cursor.execute("CREATE DATABASE IF NOT EXISTS PWBE")

#seleciona o banco de dados 'pwbe'
cursor.execute("USE PWBE")

#cria uma tabela chamada 'tabela_1' com os campos 'id' e 'nome'
cursor.execute("CREATE TABLE IF NOT EXISTS tabela_pwbe (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255))")

#fecha o cursor e a conexão
cursor.close()
conexao.close()

print("Banco de dados e tabela criados com sucesso.")
