"""
Sistema de Gestão de Indicadores Hospitalares - Backend API
Desenvolvido em Flask para integração com Google Sheets e deployment no Netlify
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
import gspread
from google.oauth2.service_account import Credentials
from google.oauth2 import id_token
from google.auth.transport import requests
import traceback

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuração JWT
jwt = JWTManager(app)

# Configuração CORS
CORS(app, supports_credentials=True, origins=[
    'http://localhost:3000',
    'http://localhost:8080', 
    'https://*.netlify.app',
    'https://*.netlify.com'
])

# Configuração de sessão
Session(app)

# Configurações do Google Sheets
GOOGLE_SHEETS_CONFIG = {
    'SPREADSHEET_ID': os.environ.get('GOOGLE_SPREADSHEET_ID', '1RXm-9-K_1H8GZjvNjnhpBvNnDQCejDMkBUPEKF26Too'),
    'SCOPES': [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
}

# Configuração OAuth Google
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')

class GoogleSheetsManager:
    """Gerenciador de conexão com Google Sheets"""
    
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente Google Sheets"""
        try:
            # Obtém credenciais do ambiente
            credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            
            if credentials_json:
                # Parse das credenciais JSON
                credentials_data = json.loads(credentials_json)
                credentials = Credentials.from_service_account_info(
                    credentials_data,
                    scopes=GOOGLE_SHEETS_CONFIG['SCOPES']
                )
            else:
                # Fallback para arquivo de credenciais
                credentials_file = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
                if os.path.exists(credentials_file):
                    credentials = Credentials.from_service_account_file(
                        credentials_file,
                        scopes=GOOGLE_SHEETS_CONFIG['SCOPES']
                    )
                else:
                    raise Exception("Credenciais do Google não encontradas")
            
            # Inicializa cliente
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(GOOGLE_SHEETS_CONFIG['SPREADSHEET_ID'])
            
            logger.info("Cliente Google Sheets inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Google Sheets: {str(e)}")
            self.client = None
            self.spreadsheet = None
    
    def get_worksheet(self, sheet_name):
        """Obtém uma planilha específica"""
        try:
            if not self.spreadsheet:
                self._initialize_client()
            
            return self.spreadsheet.worksheet(sheet_name)
        except Exception as e:
            logger.error(f"Erro ao acessar planilha '{sheet_name}': {str(e)}")
            return None
    
    def get_all_records(self, sheet_name):
        """Obtém todos os registros de uma planilha"""
        try:
            worksheet = self.get_worksheet(sheet_name)
            if worksheet:
                return worksheet.get_all_records()
            return []
        except Exception as e:
            logger.error(f"Erro ao obter registros de '{sheet_name}': {str(e)}")
            return []
    
    def append_row(self, sheet_name, row_data):
        """Adiciona uma linha à planilha"""
        try:
            worksheet = self.get_worksheet(sheet_name)
            if worksheet:
                worksheet.append_row(row_data)
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao adicionar linha em '{sheet_name}': {str(e)}")
            return False
    
    def update_cell(self, sheet_name, row, col, value):
        """Atualiza uma célula específica"""
        try:
            worksheet = self.get_worksheet(sheet_name)
            if worksheet:
                worksheet.update_cell(row, col, value)
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar célula em '{sheet_name}': {str(e)}")
            return False

# Instância global do gerenciador
sheets_manager = GoogleSheetsManager()

