from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# 1. INSTÂNCIA DA APLICAÇÃO
# O Flask precisa saber onde encontrar seus arquivos (templates, estáticos). 
# O __name__ ajuda o Flask a se localizar no sistema de arquivos.
app = Flask(__name__)  

# --- GARANTIA DA PASTA INSTANCE ---
# Verifica se a pasta 'instance' existe. Se não existir, ele cria automaticamente.
# Isso evita erros ao tentar criar o arquivo .db em um local inexistente.
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

# 2. CONFIGURAÇÃO DO BANCO DE DADOS
# Aqui dizemos ao Flask onde o banco vai morar. 
# 'sqlite:///site.db' cria um arquivo local chamado site.db na pasta instance do projeto.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# 3. INICIALIZAÇÃO DO BANCO
# Criamos o objeto 'db' que é a ponte de comunicação entre seu código Python e o SQL.
db = SQLAlchemy(app)


# 4. DEFINIÇÃO DO MODELO (A TABELA)
# Cada classe que herda de db.Model vira uma tabela no banco de dados.
class Tasks(db.Model):
    # id: Chave primária. É o RG da tarefa, garantindo que cada uma seja única.
    id = db.Column(db.Integer, primary_key=True)
    
    # description: O texto da tarefa. 
    # unique=True: Não permite duas tarefas com o mesmo nome.
    # nullable=False: Obriga o preenchimento (não pode salvar tarefa vazia no banco).
    description = db.Column(db.String(100), unique=True, nullable=False)
    

# --- CRUD: OPERAÇÕES DO BANCO ---

# C de Create (Criar)
@app.route('/create', methods=["POST"])
def create_task():
    # request.form: Pega o que o usuário digitou no campo <input name="description"> do HTML.
    # .strip(): Remove espaços inúteis no início e fim (evita criar tarefas só com espaços).
    description = request.form.get('description', '').strip()

    # Validação simples: Se estiver vazio, apenas volta para a página inicial.
    if not description:
        return redirect('/')

    # Verifica se já existe uma tarefa idêntica no banco para evitar erro de Unique.
    existing_task = Tasks.query.filter_by(description=description).first()
    if existing_task:
        return 'Erro: Tarefa ja existe!', 400

    # Cria o objeto da tarefa e salva no banco (Add + Commit).
    new_task = Tasks(description=description)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

# R de Read (Ler/Exibir)
@app.route('/')
def index():
    # Tasks.query.all(): Busca TODAS as linhas da tabela Tasks no banco de dados.
    tasks = Tasks.query.all()
    
    # render_template: Envia a lista vinda do banco real para o navegador.
    return render_template('index.html', tasks=tasks)

# U de Update (Atualizar)
@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    # Busca no banco a tarefa específica pelo ID enviado pela URL.
    task = Tasks.query.get(task_id)

    if task:
        # Atualiza o texto da tarefa com o novo valor digitado no input de edição.
        task.description = request.form['description']
        db.session.commit() # Salva a alteração
    return redirect('/')

# D de Delete (Apagar)
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    # Busca a tarefa no banco pelo ID.
    task = Tasks.query.get(task_id)

    if task:
        # Comando para remover o registro e confirmar a exclusão.
        db.session.delete(task)
        db.session.commit()
    return redirect('/')


# 6. EXECUÇÃO DO SERVIDOR
# Garante que o servidor só rode se você executar este arquivo diretamente.
if __name__ == '__main__':
    # Contexto de aplicação: Necessário para o SQLAlchemy interagir com o app fora das rotas.
    with app.app_context():
        # db.create_all(): Cria o arquivo site.db e as tabelas se eles ainda não existirem.
        db.create_all()
    
    # debug=True: Reinicia o servidor sozinho sempre que você salvar uma alteração.
    # port=5153: Define uma porta específica.
    app.run(debug=True, port=5153)