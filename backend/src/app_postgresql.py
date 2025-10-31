"""
Sistema de Gestão de Indicadores Hospitalares - Backend API
Versão com PostgreSQL e SQLAlchemy
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import logging
from functools import wraps

# Importar configurações e modelos
from config.database import config
from models import db, Usuario, Unidade, Indicador, Lancamento

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Carreguar configurações
    app.config.from_object(config[config_name])
    
    # Configurar extensões
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Configurar CORS
    CORS(app, supports_credentials=True, origins=app.config['CORS_ORIGINS'])
    
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

    @app.route('/api/indicadores', methods=['POST'])
    @role_required(['admin', 'gestor'])
    def create_indicador():
        """Criar novo indicador"""
        try:
            data = request.get_json()
            
            required_fields = ['nome', 'tipo']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'message': f'Campo {field} é obrigatório'}), 400
            
            indicador = Indicador(
                nome=data['nome'],
                descricao=data.get('descricao'),
                tipo=data['tipo'],
                unidade_medida=data.get('unidade_medida'),
                meta_mensal=data.get('meta_mensal')
            )
            
            db.session.add(indicador)
            db.session.commit()
            
            return jsonify({
                'indicador': indicador.to_dict(),
                'message': 'Indicador criado com sucesso'
            }), 201
            
        except Exception as e:
            logger.error(f"Erro ao criar indicador: {str(e)}")
            db.session.rollback()
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
            
            # Executar query com joins
            lancamentos = query.join(Indicador).join(Unidade).join(Usuario).all()
            
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

    @app.route('/api/lancamentos/<int:lancamento_id>', methods=['PUT'])
    @jwt_required()
    def update_lancamento(lancamento_id):
        """Atualizar lançamento"""
        try:
            current_user_id = get_jwt_identity()
            user = Usuario.query.get(current_user_id)
            
            if not user:
                return jsonify({'message': 'Usuário não encontrado'}), 404
            
            lancamento = Lancamento.query.get(lancamento_id)
            if not lancamento:
                return jsonify({'message': 'Lançamento não encontrado'}), 404
            
            # Verificar permissões
            if user.role == 'operador' and lancamento.usuario_id != user.id:
                return jsonify({'message': 'Acesso negado'}), 403
            
            if not user.can_access_unidade(lancamento.unidade_id):
                return jsonify({'message': 'Acesso negado à unidade'}), 403
            
            data = request.get_json()
            
            # Atualizar campos permitidos
            if 'valor' in data:
                lancamento.valor = data['valor']
            if 'observacoes' in data:
                lancamento.observacoes = data['observacoes']
            
            db.session.commit()
            
            return jsonify({
                'lancamento': lancamento.to_dict(),
                'message': 'Lançamento atualizado com sucesso'
            }), 200
            
        except Exception as e:
            logger.error(f"Erro ao atualizar lançamento: {str(e)}")
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

    return app

# Criar aplicação
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    with app.app_context():
        try:
            # Criar tabelas se não existirem
            db.create_all()
            logger.info("Tabelas criadas/verificadas")
            
            # Popular dados iniciais se necessário
            if not Usuario.query.first():
                from database.manage_db import init_database
                init_database()
                logger.info("Dados iniciais populados")
                
        except Exception as e:
            logger.error(f"Erro na inicialização do banco: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )