# db.py — Módulo central de acesso ao banco de dados
# Qualquer arquivo que precise do banco importa apenas este módulo

import mysql.connector
from mysql.connector import Error, pooling
import os

# Parâmetros de conexão — editados apenas aqui, usados em todo o sistema
_DB_PARAMS = {
    'host':               'localhost',
    'user':               'root',
    'password':           '',
    'database':           'projeto_clinica_medica',
    'charset':            'utf8mb4',
    'sql_mode':           ('STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,'
                           'ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'),
    'use_pure':           True,       # Python puro — compatível com todos os ambientes
    'connection_timeout': 10,         # desiste após 10s sem resposta
    'autocommit':         False,      # exige commit() explícito
}

# Pool criado uma única vez quando o módulo é carregado pela primeira vez.
# conn.close() devolve a conexão ao pool — não fecha fisicamente.
_pool = pooling.MySQLConnectionPool(
    pool_name='webapp_pool',
    pool_size=5,           # conexões abertas permanentemente
    pool_reset_session=True,
    **_DB_PARAMS
)


def get_connection():
    """Retorna uma conexão do pool. Levanta Exception em caso de falha."""
    try:
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'Não foi possível obter conexão do pool: {e}')


def execute_query(sql, params=None, fetch=False):
    """
    Executa uma query SQL de forma segura.

    Parâmetros:
        sql    — string SQL com %s como placeholders
        params — tupla ou lista com os valores dos placeholders
        fetch  — True para SELECT (retorna lista de dicts); False para INSERT/UPDATE/DELETE

    Retorna:
        fetch=True  → lista de dicionários (cada linha = {'coluna': valor})
        fetch=False → número de linhas afetadas
    """
    conn = get_connection()
    try:
        # dictionary=True: cada linha retorna como dicionário — produto['nome'] em vez de produto[0]
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        if fetch:
            return cursor.fetchall()   # retorna todas as linhas
        else:
            conn.commit()              # confirma a transação
            return cursor.rowcount     # número de linhas afetadas

    except Error as e:
        conn.rollback()  # desfaz alterações parciais em caso de erro
        raise Exception(f'Erro ao executar query: {e}')
    finally:
        cursor.close()
        conn.close()   # devolve ao pool, não fecha fisicamente


def execute_one(sql, params=None):
    """
    Executa um SELECT e retorna apenas a primeira linha (ou None).
    Útil para buscar um registro por ID.
    """
    resultados = execute_query(sql, params, fetch=True)
    return resultados[0] if resultados else None

import os
import mysql.connector
from mysql.connector import Error, pooling

# --- MANTENHA SUAS CONFIGURAÇÕES AQUI (Atenção para o nome do database) ---
_DB_PARAMS = {
    'host':               'localhost',
    'user':               'root',
    'password':           '', # A senha que arrumamos na etapa anterior
    'database':           'vitasaude_db', # Tem que ser o mesmo nome do CREATE DATABASE do seu schema.sql
    'charset':            'utf8mb4',
    'sql_mode':           ('STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,'
                           'ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'),
    'time_zone':          '-03:00',
    'use_pure':           True,
    'connection_timeout': 10,
    'autocommit':         False,
}

_pool = pooling.MySQLConnectionPool(pool_name='vitasaude_pool', pool_size=5, pool_reset_session=True, **_DB_PARAMS)

# --- FUNÇÕES GET_CONNECTION E EXECUTE_QUERY CONTINUAM IGUAIS ---
# (Mantenha elas aqui...)


# --- SUBSTITUA A FUNÇÃO DE INICIAR O BD POR ESTA ---
def iniciar_bd():
    # Caminho do arquivo schema.sql na mesma pasta do db.py
    caminho_schema = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    if not os.path.exists(caminho_schema):
        print("⚠️ Arquivo schema.sql não encontrado!")
        return

    # ATENÇÃO: Criamos uma conexão DIRETA (fora do Pool) e SEM o parâmetro 'database'.
    # Fazemos isso para rodar o "CREATE DATABASE". Se usássemos o Pool, daria erro de "banco desconhecido".
    try:
        conn = mysql.connector.connect(
            host=_DB_PARAMS['host'],
            user=_DB_PARAMS['user'],
            password=_DB_PARAMS['password']
            # Deixamos o database de fora de propósito!
        )
        cursor = conn.cursor()
        
        # Lê o arquivo schema.sql
        with open(caminho_schema, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        # Divide os comandos usando o ponto-e-vírgula e executa um a um
        # (Isto resolve definitivamente o erro do "multi")
        comandos = sql_script.split(';')
        
        for comando in comandos:
            comando_limpo = comando.strip()
            if comando_limpo: # Se não for uma linha em branco
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