def require_auth(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Autenticação necessária'}), 401
        return f(*args, **kwargs)
    return decorated_function

def handle_errors(f):
    """Decorator para tratamento de erros"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erro em {f.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': 'Erro interno do servidor',
                'message': str(e) if app.debug else 'Erro interno'
            }), 500
    return decorated_function

def auth_required(f):
    """Decorator para verificar autenticação JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verifica se tem token JWT
            current_user = get_jwt_identity()
            if not current_user:
                return jsonify({'message': 'Token de acesso necessário'}), 401
            
            # Busca dados do usuário
            usuarios = sheets_manager.get_all_records('Usuarios')
            user_data = None
            
            for usuario in usuarios:
                if usuario.get('Email', '').lower() == current_user.lower():
                    user_data = usuario
                    break
            
            if not user_data or user_data.get('Status', '').lower() != 'ativo':
                return jsonify({'message': 'Usuário inválido ou inativo'}), 401
            
            # Adiciona dados do usuário à request
            request.current_user = {
                'email': user_data['Email'],
                'nome': user_data['Nome'],
                'role': user_data.get('Role', 'operador'),
                'unidade': user_data.get('Unidade', '')
            }
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Erro na verificação de autenticação: {str(e)}")
            return jsonify({'message': 'Erro na verificação de autenticação'}), 401
    
    return decorated_function

def role_required(required_role):
    """Decorator para verificar autorização por role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'message': 'Autenticação necessária'}), 401
            
            user_role = request.current_user.get('role')
            
            # Hierarquia de roles
            role_hierarchy = {
                'operador': 1,
                'gestor': 2,
                'admin': 3
            }
            
            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(required_role, 999)
            
            if user_level < required_level:
                return jsonify({'message': 'Permissão insuficiente'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def unit_access_required(f):
    """Decorator para verificar acesso por unidade"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'message': 'Autenticação necessária'}), 401
        
        user_role = request.current_user.get('role')
        user_unit = request.current_user.get('unidade')
        
        # Gestores e admins acessam tudo
        if user_role in ['gestor', 'admin']:
            return f(*args, **kwargs)
        
        # Para operadores, verificar se a unidade solicitada é a dele
        requested_unit = request.args.get('unidade') or request.json.get('unidade') if request.json else None
        
        if requested_unit and requested_unit != user_unit:
            return jsonify({'message': 'Acesso negado à unidade'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

# ========================================
# ROTAS DE AUTENTICAÇÃO
# ========================================

@app.route('/api/auth/google', methods=['POST'])
@handle_errors
def google_auth():
    """Autenticação via Google OAuth"""
    try:
        token = request.json.get('token')
        
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 400
        
        # Verifica o token Google
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID)
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Token inválido')
        
        user_email = idinfo['email']
        user_name = idinfo['name']
        
        # Busca o usuário na planilha
        usuarios = sheets_manager.get_all_records('Usuarios')
        user_profile = None
        
        for usuario in usuarios:
            if usuario.get('Email', '').lower() == user_email.lower():
                user_profile = {
                    'email': usuario['Email'],
                    'nome': usuario['Nome'],
                    'perfil': usuario['Perfil']
                }
                break
        
        if not user_profile:
            # Usuário não cadastrado
            user_profile = {
                'email': user_email,
                'nome': user_name,
                'perfil': 'visualizador'  # Perfil padrão
            }
        
        # Cria sessão
        session['user_id'] = user_email
        session['user_profile'] = user_profile
        
        logger.info(f"Usuário autenticado: {user_email}")
        
        return jsonify({
            'success': True,
            'user': user_profile
        })
        
    except ValueError as e:
        logger.error(f"Erro de validação do token: {str(e)}")
        return jsonify({'error': 'Token inválido'}), 401
    except Exception as e:
        logger.error(f"Erro na autenticação Google: {str(e)}")
        return jsonify({'error': 'Erro na autenticação'}), 500

@app.route('/api/auth/profile', methods=['GET'])
@handle_errors
def get_profile():
    """Obtém o perfil do usuário atual"""
    user_profile = session.get('user_profile')
    
    if not user_profile:
        return jsonify({
            'email': None,
            'nome': 'Visitante',
            'perfil': 'none'
        })
    
    return jsonify(user_profile)

@app.route('/api/auth/logout', methods=['POST'])
@handle_errors
def logout():
    """Logout do usuário"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/register', methods=['POST'])
@handle_errors
def register():
    """Cadastro de novo usuário"""
    try:
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        required_fields = ['nome', 'email', 'password', 'unidade']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        email = data['email'].lower().strip()
        nome = data['nome'].strip()
        password = data['password']
        unidade = data['unidade']
        coren = data.get('coren', '').strip()
        role = 'operador'  # Padrão para novos usuários
        
        # Validação de email
        if '@' not in email or '.' not in email:
            return jsonify({'message': 'Email inválido'}), 400
        
        # Validação de senha
        if len(password) < 6:
            return jsonify({'message': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        # Verificar se usuário já existe
        usuarios = sheets_manager.get_all_records('Usuarios')
        for usuario in usuarios:
            if usuario.get('Email', '').lower() == email:
                return jsonify({'message': 'Email já cadastrado'}), 409
        
        # Hash da senha
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Preparar dados para inserção
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        usuario_data = [
            email,
            nome,
            password_hash,
            role,
            unidade,
            coren,
            timestamp,
            'Ativo'
        ]
        
        # Inserir no Google Sheets
        success = sheets_manager.append_row('Usuarios', usuario_data)
        
        if success:
            logger.info(f"Usuário cadastrado: {email}")
            return jsonify({
                'message': 'Usuário cadastrado com sucesso',
                'user': {
                    'email': email,
                    'nome': nome,
                    'role': role,
                    'unidade': unidade
                }
            }), 201
        else:
            return jsonify({'message': 'Erro ao salvar usuário'}), 500
            
    except Exception as e:
        logger.error(f"Erro no cadastro: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@app.route('/api/auth/login', methods=['POST'])
@handle_errors
def login():
    """Login de usuário"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário
        usuarios = sheets_manager.get_all_records('Usuarios')
        user_data = None
        
        for usuario in usuarios:
            if usuario.get('Email', '').lower() == email:
                user_data = usuario
                break
        
        if not user_data:
            return jsonify({'message': 'Email ou senha incorretos'}), 401
        
        # Verificar senha
        stored_password = user_data.get('Password', '')
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({'message': 'Email ou senha incorretos'}), 401
        
        # Verificar se usuário está ativo
        if user_data.get('Status', '').lower() != 'ativo':
            return jsonify({'message': 'Usuário inativo'}), 401
        
        # Criar perfil do usuário
        user_profile = {
            'email': user_data['Email'],
            'nome': user_data['Nome'],
            'role': user_data.get('Role', 'operador'),
            'unidade': user_data.get('Unidade', ''),
            'coren': user_data.get('COREN', '')
        }
        
        # Criar token JWT
        token = create_access_token(identity=email)
        
        logger.info(f"Login realizado: {email}")
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': token,
            'user': user_profile
        })
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

