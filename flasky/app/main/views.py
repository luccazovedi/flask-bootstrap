from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from datetime import datetime
from . import bp
from .forms import CadastroForm, NomeForm, LoginForm
from ..email import send_email

# in-memory data stores (kept for compatibility with the original app)
usuarios = [
    {"nome": "Lucca", "funcao": "Administrador"},
    {"nome": "Zovedi", "funcao": "User"},
    {"nome": "Lucca Zovedi", "funcao": "Moderador"},
]

usuarios_cadastrados = [
    {"nome": "Lucca", "funcao": "Administrador"}
]
emails_enviados = []


@bp.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@bp.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@bp.route('/user/<name>/<institution>/<course>')
def identify(name, institution, course):
    return render_template('identify.html', name=name, institution=institution, course=course)


@bp.route('/request/<name>')
def request_context(name):
    return render_template('request.html', name=name)


@bp.route('/forms', methods=['GET', 'POST'])
def forms():
    form = NomeForm()
    nome = sobrenome = instituicao = disciplina = ''

    if form.validate_on_submit():
        nome = form.nome.data
        sobrenome = form.sobrenome.data
        instituicao = form.instituicao.data
        disciplina = form.disciplina.data

    return render_template('forms.html', form=form, nome=nome, sobrenome=sobrenome, instituicao=instituicao, disciplina=disciplina)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = form.usuario.data
        return redirect(url_for('loginResponse', usuario=usuario))
    return render_template('login.html', form=form)


@bp.route('/loginResponse/<usuario>')
def loginResponse(usuario):
    return render_template('loginResponse.html', usuario=usuario)


@bp.route('/listausuario', methods=['GET', 'POST'])
def listausuario():
    nome = None
    funcao = None

    if request.method == 'POST':
        nome = request.form.get('nome')
        funcao = request.form.get('funcao')
        if nome and funcao:
            usuarios.append({'nome': nome, 'funcao': funcao})

    return render_template('listausuario.html', nome=nome, funcao=funcao, usuarios=usuarios)


@bp.route('/verificar_usuario')
def verificar_usuario():
    nome = request.args.get('nome', '').strip().lower()
    existe = any(u['nome'].lower() == nome for u in usuarios_cadastrados)
    return jsonify({'existe': existe})


@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    nome_usuario = None
    mensagem_extra = None

    if form.validate_on_submit():
        prontuario = (form.prontuario.data or '').strip()
        nome_usuario = form.nome.data.strip()
        endereco_email = form.email.data.strip() if form.email.data else None
        funcao = 'User'

        usuarios_cadastrados.append({'nome': nome_usuario, 'funcao': funcao, 'prontuario': prontuario, 'email': endereco_email})

        # Recipients: always admin, institutional and optionally the provided email
        recipients = []
        admin_address = 'flaskaulasweb@zohomail.com'
        recipients.append(admin_address)

        # institutional address from config (fallback to previous default)
        inst_email = current_app.config.get('INSTITUTIONAL_EMAIL', 'lucca.z@aluno.ifsp.edu.br')
        if inst_email:
            recipients.append(inst_email)

        if endereco_email:
            recipients.append(endereco_email)

        assunto = f"[Flasky] Novo usuário cadastrado: {nome_usuario}"
        texto = (
            (f"Prontuário: {prontuario}\n" if prontuario else '') +
            f"Nome: {nome_usuario}\n" +
            f"Usuário cadastrado: {nome_usuario}\n"
        )

        # Save to in-memory history
        emails_enviados.append({
            'de': nome_usuario,
            'para': ', '.join(recipients),
            'assunto': assunto,
            'texto': texto,
            'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })

        # Try sending email via provider (Mailgun or SendGrid)
        try:
            send_email(recipients, assunto, texto)
        except Exception as e:
            # log send failure but don't break the request
            print('Erro ao enviar e-mail:', e)

        flash('Cadastro realizado com sucesso!', 'success')
        form.prontuario.data = ''
        form.nome.data = ''
        form.email.data = ''

    return render_template('cadastro.html', form=form, usuarios=usuarios_cadastrados, nome_envio=nome_usuario, mensagem_extra=mensagem_extra)


@bp.route('/emailsEnviados')
def emails_enviados_page():
    return render_template('emailsEnviados.html', emails=emails_enviados)
