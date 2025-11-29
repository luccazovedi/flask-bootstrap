"""Script para criar o banco de dados no PythonAnywhere.

Execute no console Bash do PythonAnywhere:
    cd ~/flask-bootstrap
    python scripts/create_db.py

Edite USERNAME abaixo com seu usuário do PythonAnywhere.
"""
import os
import sys

# Usuário do PythonAnywhere
USERNAME = 'zovedi'  # Exemplo: se sua URL é 'seunome.pythonanywhere.com', use 'seunome'

PROJECT_ROOT = f'/home/{USERNAME}/flask-bootstrap'
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

try:
    from flasky import create_app
    from flasky.app import db
    from flasky.app.models import Discipline
except Exception as e:
    print("❌ Erro ao importar módulos do flasky:")
    print(f"   {e}")
    print("\n💡 Verifique:")
    print("   1. Virtualenv ativado")
    print("   2. Dependências instaladas (pip install -r flasky/requirements.txt)")
    print(f"   3. USERNAME correto (atual: '{USERNAME}')")
    sys.exit(1)


def main():
    print("🚀 Criando banco de dados...")
    print(f"📁 Projeto: {PROJECT_ROOT}")

    app = create_app('flasky.config.ProductionConfig')
    print(f"📊 URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    with app.app_context():
        # db.drop_all()  # Descomente se quiser limpar tudo (cuidado)
        db.create_all()
        print("✅ Tabelas criadas.")

        try:
            disc_count = Discipline.query.count()
            print(f"📚 Disciplinas existentes: {disc_count}")
        except Exception as e:
            print(f"⚠️ Aviso ao consultar Discipline: {e}")

        print("\n🎉 Banco pronto.")
        print("Próximos passos:")
        print(" 1. Configure variáveis de ambiente")
        print(" 2. Ajuste o WSGI se necessário")
        print(" 3. Reload no painel Web")


if __name__ == '__main__':
    main()