# ========================================
# ROTAS DE DADOS
# ========================================

@app.route('/api/unidades', methods=['GET'])
@handle_errors
def get_unidades():
    """Obtém lista de unidades hospitalares"""
    try:
        records = sheets_manager.get_all_records('Unidades')
        
        unidades = []
        for record in records:
            unidades.append({
                'id': str(record.get('ID', '')),
                'nome': record.get('Nome', ''),
                'foto_url': record.get('Foto_URL', '') or None
            })
        
        return jsonify(unidades)
        
    except Exception as e:
        logger.error(f"Erro ao buscar unidades: {str(e)}")
        return jsonify({'error': 'Erro ao buscar unidades'}), 500

@app.route('/api/unidades/<unidade_id>/foto', methods=['PUT'])
@require_auth
@handle_errors
def update_unidade_foto(unidade_id):
    """Atualiza a foto de uma unidade"""
    try:
        data = request.get_json()
        foto_url = data.get('foto_url', '')
        
        # Busca a unidade na planilha
        worksheet = sheets_manager.get_worksheet('Unidades')
        if not worksheet:
            return jsonify({'error': 'Planilha não encontrada'}), 500
        
        # Obtém todos os dados
        all_values = worksheet.get_all_values()
        
        # Procura pela unidade
        for i, row in enumerate(all_values[1:], start=2):  # Pula cabeçalho
            if row[0] == unidade_id:  # Coluna A = ID
                # Atualiza coluna C (foto_url)
                worksheet.update_cell(i, 3, foto_url)
                return jsonify({
                    'success': True,
                    'message': 'Foto da unidade atualizada com sucesso'
                })
        
        return jsonify({'error': 'Unidade não encontrada'}), 404
        
    except Exception as e:
        logger.error(f"Erro ao atualizar foto da unidade: {str(e)}")
        return jsonify({'error': 'Erro ao atualizar foto'}), 500

