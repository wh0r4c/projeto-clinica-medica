from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import iniciar_bd
from db import execute_one
from db import execute_query
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'vitasaude-fatec-2026'

iniciar_bd()
# ─── Dados simulados ─────────────────────────────────────────────────────────

funcoes = [
    {'id': 1, 'nome': 'Administrador', 'descricao': 'Acesso total ao sistema', 'status': True, 'pode_gerenciar_usuarios': True, 'ativo': True},
    {'id': 2, 'nome': 'Médico', 'descricao': 'Consulta e prontuários', 'status': True, 'pode_gerenciar_usuarios': False, 'ativo': True},
    {'id': 3, 'nome': 'Recepcionista', 'descricao': 'Atendimento e agendamentos', 'status': True, 'pode_gerenciar_usuarios': False, 'ativo': True},
]

usuarios = [
    {'id': 1, 'nome': 'Dra. Ana Paula Reis', 'email': 'ana@vitasaude.com', 'funcao': 'Médico', 'status': 'Ativo', 'senha': '123', 'ativo': True},
    {'id': 2, 'nome': 'Dr. Carlos Mendonça', 'email': 'carlos@vitasaude.com', 'funcao': 'Médico', 'status': 'Ativo', 'senha': '123', 'ativo': True},
    {'id': 3, 'nome': 'Fernanda Lima', 'email': 'fernanda@vitasaude.com', 'funcao': 'Recepcionista', 'status': 'Ativo', 'senha': '123', 'ativo': True},
    {'id': 4, 'nome': 'Juliana Costa', 'email': 'juliana@vitasaude.com', 'funcao': 'Administrador', 'status': 'Ativo', 'senha': '123', 'ativo': True},
]

pacientes = [
    {'id': 1, 'nome': 'Marcos Oliveira',   'cpf': '321.654.987-00', 'nascimento': '1985-03-12', 'telefone': '(14) 99812-3456', 'convenio': 'Unimed'},
    {'id': 2, 'nome': 'Patrícia Souza',    'cpf': '456.789.123-11', 'nascimento': '1992-07-28', 'telefone': '(14) 99723-4567', 'convenio': 'SulAmérica'},
    {'id': 3, 'nome': 'Eduardo Ferreira',  'cpf': '789.123.456-22', 'nascimento': '1978-11-05', 'telefone': '(14) 99634-5678', 'convenio': 'Particular'},
]

especialidades = [
    {'id': 1, 'nome': 'Clínica Geral',      'descricao': 'Atendimento geral e preventivo.', 'medico': 'Dr. Carlos Mendonça',  'duracao': 30},
    {'id': 2, 'nome': 'Cardiologia',        'descricao': 'Doenças do coração e vasos.', 'medico': 'Dra. Ana Paula Reis',  'duracao': 45},
]

consultas = [
    {'id': 1, 'paciente': 'Marcos Oliveira',  'medico': 'Dra. Ana Paula Reis',  'especialidade': 'Cardiologia',   'data': '2026-04-02', 'hora': '08:00', 'status': 'Agendada'},
    {'id': 2, 'paciente': 'Patrícia Souza',   'medico': 'Dr. Carlos Mendonça',  'especialidade': 'Clínica Geral', 'data': '2026-04-02', 'hora': '09:30', 'status': 'Confirmada'},
]

# ─── Rotas públicas ───────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', especialidades=especialidades)

