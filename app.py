from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import iniciar_bd

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
    funcoes_visiveis = [f for f in funcoes if f.get('ativo', True)]
    return render_template('funcoes/listar_funcoes.html', funcoes=funcoes_visiveis)

@app.route('/funcoes/inserir', methods=['GET', 'POST'])
def inserir_funcao():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        status = True if request.form.get('status') else False
        pode_gerenciar = True if request.form.get('pode_gerenciar') else False

        novo_id = max([f['id'] for f in funcoes], default=0) + 1
        funcoes.append({
            'id': novo_id, 'nome': nome, 'descricao': descricao,
            'status': status, 'pode_gerenciar_usuarios': pode_gerenciar, 'ativo': True
        })
        flash(f'Função "{nome}" cadastrada com sucesso!', 'success')
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
    usuarios_visiveis = [u for u in usuarios if u.get('ativo', True)]
    return render_template('usuarios/listar_usuarios.html', usuarios=usuarios_visiveis)

@app.route('/usuarios/inserir', methods=['GET', 'POST'])
def inserir_usuario():
    if request.method == 'POST':
        nome   = request.form.get('nome', '').strip()
        email  = request.form.get('email', '').strip()
        funcao = request.form.get('funcao', '').strip()
        senha  = request.form.get('senha', '').strip()
        status = request.form.get('status', 'Ativo').strip()

        novo_id = max([u['id'] for u in usuarios], default=0) + 1
        usuarios.append({
            'id': novo_id, 'nome': nome, 'email': email,
            'funcao': funcao, 'senha': senha, 'status': status, 'ativo': True
        })
        flash(f'Usuário "{nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))

    funcoes_ativas = [f for f in funcoes if f.get('status', True) and f.get('ativo', True)]
    return render_template('usuarios/inserir_usuario.html', dados=None, funcoes=funcoes_ativas)

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