@app.route('/api/indicadores/dicionario', methods=['GET'])
@handle_errors
def get_indicadores_dicionario():
    """Obtém o dicionário de indicadores"""
    try:
        records = sheets_manager.get_all_records('Indicadores_Dicionario')
        
        indicadores = []
        for record in records:
            if record.get('Indicador'):  # Só adiciona se tem nome
                indicadores.append({
                    'nome': record.get('Indicador', ''),
                    'descricao': record.get('O que Mede', ''),
                    'label_numerador': record.get('Numerador', ''),
                    'label_denominador': record.get('Denominador', '')
                })
        
        return jsonify(indicadores)
        
    except Exception as e:
        logger.error(f"Erro ao buscar dicionário de indicadores: {str(e)}")
        return jsonify({'error': 'Erro ao buscar indicadores'}), 500

@app.route('/api/lancamentos', methods=['GET'])
@jwt_required()
@auth_required
@unit_access_required
@handle_errors
def get_lancamentos():
    """Obtém lançamentos com filtros"""
    try:
        # Parâmetros de filtro
        unidade = request.args.get('unidade')
        ano = request.args.get('ano')
        mes = request.args.get('mes')
        
        # Para operadores, filtrar apenas sua unidade
        user_role = request.current_user.get('role')
        user_unit = request.current_user.get('unidade')
        
        if user_role == 'operador':
            unidade = user_unit
        
        # Busca dados do dicionário
        dicionario_records = sheets_manager.get_all_records('Indicadores_Dicionario')
        mapa_indicadores = {}
        
        for record in dicionario_records:
            nome = record.get('Indicador')
            if nome:
                mapa_indicadores[nome] = {
                    'descricao': record.get('O que Mede', ''),
                    'num_label': record.get('Numerador', ''),
                    'den_label': record.get('Denominador', ''),
                    'formula': record.get('Fórmula', ''),
                    'meta': record.get('Meta', '')
                }
        
        # Busca lançamentos
        lancamentos_records = sheets_manager.get_all_records('Lancamentos')
        
        # Filtra lançamentos
        lancamentos_filtrados = []
        
        if unidade:
            # Filtro por unidade específica
            for record in lancamentos_records:
                match = True
                if ano and str(record.get('Ano', '')) != str(ano):
                    match = False
                if mes and str(record.get('Mes', '')) != str(mes):
                    match = False
                if str(record.get('ID_Unidade', '')) != str(unidade):
                    match = False
                
                if match:
                    lancamentos_filtrados.append(record)
        else:
            # Agregação para todas as unidades
            lancamentos_periodo = []
            for record in lancamentos_records:
                match = True
                if ano and str(record.get('Ano', '')) != str(ano):
                    match = False
                if mes and str(record.get('Mes', '')) != str(mes):
                    match = False
                
                if match:
                    lancamentos_periodo.append(record)
            
            # Agrega por indicador
            agregados = {}
            for record in lancamentos_periodo:
                nome = record.get('Indicador_Nome', '')
                if nome not in agregados:
                    agregados[nome] = {
                        'Indicador_Nome': nome,
                        'ID_Unidade': 'Média Geral',
                        'Mes': mes or 'N/A',
                        'Ano': ano or 'N/A',
                        'Valor_Numerador': 0,
                        'Valor_Denominador': 0
                    }
                
                agregados[nome]['Valor_Numerador'] += float(record.get('Valor_Numerador', 0) or 0)
                agregados[nome]['Valor_Denominador'] += float(record.get('Valor_Denominador', 0) or 0)
            
            lancamentos_filtrados = list(agregados.values())
        
        # Processa resultados
        resultado = []
        for lanc in lancamentos_filtrados:
            dic = mapa_indicadores.get(lanc.get('Indicador_Nome', ''), {})
            num = float(lanc.get('Valor_Numerador', 0) or 0)
            den = float(lanc.get('Valor_Denominador', 0) or 0)
            
            # Calcula resultado
            if den != 0:
                resultado_calc = (num / den) * 100
                resultado_str = f"{resultado_calc:.2f}"
            else:
                resultado_str = 'N/A'
            
            meta = dic.get('meta', 'N/A')
            
            # Define status (simplificado)
            status = 'gray'
            if meta == 'Zero' and resultado_str != 'N/A':
                status = 'green' if float(resultado_str) == 0 else 'red'
            
            resultado.append({
                **lanc,
                'resultado': resultado_str,
                'meta': meta,
                'status': status,
                'descricao': dic.get('descricao', 'N/A'),
                'num_label': dic.get('num_label', 'N/A'),
                'den_label': dic.get('den_label', 'N/A')
            })
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro ao buscar lançamentos: {str(e)}")
        return jsonify({'error': 'Erro ao buscar lançamentos'}), 500