@app.route('/servicos')
def servicos():
    return render_template('servicos.html', especialidades=especialidades)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        session['usuario'] = email
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('listar_consultas'))
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        flash('Cadastro realizado! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

# ─── Rotas protegidas — Funções ──────────────────────────────────────────────

@app.route('/funcoes/listar')
def listar_funcoes():
    sql = '''
    SELECT 
        id_funcao AS id, 
        nome, 
        descricao, 
        status,
        pode_gerenciar_usuarios,
        pode_gerenciar_pacientes,
        pode_gerenciar_especialidades,
        pode_gerenciar_consultas,
        criado_em,
        alterado_em
    FROM funcoes
    ORDER BY id_funcao DESC;
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('funcoes/listar_funcoes.html', funcoes=lista_dados)

@app.route('/funcoes/inserir', methods=['GET', 'POST'])
def inserir_funcao():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        status = 'Ativo' if request.form.get('status') else 'Inativo'
        
        pode_gerenciar_usuarios = 1 if request.form.get('pode_gerenciar_usuarios') else 0
        pode_gerenciar_pacientes = 1 if request.form.get('pode_gerenciar_pacientes') else 0
        pode_gerenciar_especialidades = 1 if request.form.get('pode_gerenciar_especialidades') else 0
        pode_gerenciar_consultas = 1 if request.form.get('pode_gerenciar_consultas') else 0

        try:
            
            sql = '''
            INSERT INTO funcoes (
                nome, descricao, status, 
                pode_gerenciar_usuarios, pode_gerenciar_pacientes, 
                pode_gerenciar_especialidades, pode_gerenciar_consultas
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            '''
            
            valores = (
                nome, descricao, status, 
                pode_gerenciar_usuarios, pode_gerenciar_pacientes, 
                pode_gerenciar_especialidades, pode_gerenciar_consultas
            )
            
            execute_query(sql, valores)
            flash('Função cadastrada com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro ao salvar no banco!', 'danger')
            app.logger.error(f'Erro no INSERT: {e}')

        return redirect(url_for('listar_funcoes'))

    return render_template('funcoes/inserir_funcao.html', dados=None)

@app.route('/funcoes/editar/<int:id>', methods=['GET', 'POST'])
def editar_funcao(id):
    funcao = next((f for f in funcoes if f['id'] == id), None)
    if not funcao:
        flash('Função não encontrada!', 'danger')
        return redirect(url_for('listar_funcoes'))

    if request.method == 'POST':
        funcao['nome'] = request.form.get('nome', '').strip()
        funcao['descricao'] = request.form.get('descricao', '').strip()
        funcao['status'] = True if request.form.get('status') else False
        funcao['pode_gerenciar_usuarios'] = True if request.form.get('pode_gerenciar') else False
        flash(f'Função "{funcao["nome"]}" atualizada com sucesso!', 'warning')
        return redirect(url_for('listar_funcoes'))

    return render_template('funcoes/inserir_funcao.html', dados=funcao)

@app.route('/funcoes/esconder/<int:id>', methods=['POST'])
def esconder_funcao(id):
    funcao = next((f for f in funcoes if f['id'] == id), None)
    if funcao:
        funcao['ativo'] = False
        flash(f'Função "{funcao["nome"]}" escondida!', 'secondary')
    return redirect(url_for('listar_funcoes'))

@app.route('/funcoes/excluir/<int:id>', methods=['POST'])
def excluir_funcao(id):
    funcao = next((f for f in funcoes if f['id'] == id), None)
    if funcao:
        funcoes.remove(funcao)
        flash(f'Função "{funcao["nome"]}" deletada permanentemente!', 'danger')
    return redirect(url_for('listar_funcoes'))

# ─── Rotas protegidas — Usuários ─────────────────────────────────────────────

@app.route('/usuarios/listar')
def listar_usuarios():
    sql = '''
        SELECT
            id_usuario AS id,
            u.nome,
            email,
            f.nome AS funcao,
            u.status
        FROM usuarios AS u
        INNER JOIN funcoes AS f ON u.funcao_id = f.id_funcao
        ORDER BY id_usuario DESC ;
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('usuarios/listar_usuarios.html', usuarios=lista_dados)

@app.route('/usuarios/inserir', methods=['GET', 'POST'])
def inserir_usuario():

    sql = 'SELECT id_funcao, nome FROM funcoes'
    lista_funcoes = execute_query(sql, fetch=True)

    if request.method == 'POST':
        nome = request.form.get('nome','').strip()
        email = request.form.get('email','').strip()
        funcao_id = request.form.get('funcao')
        senha = request.form.get('senha', '').strip()
        status = request.form.get('status','Ativo').strip()

        if not all([nome, email, funcao_id, senha, status]):
            flash('Preencha todos os campos necessarios!', 'danger')
            return redirect(url_for('inserir_usuarios'))
        
        if senha != confirmar_senha:
            flash('As senhas nao conferem!')
            return redirect(url_for('inserir_usuarios'))
        
        if len(senha) < 0:
            flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('inserir_usuarios'))
        
        sql = '''SELECT COUNT (*) AS qtde FROM usuarios
                WHERE email = %s OR cpf = %s;
                '''
        
        existente = execute_one(sql)
        if existente:
            flash('E-mail ou CPF já cadastrados!', 'danger')
            return redirect(url_for('inserir_usuarios'))
        
        senha_hash = generate_password_hash(senha)

        try:
            sql_insert = '''
                INSERT INTO usuarios (nome, email, senha, status, funcao_id)
                VALUES (%s, %s, %s, %s, %s)
            '''

            execute_query(sql_insert, (nome, email, senha, status, funcao_id))
            
            flash(f'Usuário "{nome}" cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
            
        except Exception as e:
            flash(f'Erro ao salvar usuário no banco de dados. Tente novamente.', 'danger')
            return redirect(url_for('listar_usuarios'))


    return render_template('usuarios/inserir_usuario.html', titulo='Cadastrar Usuário', 
    modo='cadastrar', item=None, lista_funcoes=lista_funcoes)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = next((u for u in usuarios if u['id'] == id), None)
    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('listar_usuarios'))

    if request.method == 'POST':
        usuario['nome'] = request.form.get('nome', '').strip()
        usuario['email'] = request.form.get('email', '').strip()
        usuario['funcao'] = request.form.get('funcao', '').strip()
        usuario['status'] = request.form.get('status', 'Ativo').strip()
        nova_senha = request.form.get('senha', '').strip()
        if nova_senha:
            usuario['senha'] = nova_senha
            
        flash(f'Usuário "{usuario["nome"]}" atualizado com sucesso!', 'warning')
        return redirect(url_for('listar_usuarios'))

    funcoes_ativas = [f for f in funcoes if f.get('status', True) and f.get('ativo', True)]
    return render_template('usuarios/inserir_usuario.html', dados=usuario, funcoes=funcoes_ativas)

@app.route('/usuarios/esconder/<int:id>', methods=['POST'])
def esconder_usuario(id):
    usuario = next((u for u in usuarios if u['id'] == id), None)
    if usuario:
        usuario['ativo'] = False
        flash(f'Usuário "{usuario["nome"]}" escondido!', 'secondary')
    return redirect(url_for('listar_usuarios'))

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    usuario = next((u for u in usuarios if u['id'] == id), None)
    if usuario:
        usuarios.remove(usuario)
        flash(f'Usuário "{usuario["nome"]}" deletado permanentemente!', 'danger')
    return redirect(url_for('listar_usuarios'))

# ─── Rotas Restantes (Padrão) ────────────────────────────────────────────────

@app.route('/consultas/listar')
def listar_consultas():
    return render_template('consultas/listar_consultas.html', consultas=consultas)

@app.route('/consultas/inserir', methods=['GET', 'POST'])
def inserir_consulta():
    if request.method == 'POST':
        flash('Consulta agendada com sucesso!', 'success')
        return redirect(url_for('listar_consultas'))
    return render_template('consultas/inserir_consulta.html', pacientes=pacientes, especialidades=especialidades)

@app.route('/especialidades/listar')
def listar_especialidades():
    return render_template('especialidades/listar_especialidades.html', especialidades=especialidades)

@app.route('/especialidades/inserir', methods=['GET', 'POST'])
def inserir_especialidade():
    if request.method == 'POST':
        flash('Especialidade cadastrada com sucesso!', 'success')
        return redirect(url_for('listar_especialidades'))
    return render_template('especialidades/inserir_especialidade.html', medicos=usuarios)

@app.route('/pacientes/listar')
def listar_pacientes():
    return render_template('pacientes/listar_pacientes.html', pacientes=pacientes)

@app.route('/pacientes/inserir', methods=['GET', 'POST'])
def inserir_paciente():
    if request.method == 'POST':
        flash('Paciente cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_pacientes'))
    return render_template('pacientes/inserir_paciente.html')

@app.route('/equipe')
def equipe():
    return render_template('equipe.html')

if __name__ == '__main__':
    app.run(debug=True)