-- Schema do banco de dados para Gestão de Indicadores Hospitalares
-- PostgreSQL Database Schema

-- Tabela de Unidades Hospitalares
CREATE TABLE unidades (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Usuários
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operador' CHECK (role IN ('operador', 'gestor', 'admin')),
    unidade_id INTEGER NOT NULL REFERENCES unidades(id),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP
);

-- Tabela de Indicadores
CREATE TABLE indicadores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL, -- 'qualidade', 'produtividade', 'seguranca', etc
    unidade_medida VARCHAR(50), -- 'percentual', 'numero', 'tempo', etc
    meta_mensal DECIMAL(10,2),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Lançamentos de Indicadores
CREATE TABLE lancamentos (
    id SERIAL PRIMARY KEY,
    indicador_id INTEGER NOT NULL REFERENCES indicadores(id),
    unidade_id INTEGER NOT NULL REFERENCES unidades(id),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    valor DECIMAL(15,4) NOT NULL,
    observacoes TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(indicador_id, unidade_id, ano, mes)
);

-- Índices para melhor performance
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_unidade ON usuarios(unidade_id);
CREATE INDEX idx_lancamentos_indicador ON lancamentos(indicador_id);
CREATE INDEX idx_lancamentos_unidade ON lancamentos(unidade_id);
CREATE INDEX idx_lancamentos_periodo ON lancamentos(ano, mes);
CREATE INDEX idx_lancamentos_usuario ON lancamentos(usuario_id);

-- Triggers para atualizar timestamp automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_unidades_updated_at BEFORE UPDATE ON unidades FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_indicadores_updated_at BEFORE UPDATE ON indicadores FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lancamentos_updated_at BEFORE UPDATE ON lancamentos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Dados iniciais das unidades
INSERT INTO unidades (nome, codigo) VALUES
('UTI Geral', 'UTI_GERAL'),
('UTI Coronariana', 'UTI_CORONARIANA'),
('UTI Pediátrica', 'UTI_PEDIATRICA'),
('UTI Neonatal', 'UTI_NEONATAL'),
('Centro Cirúrgico', 'CENTRO_CIRURGICO'),
('Emergência', 'EMERGENCIA'),
('Pronto Socorro', 'PRONTO_SOCORRO'),
('Internação Clínica', 'INTERNACAO_CLINICA'),
('Internação Cirúrgica', 'INTERNACAO_CIRURGICA'),
('Pediatria', 'PEDIATRIA'),
('Maternidade', 'MATERNIDADE'),
('Ambulatório', 'AMBULATORIO');

-- Indicadores padrão do sistema
INSERT INTO indicadores (nome, descricao, tipo, unidade_medida, meta_mensal) VALUES
('Taxa de Ocupação', 'Percentual de ocupação de leitos', 'produtividade', 'percentual', 85.00),
('Tempo Médio de Permanência', 'Tempo médio de permanência em dias', 'eficiencia', 'dias', 7.00),
('Taxa de Mortalidade', 'Taxa de mortalidade hospitalar', 'qualidade', 'percentual', 2.00),
('Taxa de Infecção Hospitalar', 'Taxa de infecção hospitalar', 'seguranca', 'percentual', 5.00),
('Satisfação do Paciente', 'Índice de satisfação do paciente', 'qualidade', 'nota', 8.50),
('Rotatividade de Leitos', 'Número de vezes que o leito foi ocupado', 'produtividade', 'numero', 3.00),
('Taxa de Reinternação', 'Taxa de reinternação em 30 dias', 'qualidade', 'percentual', 10.00),
('Cancelamento de Cirurgias', 'Taxa de cancelamento de cirurgias', 'eficiencia', 'percentual', 5.00),
('Tempo de Espera Emergência', 'Tempo médio de espera na emergência', 'eficiencia', 'minutos', 60.00),
('Adesão à Higienização', 'Taxa de adesão à higienização das mãos', 'seguranca', 'percentual', 95.00);

-- Usuário administrador padrão (senha: admin123)
INSERT INTO usuarios (nome, email, senha_hash, role, unidade_id) VALUES
('Administrador', 'admin@hospital.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/GjQhUU7qO4.Dm3h8G', 'admin', 1);