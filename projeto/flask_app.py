from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/jaozinpagod/mysite/arena_louzada.db'
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# --- MODELOS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Aluno(db.Model):
    matricula = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    nascimento = db.Column(db.Date, nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    plano = db.Column(db.String(50), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    proximo_pagamento = db.Column(db.Date)
    dias_aula = db.Column(db.Text)
    professor = db.Column(db.String(100))
    horario_aula = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Ativo')
    foto_url = db.Column(db.Text)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.Text)
    disponivel = db.Column(db.Boolean, default=True)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    cliente = db.Column(db.String(100))
    total = db.Column(db.Float, nullable=False)
    itens = db.Column(db.Text)

class Presenca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), db.ForeignKey('aluno.matricula'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, default=True)

class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    professor = db.Column(db.String(100), nullable=False)
    duracao = db.Column(db.Float, nullable=False)
    alunos = db.Column(db.Text)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(20), nullable=False)
    professor = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.String(50))

# NOVA TABELA: PLANOS OFICIAIS
class Plano(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    duracao = db.Column(db.Integer, default=1)

# --- ROTAS DA API ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify(access_token=access_token, role=user.role), 200
    return jsonify({'error': 'Credenciais inválidas'}), 401

@app.route('/alunos', methods=['GET'])
@jwt_required()
def get_alunos():
    alunos = Aluno.query.all()
    return jsonify([{
        'matricula': a.matricula, 'nome': a.nome, 'cpf': a.cpf,
        'nascimento': str(a.nascimento) if a.nascimento else None, 'celular': a.celular,
        'email': a.email, 'plano': a.plano, 'data_inicio': str(a.data_inicio) if a.data_inicio else None,
        'proximo_pagamento': str(a.proximo_pagamento) if a.proximo_pagamento else None,
        'dias_aula': a.dias_aula, 'professor': a.professor, 'horario_aula': a.horario_aula,
        'status': a.status, 'foto_url': a.foto_url
    } for a in alunos])

@app.route('/alunos', methods=['POST'])
@jwt_required()
def create_aluno():
    data = request.get_json()
    matricula = f"{datetime.now().year}{datetime.now().strftime('%m%d%H%M%S')}"
    aluno = Aluno(
        matricula=matricula, nome=data['nome'], cpf=data['cpf'],
        nascimento=datetime.strptime(data['nascimento'], '%Y-%m-%d').date(), celular=data['celular'],
        email=data['email'], plano=data['plano'], data_inicio=datetime.strptime(data['data_inicio'], '%Y-%m-%d').date(),
        proximo_pagamento=datetime.strptime(data['proximo_pagamento'], '%Y-%m-%d').date() if data.get('proximo_pagamento') else None,
        dias_aula=json.dumps(data.get('dias_aula', [])), professor=data.get('professor'),
        horario_aula=data.get('horario_aula'), foto_url=data.get('foto_url')
    )
    db.session.add(aluno)
    db.session.commit()
    return jsonify({'matricula': matricula}), 201

@app.route('/alunos/<matricula>', methods=['PUT'])
@jwt_required()
def update_aluno(matricula):
    data = request.get_json()
    aluno = Aluno.query.get_or_404(matricula)
    for key, value in data.items():
        if key == 'dias_aula':
            setattr(aluno, key, json.dumps(value))
        elif key in ['proximo_pagamento', 'nascimento', 'data_inicio']:
            if value:
                setattr(aluno, key, datetime.strptime(value, '%Y-%m-%d').date())
        else:
            setattr(aluno, key, value)
    db.session.commit()
    return jsonify({'message': 'Atualizado'}), 200

@app.route('/alunos/<matricula>', methods=['DELETE'])
@jwt_required()
def delete_aluno(matricula):
    aluno = Aluno.query.get_or_404(matricula)
    db.session.delete(aluno)
    db.session.commit()
    return jsonify({'message': 'Removido'}), 200

# ROTAS PLANOS
@app.route('/planos', methods=['GET'])
@jwt_required()
def get_planos():
    planos = Plano.query.all()
    return jsonify([{'id': p.id, 'nome': p.nome, 'valor': p.valor, 'duracao': p.duracao} for p in planos])

@app.route('/planos', methods=['POST'])
@jwt_required()
def create_plano():
    data = request.get_json()
    plano = Plano(nome=data['nome'], valor=data['valor'], duracao=data.get('duracao', 1))
    db.session.add(plano)
    db.session.commit()
    return jsonify({'id': plano.id}), 201

@app.route('/planos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_plano(id):
    plano = Plano.query.get_or_404(id)
    db.session.delete(plano)
    db.session.commit()
    return jsonify({'message': 'Removido'}), 200

# ROTAS USUÁRIOS
@app.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    usuarios = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role} for u in usuarios])

