-- DROP DATABASE IF EXISTS projeto_clinica_medica;

CREATE DATABASE IF NOT EXISTS projeto_clinica_medica
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE projeto_clinica_medica;

CREATE TABLE IF NOT EXISTS funcoes(
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao VARCHAR(255),
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo', 

    funcao_id BIGINT UNSIGNED NOT NULL,

    pode_gerenciar_usuarios BOOLEAN DEFAULT 0 

    --log
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_cliente_funcao
    FOREIGN KEY (funcao id) REFERENCES funcoes (id_funcao)

);