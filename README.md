# Flasky Bootstrap Project 🚀

[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3.2-orange)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🔹 Sobre o Projeto

Aplicação web de exemplo utilizando **Flask**, **Bootstrap** e **Flask-Moment**.  

Funcionalidades principais:
- Página inicial com **hora local dinâmica** (`Flask-Moment`)  
- Página de usuário personalizada (`/user/<nome>`)  
- Página 404 personalizada para rotas inexistentes  
- Layout responsivo com **Bootstrap**  

O projeto pode ser rodado **localmente** ou feito deploy no **PythonAnywhere**.

---

## 📂 Estrutura do Projeto
bootstrap/

│── flaskbootstrap.py # Arquivo principal Flask

│── static/ # Arquivos estáticos (favicon, CSS, JS)

│── templates/ # Templates HTML

│ ├── base.html # Template base com navbar e Bootstrap

│ ├── index.html # Página inicial

│ ├── user.html # Página personalizada do usuário

│ └── 404.html # Página de erro 404


---

## ⚙️ Dependências

- Flask  
- Flask-Bootstrap  
- Flask-Moment  

Instalação recomendada via **virtualenv**:

```bash
pip install flask flask-bootstrap flask-moment
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
