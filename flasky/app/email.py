from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail

import requests
from datetime import datetime
from urllib.parse import urljoin


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email_zoho(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    print('Enviando mensagem (POST)...', flush=True)
    print('API_URL: ' + str(app.config.get('API_URL')), flush=True)
    print('API_KEY: ' + str(app.config.get('API_KEY')), flush=True)
    print('API_FROM: ' + str(app.config.get('API_FROM')), flush=True)
    print('MAILGUN_DOMAIN: ' + str(app.config.get('MAILGUN_DOMAIN')), flush=True)
    print('MAILGUN_API_KEY present: ' + str(bool(app.config.get('MAILGUN_API_KEY'))), flush=True)
    print('to: ' + str(to), flush=True)
    print('subject: ' + str(app.config.get('FLASKY_MAIL_SUBJECT_PREFIX')) + ' ' + subject, flush=True)
    #print('text: ' + "Novo usuário cadastrado: " + newUser, flush=True)

    # Provider selection: prefer Mailgun (if configured), then generic API_URL, then SMTP
    mailgun_domain = app.config.get('MAILGUN_DOMAIN')
    mailgun_key = app.config.get('MAILGUN_API_KEY')
    api_from = app.config.get('API_FROM') or app.config.get('FLASKY_MAIL_SENDER')
    # Try rendering the template. Email templates frequently use url_for(..., _external=True).
    # That raises if SERVER_NAME is not configured. Try to recover using BASE_URL from config.
    try:
        html_body = render_template(template + '.html', **kwargs)
    except Exception as e:
        # Attempt to set SERVER_NAME and PREFERRED_URL_SCHEME from config BASE_URL
        base = app.config.get('BASE_URL')
        if base:
            from urllib.parse import urlparse
            parsed = urlparse(base)
            host = parsed.netloc
            scheme = parsed.scheme or app.config.get('PREFERRED_URL_SCHEME', 'https')
            # Temporarily set values so url_for(_external=True) can build URLs
            old_server = app.config.get('SERVER_NAME')
            old_scheme = app.config.get('PREFERRED_URL_SCHEME')
            app.config['SERVER_NAME'] = host
            app.config['PREFERRED_URL_SCHEME'] = scheme
            try:
                html_body = render_template(template + '.html', **kwargs)
            finally:
                # restore
                if old_server is None:
                    app.config.pop('SERVER_NAME', None)
                else:
                    app.config['SERVER_NAME'] = old_server
                app.config['PREFERRED_URL_SCHEME'] = old_scheme
        else:
            # re-raise if we can't recover
            raise

    # Try Mailgun first

    if mailgun_domain and mailgun_key:
        mg_url = f'https://api.mailgun.net/v3/{mailgun_domain}/messages'
        try:
            resp = requests.post(
                mg_url,
                auth=('api', mailgun_key),
                data={
                    'from': api_from,
                    'to': to,
                    'subject': app.config.get('FLASKY_MAIL_SUBJECT_PREFIX') + ' ' + subject,
                    'html': html_body
                }
            )
            status = resp.status_code
            text = resp.text
            try:
                resp.raise_for_status()
                print('Enviado via Mailgun:', status, flush=True)
            except Exception as e:
                print('Mailgun returned error status:', status, 'body:', text, flush=True)
                raise
            print('Mailgun response body:', text, flush=True)
            return resp
        except Exception as e:
            print('Erro ao enviar via Mailgun:', e, flush=True)
            # fallback to other providers

    # Next try generic API_URL/API_KEY/API_FROM (backwards compatibility)
    url = app.config.get('API_URL')
    api_key = app.config.get('API_KEY')
    if url and api_key and api_from:
        try:
            resposta = requests.post(
                url,
                auth=("api", api_key),
                data={
                    "from": api_from,
                    "to": to,
                    "subject": app.config.get('FLASKY_MAIL_SUBJECT_PREFIX') + ' ' + subject,
                    "html": html_body
                }
            )
            resposta.raise_for_status()
            return resposta
        except Exception as e:
            print('Erro ao enviar via API_URL:', e)

    # If no API configured, try to send via Flask-Mail (SMTP) if configured
    mail_server = app.config.get('MAIL_SERVER')
    mail_sender = app.config.get('FLASKY_MAIL_SENDER')
    if mail_server and mail_sender:
        try:
            # use the async SMTP sending helper
            return send_email_zoho(to, subject, template, **kwargs)
        except Exception as e:
            print('Erro ao enviar via Flask-Mail:', e)

    # No provider configured: log and return None
    print('Nenhum provedor de e-mail configurado (API_URL ou MAIL_SERVER). Mensagem não enviada.')
    return None
