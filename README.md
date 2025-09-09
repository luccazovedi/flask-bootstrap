# Flasky Bootstrap Project 🚀

[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3.2-orange)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/bootstrap-5.3-purple)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
---

## 🔹 Sobre o Projeto

Aplicação web de exemplo utilizando **Flask**, **Bootstrap** e **Flask-Moment**

Funcionalidades principais:
- Página inicial com **hora local dinâmica** (`Flask-Moment`)
- Página de usuário personalizada (`/user/<nome>`)
- Página de identificação (`/user/<nome>/<ra>/<instituicao>`)
- Página de formulário com validação (`Flask-WTF`)
- Página 404 personalizada para rotas inexistentes
- Layout responsivo com **Bootstrap**

O projeto pode ser rodado **localmente** ou feito deploy no **PythonAnywhere**.
---

## 📂 Estrutura do Projeto
bootstrap/
│── flaskbootstrap.py # Arquivo principal Flask

│── static/ # Arquivos estáticos (favicon, CSS, JS, imagens)

│── templates/ # Templates HTML

│ ├── base.html # Template base com navbar e Bootstrap

│ ├── index.html # Página inicial

│ ├── user.html # Página personalizada do usuário

│ ├── forms.html # Formulário com validação

│ ├── request.html # Informações da requisição

│ └── 404.html # Página de erro 404

└── README.md


---

## ⚙️ Dependências

- Flask
- Flask-Bootstrap
- Flask-WTF
- Flask-Moment
-
Instalação recomendada via **virtualenv**:

```bash
pip install flask flask-bootstrap flask-wtf flask-moment
```

## Rodando Localmente

Clone o projeto:

```bash
git clone https://github.com/luccazovedi/flask-bootstrap.git
```
```bash
cd bootstrap
```

## Execute o app:

```
python flaskbootstrap.py
```

Acesse: http://127.0.0.1:5000/

## Deploy:

O projeto também está disponível online em:
https://zovedi.pythonanywhere.com
