# Gestão de Indicadores Hospitalares - PostgreSQL

Este documento descreve como configurar e usar o sistema com PostgreSQL.

## Pré-requisitos

1. **PostgreSQL** instalado e rodando
2. **Python 3.8+** instalado
3. **pip** para gerenciar pacotes Python

## Configuração do Ambiente

### 1. Instalar PostgreSQL

**Windows:**
```bash
# Baixar do site oficial: https://www.postgresql.org/download/windows/
# Ou usar chocolatey:
choco install postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
```

### 2. Configurar PostgreSQL

```bash
# Iniciar serviço (Linux/macOS)
sudo systemctl start postgresql

# Acessar como usuário postgres
sudo -u postgres psql

# Criar usuário (opcional)
CREATE USER hospital_user WITH ENCRYPTED PASSWORD 'hospital_pass';
CREATE DATABASE gestao_indicadores OWNER hospital_user;
GRANT ALL PRIVILEGES ON DATABASE gestao_indicadores TO hospital_user;
```

### 3. Configurar Variáveis de Ambiente

Crie um arquivo `.env` no diretório `backend/`:

```env
# Configurações gerais
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Configurações do banco PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gestao_indicadores
DB_USER=postgres
DB_PASSWORD=postgres

# Ambiente
FLASK_ENV=development
FLASK_DEBUG=True
```

## Instalação

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Inicializar Banco de Dados

**Opção 1: Usando Flask-SQLAlchemy (Recomendado)**
```bash
cd backend/database
python manage_db.py
```

**Opção 2: Usando SQL diretamente**
```bash
# Conectar ao PostgreSQL
psql -h localhost -U postgres -d gestao_indicadores

# Executar schema
\i schema.sql
```

### 3. Resetar Banco (se necessário)

```bash
cd backend/database
python manage_db.py --reset
```

## Executar Aplicação

### 1. Iniciar Backend

```bash
cd backend/src
python app_postgresql.py
```

A API estará disponível em: `http://localhost:5000`

### 2. Testar Endpoints

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Login:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@hospital.com", "senha": "admin123"}'
```

## Estrutura do Banco

### Tabelas Principais

1. **unidades** - Unidades hospitalares
2. **usuarios** - Usuários do sistema
3. **indicadores** - Indicadores de qualidade/performance
4. **lancamentos** - Lançamentos dos valores dos indicadores

### Relacionamentos

- `usuarios.unidade_id` → `unidades.id`
- `lancamentos.indicador_id` → `indicadores.id`
- `lancamentos.unidade_id` → `unidades.id`
- `lancamentos.usuario_id` → `usuarios.id`

### Roles de Usuário

- **operador**: Acesso apenas à sua unidade
- **gestor**: Acesso a todas as unidades
- **admin**: Acesso total + gerenciamento de usuários

## Usuários Padrão

Após a inicialização, os seguintes usuários estarão disponíveis:

| Email | Senha | Role | Descrição |
|-------|-------|------|-----------|
| admin@hospital.com | admin123 | admin | Administrador do sistema |
| gestor@hospital.com | gestor123 | gestor | Gestor geral |
| operador@hospital.com | operador123 | operador | Operador da UTI Geral |

## API Endpoints

### Autenticação
- `POST /auth/login` - Login
- `POST /auth/register` - Cadastro
- `GET /auth/profile` - Perfil do usuário

### Unidades
- `GET /api/unidades` - Listar unidades

### Indicadores
- `GET /api/indicadores` - Listar indicadores
- `POST /api/indicadores` - Criar indicador (admin/gestor)

### Lançamentos
- `GET /api/lancamentos` - Listar lançamentos
- `POST /api/lancamentos` - Criar lançamento
- `PUT /api/lancamentos/<id>` - Atualizar lançamento

## Desenvolvimento

### Comandos Úteis

```bash
# Instalar nova dependência
pip install package_name
pip freeze > requirements.txt

# Verificar estrutura do banco
psql -h localhost -U postgres -d gestao_indicadores -c "\dt"

# Backup do banco
pg_dump -h localhost -U postgres gestao_indicadores > backup.sql

# Restaurar backup
psql -h localhost -U postgres gestao_indicadores < backup.sql
```

### Logs

Para debugging, os logs da aplicação são exibidos no console durante execução.

## Migração do Google Sheets

Para migrar dados do Google Sheets:

1. Exporte os dados existentes
2. Use o script `migrate_from_sheets.py` (a ser criado)
3. Ou importe manualmente via SQL

## Troubleshooting

### Erro de Conexão

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar se porta está aberta
netstat -an | grep :5432
```

### Erro de Permissão

```bash
# Verificar usuário do banco
psql -h localhost -U postgres -c "\du"
```

### Reset Completo

```bash
# Remover banco e recriar
dropdb -h localhost -U postgres gestao_indicadores
createdb -h localhost -U postgres gestao_indicadores
python manage_db.py
```