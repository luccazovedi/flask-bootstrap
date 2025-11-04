import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta')
    MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
    INSTITUTIONAL_EMAIL = os.getenv('INSTITUTIONAL_EMAIL', 'lucca.z@aluno.ifsp.edu.br')