@app.route('/usuarios', methods=['POST'])
@jwt_required()
def create_usuario():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Usuário já existe'}), 400
    new_user = User(username=data['username'], password_hash=generate_password_hash(data['password']), role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Criado'}), 201

@app.route('/usuarios/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    user = User.query.get_or_404(id)
    if user.role == 'CEO':
        return jsonify({'error': 'CEO não pode ser apagado'}), 403
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Removido'}), 200

# OUTRAS ROTAS (Grade, Vendas, Presenças, Produtos)
@app.route('/grade', methods=['GET'])
@jwt_required()
def get_grade():
    grades = Grade.query.all()
    return jsonify([{'id': g.id, 'dia': g.dia, 'hora': g.hora, 'professor': g.professor, 'nivel': g.nivel} for g in grades])

@app.route('/grade', methods=['POST'])
@jwt_required()
def create_grade():
    data = request.get_json()
    grade = Grade(dia=data['dia'], hora=data['hora'], professor=data['professor'], nivel=data.get('nivel', 'Geral'))
    db.session.add(grade)
    db.session.commit()
    return jsonify({'id': grade.id}), 201

@app.route('/grade/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_grade(id):
    grade = Grade.query.get_or_404(id)
    db.session.delete(grade)
    db.session.commit()
    return jsonify({'message': 'Removido'}), 200

@app.route('/vendas', methods=['GET'])
@jwt_required()
def get_vendas():
    vendas = Venda.query.all()
    return jsonify([{'id': v.id, 'data': str(v.data), 'cliente': v.cliente, 'total': v.total} for v in vendas])

@app.route('/vendas', methods=['POST'])
@jwt_required()
def create_venda():
    data = request.get_json()
    venda = Venda(data=datetime.strptime(data['data'], '%Y-%m-%d').date(), cliente=data.get('cliente'), total=data['total'], itens=json.dumps(data['itens']))
    db.session.add(venda)
    db.session.commit()
    return jsonify({'id': venda.id}), 201

@app.route('/presencas', methods=['GET'])
@jwt_required()
def get_presencas():
    data = request.args.get('data')
    presencas = Presenca.query.filter_by(data=datetime.strptime(data, '%Y-%m-%d').date()).all()
    return jsonify([{'matricula': p.matricula, 'presente': p.presente} for p in presencas])

@app.route('/presencas', methods=['POST'])
@jwt_required()
def create_presenca():
    data = request.get_json()
    presenca = Presenca(matricula=data['matricula'], data=datetime.strptime(data['data'], '%Y-%m-%d').date(), presente=data['presente'])
    db.session.add(presenca)
    db.session.commit()
    return jsonify({'message': 'Registrada'}), 201

@app.route('/produtos', methods=['GET'])
@jwt_required()
def get_produtos():
    produtos = Produto.query.all()
    return jsonify([{'id': p.id, 'nome': p.nome, 'preco': p.preco, 'imagem': p.imagem, 'disponivel': p.disponivel} for p in produtos])

@app.route('/produtos', methods=['POST'])
@jwt_required()
def create_produto():
    data = request.get_json()
    produto = Produto(nome=data['nome'], preco=data['preco'], imagem=data.get('imagem'))
    db.session.add(produto)
    db.session.commit()
    return jsonify({'id': produto.id}), 201

# Inicialização do Banco de Dados para a Nuvem
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password_hash=generate_password_hash('admin'), role='CEO')
        db.session.add(admin)
    # Cria planos padrão caso o banco esteja vazio
    if not Plano.query.first():
        db.session.add(Plano(nome='Mensal Base', valor=100.0, duracao=1))
        db.session.add(Plano(nome='Trimestral', valor=250.0, duracao=3))
    db.session.commit()
