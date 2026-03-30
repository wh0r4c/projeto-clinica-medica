from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'vitasaude-fatec-2026'

# ─── Dados simulados ─────────────────────────────────────────────────────────

usuarios = [
    {'id': 1, 'nome': 'Dra. Ana Paula Reis',    'email': 'ana@vitasaude.com',    'perfil': 'Médico'},
    {'id': 2, 'nome': 'Dr. Carlos Mendonça',     'email': 'carlos@vitasaude.com', 'perfil': 'Médico'},
    {'id': 3, 'nome': 'Fernanda Lima',           'email': 'fernanda@vitasaude.com','perfil': 'Recepcionista'},
    {'id': 4, 'nome': 'Dr. Roberto Alves',       'email': 'roberto@vitasaude.com','perfil': 'Médico'},
    {'id': 5, 'nome': 'Juliana Costa',           'email': 'juliana@vitasaude.com','perfil': 'Administrador'},
]

pacientes = [
    {'id': 1, 'nome': 'Marcos Oliveira',   'cpf': '321.654.987-00', 'nascimento': '1985-03-12', 'telefone': '(14) 99812-3456', 'convenio': 'Unimed'},
    {'id': 2, 'nome': 'Patrícia Souza',    'cpf': '456.789.123-11', 'nascimento': '1992-07-28', 'telefone': '(14) 99723-4567', 'convenio': 'SulAmérica'},
    {'id': 3, 'nome': 'Eduardo Ferreira',  'cpf': '789.123.456-22', 'nascimento': '1978-11-05', 'telefone': '(14) 99634-5678', 'convenio': 'Particular'},
    {'id': 4, 'nome': 'Lucia Nascimento',  'cpf': '123.456.789-33', 'nascimento': '2001-01-19', 'telefone': '(14) 99545-6789', 'convenio': 'Bradesco Saúde'},
    {'id': 5, 'nome': 'Rafael Cardoso',    'cpf': '654.321.098-44', 'nascimento': '1969-09-30', 'telefone': '(14) 99456-7890', 'convenio': 'Unimed'},
]

especialidades = [
    {'id': 1, 'nome': 'Clínica Geral',      'descricao': 'Atendimento geral e preventivo para todas as idades.',         'medico': 'Dr. Carlos Mendonça',  'duracao': 30},
    {'id': 2, 'nome': 'Cardiologia',        'descricao': 'Diagnóstico e tratamento de doenças do coração e vasos.',       'medico': 'Dra. Ana Paula Reis',  'duracao': 45},
    {'id': 3, 'nome': 'Dermatologia',       'descricao': 'Cuidados com a pele, cabelo e unhas.',                          'medico': 'Dr. Roberto Alves',    'duracao': 30},
    {'id': 4, 'nome': 'Ortopedia',          'descricao': 'Tratamento de ossos, articulações e lesões musculares.',         'medico': 'Dr. Carlos Mendonça',  'duracao': 40},
    {'id': 5, 'nome': 'Pediatria',          'descricao': 'Saúde e desenvolvimento de crianças e adolescentes.',           'medico': 'Dra. Ana Paula Reis',  'duracao': 30},
]

consultas = [
    {'id': 1, 'paciente': 'Marcos Oliveira',  'medico': 'Dra. Ana Paula Reis',  'especialidade': 'Cardiologia',   'data': '2026-04-02', 'hora': '08:00', 'status': 'Agendada'},
    {'id': 2, 'paciente': 'Patrícia Souza',   'medico': 'Dr. Carlos Mendonça',  'especialidade': 'Clínica Geral', 'data': '2026-04-02', 'hora': '09:30', 'status': 'Confirmada'},
    {'id': 3, 'paciente': 'Eduardo Ferreira', 'medico': 'Dr. Roberto Alves',    'especialidade': 'Dermatologia',  'data': '2026-04-03', 'hora': '14:00', 'status': 'Agendada'},
    {'id': 4, 'paciente': 'Lucia Nascimento', 'medico': 'Dra. Ana Paula Reis',  'especialidade': 'Pediatria',     'data': '2026-03-28', 'hora': '10:00', 'status': 'Concluída'},
    {'id': 5, 'paciente': 'Rafael Cardoso',   'medico': 'Dr. Carlos Mendonça',  'especialidade': 'Ortopedia',     'data': '2026-03-27', 'hora': '16:30', 'status': 'Cancelada'},
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

        erros = []
        if not email:
            erros.append('O e-mail é obrigatório.')
        if not senha:
            erros.append('A senha é obrigatória.')

        if erros:
            for e in erros:
                flash(e, 'danger')
            return render_template('login.html', email=email)

        session['usuario'] = email
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('listar_consultas'))

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome  = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        conf  = request.form.get('confirmar_senha', '').strip()

        erros = []
        if not nome:
            erros.append('O nome é obrigatório.')
        if not email:
            erros.append('O e-mail é obrigatório.')
        if not senha:
            erros.append('A senha é obrigatória.')
        elif len(senha) < 6:
            erros.append('A senha deve ter ao menos 6 caracteres.')
        elif senha != conf:
            erros.append('As senhas não coincidem.')

        if erros:
            for e in erros:
                flash(e, 'danger')
            return render_template('cadastro.html', nome=nome, email=email)

        flash('Cadastro realizado! Faça login para continuar.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

# ─── Rotas protegidas — Consultas ────────────────────────────────────────────

@app.route('/consultas/listar')
def listar_consultas():
    return render_template('consultas/listar_consultas.html', consultas=consultas)

