# Flasky (Flask + Bootstrap) 🚀

Aplicação Flask modular com Bootstrap, autenticação, formulários com Flask-WTF e opções de envio de e-mails (Mailgun/SMTP). Compatível com execução local (Windows) e deploy no PythonAnywhere.

Principais recursos:
- Página inicial com hora dinâmica (Flask-Moment)
- Rotas de usuário/identificação (`/user/<nome>`, `/user/<nome>/<institution>/<course>`)
- Formulários com validação (`/forms`)
- Autenticação (login/logout, confirmação de conta local, usuário não confirmado redireciona para `auth/unconfirmed`)
- Alterar senha e alterar e-mail (local – sem confirmação por e-mail)
- Cadastro de usuários com histórico de e-mails enviados (`/cadastro`, `/emailsEnviados`)
- Listagem de usuários persistidos (`/usuarios`) e confirmação manual por admin
- Tratamento de erro 404 com template dedicado

---

## 📂 Estrutura do Projeto (modular)

```
flasky/
├─ app/
│  ├─ templates/
│  ├─ static/
│  ├─ main/
│  │  ├─ __init__.py
│  │  ├─ errors.py
│  │  ├─ forms.py
│  │  └─ views.py
│  ├─ auth/
│  │  ├─ __init__.py
│  │  ├─ forms.py
│  │  └─ views.py
│  ├─ __init__.py
│  ├─ email.py
│  └─ models.py
├─ migrations/
├─ tests/
│  ├─ __init__.py
│  └─ test_app.py
├─ scripts/
│  └─ create_db.py
├─ requirements.txt
├─ config.py
└─ flasky.py
```

---

## ⚙️ Dependências

Definidas em `flasky/requirements.txt`:
- Flask, Flask-Bootstrap, Flask-Moment, Flask-WTF, WTForms
- Flask-Login, Flask-Mail (SMTP opcional)
- python-dotenv (carregar `.env` localmente)
- requests (Mailgun/integrações HTTP)
- email-validator (validação de e-mail)

---

## 🚀 Rodando localmente (Windows PowerShell)

No diretório do projeto:

```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -r .\flasky\requirements.txt

# Variável de app para o Flask CLI
$env:FLASK_APP = 'flasky.flasky'
flask run
```

Acesse: http://127.0.0.1:5000

---

## 🔐 Variáveis de Ambiente (.env)

Crie um `.env` na raiz do projeto (mesmo nível do `flask run`):

```dotenv
# Segurança
SECRET_KEY=uma-chave-secreta-segura

# E-mail (opcional)
MAILGUN_API_KEY=key-xxxxxxxx
MAILGUN_DOMAIN=sandboxXXXX.mailgun.org
API_FROM=Flasky <postmaster@sandboxXXXX.mailgun.org>
INSTITUTIONAL_EMAIL=seu.email@instituicao.com

# URL base para geração de links externos (deploy)
BASE_URL=https://SEU_USUARIO.pythonanywhere.com
PREFERRED_URL_SCHEME=https
```

Notas:
- Para Mailgun Sandbox, autorize os destinatários de teste (“Authorized Recipients”).
- Não faça commit do `.env` (adicione ao `.gitignore`).

---

## ✉️ Envio de E-mails (Opcional)

- O código tenta enviar via Mailgun se `MAILGUN_DOMAIN` e `MAILGUN_API_KEY` estiverem configurados.
- Se não houver provedor, a aplicação não quebra: registra nos logs e prossegue.
- A página de “conta não confirmada” possui botão de confirmação local (sem e-mail).
- Alteração de e-mail é aplicada localmente (sem confirmação por e-mail) quando logado.

---

## ✅ Testes

```powershell
./.venv/Scripts/Activate.ps1
python -m pip install pytest
python -m pytest flasky/tests -q
```

---

## ☁️ Deploy Completo no PythonAnywhere

### ⚠️ Problemas Comuns e Soluções

1) Banco de dados não criado → Crie conforme passos abaixo.
2) Configuração WSGI incorreta → Revise o WSGI conforme exemplo.
3) Variáveis de ambiente faltando → Configure em Web > Environment variables.
4) Virtualenv errado → Aponte para o caminho correto.

---

### 1) Clonar o Repositório (Console Bash)

```bash
cd ~
git clone https://github.com/luccazovedi/flask-bootstrap.git
cd flask-bootstrap
```

### 2) Criar o Ambiente Virtual

```bash
python3.13 -m venv ~/virtualenvs/flaskbootstrap
source ~/virtualenvs/flaskbootstrap/bin/activate
```

### 3) Instalar Dependências

```bash
cd ~/flask-bootstrap/flasky
pip install -r requirements.txt
```

### 4) IMPORTANTE: Criar o Banco de Dados