@app.route('/api/lancamentos', methods=['POST'])
@jwt_required()
@auth_required
@handle_errors
def salvar_lancamentos():
    """Salva múltiplos lançamentos"""
    try:
        data = request.get_json()
        
        unidade = data.get('unidade')
        mes = data.get('mes')
        ano = data.get('ano')
        lancamentos = data.get('lancamentos', [])
        
        if not all([unidade, mes, ano]):
            return jsonify({'error': 'Dados obrigatórios não fornecidos'}), 400
        
        if not lancamentos:
            return jsonify({
                'success': False,
                'error': 'Nenhum indicador foi preenchido'
            })
        
        # Obtém informações do usuário
        user_email = session.get('user_id', '')
        timestamp = datetime.now().isoformat()
        
        # Prepara dados para inserção
        rows_to_append = []
        for lanc in lancamentos:
            row = [
                timestamp,
                user_email,
                unidade,
                lanc.get('indicador', ''),
                mes,
                ano,
                lanc.get('numerador', ''),
                lanc.get('denominador', '')
            ]
            rows_to_append.append(row)
        
        # Insere no Google Sheets
        worksheet = sheets_manager.get_worksheet('Lancamentos')
        if not worksheet:
            return jsonify({'error': 'Planilha não encontrada'}), 500
        
        # Adiciona todas as linhas
        for row in rows_to_append:
            worksheet.append_row(row)
        
        return jsonify({
            'success': True,
            'message': f'{len(rows_to_append)} indicadores salvos com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar lançamentos: {str(e)}")
        return jsonify({'error': 'Erro ao salvar lançamentos'}), 500

# ========================================
# ROTAS ADMINISTRATIVAS
# ========================================

@app.route('/api/admin/usuarios', methods=['GET'])
@require_auth
@handle_errors
def get_usuarios():
    """Obtém lista de usuários (apenas admins)"""
    user_profile = session.get('user_profile', {})
    
    if user_profile.get('perfil') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        usuarios = sheets_manager.get_all_records('Usuarios')
        return jsonify(usuarios)
    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {str(e)}")
        return jsonify({'error': 'Erro ao buscar usuários'}), 500

# ========================================
# ROTAS DE SAÚDE E UTILITÁRIOS
# ========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica saúde da API"""
    try:
        # Testa conexão com Google Sheets
        if sheets_manager.client:
            sheets_status = 'connected'
        else:
            sheets_status = 'disconnected'
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'google_sheets': sheets_status,
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Obtém configurações públicas"""
    return jsonify({
        'google_client_id': GOOGLE_CLIENT_ID,
        'version': '1.0.0',
        'features': {
            'google_auth': bool(GOOGLE_CLIENT_ID),
            'google_sheets': bool(sheets_manager.client)
        }
    })

# ========================================
# TRATAMENTO DE ERROS GLOBAIS
# ========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Método não permitido'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {str(error)}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

# ========================================
# INICIALIZAÇÃO
# ========================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando servidor na porta {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )