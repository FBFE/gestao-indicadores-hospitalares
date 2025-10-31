"""
Configurações de ambiente para a aplicação Flask
"""

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env se existir
load_dotenv()

class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Google Sheets
    GOOGLE_SPREADSHEET_ID = os.environ.get('GOOGLE_SPREADSHEET_ID')
    GOOGLE_CREDENTIALS_JSON = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    GOOGLE_CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE')
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    
    # Flask
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Sessão
    SESSION_TYPE = 'redis' if os.environ.get('REDIS_URL') else 'filesystem'
    SESSION_REDIS = os.environ.get('REDIS_URL')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'sessions')
    
    # CORS
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:8080',
        'https://*.netlify.app',
        'https://*.netlify.com'
    ]
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    DEBUG = True

# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}