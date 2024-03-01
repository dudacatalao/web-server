#importa o modulo http server
from urllib.parse import parse_qs, urlparse
import os
from http.server import SimpleHTTPRequestHandler
import socketserver
import hashlib
from database import conectar

conexao = conectar()



class MyHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            f = open(os.path.join(path, 'pwbe.html'), 'r')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f.read().encode('utf-8'))
            f.close()
            return None
        except FileNotFoundError:
            pass

        return super().list_directory(path)

    def do_GET(self):
        if self.path == '/login':
            try:
                with open(os.path.join(os.getcwd(), 'login.html'), 'r', encoding='utf-8') as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, 'File Not Found')


        elif self.path == '/login_failed':
            self.send_response(200)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'login.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()

            mensagem = 'Login e/ou senha incorreos. Tente novamente'
            content = content.replace('<!--Erro-->',
                                      f'<div class="error-message"> {mensagem} </div>')
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/cadastro'):
            query_params = parse_qs(urlparse(self.path).query)
            login = query_params.get('login', [''])[0]
            senha = query_params.get('senha', [''])[0]

            welcome_message = f'Olá {login}, seja bem-vindo! Percebemos que é novo por aqui'

            self.send_response(200)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastro.html'), 'r' , encoding='utf-8') as cadastro_file:
                content = cadastro_file.read()

                content = content.replace('{login}', login)
                content = content.replace('{senha}', senha)
                content = content.replace('{welcome_message}', welcome_message)

                self.wfile.write(content.encode('utf-8'))

                return
            
        elif self.path == '/turmas':
            query_params = parse_qs(urlparse(self.path).query)
            descricao = query_params.get('descricao', [''])[0]
            codigo = query_params.get('codigo', [''])[0]

            self.send_response(200)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastro_turmas.html'), 'r' , encoding='utf-8') as file:
                content = file.read()
                content = content.replace('{descricao}', descricao)
                content = content.replace('{codigo}', codigo)

                self.wfile.write(content.encode('utf-8'))
                return
            
        elif self.path == '/atividade':
            query_params = parse_qs(urlparse(self.path).query)
            descricao = query_params.get('descricao', [''])[0]
            codigo = query_params.get('codigo', [''])[0]

            self.send_response(200)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cad_atividades.html'), 'r' , encoding='utf-8') as file:
                content = file.read()
                content = content.replace('{descricao}', descricao)
                content = content.replace('{codigo}', codigo)

                self.wfile.write(content.encode('utf-8'))
                return

        elif self.path == '/atividades_prof':
            query_params = parse_qs(urlparse(self.path).query)
            professor = query_params.get('professor', [''])[0]
            codigo = query_params.get('codigo', [''])[0]

            with open(os.path.join(os.getcwd(), 'atividades_professor.html'), 'r' , encoding='utf-8') as file:
                content = file.read()

                # nomes = self.obter_nomes()  
                # nomes_html = '<ul>'
                # for nome in nomes:
                #     nomes_html += f'<li>{nome}</li>'
                # nomes_html += '</ul>'
                # content = content.replace('<!--NOMES-->', nomes_html)

                content = content.replace('{professor}', professor)  
                content = content.replace('{codigo}', codigo)

            self.send_response(200)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

            return

        else:
            #se não achar a rota "/login", continua o comportamento padrão
            super().do_GET()

    def usuario_existente(self, login, senha):
        cursor = conexao.cursor()
        cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            senha_hash = hashlib.sha3_256(senha.encode('utf-8')).hexdigest()
            return senha_hash == resultado[0]
        return False
    
    # def turma_existente(self, codigo, descricao):
    #     cursor = conexao.cursor()
    #     cursor.execute("SELECT descricao FROM dados_login WHERE login = %s", (codigo,))
    #     resultado = cursor.fetchone()
    #     cursor.close()

    #     if resultado:
    #         senha_hash = hashlib.sha3_256(senha.encode('utf-8')).hexdigest()
    #         return senha_hash == resultado[0]
    #     return False
    
        # with open('dados_login.txt', 'r',encoding='utf-8') as file:
        #     for line in file:
        #         if line.strip():
        #             stored_login, stored_senha_hash, stored_nome = line.strip().split(';')
        #             if login == stored_login:
        #                 print('Login informado localizado')
        #                 print('senha: ' + senha)

        #                 #trecho hash
        #                 senha_hash = hashlib.sha3_256(senha.encode('utf-8')).hexdigest()
        #                 return senha_hash == stored_senha_hash
        # return False
    
    def adicionar_usuario(self, login, senha, nome):
        #trecho hash
        cursor = conexao.cursor()

        senha_hash = hashlib.sha3_256(senha.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO dados_login (login, senha, nome) VALUES (%s, %s, %s)", (login, senha_hash, nome))
        conexao.commit()
        cursor.close()
        # senha_hash = hashlib.sha3_256(senha.encode('utf-8')).hexdigest()

        # with open('dados_login.txt', 'w', encoding='utf-8') as file:
        #     file.write(f'{login};{senha_hash};{nome}\n')
    
    def remover_ultima_linha(self, arquivo):
            print('Excluindo a ultima linha..')

            with open(arquivo, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            with open(arquivo, 'w', encoding='utf-8') as file:
                file.writelines(lines[:-1])

    def obter_nomes(self): #ainda não utilizado
        nomes = [] 
        with open('dados_login.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                partes = line.split(';')
                if len(partes) >= 3:  
                    conteudo = partes[2].strip() 
                    nomes.append(conteudo)

        with open(os.path.join(os.getcwd(), 'atividades_professor.html'), 'r', encoding='utf-8') as login_file:
            content = login_file.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

            nomes_html = '<ul>'
            for nome in nomes:
                nomes_html += f'<li>{nome}</li>'
            nomes_html += '</ul>'

            content = content.replace('<!--NOMES-->', nomes_html)

            


    def do_POST(self):
        #verifica se a rota é enviar login
        if self.path == '/enviar_login':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body)

            print('Email:', form_data.get('email', [''])[0])
            print('Senha:', form_data.get('senha', [''])[0])

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]
            

            if self.usuario_existente(login, senha):
                self.send_response(200)
                self.send_header('Content-type', 'text/html ; charset=utf-8')
                self.end_headers()
                mensagem = f'Usuário {login} logado com sucesso!'
                self.wfile.write(mensagem.encode('utf-8'))
            else:
                cursor = conexao.cursor()
                cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
                resultado = cursor.fetchone()

                if resultado:
                    self.send_response(302)
                    self.send_header('Location', '/login/failed')
                    self.end_headers()
                    cursor.close()
                    return
                else:
                    self.send_response(302)
                    self.send_header('Location', f'/cadastro?login={login}&senha={senha}')
                    self.end_headers()
                    cursor.close()
                    return
                
                # if any(line.startswith(f"{login};") for line in open('dados_login.txt', 'r', encoding='utf-8')):
                #     self.send_response(302)
                #     self.send_header('Location', '/login_failed')
                #     self.end_headers()
                #     return  
                # else:
                #     self.adicionar_usuario(login, senha, nome='None')

                    
                #     self.send_response(302)
                #     self.send_header('Location', f'/cadastro?login={login}&senha{senha}')
                #     self.end_headers()

                #     return      
                
        elif self.path.startswith('/confirmar_cadastro'):

            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]
            nome = form_data.get('nome', [''])[0]

            self.adicionar_usuario(login, senha, nome)

            with open(os.path.join(os.getcwd(), 'msg_sucesso.html'), 'rb') as file:
                    content = file.read().decode('utf-8')

            content = content.replace('{login}', login)
            content = content.replace('{nome}', nome)

            self.send_response(200)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

            # senha_hash = hashlib.sha3_256(senha.encode('utf-8')).hexdigest()
            # print('nome:' + nome)
            # if self.usuario_existente(login, senha):
            #     with open('dados_login.txt', 'r', encoding='utf-8') as file:
            #         lines = file.readlines()

            #     with open('dados_login.txt', 'a', encoding='utf-8') as file:
            #         for line in lines:
            #             stored_login, stored_senha, stored_nome = line.strip().split(';')
            #             if login == stored_login and senha_hash == stored_senha:
            #                 line = f"{login};{senha_hash};{nome}\n"

            #             file.write(line)

            #     self.send_response(302)
            #     self.send_header('Content-type', 'text/html ; charset=utf-8')
            #     self.end_headers()
            #     self.wfile.write('Registro recebido com sucesso!'.encode('utf-8'))

            # else:
            #     self.remover_ultima_linha('dados_login.txt')
            #     self.send_response(302)
            #     self.send_header('Content-type', 'text/html; charset=utf-8')
            #     self.end_headers()
            #     self.wfile.write('A senha não confere. Retome o procedimento!'.encode('utf-8'))

        elif self.path == '/cad_turma':
            #criar uma pagina ou msg pra ser mostrada
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            codigo = form_data.get('codigo', [''])[0]
            descricao = form_data.get('descricao', [''])[0]

            with open('dados_turma.txt', 'a', encoding='utf-8') as file:
                file.write(f'{codigo};{descricao}\n')

            self.send_response(302)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()
            

        elif self.path == '/cad_atividade':
            #criar uma pagina ou msg pra ser mostrada
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            codigo = form_data.get('codigo', [''])[0]
            descricao = form_data.get('descricao', [''])[0]

            with open('dados_atividades.txt', 'a', encoding='utf-8') as file:
                file.write(f'{codigo};{descricao}\n')

            self.send_response(302)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()

        elif self.path == '/confirmar_associacao':
            #criar uma pagina ou msg pra ser mostrada
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            professor = form_data.get('professor', [''])[0]
            codigo = form_data.get('codigo', [''])[0]
            
            with open('turma_atividade.txt', 'w', encoding='utf-8') as file:
                file.write(f'{professor};{codigo}\n')

            self.send_response(302)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()
            self.wfile.write('Turma associada com sucesso!'.encode('utf-8'))
        else:
            super(MyHandler, self).do_POST()


#define a porta e e ip utilizados
endereco_ip = "0.0.0.0"
porta = 8000

# #configura o manipulador handler para o servidor
# handler = http.server.SimpleHTTPRequestHandler

#cria um servidor na porta especificada
with socketserver.TCPServer((endereco_ip, porta), MyHandler) as httpd:
    print(f'Servidor iniciado em {endereco_ip} , {porta}')
    #mantem o servidor na execução
    httpd.serve_forever()
