from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import iniciar_bd
from db import execute_one
from db import execute_query
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'vitasaude-fatec-2026'

iniciar_bd()

def garantir_admin():
    total = execute_one('SELECT COUNT(*) AS total FROM usuarios')
    if total and total['total'] > 0:
        return 

    funcao = execute_one("SELECT id_funcao FROM funcoes WHERE nome = 'Administrador'")
    if not funcao:
        execute_query(
            """INSERT INTO funcoes (nome, descricao, status, pode_gerenciar_usuarios, pode_gerenciar_pacientes, pode_gerenciar_especialidades, pode_gerenciar_consultas) 
               VALUES ('Administrador', 'Acesso total', 'Ativo', 1, 1, 1, 1)"""
        )
        funcao = execute_one("SELECT id_funcao FROM funcoes WHERE nome = 'Administrador'")

    senha_hash = generate_password_hash('admin1234')
    execute_query(
        """INSERT INTO usuarios (nome, email, senha, status, funcao_id) 
           VALUES ('Administrador', 'admin@vitasaude.com', %s, 'Ativo', %s)""",
        (senha_hash, funcao['id_funcao'])
    )

garantir_admin()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('usuario'):
            flash('Faça login para acessar o sistema.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.context_processor
def injetar_usuario():
    return dict(usuario_logado=session.get('usuario'))

# ─── Rotas públicas ───────────────────────────────────────────────────────────

@app.route('/')
def index():
    sql = '''
        SELECT
        nome,
        descricao
        FROM especialidades
        WHERE status = "Ativo"
    '''
    especialidades_bd = execute_query(sql, fetch=True)
    return render_template('index.html', especialidades=especialidades_bd)

@app.route('/servicos')
def servicos():
    sql = '''
        SELECT
        nome,
        descricao
        FROM especialidades
        WHERE status = "Ativo"
    '''
    especialidades_bd = execute_query(sql, fetch=True)
    return render_template('servicos.html', especialidades=especialidades_bd)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        sql = '''
        SELECT 
            u.id_usuario,
            u.nome,
            u.email,
            u.senha,
            u.status,
            f.nome AS funcao
            FROM usuarios u
            JOIN funcoes f ON u.funcao_id = f.id_funcao
            WHERE u.email = %s
        '''
        usuario = execute_one(sql, (email,))

        if not usuario or not check_password_hash(usuario['senha'], senha):
            flash('E-mail ou senha inválidos!', 'danger')
            return redirect(url_for('login'))
        
        if usuario['status'] != 'Ativo':
            flash('Sua conta está inativa. Procure a administração.', 'warning')
            return redirect(url_for('login'))
        
        session['usuario'] = {
            'id': usuario['id_usuario'],
            'nome': usuario['nome'],
            'email': usuario['email'],
            'funcao': usuario['funcao']
        }

        flash(f'Bem-vindo(a), {usuario["nome"]}!', 'success')
        return redirect(url_for('listar_pacientes'))
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        flash('Cadastro realizado! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

# ─── Rotas protegidas — Funções ──────────────────────────────────────────────

@app.route('/funcoes/listar')
@login_required
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
@login_required
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
@login_required
def editar_funcao(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        status = 'Ativo' if request.form.get('status') else 'Inativo'
        p_usuarios = 1 if request.form.get('pode_gerenciar_usuarios') else 0
        p_pacientes = 1 if request.form.get('pode_gerenciar_pacientes') else 0
        p_especialidades = 1 if request.form.get('pode_gerenciar_especialidades') else 0
        p_consultas = 1 if request.form.get('pode_gerenciar_consultas') else 0

        try:
            sql = '''
                UPDATE funcoes 
                SET 
                    nome = %s, 
                    descricao = %s, 
                    status = %s, 
                    pode_gerenciar_usuarios = %s, 
                    pode_gerenciar_pacientes = %s, 
                    pode_gerenciar_especialidades = %s, 
                    pode_gerenciar_consultas = %s 
                WHERE id_funcao = %s
            '''
            execute_query(sql, (nome, descricao, status, p_usuarios, p_pacientes, p_especialidades, p_consultas, id))
            flash('Função atualizada com sucesso!', 'warning')
            return redirect(url_for('listar_funcoes'))
        except Exception as e:
            flash('Erro ao atualizar.', 'danger')

    funcao = execute_one('SELECT * FROM funcoes WHERE id_funcao = %s', (id,))

    return render_template('funcoes/inserir_funcao.html', dados=funcao)

@app.route('/funcoes/esconder/<int:id>', methods=['POST'])
@login_required
def esconder_funcao(id):
    try:
        execute_query("UPDATE funcoes SET status = 'Inativo' WHERE id_funcao = %s", (id,))
        flash('Função inativada!', 'secondary')
    except Exception as e:
        flash('Erro ao inativar função.', 'danger')
    return redirect(url_for('listar_funcoes'))

@app.route('/funcoes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_funcao(id):
    try:
        execute_query("DELETE FROM funcoes WHERE id_funcao = %s", (id,))
        flash('Função deletada!', 'danger')
    except Exception as e:
        flash('Não foi possível deletar. Função em uso.', 'danger')
        app.logger.error(f'Erro ao excluir função: {e}')
    return redirect(url_for('listar_funcoes'))

# ─── Rotas protegidas — Usuários ─────────────────────────────────────────────

@app.route('/usuarios/listar')
@login_required
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
@login_required
def inserir_usuario():

    sql_funcoes = 'SELECT id_funcao, nome FROM funcoes WHERE status = "Ativo"'
    lista_funcoes = execute_query(sql_funcoes, fetch=True)

    if request.method == 'POST':
        nome = request.form.get('nome','').strip()
        email = request.form.get('email','').strip()
        funcao_id = request.form.get('funcao_id')
        senha = request.form.get('senha', '').strip()
        status = request.form.get('status','Ativo').strip()

        if not all([nome, email, funcao_id, senha]):
            flash('Preencha todos os campos necessarios!', 'danger')
            return redirect(url_for('inserir_usuario'))
        
        if len(senha) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('inserir_usuario'))
        
        sql = 'SELECT id_usuario FROM usuarios WHERE email = %s'
        
        existente = execute_one(sql, (email,))
        if existente:
            flash('E-mail ou CPF já cadastrados!', 'danger')
            return redirect(url_for('inserir_usuario'))
        
        senha_hash = generate_password_hash(senha)

        try:
            sql_insert = '''
                INSERT INTO usuarios (nome, email, senha, status, funcao_id)
                VALUES (%s, %s, %s, %s, %s)
            '''

            execute_query(sql_insert, (nome, email, senha_hash, status, funcao_id))
            
            flash(f'Usuário "{nome}" cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
            
        except Exception as e:
            flash(f'Erro ao salvar usuário no banco de dados. Tente novamente.', 'danger')
            return redirect(url_for('inserir_usuario'))


    return render_template('usuarios/inserir_usuario.html', titulo='Cadastrar Usuário', 
    modo='cadastrar', item=None, funcoes=lista_funcoes)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if request.method == 'POST':
        nome = request.form.get('nome','').strip()
        email = request.form.get('email','').strip()
        funcao_id = request.form.get('funcao_id')
        status = request.form.get('status','Ativo').strip()
        nova_senha = request.form.get('senha', '').strip()

        if not all([nome, email, funcao_id]):
            flash('Preencha todos os campos necessarios!', 'danger')
            return redirect(url_for('editar_usuario', id=id))
        
        sql = '''SELECT id_usuario FROM usuarios
                WHERE (email = %s) AND id_usuario != %s;
                '''
        
        existente = execute_one(sql, (email, id))
        if existente:
            flash('E-mail já cadastrado para outro usuário!', 'danger')
            return redirect(url_for('editar_usuario', id=id))

        try:
            if nova_senha:
                if len(nova_senha) < 8:
                    flash('A nova senha deve ter pelo menos 8 caracteres.', 'danger')
                    return redirect(url_for('editar_usuario', id=id))
                senha_hash = generate_password_hash(nova_senha)
                sql_update = '''
                    UPDATE usuarios
                    SET nome = %s, email = %s, status = %s, funcao_id = %s, senha = %s
                    WHERE id_usuario = %s
                '''
                execute_query(sql_update, (nome, email, status, funcao_id, senha_hash, id))

            else:
                sql_update = '''
                    UPDATE usuarios
                    SET nome = %s, email = %s, status = %s, funcao_id = %s
                    WHERE id_usuario = %s
                '''
                execute_query(sql_update, (nome, email, status, funcao_id, id))

            flash(f'Usuário "{nome}" atualizado com sucesso!', 'warning')
            return redirect(url_for('listar_usuarios'))
            
        except Exception as e:
            flash(f'Erro ao atualizar usuário no banco de dados. Tente novamente.', 'danger')
            return redirect(url_for('editar_usuario', id=id))
    usuario = execute_one('SELECT id_usuario AS id, nome, email, funcao_id, status FROM usuarios WHERE id_usuario = %s', (id,))
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('listar_usuarios'))
    
    sql_funcoes = '''
    SELECT id_funcao, nome 
    FROM funcoes WHERE status = "Ativo"
    '''
    funcoes_ativas = execute_query(sql_funcoes, fetch=True)
    return render_template('usuarios/inserir_usuario.html', dados=usuario, funcoes=funcoes_ativas)

@app.route('/usuarios/esconder/<int:id>', methods=['POST'])
@login_required
def esconder_usuario(id):
    try:
        execute_query("UPDATE usuarios SET status = 'Inativo' WHERE id_usuario = %s", (id,))
        flash('Usuário inativado!', 'secondary')
    except Exception as e:
        flash('Erro ao inativar usuário.', 'danger')
    return redirect(url_for('listar_usuarios'))

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_usuario(id):
    try:
        execute_query("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
        flash('Usuário excluído permanentemente!', 'danger')
    except Exception as e:
        flash('Erro ao excluir usuário.', 'danger')
    return redirect(url_for('listar_usuarios'))

# ─── Rotas Restantes (Padrão) ────────────────────────────────────────────────

@app.route('/consultas/listar')
@login_required
def listar_consultas():
    return render_template('consultas/listar_consultas.html', consultas=[])

@app.route('/consultas/inserir', methods=['GET', 'POST'])
@login_required
def inserir_consulta():
    if request.method == 'POST':
        flash('Consulta agendada com sucesso!', 'success')
        return redirect(url_for('listar_consultas'))
    
    listar_pacientes = execute_query('SELECT id_paciente, nome FROM pacientes WHERE status = "Ativo"', fetch=True)
    lista_especialidades = execute_query('SELECT id_especialidade, nome FROM especialidades WHERE status = "Ativo"', fetch=True)

    return render_template('consultas/inserir_consulta.html', pacientes=listar_pacientes, especialidades=lista_especialidades)

@app.route('/especialidades/listar')
@login_required
def listar_especialidades():
    sql = '''
        SELECT 
            id_especialidade AS id, 
            e.nome, 
            e.descricao,
            e.status,
            e.duracao,
            u.nome AS medico
        FROM especialidades AS e 
        JOIN usuarios AS u ON e.usuario_id = u.id_usuario
        ORDER BY e.id_especialidade DESC;
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('especialidades/listar_especialidades.html', especialidades=lista_dados)

@app.route('/especialidades/inserir', methods=['GET', 'POST'])
@login_required
def inserir_especialidade():
    sql_medicos = '''
        SELECT u.id_usuario, u.nome 
        FROM usuarios u 
        JOIN funcoes f 
        ON u.funcao_id = f.id_funcao
        WHERE f.nome = "Médico" 
        AND u.status = "Ativo"
    '''
    lista_medicos = execute_query(sql_medicos, fetch=True)
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        usuario_id = request.form.get('medico')
        duracao = request.form.get('duracao', '').strip()

        if not all([nome, descricao, usuario_id, duracao]):
            flash('Preencha todos os campos necessários!', 'danger')
            return redirect(url_for('inserir_especialidade'))

        try:
            sql_insert = '''
                INSERT INTO especialidades (
                nome, 
                descricao, 
                usuario_id, 
                duracao
                )
                VALUES (%s, %s, %s, %s)
            '''
            execute_query(sql_insert, (nome, descricao, usuario_id, duracao))
            flash('Especialidade cadastrada com sucesso!', 'success')
            return redirect(url_for('listar_especialidades'))
        except Exception as e:
            flash('Erro ao salvar especialidade no banco de dados. Tente novamente.', 'danger')
            return redirect(url_for('inserir_especialidade'))
        
    return render_template('especialidades/inserir_especialidade.html', dados=None, medicos=lista_medicos)

@app.route('/especialidades/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_especialidade(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        usuario_id = request.form.get('medico')
        duracao = request.form.get('duracao', '').strip()
        status = 'Ativo' if request.form.get('status') else 'Inativo'

        sql = '''
        UPDATE especialidades SET 
        nome=%s, 
        descricao=%s, 
        duracao=%s, 
        usuario_id=%s, 
        status=%s 
        WHERE id_especialidade=%s
        '''
        execute_query(sql, (nome, descricao, duracao, usuario_id, status, id))
        flash('Especialidade atualizada!', 'warning')
        return redirect(url_for('listar_especialidades'))

    especialidade = execute_one('SELECT * FROM especialidades WHERE id_especialidade = %s', (id,))
    lista_medicos = execute_query("SELECT u.id_usuario, u.nome FROM usuarios u JOIN funcoes f ON u.funcao_id = f.id_funcao WHERE f.nome = 'Médico'", fetch=True)
    return render_template('especialidades/inserir_especialidade.html', dados=especialidade, medicos=lista_medicos)

@app.route('/especialidades/esconder/<int:id>', methods=['POST'])
@login_required
def esconder_especialidade(id):
    execute_query("UPDATE especialidades SET status = 'Inativo' WHERE id_especialidade = %s", (id,))
    flash('Especialidade inativada!', 'secondary')
    return redirect(url_for('listar_especialidades'))

@app.route('/especialidades/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_especialidade(id):
    try:
        execute_query("DELETE FROM especialidades WHERE id_especialidade = %s", (id,))
        flash('Especialidade deletada!', 'danger')
    except:
        flash('Erro ao deletar especialidade. Existem consultas vinculadas.', 'danger')
    return redirect(url_for('listar_especialidades'))

@app.route('/pacientes/listar')
@login_required
def listar_pacientes():
    sql = '''
        SELECT 
            id_paciente AS id, 
            nome, 
            cpf, 
            nascimento, 
            telefone, 
            convenio,
            status
        FROM pacientes
        ORDER BY id_paciente DESC;
    '''
    lista_dados = execute_query(sql, fetch=True)
    return render_template('pacientes/listar_pacientes.html', pacientes=lista_dados)

@app.route('/pacientes/inserir', methods=['GET', 'POST'])
@login_required
def inserir_paciente():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        nascimento = request.form.get('nascimento', '').strip()
        telefone = request.form.get('telefone', '').strip()
        convenio = request.form.get('convenio', '').strip()

        if not all([nome, cpf, nascimento, telefone, convenio]):
            flash('Preencha todos os campos necessários!', 'danger')
            return redirect(url_for('inserir_paciente'))
        
        if execute_one('SELECT id_paciente FROM pacientes WHERE cpf = %s', (cpf,)):
            flash('CPF já cadastrado!', 'danger')
            return redirect(url_for('inserir_paciente'))

        sql = '''
            INSERT INTO pacientes(
            nome, 
            cpf, 
            nascimento, 
            telefone, 
            convenio
            )
            VALUES (%s, %s, %s, %s, %s)
        '''
        execute_query(sql, params=(nome, cpf, nascimento, telefone, convenio))
        flash('Paciente cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_pacientes'))
    return render_template('pacientes/inserir_paciente.html', dados=None)

@app.route('/pacientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_paciente(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        nascimento = request.form.get('nascimento', '').strip()
        telefone = request.form.get('telefone', '').strip()
        convenio = request.form.get('convenio', '').strip()
        status = 'Ativo' if request.form.get('status') else 'Inativo'

        if not all([nome, cpf, nascimento, telefone, convenio]):
            flash('Preencha todos os campos necessários!', 'danger')
            return redirect(url_for('editar_paciente', id=id))

        sql = '''
            UPDATE pacientes
            SET 
                nome = %s, 
                cpf = %s, 
                nascimento = %s, 
                telefone = %s, 
                convenio = %s,
                status = %s
            WHERE id_paciente = %s
        '''
        execute_query(sql, params=(nome, cpf, nascimento, telefone, convenio, status, id))
        flash('Paciente atualizado com sucesso!', 'warning')
        return redirect(url_for('listar_pacientes'))
    
    paciente = execute_one('SELECT * FROM pacientes WHERE id_paciente = %s', (id,))
    return render_template('pacientes/inserir_paciente.html', dados=paciente)

@app.route('/pacientes/esconder/<int:id>', methods=['POST'])
@login_required
def esconder_paciente(id):
    execute_query("UPDATE pacientes SET status = 'Inativo' WHERE id_paciente = %s", (id,))
    flash('Paciente inativado!', 'secondary')
    return redirect(url_for('listar_pacientes'))

@app.route('/pacientes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_paciente(id):
    try:
        execute_query("DELETE FROM pacientes WHERE id_paciente = %s", (id,))
        flash('Paciente deletado!', 'danger')
    except:
        flash('Não foi possível deletar. Paciente em uso.', 'danger')
    return redirect(url_for('listar_pacientes'))

@app.route('/equipe')
def equipe():
    return render_template('equipe.html')

if __name__ == '__main__':
    app.run(debug=True)