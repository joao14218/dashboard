-- Usuários (para login e permissões)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('CEO', 'Administrador', 'Professor', 'Vendedor'))
);

-- Alunos
CREATE TABLE alunos (
    matricula TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    nascimento DATE NOT NULL,
    celular TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    plano TEXT NOT NULL,
    data_inicio DATE NOT NULL,
    proximo_pagamento DATE,
    dias_aula TEXT,  -- JSON string para lista de dias
    professor TEXT,
    horario_aula TEXT,
    status TEXT NOT NULL DEFAULT 'Ativo',
    foto_url TEXT
);

-- Produtos (para vendas)
CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    imagem TEXT,
    disponivel BOOLEAN DEFAULT 1
);

-- Comandas (para vendas em andamento)
CREATE TABLE comandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_nome TEXT NOT NULL,
    itens TEXT,  -- JSON string para lista de itens
    total REAL DEFAULT 0.0,
    data_criacao DATE DEFAULT CURRENT_DATE
);

-- Histórico de Vendas
CREATE TABLE vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    cliente TEXT,
    total REAL NOT NULL,
    itens TEXT  -- JSON string
);

-- Presenças
CREATE TABLE presencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula TEXT NOT NULL,
    data DATE NOT NULL,
    presente BOOLEAN DEFAULT 1,
    FOREIGN KEY (matricula) REFERENCES alunos(matricula)
);

-- Aulas
CREATE TABLE aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    professor TEXT NOT NULL,
    duracao REAL NOT NULL,
    alunos TEXT  -- JSON string para lista de alunos
);

-- Inserir usuário admin padrão
INSERT INTO users (username, password_hash, role) VALUES ('admin', 'pbkdf2:sha256:150000$example$hashed_password', 'CEO');