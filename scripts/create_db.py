"""Script para criar o banco de dados no PythonAnywhere.

Execute este script no console Bash do PythonAnywhere:
    cd ~/flask-bootstrap
    python scripts/create_db_pythonanywhere.py

IMPORTANTE: Edite a linha USERNAME abaixo com seu usuário do PythonAnywhere!
"""
import os
import sys

# ⚠️ EDITE AQUI: Coloque seu username do PythonAnywhere
USERNAME = 'zovedi'  # Exemplo: se sua URL é 'seunome.pythonanywhere.com', use 'seunome'

# Configuração do caminho do projeto
PROJECT_ROOT = f'/home/{USERNAME}/flask-bootstrap'

# Adiciona o projeto ao path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Muda para o diretório do projeto
os.chdir(PROJECT_ROOT)

try:
    from flasky import create_app
    from flasky.app import db
    from flasky.app.models import User, Role
except Exception as e:
    print(f"❌ Erro ao importar módulos do flasky:")
    print(f"   {e}")
    print(f"\n💡 Certifique-se de que:")
    print(f"   1. O virtualenv está ativado")
    print(f"   2. As dependências foram instaladas (pip install -r flasky/requirements.txt)")
    print(f"   3. O USERNAME está correto no script (atualmente: '{USERNAME}')")
    sys.exit(1)


def main():
    print("🚀 Iniciando criação do banco de dados...")
    print(f"📁 Diretório do projeto: {PROJECT_ROOT}")
    
    # Usa ProductionConfig para PythonAnywhere
    app = create_app('flasky.config.ProductionConfig')
    
    print(f"📊 Banco de dados: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    with app.app_context():
        # Remove todas as tabelas existentes (use com cuidado!)
        # db.drop_all()
        # print("⚠️  Tabelas antigas removidas")
        
        # Cria todas as tabelas
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
        # Verifica se as tabelas foram criadas
        try:
            user_count = User.query.count()
            role_count = Role.query.count()
            print(f"✅ Verificação: {user_count} usuário(s) e {role_count} role(s) no banco")
        except Exception as e:
            print(f"⚠️  Aviso ao verificar tabelas: {e}")
        
        print("\n🎉 Banco de dados configurado com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Configure as variáveis de ambiente no PythonAnywhere")
        print("   2. Configure o arquivo WSGI")
        print("   3. Clique em 'Reload' no painel Web")


if __name__ == '__main__':
    main()
