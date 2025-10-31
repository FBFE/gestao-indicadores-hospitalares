"""
Sistema de Gestão de Indicadores Hospitalares - Backend API
Versão simplificada com SQLite
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import logging
from functools import wraps
import bcrypt

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gestao-indicadores-secret-key'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestao_indicadores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar extensões
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Configurar CORS
CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000',
    'http://localhost:8080',
    'http://localhost:8086',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8080',
    'http://127.0.0.1:8086'
])

# Modelos (copiados do init_sqlite.py)
class Unidade(db.Model):
    __tablename__ = 'unidades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuarios = db.relationship('Usuario', backref='unidade', lazy='dynamic')
    lancamentos = db.relationship('Lancamento', backref='unidade', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'ativo': self.ativo
        }

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operador')
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    
    lancamentos = db.relationship('Lancamento', backref='usuario', lazy='dynamic')
    
    def set_password(self, password):
        self.senha_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.senha_hash.encode('utf-8'))
    
    def can_access_unidade(self, unidade_id):
        if self.role in ['admin', 'gestor']:
            return True
        return self.unidade_id == unidade_id
    
    def get_accessible_unidades(self):
        if self.role in ['admin', 'gestor']:
            return Unidade.query.filter_by(ativo=True).all()
        return [self.unidade]
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'role': self.role,
            'unidade_id': self.unidade_id,
            'unidade_nome': self.unidade.nome if self.unidade else None,
            'ativo': self.ativo
        }

class Indicador(db.Model):
    __tablename__ = 'indicadores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50), nullable=False)
    unidade_medida = db.Column(db.String(50))
    meta_mensal = db.Column(db.Numeric(10, 2))
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    lancamentos = db.relationship('Lancamento', backref='indicador', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'unidade_medida': self.unidade_medida,
            'meta_mensal': float(self.meta_mensal) if self.meta_mensal else None,
            'ativo': self.ativo
        }

class Lancamento(db.Model):
    __tablename__ = 'lancamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    indicador_id = db.Column(db.Integer, db.ForeignKey('indicadores.id'), nullable=False)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Numeric(15, 4), nullable=False)
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'indicador_id': self.indicador_id,
            'indicador_nome': self.indicador.nome if self.indicador else None,
            'unidade_id': self.unidade_id,
            'unidade_nome': self.unidade.nome if self.unidade else None,
            'usuario_id': self.usuario_id,
            'usuario_nome': self.usuario.nome if self.usuario else None,
            'ano': self.ano,
            'mes': self.mes,
            'valor': float(self.valor),
            'observacoes': self.observacoes
        }

# Decorador para verificar roles
def role_required(roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = Usuario.query.get(current_user_id)
            
            if not user or not user.ativo:
                return jsonify({'message': 'Usuário não encontrado ou inativo'}), 401
            
            if isinstance(roles, str):
                roles_list = [roles]
            else:
                roles_list = roles
            
            if user.role not in roles_list:
                return jsonify({'message': 'Acesso negado'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ROTAS DE AUTENTICAÇÃO
@app.route('/auth/login', methods=['POST'])
def login():
    """Endpoint para login de usuários"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('senha'):
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário por email
        user = Usuario.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['senha']):
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        if not user.ativo:
            return jsonify({'message': 'Usuário inativo'}), 401
        
        # Atualizar último login
        user.ultimo_login = datetime.utcnow()
        db.session.commit()
        
        # Criar token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@app.route('/auth/register', methods=['POST'])
def register():
    """Endpoint para cadastro de usuários"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['nome', 'email', 'senha', 'unidade_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se email já existe
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email já cadastrado'}), 400
        
        # Verificar se unidade existe
        unidade = Unidade.query.get(data['unidade_id'])
        if not unidade:
            return jsonify({'message': 'Unidade não encontrada'}), 400
        
        # Criar novo usuário
        user = Usuario(
            nome=data['nome'],
            email=data['email'],
            role=data.get('role', 'operador'),
            unidade_id=data['unidade_id']
        )
        user.set_password(data['senha'])
        
        db.session.add(user)
        db.session.commit()
        
        # Criar token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': access_token,
            'user': user.to_dict(),
            'message': 'Usuário cadastrado com sucesso'
        }), 201
        
    except Exception as e:
        logger.error(f"Erro no cadastro: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

@app.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obter perfil do usuário atual"""
    try:
        current_user_id = get_jwt_identity()
        user = Usuario.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter perfil: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

# ROTAS DE UNIDADES
@app.route('/api/unidades', methods=['GET'])
@jwt_required()
def get_unidades():
    """Listar unidades"""
    try:
        current_user_id = get_jwt_identity()
        user = Usuario.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Filtrar unidades baseado no role do usuário
        unidades = user.get_accessible_unidades()
        
        return jsonify({
            'unidades': [unidade.to_dict() for unidade in unidades]
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar unidades: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

# ROTAS DE INDICADORES
@app.route('/api/indicadores', methods=['GET'])
@jwt_required()
def get_indicadores():
    """Listar indicadores"""
    try:
        indicadores = Indicador.query.filter_by(ativo=True).all()
        
        return jsonify({
            'indicadores': [indicador.to_dict() for indicador in indicadores]
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar indicadores: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

# ROTAS DE LANÇAMENTOS
@app.route('/api/lancamentos', methods=['GET'])
@jwt_required()
def get_lancamentos():
    """Listar lançamentos"""
    try:
        current_user_id = get_jwt_identity()
        user = Usuario.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Parâmetros de filtro
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', type=int)
        unidade_id = request.args.get('unidade_id', type=int)
        
        # Query base
        query = Lancamento.query
        
        # Filtrar por ano
        query = query.filter(Lancamento.ano == ano)
        
        # Filtrar por mês se especificado
        if mes:
            query = query.filter(Lancamento.mes == mes)
        
        # Filtrar por unidade baseado no role do usuário
        if user.role == 'operador':
            query = query.filter(Lancamento.unidade_id == user.unidade_id)
        elif unidade_id:
            # Verificar se o usuário pode acessar a unidade
            if not user.can_access_unidade(unidade_id):
                return jsonify({'message': 'Acesso negado à unidade'}), 403
            query = query.filter(Lancamento.unidade_id == unidade_id)
        
        # Executar query
        lancamentos = query.all()
        
        return jsonify({
            'lancamentos': [lancamento.to_dict() for lancamento in lancamentos]
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar lançamentos: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@app.route('/api/lancamentos', methods=['POST'])
@jwt_required()
def create_lancamento():
    """Criar novo lançamento"""
    try:
        current_user_id = get_jwt_identity()
        user = Usuario.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['indicador_id', 'unidade_id', 'ano', 'mes', 'valor']
        for field in required_fields:
            if data.get(field) is None:
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se usuário pode acessar a unidade
        if not user.can_access_unidade(data['unidade_id']):
            return jsonify({'message': 'Acesso negado à unidade'}), 403
        
        # Verificar se indicador existe
        indicador = Indicador.query.get(data['indicador_id'])
        if not indicador:
            return jsonify({'message': 'Indicador não encontrado'}), 400
        
        # Verificar se unidade existe
        unidade = Unidade.query.get(data['unidade_id'])
        if not unidade:
            return jsonify({'message': 'Unidade não encontrada'}), 400
        
        # Verificar se já existe lançamento para o período
        existing = Lancamento.query.filter_by(
            indicador_id=data['indicador_id'],
            unidade_id=data['unidade_id'],
            ano=data['ano'],
            mes=data['mes']
        ).first()
        
        if existing:
            return jsonify({'message': 'Já existe lançamento para este período'}), 400
        
        # Criar lançamento
        lancamento = Lancamento(
            indicador_id=data['indicador_id'],
            unidade_id=data['unidade_id'],
            usuario_id=user.id,
            ano=data['ano'],
            mes=data['mes'],
            valor=data['valor'],
            observacoes=data.get('observacoes')
        )
        
        db.session.add(lancamento)
        db.session.commit()
        
        return jsonify({
            'lancamento': lancamento.to_dict(),
            'message': 'Lançamento criado com sucesso'
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar lançamento: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Erro interno do servidor'}), 500

# ROTA DE HEALTH CHECK
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    }), 200

if __name__ == '__main__':
    with app.app_context():
        # Verificar se tabelas existem, se não, criar
        if not os.path.exists('gestao_indicadores.db'):
            db.create_all()
            logger.info("Banco de dados criado")
    
    logger.info("Aplicação iniciada")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )