"""
Modelos SQLAlchemy para o sistema da Academia Amigo do Povo
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Date, Time, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Configuração do banco de dados
# Tentar carregar variáveis de ambiente primeiro
from dotenv import load_dotenv
load_dotenv()

# Configurar URL do banco de dados com fallback para SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    # Construir URL do PostgreSQL a partir das variáveis individuais
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'postgres')
    db_name = os.environ.get('DB_NAME', 'academia_amigo_povo')
    
    if all([db_host, db_port, db_user, db_password, db_name]):
        DATABASE_URL = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        # Fallback para SQLite se PostgreSQL não estiver configurado
        DATABASE_URL = 'sqlite:///academia_amigo_povo.db'
        print("⚠️  PostgreSQL não configurado, usando SQLite como fallback")

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

class Usuario(Base):
    """Modelo para usuários do sistema"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nome = Column(String(100), nullable=False)
    nivel = Column(String(20), nullable=False)
    permissoes = Column(String(500))  # JSON string for SQLite
    atividade_responsavel = Column(String(100))
    alunos_atribuidos = Column(String(500))  # JSON string for SQLite
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    criado_por = Column(String(50))
    ultimo_acesso = Column(DateTime)
    
    # Relacionamentos
    turmas_responsavel = relationship("Turma", back_populates="professor")
    presencas_registradas = relationship("Presenca", foreign_keys="Presenca.registrado_por")
    
    __table_args__ = (
        CheckConstraint("nivel IN ('admin_master', 'admin', 'usuario')", name='check_nivel_usuario'),
    )

class Atividade(Base):
    """Modelo para atividades da academia"""
    __tablename__ = "atividades"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    descricao = Column(Text)
    ativa = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    criado_por = Column(String(50))
    professores_vinculados = Column(String(500))  # JSON string for SQLite
    total_alunos = Column(Integer, default=0)
    
    # Relacionamentos
    turmas = relationship("Turma", back_populates="atividade")
    alunos = relationship("Aluno", back_populates="atividade")
    presencas = relationship("Presenca", back_populates="atividade")

class Turma(Base):
    """Modelo para turmas das atividades"""
    __tablename__ = "turmas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    atividade_id = Column(Integer, ForeignKey("atividades.id"), nullable=False)
    horario = Column(String(20), nullable=False)
    dias_semana = Column(String(100))
    periodo = Column(String(20))
    capacidade_maxima = Column(Integer, default=20)
    professor_responsavel = Column(Integer, ForeignKey("usuarios.id"))
    ativa = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    criado_por = Column(String(50))
    total_alunos = Column(Integer, default=0)
    descricao = Column(Text)
    
    # Relacionamentos
    atividade = relationship("Atividade", back_populates="turmas")
    professor = relationship("Usuario", back_populates="turmas_responsavel")
    alunos = relationship("Aluno", back_populates="turma")
    presencas = relationship("Presenca", back_populates="turma")

class Aluno(Base):
    """Modelo para alunos da academia"""
    __tablename__ = "alunos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    telefone = Column(String(20))
    endereco = Column(Text)
    email = Column(String(200))
    data_nascimento = Column(Date)
    data_cadastro = Column(Date, default=datetime.utcnow().date())
    atividade_id = Column(Integer, ForeignKey("atividades.id"))
    turma_id = Column(Integer, ForeignKey("turmas.id"))
    status_frequencia = Column(String(200))
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    criado_por = Column(String(50))
    
    # Relacionamentos
    atividade = relationship("Atividade", back_populates="alunos")
    turma = relationship("Turma", back_populates="alunos")
    presencas = relationship("Presenca", back_populates="aluno")

class Presenca(Base):
    """Modelo para registros de presença"""
    __tablename__ = "presencas"
    
    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    data_presenca = Column(Date, nullable=False, index=True)
    horario = Column(Time)
    turma_id = Column(Integer, ForeignKey("turmas.id"))
    atividade_id = Column(Integer, ForeignKey("atividades.id"))
    status = Column(String(10))  # P=Presente, F=Faltou, J=Justificado
    observacoes = Column(Text)
    tipo_registro = Column(String(20), default='MANUAL')
    data_registro = Column(DateTime, default=datetime.utcnow)
    registrado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    aluno = relationship("Aluno", back_populates="presencas")
    turma = relationship("Turma", back_populates="presencas")
    atividade = relationship("Atividade", back_populates="presencas")
    registrador = relationship("Usuario", foreign_keys=[registrado_por])
    
    __table_args__ = (
        CheckConstraint("status IN ('P', 'F', 'J')", name='check_status_presenca'),
    )

