# Flasky (Flask + Bootstrap) 🚀

Aplicação Flask modular com Bootstrap, formulários com Flask-WTF e envio de e-mails via Mailgun/SendGrid.

Principais recursos:
- Página inicial com hora local dinâmica (Flask-Moment)
- Rotas de usuário e identificação (`/user/<nome>`, `/user/<nome>/<institution>/<course>`)
- Formulários com validação (`/forms`, `Flask-WTF`)
- Login simples (`/login`)
- Cadastro de usuários e listagem por função (`/listausuario`)
- Cadastro com notificação por e-mail e histórico (`/cadastro`, `/emailsEnviados`)
- Tratamento de erro 404 com template dedicado

Compatível com execução local e deploy no PythonAnywhere.

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
│  ├─ __init__.py
│  ├─ email.py
│  └─ models.py
├─ migrations/
├─ tests/
│  ├─ __init__.py
│  └─ test_app.py
├─ venv/           # placeholder (não versione um venv real)
├─ requirements.txt
├─ config.py
└─ flasky.py       # cria a app via factory e roda em dev
```

---

## ⚙️ Dependências

As principais dependências estão em `flasky/requirements.txt`:
- Flask, Flask-Bootstrap, Flask-Moment, Flask-WTF, WTForms
- python-dotenv (carrega `.env`)
- requests (para Mailgun/SendGrid)
- email-validator (validação do campo e-mail)

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

## 🔐 Variáveis de ambiente (.env)

Crie um arquivo `.env` na raiz do projeto (mesmo nível do `flask run`) com, por exemplo:

```dotenv
# Segurança
SECRET_KEY=uma-chave-secreta-segura

# Mailgun (Sandbox ou domínio próprio)
MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=sandboxXXXX.mailgun.org
MAILGUN_FROM=Flasky <postmaster@sandboxXXXX.mailgun.org>

# E-mail institucional para notificação
INSTITUTIONAL_EMAIL=lucca.z@aluno.ifsp.edu.br

# (Opcional) SendGrid
# SENDGRID_API_KEY=...
# SENDGRID_FROM=noreply@yourdomain.com
```

Notas:
- Para Mailgun Sandbox, cadastre os destinatários de teste como “Authorized Recipients”.
- Não faça commit do `.env` (adicione ao `.gitignore`).

---

## ✉️ Envio de e-mails

- O cadastro (`/cadastro`) envia e-mails para:
  - Admin: `flaskaulasweb@zohomail.com`
  - Institucional: `INSTITUTIONAL_EMAIL`
  - E para o e-mail informado no formulário (se preenchido)
- O corpo inclui: Prontuário (se informado), Nome e o usuário cadastrado.
- A implementação tenta Mailgun; se não configurado, tenta SendGrid; caso nenhum esteja configurado, loga e segue.

---

## ✅ Testes

Há um teste simples em `flasky/tests/test_app.py`.

```powershell
./.venv/Scripts/Activate.ps1
python -m pip install pytest
python -m pytest flasky/tests -q
```

---

## ☁️ Deploy no PythonAnywhere (resumo)

1) Crie um Web app (Manual configuration) com a mesma versão do Python usada localmente.
2) No console Bash do PythonAnywhere:
	```bash
	cd ~
	git clone https://github.com/SEU_USUARIO/flask-bootstrap.git
	python3.11 -m venv ~/virtualenvs/flaskbootstrap
	source ~/virtualenvs/flaskbootstrap/bin/activate
	pip install -r ~/flask-bootstrap/flasky/requirements.txt
	```
3) Em Web > WSGI configuration file, use algo como:
	```python
	import sys, os
	project_home = '/home/SEU_USUARIO/flask-bootstrap'
	if project_home not in sys.path:
		 sys.path.insert(0, project_home)
	os.chdir(project_home)
	from flasky.flasky import app as application
	```
4) Em Web > Environment variables, configure as variáveis (SECRET_KEY, MAILGUN_*, INSTITUTIONAL_EMAIL...)
5) Em Web > Virtualenv, aponte para `/home/SEU_USUARIO/virtualenvs/flaskbootstrap`
6) Clique “Reload”.

---

## 🧠 Dicas

- `.env` nunca deve ser comitado. Considere manter um `.env.example` com placeholders.
- Para Mailgun Sandbox, autorize previamente todos os destinatários usados nos testes.
- Se preferir, podemos adicionar uma rota de teste de e-mail apenas para desenvolvimento.

---

## 📎 Licença

Uso educacional/demonstrativo. Adapte e inclua a licença de sua preferência (por exemplo, MIT) se for publicar.
