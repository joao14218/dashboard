# 🏐 Arena Louzada - Sistema de Gestão Esportiva

![Status](https://img.shields.io/badge/Status-Em%20Produção-success)
![Python](https://img.shields.io/badge/Backend-Python%20%7C%20Flask-blue)
![Frontend](https://img.shields.io/badge/Frontend-HTML%20%7C%20JS-orange)

Um sistema *Full-Stack* completo e seguro desenvolvido para a administração de uma arena de futevôlei. O sistema gerencia desde o cadastro de alunos e responsáveis até o controle financeiro de mensalidades, grade de horários e lista de presença.

## ✨ Funcionalidades Principais

* **Gestão de Alunos:** Cadastro completo com foto, dados pessoais e vinculação de responsáveis legais (para menores).
* **Painel Financeiro Integrado:** Controle automático de mensalidades e planos. Tags visuais indicam se o aluno está com o pagamento "Em dia", "Vencendo" ou "Vencido".
* **Módulo de Caixa:** Registro de recebimentos de mensalidades (Dinheiro, Cartões, Pix com geração de QR Code).
* **Grade de Aulas Inteligente:** Criação de turmas por dia/horário/professor com bloqueio automático de vagas (limite máximo de 16 alunos por turma).
* **Lista de Chamada em Tempo Real:** Tela otimizada para os professores realizarem a chamada na quadra, já visualizando o status de pagamento de cada aluno.
* **Busca de Alta Precisão:** Filtro inteligente em tempo real por nome ou matrícula.

## 🛠️ Tecnologias Utilizadas

**Backend (API Restful):**
* [Python 3](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/) (Microframework)
* **SQLAlchemy** (ORM) + **SQLite** (Banco de Dados)
* **Flask-JWT-Extended** (Autenticação baseada em Tokens)
* **Flask-CORS** (Controle de acesso à API)
* **python-dotenv** (Gestão de variáveis de ambiente e segurança)

**Frontend:**
* HTML5, CSS3 puro (Variáveis CSS, CSS Grid/Flexbox)
* JavaScript (Vanilla JS, Fetch API)
* [Phosphor Icons](https://phosphoricons.com/) (Ícones vetorizados)

**Hospedagem & Deploy:**
* Backend: [PythonAnywhere](https://www.pythonanywhere.com/)
* Frontend: [Netlify](https://www.netlify.com/)

## 🔒 Segurança e Arquitetura

O projeto adota boas práticas de segurança corporativa:
* **Autenticação JWT:** Senhas de usuários não transitam em texto plano. As rotas da API são protegidas por Tokens de acesso que expiram.
* **CORS Blindado:** Apenas o domínio oficial do frontend tem permissão de leitura e escrita no banco de dados.
* **Variáveis de Ambiente (.env):** Chaves de criptografia e segredos do servidor não são versionados no código fonte, prevenindo vazamentos de credenciais.

---

## 🚀 Como executar este projeto localmente

### Pré-requisitos
* Python 3.x instalado na máquina.
* Extensão *Live Server* no VS Code (ou servidor local similar) para rodar o Frontend.

### 1. Configurando o Backend
No terminal, clone o repositório e instale as dependências:

```bash
# Clone este repositório
git clone [https://github.com/joao14218/arena-louzada.git](https://github.com/SEU-USUARIO/arena-louzada.git)
cd arena-louzada

# Instale as bibliotecas necessárias
pip install flask flask-sqlalchemy flask-jwt-extended flask-cors python-dotenv
