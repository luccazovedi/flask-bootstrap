# Flasky Simplificado (Flask + Bootstrap)

Aplicação Flask enxuta para demonstração de:
- Layout base com Bootstrap
- Página inicial com hora dinâmica (Flask-Moment)
- Cadastro e listagem de disciplinas (SQLite via SQLAlchemy)
- Validação simples no backend
- Tabela interativa (filtro por nome em JavaScript)
- Tratamento de erro 404 com template dedicado

---

## Estrutura Atual do Projeto

```
flask-bootstrap/
├─ flasky/
│  ├─ app/
│  │  ├─ __init__.py        # factory e rotas / e /disciplina + handler 404
│  │  ├─ models.py          # modelo Discipline
│  │  ├─ templates/
│  │  │  ├─ base.html
│  │  │  ├─ index.html
│  │  │  ├─ disciplina.html
│  │  │  └─ 404.html
│  │  └─ static/            # (recursos estáticos se necessário)
│  ├─ config.py             # Configurações (SECRET_KEY etc.)
│  ├─ requirements.txt
├─ scripts/
│  └─ create_db.py          # Script opcional para criar o banco
└─ README.md
```

---

## Dependências Principais

Definidas em `flasky/requirements.txt`:
- Flask
- Flask-Bootstrap
- Flask-Moment
- Flask-SQLAlchemy
- python-dotenv

(O projeto não usa nesta versão: Flask-Login, Flask-Mail, Flask-WTF.)

---

## Executando Localmente (Windows PowerShell)

No diretório do projeto:

```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -r .\flasky\requirements.txt

# Define a aplicação para o Flask CLI
$env:FLASK_APP = 'flasky.flasky'
flask run
```

Acesse: http://127.0.0.1:5000

---

## Banco de Dados

O SQLite é criado automaticamente na primeira execução (se configurado em `config.py`). Para garantir manualmente:

```powershell
python -c "from flasky import create_app; from flasky.app import db; app=create_app();\nfrom flasky.app.models import Discipline;\n\nwith app.app_context(): db.create_all(); print('Banco OK')"
```

Script alternativo:

```powershell
python scripts/create_db.py
```

---

## Rotas Disponíveis

| Rota            | Método     | Descrição                                |
|-----------------|------------|------------------------------------------|
| `/`             | GET        | Página inicial com hora atual            |
| `/disciplina`   | GET/POST   | Formulário e listagem de disciplinas     |

Erro 404 qualquer rota inexistente → renderiza `404.html`.

---

## Cadastro de Disciplinas

Campos:
- Nome / Sigla (texto)
- Semestre (checkbox na interface porém tratado como seleção única)

Validações backend:
- Nome e semestre obrigatórios
- Semestre entre 1 e 6

Mensagem flash informa sucesso ou erro.

---

## Melhorias da Interface

- Navbar com links (alguns placeholders)
- Tabela responsiva com: índice, badge do semestre e filtro por nome
- Feedback imediato via mensagens flash

---

## Variáveis de Ambiente (.env opcional)

```
SECRET_KEY=uma-chave-secreta-segura
```

Se `SECRET_KEY` não for definida, usa-se um valor de desenvolvimento inseguro.

---

## Customização Rápida

- Adicionar novos campos à disciplina: editar `models.py` e ajustar o formulário/template.
- Adicionar novas rotas: incluir dentro de `create_app` em `__init__.py`.
- Trocar radios / selects: ajustar HTML em `disciplina.html`.

---

## Próximos Passos Sugeridos

1. Migrar checkbox de semestre para radio/select para evitar múltiplas seleções simultâneas.
2. Adicionar paginação na tabela de disciplinas.
3. Incluir testes automatizados para rota `/disciplina`.
4. Expandir para modelos (Curso, Professor, Aluno) conforme necessidade.

---

## Teste Rápido (Opcional)

```powershell
python - <<'PY'
from flasky import create_app
from flasky.app import db
from flasky.app.models import Discipline
app = create_app()
with app.app_context():
    db.create_all()
    db.session.add(Discipline(name='DSWA5', semester=5))
    db.session.commit()
    print([d.name for d in Discipline.query.all()])
PY
```

---

## Suporte

Se algo falhar:
1. Verifique mensagens no console.
2. Confirme virtualenv ativado.
3. Cheque `SECRET_KEY`.
4. Recrie o banco com `db.create_all()`.

---

## Licença

Uso educacional / demonstrativo.

---

Boa prática: mantenha este README alinhado às mudanças de código.