Opção A (script):
```bash
cd ~/flask-bootstrap
python scripts/create_db.py
```

Opção B (alternativa, se o script não existir):
```bash
python -c "
import sys
sys.path.insert(0, '/home/SEU_USUARIO/flask-bootstrap')
from flasky import create_app
from flasky.app import db

app = create_app('flasky.config.ProductionConfig')
with app.app_context():
    db.create_all()
    print('✅ Banco de dados criado com sucesso!')
"
```
Substitua `SEU_USUARIO` pelo seu username no PythonAnywhere.

### 5) Configurar o WSGI

Em Web > WSGI configuration file, use algo como:

```python
import sys
import os

# Caminho do projeto (mude SEU_USUARIO)
project_home = '/home/SEU_USUARIO/flask-bootstrap'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from flasky import create_app
from flasky.app import db

application = create_app('flasky.config.ProductionConfig')

# (Opcional) cria as tabelas na primeira carga
with application.app_context():
    db.create_all()
```

### 6) Configurar Variáveis de Ambiente

Em Web > Environment variables:

| Nome | Valor | Obrigatório |
|------|-------|-------------|
| `SECRET_KEY` | Uma string aleatória segura | ✅ |
| `DATABASE_URL` | `sqlite:////home/SEU_USUARIO/flask-bootstrap/flasky/data.sqlite` | ✅ |
| `MAILGUN_API_KEY` | Sua chave do Mailgun | Opcional |
| `MAILGUN_DOMAIN` | Seu domínio do Mailgun | Opcional |
| `API_FROM` | Remetente (ex: `noreply@seudominio.com`) | Opcional |
| `FLASKY_ADMIN` | Email de admin | Opcional |
| `INSTITUTIONAL_EMAIL` | Email institucional | Opcional |
| `BASE_URL` | `https://SEU_USUARIO.pythonanywhere.com` | Recomendado |
| `PREFERRED_URL_SCHEME` | `https` | Recomendado |

Gerar `SECRET_KEY` segura:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 7) Virtualenv

Em Web > Virtualenv, informe:
```
/home/SEU_USUARIO/virtualenvs/flaskbootstrap
```

### 8) Reload da Aplicação

Clique em “Reload SEU_USUARIO.pythonanywhere.com”.

---

## 🔍 Verificação Rápida

- Acesse `https://SEU_USUARIO.pythonanywhere.com/`
- Verifique logs: Web > Log files > Error log
- Teste de cadastro: `https://SEU_USUARIO.pythonanywhere.com/cadastro`

---

## 🐛 Debugging

1) Verifique os logs de erro (Web > Log files > Error log)
   - `ImportError`, `OperationalError`, `RuntimeError`
2) Teste o banco manualmente:

```bash
source ~/virtualenvs/flaskbootstrap/bin/activate
cd ~/flask-bootstrap
python
```

No Python interativo:
```python
import sys
sys.path.insert(0, '/home/SEU_USUARIO/flask-bootstrap')

from flasky import create_app
from flasky.app import db
from flasky.app.models import User

app = create_app('flasky.config.ProductionConfig')
with app.app_context():
    users = User.query.all()
    print(f"Usuários no banco: {len(users)}")
    db.create_all()
    print("✅ Banco verificado!")
```

3) Permissões de arquivo:
```bash
ls -la ~/flask-bootstrap/flasky/*.sqlite
chmod 664 ~/flask-bootstrap/flasky/*.sqlite
```

4) Verifique import do módulo:
```bash
source ~/virtualenvs/flaskbootstrap/bin/activate
cd ~/flask-bootstrap
python -c "from flasky import create_app; print('✅ Import OK')"
```

---

## 🔄 Atualizando o Código (PythonAnywhere)

```bash
cd ~/flask-bootstrap
git pull origin main
source ~/virtualenvs/flaskbootstrap/bin/activate
pip install -r flasky/requirements.txt
```

Depois, faça o “Reload”.

---

## ✅ Checklist Final

- [ ] Repositório clonado
- [ ] Virtualenv criado e ativado
- [ ] Dependências instaladas (`requirements.txt`)
- [ ] Banco de dados criado (`scripts/create_db.py` ou snippet)
- [ ] WSGI configurado corretamente
- [ ] Variáveis de ambiente configuradas (`SECRET_KEY`, `DATABASE_URL`, …)
- [ ] Virtualenv configurado no painel
- [ ] Aplicação recarregada (Reload)
- [ ] Testado acesso à página inicial
- [ ] Testado cadastro

---

## 📞 Ajuda

Se ainda houver erro:
1) Verifique o Error log
2) Informe o erro completo
3) Confirme as variáveis de ambiente
4) Confirme que o banco foi criado

Erro comum: “no such table: users” → execute a criação do banco (passo 4).
