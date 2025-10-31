"""
Sistema de Gestão de Indicadores Hospitalares - Backend API SIMPLIFICADO
Versão com PostgreSQL sem dependências complexas
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import logging
from functools import wraps
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação Flask
app = Flask(__name__)

# Configuração
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Configurar JWT
jwt = JWTManager(app)

# Configurar CORS
cors_origins = os.environ.get('CORS_ORIGINS', '*')
if cors_origins == '*':
    CORS(app, supports_credentials=True, origins=True)
else:
    CORS(app, supports_credentials=True, origins=cors_origins.split(','))

# Configuração do banco PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def get_db_connection():
    """Conectar ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar no banco: {e}")
        return None

def init_database():
    """Inicializar banco de dados"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Criar tabelas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS unidades (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE,
                codigo VARCHAR(20) NOT NULL UNIQUE,
                ativo BOOLEAN DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                nome VARCHAR(100) NOT NULL,
                senha_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'operador',
                unidade_id INTEGER REFERENCES unidades(id),
                ativo BOOLEAN DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS indicadores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL UNIQUE,
                codigo VARCHAR(20) NOT NULL UNIQUE,
                tipo VARCHAR(50) NOT NULL,
                unidade_medida VARCHAR(20),
                ativo BOOLEAN DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS lancamentos (
                id SERIAL PRIMARY KEY,
                indicador_id INTEGER REFERENCES indicadores(id),
                unidade_id INTEGER REFERENCES unidades(id),
                usuario_id INTEGER REFERENCES usuarios(id),
                valor DECIMAL(10,2) NOT NULL,
                data_lancamento DATE NOT NULL,
                observacoes TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Verificar se já existe dados
        cur.execute("SELECT COUNT(*) FROM unidades")
        count = cur.fetchone()[0]
        
        if count == 0:
            # Inserir dados iniciais
            unidades = [
                ('UTI Geral', 'UTI01'),
                ('UTI Cardiológica', 'UTI02'),
                ('Pronto Socorro', 'PS01'),
                ('Enfermaria Clínica', 'ENF01'),
                ('Centro Cirúrgico', 'CC01')
            ]
            
            for nome, codigo in unidades:
                cur.execute(
                    "INSERT INTO unidades (nome, codigo) VALUES (%s, %s)",
                    (nome, codigo)
                )
            
            # Criar usuários
            senha_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            usuarios = [
                ('admin@hospital.com', 'Administrador', senha_hash, 'admin', 1),
                ('gestor@hospital.com', 'Gestor Hospitalar', senha_hash, 'gestor', 1),
                ('operador@hospital.com', 'Operador UTI', senha_hash, 'operador', 1)
            ]
            
            for email, nome, senha, role, unidade_id in usuarios:
                cur.execute(
                    "INSERT INTO usuarios (email, nome, senha_hash, role, unidade_id) VALUES (%s, %s, %s, %s, %s)",
                    (email, nome, senha, role, unidade_id)
                )
            
            logger.info("Dados iniciais criados!")
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Banco inicializado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        return False

# Decorador para verificar roles
def role_required(roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'message': 'Erro de conexão com banco'}), 500
            
            try:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT * FROM usuarios WHERE id = %s AND ativo = TRUE", (current_user_id,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if not user:
                    return jsonify({'message': 'Usuário não encontrado'}), 401
                
                if isinstance(roles, list):
                    if user['role'] not in roles:
                        return jsonify({'message': 'Acesso negado'}), 403
                else:
                    if user['role'] != roles:
                        return jsonify({'message': 'Acesso negado'}), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Erro na verificação de role: {e}")
                return jsonify({'message': 'Erro interno'}), 500
                
        return decorated_function
    return decorator

# ROTAS DE AUTENTICAÇÃO
@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Erro de conexão'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT u.*, un.nome as unidade_nome 
            FROM usuarios u 
            LEFT JOIN unidades un ON u.unidade_id = un.id 
            WHERE u.email = %s AND u.ativo = TRUE
        """, (email,))
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user or not bcrypt.checkpw(senha.encode('utf-8'), user['senha_hash'].encode('utf-8')):
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        access_token = create_access_token(identity=user['id'])
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'nome': user['nome'],
                'role': user['role'],
                'unidade_id': user['unidade_id'],
                'unidade_nome': user['unidade_nome']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

# ROTA DE HEALTH CHECK
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if get_db_connection() else 'disconnected'
    }), 200

# ROTA RAIZ
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Sistema de Gestão de Indicadores Hospitalares API',
        'version': '1.0.0',
        'status': 'running'
    }), 200

if __name__ == '__main__':
    # Inicializar banco
    if DATABASE_URL:
        init_database()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )