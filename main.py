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
    
    def atividade_existente(self, login, senha):
        cursor = conexao.cursor()
        cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            senha_hash = hashlib.sha3_256(senha.encode('utf-8')).hexdigest()
            return senha_hash == resultado[0]
        return False
    
    def turma_existente(self, codigo, descricao):
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT turmas FROM turmas WHERE id_turma = %s", (codigo,))
            resultado = cursor.fetchone()
            cursor.close()

            if resultado:
                return descricao == resultado[0]
            return False
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

    
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
        
    def adicionar_turma(self, codigo, descricao):
        #trecho hash
        cursor = conexao.cursor()
        
        cursor.execute("INSERT INTO turmas (id_turma, descricao) VALUES (%s, %s)", (codigo, descricao))
        conexao.commit()
        cursor.close()
    
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

    def carrega_turmas_professor(self, login):
        #carregtando turmas do professor
        cursor = conexao.cursor()
        cursor.execute('SELECT id_professor, nome FROM dados_login WHERE login = %s', (login,))
        resultado = cursor.fetchone()
        cursor.close()

        id_professor = resultado[0]

        #obter turmas do professor
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT turmas.id_turma, turmas.descricaoFROM turmas_professor"
            "INNER JOIN  turmas ON turmas_professor.id_turma = turmas.id_turma WHERE turmas_professor.id_professor = %s",
            (id_professor,))
        
        turmas = cursor.fetchone()
        cursor.close()

        #construindo dinamicamente as linhas da tabela turmas do professor
        linhas_tabela = ""
        for turma in turmas:
            id_turma = turma[0]
            descricao_turma = turma[1]
            link_Atividade = "<a href= 'atividade_turma?id{}'><i class='fas fa-pencil-alt'></i></a>".format(id_turma)
            linha = "<tr><td style='text-align:center'>{}</td><td style='text-align:center'>{}</td></tr>".format(id_turma,descricao_turma,link_Atividade)
            linhas_tavela += linha

        cursor = conexao.cursor()
        cursor.execute("SELECT id_turma, descricao FROM turmas")
        turmas = cursor.fetchall()
        cursor.close()

        opcoes_caixa_selecao = ""
        for turma in turmas:
            opcoes_caixa_selecao += "<option value='{}'>{}</option>".format(turma[0], turma[1])

        with open(os.path.join(os.getcwd(), 'Turma_Professor.html'), 'r', encoding='utf-8') as cad_turma_file:
            content = cad_turma_file.read()

            content = content.replace('{nome_professor}', resultado[1])
            content = content.replace('{id_professor}', str(id_professor))
            content = content.replace('{login}', str(login))

            content = content.replace('<!-- Opções da caixa de seleção serão inseridas aqui -->', opcoes_caixa_selecao)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")

        self.wfile.write(content.encode('utf-8'))

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
                #aqui
                self.wfile.write(mensagem.encode('utf-8'))
                #self.carrega_turmas_professor(login)
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

            if self.turma_existente(codigo, descricao):
                self.send_response(200)
                self.send_header()
                self.send_header('Content-type', 'text/html ; charset=utf-8')
                self.end_headers()
                mensagem = f'Turma cadastrada com sucesso!'
                self.wfile(mensagem.encode('utf-8'))

            else:
                cursor = conexao.cursor()
                cursor.execute("SELECT id_turma FROM turmas WHERE id_turma = %s", (codigo,))
                resultado = cursor.fetchone()

                if resultado:
                    self.send_response(302)
                    self.send_header('Location', '/login/failed')
                    self.end_headers()
                    cursor.close()
                    return
                else:
                    self.send_response(302)
                    self.send_header('Location', f'/cad_turma?codigo={codigo}&descricao={descricao}') #parei aqui
                    self.end_headers()
                    cursor.close()
                    return

        elif self.path == '/cad_atividade':
            #criar uma pagina ou msg pra ser mostrada
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            codigo = form_data.get('codigo', [''])[0]
            descricao = form_data.get('descricao', [''])[0]


            self.send_response(302)
            self.send_header('Content-type', 'text/html ; charset=utf-8')
            self.end_headers()

            # with open('dados_atividades.txt', 'a', encoding='utf-8') as file:
            #     file.write(f'{codigo};{descricao}\n')

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
