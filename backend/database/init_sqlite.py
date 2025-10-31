"""
Script simples para inicializar o banco usando SQLite como fallback
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask
from datetime import datetime
import bcrypt

# Configuração simples com SQLite como fallback
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestao_indicadores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar e configurar modelos
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
db.init_app(app)

# Definir modelos diretamente aqui para simplicidade
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

def init_database():
    """Inicializar banco de dados"""
    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        
        # Verificar se dados já existem
        if Unidade.query.first():
            print("Dados já existem no banco.")
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
        
        db.session.commit()
        
        # Criar usuários
        uti_geral = Unidade.query.filter_by(codigo='UTI_GERAL').first()
        
        admin_user = Usuario(
            nome='Administrador',
            email='admin@hospital.com',
            role='admin',
            unidade_id=uti_geral.id
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        gestor_user = Usuario(
            nome='Gestor Teste',
            email='gestor@hospital.com',
            role='gestor',
            unidade_id=uti_geral.id
        )
        gestor_user.set_password('gestor123')
        db.session.add(gestor_user)
        
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

if __name__ == '__main__':
    if init_database():
        print("Inicialização concluída com sucesso!")
    else:
        print("Erro na inicialização!")
        sys.exit(1)