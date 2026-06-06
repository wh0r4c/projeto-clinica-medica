-- DROP DATABASE IF EXISTS projeto_clinica_medica;

CREATE DATABASE IF NOT EXISTS projeto_clinica_medica
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE projeto_clinica_medica;

-- TABELA DE FUNÇÕES
CREATE TABLE IF NOT EXISTS funcoes(
    id_funcao INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao VARCHAR(255),
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo', 

    -- PERMISSÕES DO SEU SISTEMA (O que o professor pediu)
    pode_gerenciar_usuarios BOOLEAN DEFAULT 0,
    pode_gerenciar_pacientes BOOLEAN DEFAULT 0,
    pode_gerenciar_especialidades BOOLEAN DEFAULT 0,
    pode_gerenciar_consultas BOOLEAN DEFAULT 0,

    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- TABELA DE USUÁRIOS (Aqui sim entra a chave estrangeira!)
CREATE TABLE IF NOT EXISTS usuarios(
    id_usuario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',

    -- Campo que vai ligar o usuario com a tabela de funcoes
    funcao_id INT UNSIGNED NOT NULL,

    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Criando a ligação (Chave Estrangeira)
    CONSTRAINT fk_usuario_funcao
    FOREIGN KEY (funcao_id) REFERENCES funcoes (id_funcao)
);

CREATE TABLE IF NOT EXISTS pacientes(
    id_paciente INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    convenio VARCHAR(50) NOT NULL,
    nascimento DATE NOT NULL,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',

    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS especialidades(
    id_especialidade INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao VARCHAR(255),
    duracao INT NOT NULL DEFAULT 30, -- em minutos
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    CONSTRAINT fk_especialidade_medico FOREIGN KEY (usuario_id) REFERENCES usuarios (id_usuario)

    -- log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);