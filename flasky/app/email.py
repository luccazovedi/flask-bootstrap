import os
import requests
import json


def _send_mailgun(recipients, subject, text):
    api_key = os.getenv('MAILGUN_API_KEY')
    domain = os.getenv('MAILGUN_DOMAIN')
    if not api_key or not domain:
        raise RuntimeError('Mailgun não configurado')

    from_addr = os.getenv('MAILGUN_FROM', f'Flasky <postmaster@{domain}>')
    resp = requests.post(
        f'https://api.mailgun.net/v3/{domain}/messages',
        auth=('api', api_key),
        data={
            'from': from_addr,
            'to': recipients,
            'subject': subject,
            'text': text,
        }
    )
    resp.raise_for_status()
    return resp


def _send_sendgrid(recipients, subject, text):
    api_key = os.getenv('SENDGRID_API_KEY')
    if not api_key:
        raise RuntimeError('SendGrid não configurado')

    # Build SendGrid v3 API payload
    personalizations = [{
        'to': [{'email': r} for r in recipients]
    }]
    data = {
        'personalizations': personalizations,
        'from': {'email': os.getenv('SENDGRID_FROM', 'noreply@yourdomain.com')},
        'subject': subject,
        'content': [
            {'type': 'text/plain', 'value': text}
        ]
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    resp = requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, data=json.dumps(data))
    resp.raise_for_status()
    return resp


def send_email(recipients, subject, text):
    """Send email using Mailgun if configured, otherwise SendGrid if configured.

    recipients: list[str]
    """
    if isinstance(recipients, str):
        recipients = [recipients]

    # Prefer Mailgun
    try:
        return _send_mailgun(recipients, subject, text)
    except Exception:
        # Try SendGrid
        try:
            return _send_sendgrid(recipients, subject, text)
        except Exception:
            # Neither provider available — log and return None
            print('Nenhum provedor de email configurado (Mailgun/SendGrid). Destinatários:', recipients)
            return None
