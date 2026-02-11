from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite CORS para integração com front-end
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arena_louzada.db'
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Mude para produção
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Modelos
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
    dias_aula = db.Column(db.Text)  # JSON
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

class Comanda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    itens = db.Column(db.Text, default='[]')  # JSON
    total = db.Column(db.Float, default=0.0)
    data_criacao = db.Column(db.Date, default=datetime.utcnow().date)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    cliente = db.Column(db.String(100))
    total = db.Column(db.Float, nullable=False)
    itens = db.Column(db.Text)  # JSON

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
    alunos = db.Column(db.Text)  # JSON

# Rotas de Autenticação
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify(access_token=access_token, role=user.role), 200
    return jsonify({'error': 'Credenciais inválidas'}), 401

# Rotas para Alunos
@app.route('/alunos', methods=['GET'])
@jwt_required()
def get_alunos():
    alunos = Aluno.query.all()
    return jsonify([{
        'matricula': a.matricula, 'nome': a.nome, 'status': a.status,
        'proximo_pagamento': str(a.proximo_pagamento) if a.proximo_pagamento else None
    } for a in alunos])

@app.route('/alunos', methods=['POST'])
@jwt_required()
def create_aluno():
    data = request.get_json()
    matricula = f"{datetime.now().year}{datetime.now().strftime('%m%d%H%M%S')}"
    aluno = Aluno(
        matricula=matricula, nome=data['nome'], cpf=data['cpf'],
        nascimento=datetime.strptime(data['nascimento'], '%Y-%m-%d').date(),
        celular=data['celular'], email=data['email'], plano=data['plano'],
        data_inicio=datetime.strptime(data['data_inicio'], '%Y-%m-%d').date(),
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

# Rotas para Vendas (Produtos, Comandas, Histórico)
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

@app.route('/comandas', methods=['GET'])
@jwt_required()
def get_comandas():
    comandas = Comanda.query.all()
    return jsonify([{'id': c.id, 'cliente_nome': c.cliente_nome, 'itens': json.loads(c.itens), 'total': c.total} for c in comandas])

@app.route('/comandas', methods=['POST'])
@jwt_required()
def create_comanda():
    data = request.get_json()
    comanda = Comanda(cliente_nome=data['cliente_nome'], itens=json.dumps(data.get('itens', [])))
    db.session.add(comanda)
    db.session.commit()
    return jsonify({'id': comanda.id}), 201

@app.route('/vendas', methods=['POST'])
@jwt_required()
def create_venda():
    data = request.get_json()
    venda = Venda(data=datetime.strptime(data['data'], '%Y-%m-%d').date(),
                  cliente=data.get('cliente'), total=data['total'], itens=json.dumps(data['itens']))
    db.session.add(venda)
    db.session.commit()
    return jsonify({'id': venda.id}), 201

# Rotas para Presenças
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

# Rotas para Aulas
@app.route('/aulas', methods=['GET'])
@jwt_required()
def get_aulas():
    data = request.args.get('data')
    aulas = Aula.query.filter_by(data=datetime.strptime(data, '%Y-%m-%d').date()).all()
    return jsonify([{'id': a.id, 'professor': a.professor, 'duracao': a.duracao, 'alunos': json.loads(a.alunos)} for a in aulas])

@app.route('/aulas', methods=['POST'])
@jwt_required()
def create_aula():
    data = request.get_json()
    aula = Aula(data=datetime.strptime(data['data'], '%Y-%m-%d').date(),
                professor=data['professor'], duracao=data['duracao'], alunos=json.dumps(data['alunos']))
    db.session.add(aula)
    db.session.commit()
    return jsonify({'id': aula.id}), 201

# Inicialização
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criar admin se não existir
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=generate_password_hash('admin'), role='CEO')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
