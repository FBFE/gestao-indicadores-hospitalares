"""
Sistema de Gestão de Indicadores Hospitalares - Backend TEMPORÁRIO SEM DB
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from datetime import datetime, timedelta
import os
import logging

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
CORS(app, supports_credentials=True, origins=True)

# Usuários mock (temporário)
USERS = {
    'admin@hospital.com': {
        'id': 1,
        'email': 'admin@hospital.com',
        'nome': 'Administrador',
        'senha': 'admin123',
        'role': 'admin'
    }
}

@app.route('/health')
def health():
    return {'status': 'ok', 'time': datetime.now().isoformat()}

@app.route('/')
def home():
    return {'message': 'Gestão Indicadores API - MODO TEMPORÁRIO SEM DB', 'status': 'running'}

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        logger.info(f"Login attempt: {data}")
        
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return {'message': 'Email e senha obrigatórios'}, 400
        
        # Verificar usuário mock
        user = USERS.get(email)
        if not user:
            return {'message': 'Usuário não encontrado'}, 401
        
        if user['senha'] != senha:
            return {'message': 'Senha incorreta'}, 401
        
        token = create_access_token(identity=user['id'])
        
        logger.info(f"Login successful for {email}")
        
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
        return {'message': f'Erro interno: {str(e)}'}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)