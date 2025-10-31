"""
Modelos SQLAlchemy para o sistema de Gestão de Indicadores Hospitalares
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Unidade(db.Model):
    """Modelo para unidades hospitalares"""
    __tablename__ = 'unidades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuarios = db.relationship('Usuario', backref='unidade', lazy='dynamic')
    lancamentos = db.relationship('Lancamento', backref='unidade', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
    
    def __repr__(self):
        return f'<Unidade {self.nome}>'

class Usuario(db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operador')
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    
    # Relacionamentos
    lancamentos = db.relationship('Lancamento', backref='usuario', lazy='dynamic')
    
    def set_password(self, password):
        """Define a senha do usuário (hash)"""
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, password)
    
    def can_access_unidade(self, unidade_id):
        """Verifica se o usuário pode acessar dados de uma unidade"""
        if self.role in ['admin', 'gestor']:
            return True
        return self.unidade_id == unidade_id
    
    def get_accessible_unidades(self):
        """Retorna as unidades que o usuário pode acessar"""
        if self.role in ['admin', 'gestor']:
            return Unidade.query.filter_by(ativo=True).all()
        return [self.unidade]
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'role': self.role,
            'unidade_id': self.unidade_id,
            'unidade_nome': self.unidade.nome if self.unidade else None,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None
        }
        if include_sensitive:
            data['senha_hash'] = self.senha_hash
        return data
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Indicador(db.Model):
    """Modelo para indicadores hospitalares"""
    __tablename__ = 'indicadores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50), nullable=False)
    unidade_medida = db.Column(db.String(50))
    meta_mensal = db.Column(db.Numeric(10, 2))
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    lancamentos = db.relationship('Lancamento', backref='indicador', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'unidade_medida': self.unidade_medida,
            'meta_mensal': float(self.meta_mensal) if self.meta_mensal else None,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
    
    def __repr__(self):
        return f'<Indicador {self.nome}>'

class Lancamento(db.Model):
    """Modelo para lançamentos de indicadores"""
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
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint única para evitar duplicatas
    __table_args__ = (
        db.UniqueConstraint('indicador_id', 'unidade_id', 'ano', 'mes', 
                          name='unique_lancamento_periodo'),
    )
    
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
            'observacoes': self.observacoes,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
    
    def __repr__(self):
        return f'<Lancamento {self.indicador.nome} - {self.ano}/{self.mes}>'