import os
import mysql.connector
from mysql.connector import Error, pooling

# Parâmetros de conexão — editados apenas aqui, usados em todo o sistema
_DB_PARAMS = {
    'host':               'localhost',
    'user':               'root',
    'password':           '', 
    'database':           'projeto_clinica_medica',  # Mesmo nome do CREATE DATABASE no seu schema.sql
    'charset':            'utf8mb4',
    'sql_mode':           ('STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,'
                           'ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'),
    'time_zone':          '-03:00',
    'use_pure':           True,
    'connection_timeout': 10,
    'autocommit':         False,
}

# Começamos com o pool vazio para não dar erro se o banco ainda não existir
_pool = None

def criar_pool():
    global _pool

    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name='webapp_pool',
            pool_size=5,
            pool_reset_session=True,
            **_DB_PARAMS
        )

def get_connection():
    try:
        if _pool is None: 
            criar_pool()
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'Não foi possível obter conexão: {e}')


def execute_query(sql, params=None, fetch=False):
    """Executa uma query SQL de forma segura."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount

    except Error as e:
        if conn:
            conn.rollback()
        raise Exception(f'Erro ao executar query: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_one(sql, params=None):
    """Executa um SELECT e retorna apenas a primeira linha (ou None)."""
    resultados = execute_query(sql, params, fetch=True)
    return resultados[0] if resultados else None


def iniciar_bd():
    """Lê o arquivo schema.sql e cria o banco e as tabelas se não existirem."""
    caminho_schema = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    if not os.path.exists(caminho_schema):
        print("⚠️ Arquivo schema.sql não encontrado!")
        return

    try:
        # ATENÇÃO: Conexão direta SEM o parâmetro 'database' para podermos criar o banco
        conn = mysql.connector.connect(
            host=_DB_PARAMS['host'],
            user=_DB_PARAMS['user'],
            password=_DB_PARAMS['password']
        )
        cursor = conn.cursor()
        
        # Lê o arquivo schema.sql
        with open(caminho_schema, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        # Divide os comandos usando o ponto-e-vírgula e executa um a um
        comandos = sql_script.split(';')
        
        for comando in comandos:
            comando_limpo = comando.strip()
            if comando_limpo: # Ignora linhas em branco
                cursor.execute(comando_limpo)
                
        conn.commit()
        print("✅ Banco de dados e tabelas inicializados com sucesso via schema.sql!")
        
    except Error as e:
        print(f"❌ Erro ao inicializar o banco de dados: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()