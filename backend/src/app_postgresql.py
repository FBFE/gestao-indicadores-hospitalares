"""
Sistema de Gestão de Indicadores Hospitalares - Backend ULTRA SIMPLES
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import logging
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# JWT
jwt = JWTManager(app)

# CORS
CORS(app)

# Database
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def get_db():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return None

@app.route('/health')
def health():
    return {'status': 'ok', 'time': datetime.now().isoformat()}

@app.route('/')
def home():
    return {'message': 'Gestão Indicadores API', 'status': 'running'}

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return {'message': 'Email e senha obrigatórios'}, 400
        
        conn = get_db()
        if not conn:
            return {'message': 'Erro de conexão'}, 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND ativo = TRUE", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user:
            return {'message': 'Usuário não encontrado'}, 401
        
        if not bcrypt.checkpw(senha.encode(), user['senha_hash'].encode()):
            return {'message': 'Senha incorreta'}, 401
        
        token = create_access_token(identity=user['id'])
        
        return {
            'access_token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'nome': user['nome'],
                'role': user['role']
            }
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return {'message': 'Erro interno'}, 500

def init_db():
    conn = get_db()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # Tabelas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS unidades (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE,
                codigo VARCHAR(20) UNIQUE,
                ativo BOOLEAN DEFAULT TRUE
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) UNIQUE,
                nome VARCHAR(100),
                senha_hash VARCHAR(255),
                role VARCHAR(20) DEFAULT 'operador',
                unidade_id INTEGER REFERENCES unidades(id),
                ativo BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Dados iniciais
        cur.execute("SELECT COUNT(*) FROM usuarios")
        if cur.fetchone()[0] == 0:
            # Unidade
            cur.execute("INSERT INTO unidades (nome, codigo) VALUES ('UTI Geral', 'UTI01')")
            
            # Usuários
            senha = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
            
            cur.execute("""
                INSERT INTO usuarios (email, nome, senha_hash, role, unidade_id) 
                VALUES ('admin@hospital.com', 'Admin', %s, 'admin', 1)
            """, (senha,))
            
            logger.info("Dados iniciais criados!")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Init DB error: {e}")

if __name__ == '__main__':
    if DATABASE_URL:
        init_db()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)