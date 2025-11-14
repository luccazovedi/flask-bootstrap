@auth.route('/confirm-local', methods=['POST'])
@login_required
def confirm_local():
    if not current_user.confirmed:
        current_user.confirmed = True
        db.session.add(current_user)
        db.session.commit()
        flash('Conta confirmada localmente com sucesso!')
    else:
        flash('Sua conta já está confirmada.')
    return redirect(url_for('main.index'))
from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # Se o usuário não está confirmado, redireciona para auth.unconfirmed
            if not user.confirmed:
                return redirect(url_for('auth.unconfirmed'))
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        try:
            resp = send_email(
                user.email,
                'Confirm Your Account',
                'auth/email/confirm',
                user=user,
                token=token
            )
        except Exception as e:
            # Log the error and treat as send failure to avoid 500
            print('Erro ao enviar e-mail de confirmação:', e, flush=True)
            resp = None

        if resp is None:
            flash('Não foi possível enviar o e-mail de confirmação.', 'warning')
            # Confirm user automatically if email fails
            user.confirmed = True
            db.session.add(user)
            db.session.commit()
        else:
            flash('A confirmation email has been sent to you by email.')
        
        # Build confirmation link safely
        try:
            confirm_url = url_for('auth.confirm', token=token, _external=True)
            flash(f'<p>To confirm your account <a href="{confirm_url}">click here</a></p>')
        except Exception as e:
            print('Erro ao gerar URL de confirmação:', e, flush=True)
            
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    try:
        resp = send_email(
            current_user.email,
            'Confirm Your Account',
            'auth/email/confirm',
            user=current_user,
            token=token,
            external_base=current_app.config.get('BASE_URL'),
            reply_to=(current_app.config.get('API_FROM') or current_app.config.get('FLASKY_MAIL_SENDER'))
        )
    except Exception as e:
        print('Erro ao reenviar e-mail de confirmação:', e, flush=True)
        resp = None

    if resp is None:
        flash('Não foi possível reenviar o e-mail de confirmação.', 'warning')
    else:
        flash('A new confirmation email has been sent to you by email.')
    flash('<p>To confirm your account <a href="' + url_for('auth.confirm', token=token, _external=True) + '">click here</a></p>')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            try:
                resp = send_email(
                    user.email,
                    'Reset Your Password',
                    'auth/email/reset_password',
                    user=user,
                    token=token,
                    external_base=current_app.config.get('BASE_URL'),
                    reply_to=(current_app.config.get('API_FROM') or current_app.config.get('FLASKY_MAIL_SENDER'))
                )
            except Exception as e:
                print('Erro ao enviar e-mail de reset:', e, flush=True)
                resp = None

            if resp is None:
                flash('Não foi possível enviar o e-mail de reset.', 'warning')
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        flash('<p>To reset your password <a href="' + url_for('auth.password_reset', token=token, _external=True) + '">click here</a></p>')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = (form.email.data or "").lower()
            # Evitar trocar para o mesmo e-mail
            if new_email == (current_user.email or "").lower():
                flash('O novo e-mail é igual ao atual.', 'info')
                return redirect(url_for('main.index'))

            # Proteção extra: impedir duplicidade caso o validador não seja acionado
            if User.query.filter_by(email=new_email).first() is not None:
                flash('Email already registered.', 'warning')
                return render_template("auth/change_email.html", form=form)

            current_user.email = new_email
            db.session.add(current_user)
            db.session.commit()
            flash('Your email address has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
