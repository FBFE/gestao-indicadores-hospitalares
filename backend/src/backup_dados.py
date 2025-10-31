import sqlite3
import json
from datetime import datetime

def backup_database():
    """Faz backup dos dados do SQLite para JSON"""
    
    db_path = 'instance/gestao_indicadores.db'
    backup_data = {
        'backup_date': datetime.now().isoformat(),
        'database': 'gestao_indicadores',
        'tables': {}
    }
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    for table in tables:
        print(f'📋 Fazendo backup da tabela: {table}')
        
        # Obter estrutura da tabela
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Obter dados
        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        
        # Converter para dicionários
        table_data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            table_data.append(row_dict)
        
        backup_data['tables'][table] = {
            'columns': columns,
            'rows': table_data,
            'count': len(table_data)
        }
        
        print(f'   ✅ {len(table_data)} registros salvos')
    
    conn.close()
    
    # Salvar backup
    backup_filename = f'backup_dados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f'💾 Backup salvo em: {backup_filename}')
    return backup_filename

if __name__ == '__main__':
    backup_database()