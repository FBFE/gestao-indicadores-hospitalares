"""
Script Flask para gerenciar o banco de dados
"""
import os
import sys
from flask import Flask
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.database import config
from models import db, Usuario, Unidade, Indicador, Lancamento

def create_app():
    """Criar aplicação Flask para gerenciamento do banco"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    return app

def init_database():
    """Inicializar banco de dados com Flask-SQLAlchemy"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Criando tabelas...")
            db.create_all()
            print("Tabelas criadas com sucesso!")
            
            # Verificar se dados já existem
            if Unidade.query.first():
                print("Dados já existem no banco. Skipping população inicial.")
                return True
            
            print("Populando dados iniciais...")
            
            # Criar unidades
            unidades_data = [
                ('UTI Geral', 'UTI_GERAL'),
                ('UTI Coronariana', 'UTI_CORONARIANA'),
                ('UTI Pediátrica', 'UTI_PEDIATRICA'),
                ('UTI Neonatal', 'UTI_NEONATAL'),
                ('Centro Cirúrgico', 'CENTRO_CIRURGICO'),
                ('Emergência', 'EMERGENCIA'),
                ('Pronto Socorro', 'PRONTO_SOCORRO'),
                ('Internação Clínica', 'INTERNACAO_CLINICA'),
                ('Internação Cirúrgica', 'INTERNACAO_CIRURGICA'),
                ('Pediatria', 'PEDIATRIA'),
                ('Maternidade', 'MATERNIDADE'),
                ('Ambulatório', 'AMBULATORIO')
            ]
            
            for nome, codigo in unidades_data:
                unidade = Unidade(nome=nome, codigo=codigo)
                db.session.add(unidade)
            
            # Criar indicadores
            indicadores_data = [
                ('Taxa de Ocupação', 'Percentual de ocupação de leitos', 'produtividade', 'percentual', 85.00),
                ('Tempo Médio de Permanência', 'Tempo médio de permanência em dias', 'eficiencia', 'dias', 7.00),
                ('Taxa de Mortalidade', 'Taxa de mortalidade hospitalar', 'qualidade', 'percentual', 2.00),
                ('Taxa de Infecção Hospitalar', 'Taxa de infecção hospitalar', 'seguranca', 'percentual', 5.00),
                ('Satisfação do Paciente', 'Índice de satisfação do paciente', 'qualidade', 'nota', 8.50),
                ('Rotatividade de Leitos', 'Número de vezes que o leito foi ocupado', 'produtividade', 'numero', 3.00),
                ('Taxa de Reinternação', 'Taxa de reinternação em 30 dias', 'qualidade', 'percentual', 10.00),
                ('Cancelamento de Cirurgias', 'Taxa de cancelamento de cirurgias', 'eficiencia', 'percentual', 5.00),
                ('Tempo de Espera Emergência', 'Tempo médio de espera na emergência', 'eficiencia', 'minutos', 60.00),
                ('Adesão à Higienização', 'Taxa de adesão à higienização das mãos', 'seguranca', 'percentual', 95.00)
            ]
            
            for nome, descricao, tipo, unidade_medida, meta in indicadores_data:
                indicador = Indicador(
                    nome=nome,
                    descricao=descricao,
                    tipo=tipo,
                    unidade_medida=unidade_medida,
                    meta_mensal=meta
                )
                db.session.add(indicador)
            
            # Commit unidades e indicadores primeiro
            db.session.commit()
            
            # Criar usuário administrador
            uti_geral = Unidade.query.filter_by(codigo='UTI_GERAL').first()
            admin_user = Usuario(
                nome='Administrador',
                email='admin@hospital.com',
                role='admin',
                unidade_id=uti_geral.id
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            # Criar usuário gestor
            gestor_user = Usuario(
                nome='Gestor Teste',
                email='gestor@hospital.com',
                role='gestor',
                unidade_id=uti_geral.id
            )
            gestor_user.set_password('gestor123')
            db.session.add(gestor_user)
            
            # Criar usuário operador
            operador_user = Usuario(
                nome='Operador Teste',
                email='operador@hospital.com',
                role='operador',
                unidade_id=uti_geral.id
            )
            operador_user.set_password('operador123')
            db.session.add(operador_user)
            
            db.session.commit()
            
            print("Dados iniciais criados com sucesso!")
            print("\nUsuários criados:")
            print("- admin@hospital.com (senha: admin123) - Role: admin")
            print("- gestor@hospital.com (senha: gestor123) - Role: gestor")
            print("- operador@hospital.com (senha: operador123) - Role: operador")
            
            return True
            
        except Exception as e:
            print(f"Erro ao inicializar banco: {str(e)}")
            db.session.rollback()
            return False

def reset_database():
    """Resetar banco de dados"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Removendo todas as tabelas...")
            db.drop_all()
            print("Tabelas removidas!")
            
            print("Recriando banco...")
            return init_database()
            
        except Exception as e:
            print(f"Erro ao resetar banco: {str(e)}")
            return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciar banco de dados')
    parser.add_argument('--reset', action='store_true', help='Resetar banco de dados')
    
    args = parser.parse_args()
    
    if args.reset:
        if reset_database():
            print("Banco resetado com sucesso!")
        else:
            sys.exit(1)
    else:
        if init_database():
            print("Inicialização concluída com sucesso!")
        else:
            sys.exit(1)