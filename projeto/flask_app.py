from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Carrega as variáveis de ambiente do arquivo invisível .env
load_dotenv()

app = Flask(__name__)

# CORS Blindado: Lembre-se de trocar "https://SEU-LINK-AQUI.netlify.app" pelo seu link real!
CORS(app, resources={r"/*": {"origins": ["https://SEU-LINK-AQUI.netlify.app", "http://localhost:5500"]}})

# Configurações de Banco de Dados e Segurança (A senha foi extraída do código fonte!)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/jaozinpagod/mysite/arena_louzada.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# --- MODELOS (TABELAS) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Aluno(db.Model):
    matricula = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nascimento = db.Column(db.Date, nullable=False)
    celular = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    # Dados do Responsável
    resp_nome = db.Column(db.String(100))
    resp_nascimento = db.Column(db.String(20))
    resp_telefone = db.Column(db.String(20))
    resp_email = db.Column(db.String(100))
    resp_endereco = db.Column(db.String(200))
    
    # Dados do Contrato e Múltiplas Turmas
    plano = db.Column(db.String(50), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    proximo_pagamento = db.Column(db.Date)
    dias_aula = db.Column(db.Text) 
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

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(20), nullable=False)
    professor = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.String(50))

class Plano(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    duracao = db.Column(db.Integer, default=1)

class Presenca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), db.ForeignKey('aluno.matricula'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    presente = db.Column(db.Boolean, default=True)

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
        'matricula': a.matricula, 'nome': a.nome, 
        'nascimento': str(a.nascimento) if a.nascimento else None, 'celular': a.celular,
        'email': a.email, 'plano': a.plano, 'data_inicio': str(a.data_inicio) if a.data_inicio else None,
        'proximo_pagamento': str(a.proximo_pagamento) if a.proximo_pagamento else None,
        'dias_aula': a.dias_aula, 'status': a.status, 'foto_url': a.foto_url,
        'resp_nome': a.resp_nome, 'resp_telefone': a.resp_telefone
    } for a in alunos])

@app.route('/alunos', methods=['POST'])
@jwt_required()
def create_aluno():
    data = request.get_json()
    matricula = f"{datetime.now().year}{datetime.now().strftime('%m%d%H%M%S')}"
    aluno = Aluno(
        matricula=matricula, nome=data['nome'],
        nascimento=datetime.strptime(data['nascimento'], '%Y-%m-%d').date(), celular=data.get('celular'),
        email=data.get('email'), plano=data['plano'], data_inicio=datetime.strptime(data['data_inicio'], '%Y-%m-%d').date(),
        proximo_pagamento=datetime.strptime(data['proximo_pagamento'], '%Y-%m-%d').date() if data.get('proximo_pagamento') else None,
        dias_aula=json.dumps(data.get('dias_aula', [])), foto_url=data.get('foto_url'),
        resp_nome=data.get('resp_nome'), resp_nascimento=data.get('resp_nascimento'),
        resp_telefone=data.get('resp_telefone'), resp_email=data.get('resp_email'), resp_endereco=data.get('resp_endereco')
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

@app.route('/planos', methods=['GET'])
@jwt_required()
def get_planos():
    return jsonify([{'id': p.id, 'nome': p.nome, 'valor': p.valor, 'duracao': p.duracao} for p in Plano.query.all()])

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

@app.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role} for u in User.query.all()])

@app.route('/usuarios', methods=['POST'])
@jwt_required()
def create_usuario():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first(): return jsonify({'error': 'Usuário já existe'}), 400
    new_user = User(username=data['username'], password_hash=generate_password_hash(data['password']), role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Criado'}), 201

@app.route('/usuarios/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    user = User.query.get_or_404(id)
    if user.role == 'CEO': return jsonify({'error': 'CEO não pode ser apagado'}), 403
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Removido'}), 200

@app.route('/grade', methods=['GET'])
@jwt_required()
def get_grade():
    return jsonify([{'id': g.id, 'dia': g.dia, 'hora': g.hora, 'professor': g.professor, 'nivel': g.nivel} for g in Grade.query.all()])

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
    return jsonify([{'id': v.id, 'data': str(v.data), 'cliente': v.cliente, 'total': v.total} for v in Venda.query.all()])

@app.route('/vendas', methods=['POST'])
@jwt_required()
def create_venda():
    data = request.get_json()
    venda = Venda(data=datetime.strptime(data['data'], '%Y-%m-%d').date(), cliente=data.get('cliente'), total=data['total'], itens=json.dumps(data['itens']))
    db.session.add(venda)
    db.session.commit()
    return jsonify({'id': venda.id}), 201

@app.route('/vendas/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_venda(id):
    venda = Venda.query.get_or_404(id)
    db.session.delete(venda)
    db.session.commit()
    return jsonify({'message': 'Venda estornada'}), 200

@app.route('/produtos', methods=['GET'])
@jwt_required()
def get_produtos():
    return jsonify([{'id': p.id, 'nome': p.nome, 'preco': p.preco, 'imagem': p.imagem, 'disponivel': p.disponivel} for p in Produto.query.all()])

@app.route('/produtos', methods=['POST'])
@jwt_required()
def create_produto():
    data = request.get_json()
    produto = Produto(nome=data['nome'], preco=data['preco'], imagem=data.get('imagem'))
    db.session.add(produto)
    db.session.commit()
    return jsonify({'id': produto.id}), 201

@app.route('/produtos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return jsonify({'message': 'Removido'}), 200

# --- ROTAS DE PRESENÇA BLINDADAS (UPSERT) ---
@app.route('/presencas', methods=['GET'])
@jwt_required()
def get_presencas():
    try:
        data = request.args.get('data')
        if not data:
            return jsonify([])
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        presencas = Presenca.query.filter_by(data=data_obj).all()
        return jsonify([{'matricula': p.matricula, 'presente': p.presente} for p in presencas])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/presencas', methods=['POST'])
@jwt_required()
def create_presenca():
    try:
        data = request.get_json()
        data_obj = datetime.strptime(data['data'], '%Y-%m-%d').date()
        
        # Lógica Upsert: Se a presença já existir, apenas atualiza. Se não, cria uma nova.
        presenca = Presenca.query.filter_by(matricula=data['matricula'], data=data_obj).first()
        if presenca:
            presenca.presente = data['presente']
        else:
            presenca = Presenca(matricula=data['matricula'], data=data_obj, presente=data['presente'])
            db.session.add(presenca)
            
        db.session.commit()
        return jsonify({'message': 'Presença gravada com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# INICIALIZAÇÃO E PADRÕES DO SISTEMA
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password_hash=generate_password_hash('admin'), role='CEO')
        db.session.add(admin)
    if not Plano.query.first():
        db.session.add(Plano(nome='Mensal Base', valor=100.0, duracao=1))
        db.session.add(Plano(nome='Trimestral', valor=250.0, duracao=3))
    db.session.commit()
