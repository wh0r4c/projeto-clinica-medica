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
    pode_gerenciar_usuarios BOOLEAN DEFAULT 0,

    -- log (Note a vírgula acima e o espaço aqui no comentário)
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