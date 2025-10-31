import sqlite3
import os

# Verificar se o banco existe
db_path = 'instance/gestao_indicadores.db'
if os.path.exists(db_path):
    print(f'📁 Banco encontrado em: {os.path.abspath(db_path)}')
    
    # Conectar e verificar tabelas
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Listar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('📋 Tabelas no banco:', [t[0] for t in tables])
    
    # Verificar dados em cada tabela
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f'📊 {table_name}: {count} registros')
        
        if table_name == 'users' and count > 0:
            cursor.execute("SELECT id, email, role FROM users LIMIT 5;")
            users = cursor.fetchall()
            print('👥 Usuários:')
            for user in users:
                print(f'   - ID: {user[0]}, Email: {user[1]}, Role: {user[2]}')
    
    conn.close()
else:
    print('❌ Banco não encontrado!')
    print('📁 Diretório atual:', os.getcwd())
    print('📄 Arquivos:', os.listdir('.'))