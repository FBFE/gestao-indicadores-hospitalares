"""
Script para inicializar o banco de dados PostgreSQL
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Criar banco de dados se não existir"""
    # Configurações do banco
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'gestao_indicadores')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    
    try:
        # Conectar ao PostgreSQL (banco padrão)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Verificar se banco existe
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Criando banco de dados: {DB_NAME}")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print("Banco de dados criado com sucesso!")
        else:
            print(f"Banco de dados {DB_NAME} já existe")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Erro ao criar banco de dados: {str(e)}")
        return False

def run_schema():
    """Executar script do schema"""
    # Configurações do banco
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'gestao_indicadores')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        cursor = conn.cursor()
        
        # Ler e executar schema
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("Executando schema do banco de dados...")
        cursor.execute(schema_sql)
        conn.commit()
        
        print("Schema executado com sucesso!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Erro ao executar schema: {str(e)}")
        return False

if __name__ == '__main__':
    print("Inicializando banco de dados PostgreSQL...")
    
    # Criar banco de dados
    if create_database():
        # Executar schema
        if run_schema():
            print("Inicialização concluída com sucesso!")
        else:
            sys.exit(1)
    else:
        sys.exit(1)