# Funções auxiliares para o banco de dados
def get_db():
    """Retorna uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)

def verificar_conexao():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Erro na conexão com o banco: {e}")
        return False

# Funções de consulta comuns
class AlunoDAO:
    """Data Access Object para operações com alunos"""
    
    @staticmethod
    def buscar_por_nome(db, nome):
        """Busca aluno por nome"""
        return db.query(Aluno).filter(Aluno.nome.ilike(f"%{nome}%")).all()
    
    @staticmethod
    def buscar_por_atividade(db, atividade_id):
        """Busca alunos por atividade"""
        return db.query(Aluno).filter(Aluno.atividade_id == atividade_id, Aluno.ativo == True).all()
    
    @staticmethod
    def buscar_por_turma(db, turma_id):
        """Busca alunos por turma"""
        return db.query(Aluno).filter(Aluno.turma_id == turma_id, Aluno.ativo == True).all()
    
    @staticmethod
    def calcular_frequencia(db, aluno_id, data_inicio=None, data_fim=None):
        """Calcula frequência de um aluno"""
        query = db.query(Presenca).filter(Presenca.aluno_id == aluno_id)
        
        if data_inicio:
            query = query.filter(Presenca.data_presenca >= data_inicio)
        if data_fim:
            query = query.filter(Presenca.data_presenca <= data_fim)
        
        presencas = query.all()
        total = len(presencas)
        presentes = len([p for p in presencas if p.status == 'P'])
        
        if total == 0:
            return 0
        
        return (presentes / total) * 100

class PresencaDAO:
    """Data Access Object para operações com presenças"""
    
    @staticmethod
    def registrar_presenca(db, aluno_id, data_presenca, status, turma_id=None, 
                          atividade_id=None, observacoes=None, registrado_por=None):
        """Registra uma nova presença"""
        presenca = Presenca(
            aluno_id=aluno_id,
            data_presenca=data_presenca,
            status=status,
            turma_id=turma_id,
            atividade_id=atividade_id,
            observacoes=observacoes,
            registrado_por=registrado_por
        )
        db.add(presenca)
        db.commit()
        db.refresh(presenca)
        return presenca
    
    @staticmethod
    def buscar_por_aluno(db, aluno_id, data_inicio=None, data_fim=None):
        """Busca presenças de um aluno"""
        query = db.query(Presenca).filter(Presenca.aluno_id == aluno_id)
        
        if data_inicio:
            query = query.filter(Presenca.data_presenca >= data_inicio)
        if data_fim:
            query = query.filter(Presenca.data_presenca <= data_fim)
        
        return query.order_by(Presenca.data_presenca.desc()).all()
    
    @staticmethod
    def buscar_por_turma_data(db, turma_id, data_presenca):
        """Busca presenças de uma turma em uma data específica"""
        return db.query(Presenca).filter(
            Presenca.turma_id == turma_id,
            Presenca.data_presenca == data_presenca
        ).all()

class AtividadeDAO:
    """Data Access Object para operações com atividades"""
    
    @staticmethod
    def listar_ativas(db):
        """Lista todas as atividades ativas"""
        return db.query(Atividade).filter(Atividade.ativa == True).all()
    
    @staticmethod
    def buscar_por_nome(db, nome):
        """Busca atividade por nome"""
        return db.query(Atividade).filter(Atividade.nome.ilike(f"%{nome}%")).first()
    
    @staticmethod
    def atualizar_total_alunos(db, atividade_id):
        """Atualiza o total de alunos de uma atividade"""
        total = db.query(Aluno).filter(
            Aluno.atividade_id == atividade_id,
            Aluno.ativo == True
        ).count()
        
        atividade = db.query(Atividade).filter(Atividade.id == atividade_id).first()
        if atividade:
            atividade.total_alunos = total
            db.commit()

class TurmaDAO:
    """Data Access Object para operações com turmas"""
    
    @staticmethod
    def listar_por_atividade(db, atividade_id):
        """Lista turmas de uma atividade"""
        return db.query(Turma).filter(
            Turma.atividade_id == atividade_id,
            Turma.ativa == True
        ).all()
    
    @staticmethod
    def atualizar_total_alunos(db, turma_id):
        """Atualiza o total de alunos de uma turma"""
        total = db.query(Aluno).filter(
            Aluno.turma_id == turma_id,
            Aluno.ativo == True
        ).count()
        
        turma = db.query(Turma).filter(Turma.id == turma_id).first()
        if turma:
            turma.total_alunos = total
            db.commit()

# Inicialização das tabelas
if __name__ == "__main__":
    print("Criando tabelas do banco de dados...")
    criar_tabelas()
    print("Tabelas criadas com sucesso!")
