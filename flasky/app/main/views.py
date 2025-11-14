from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from datetime import datetime
from . import bp
from .forms import CadastroForm, NomeForm, LoginForm
from ..email import send_email
from .. import db
from ..models import User
from flask_login import login_user, login_required, current_user
import secrets
from flask import render_template

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
        senha = form.senha.data
        # try to find by email first, then username
        user = User.query.filter((User.email == usuario) | (User.username == usuario)).first()
        if user and user.verify_password(senha):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Usuário ou senha inválidos', 'danger')
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

        # If an email was provided, create a User in the local DB (if not exists)
        created_user = None
        if endereco_email:
            existing = User.query.filter_by(email=endereco_email.lower()).first()
            if not existing:
                # generate a safe username from name; ensure uniqueness
                base_username = ''.join(x for x in nome_usuario if x.isalnum())[:30] or endereco_email.split('@')[0]
                username = base_username
                i = 1
                while User.query.filter_by(username=username).first() is not None:
                    username = f"{base_username}{i}"
                    i += 1

                random_pw = secrets.token_urlsafe(8)
                user = User(email=endereco_email.lower(), username=username, password=random_pw)
                # mark unconfirmed so they can confirm via auth flow if desired
                user.confirmed = False
                db.session.add(user)
                db.session.commit()
                created_user = user

                # send password-reset link so the user can set their password
                try:
                    token = user.generate_reset_token()
                    resp = send_email(user.email, 'Reset Your Password', 'auth/email/reset_password', user=user, token=token)
                    # If send_email returns None or a falsey response, consider it a send failure
                    if not resp:
                        # mark as confirmed to avoid blocking the user when e-mail sending fails
                        user.confirmed = True
                        db.session.add(user)
                        db.session.commit()
                        print('Aviso: e-mail de senha não foi enviado; usuário confirmado automaticamente.', flush=True)
                except Exception as e:
                    # log the send failure and confirm the user to avoid blocking registration
                    print('Erro ao enviar e-mail de senha inicial:', e)
                    try:
                        user.confirmed = True
                        db.session.add(user)
                        db.session.commit()
                        print('Usuário confirmado automaticamente após falha no envio de e-mail.', flush=True)
                    except Exception as _:
                        # if DB commit fails, at least log the original exception
                        print('Falha ao confirmar usuário automaticamente após erro de e-mail.', flush=True)

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

        assunto = f"Novo usuário cadastrado: {nome_usuario}"
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
        # Send to each recipient individually since send_email expects a single recipient
        if created_user:
            for recipient in recipients:
                try:
                    send_email(
                        recipient,
                        assunto,
                        'mail/new_user',
                        user=created_user,
                        prontuario=prontuario,
                        nome=nome_usuario
                    )
                except Exception as e:
                    # log send failure but don't break the request
                    print(f'Erro ao enviar e-mail para {recipient}:', e)

        flash('Cadastro realizado com sucesso!', 'success')
        form.prontuario.data = ''
        form.nome.data = ''
        form.email.data = ''

    return render_template('cadastro.html', form=form, usuarios=usuarios_cadastrados, nome_envio=nome_usuario, mensagem_extra=mensagem_extra)


@bp.route('/emailsEnviados')
def emails_enviados_page():
    return render_template('emailsEnviados.html', emails=emails_enviados)


@bp.route('/usuarios')
def usuarios_db():
    # show persisted users from the database
    try:
        users = User.query.order_by(User.id).all()
        # ensure we always pass a list to the template
        users = users or []
        empty = len(users) == 0
    except Exception as e:
        # Log the exception to the server logs and show a friendly message
        print('Erro ao buscar usuários do banco:', e, flush=True)
        flash('Erro ao acessar o banco de dados. Mostrando lista vazia.', 'warning')
        users = []
        empty = True

    return render_template('usuarios.html', users=users, empty=empty)


@bp.route('/usuarios/confirm/<int:user_id>', methods=['GET', 'POST'])
@login_required
def confirm_user(user_id):
    # Handle accidental GETs by redirecting to the unconfirmed page
    if request.method == 'GET':
        return redirect(url_for('auth.unconfirmed'))

    admin_email = current_app.config.get('FLASKY_ADMIN')
    # Permitir: admin ou o próprio usuário se quiser se auto-confirmar
    if not current_user.is_authenticated:
        flash('Faça login para confirmar.', 'warning')
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if user is None:
        flash('Usuário não encontrado.', 'warning')
        return redirect(url_for('main.usuarios_db'))

    if current_user.email != admin_email and current_user.id != user.id:
        flash('Ação não autorizada para este usuário.', 'danger')
        return redirect(url_for('main.usuarios_db'))

    if user.confirmed:
        flash('Usuário já está confirmado.', 'info')
        return redirect(url_for('main.usuarios_db'))

    user.confirmed = True
    db.session.add(user)
    db.session.commit()
    flash(f'Usuário {user.username} confirmado manualmente.', 'success')
    return redirect(url_for('main.usuarios_db'))
