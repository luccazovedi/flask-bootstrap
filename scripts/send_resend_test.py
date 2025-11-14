"""
Simple test script to send an email via Mailgun HTTP API.
Reads MAILGUN_API_KEY, MAILGUN_DOMAIN and API_FROM (or FLASKY_MAIL_SENDER) from environment or .env.

Usage:
  python scripts/send_resend_test.py --to you@example.com --subject "hello" --html "<p>it works!</p>"

This script will exit if MAILGUN_API_KEY or MAILGUN_DOMAIN are not set.
"""
import os
import sys
import argparse
import requests

# Try to load .env automatically if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()  # loads .env from project root
except Exception:
    # dotenv is optional; if not installed the script will fall back to env vars
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--to', required=True, help='Recipient email or comma-separated list')
    parser.add_argument('--subject', default='hello world', help='Email subject')
    parser.add_argument('--html', default='<p>it works!</p>', help='HTML body')
    args = parser.parse_args()

    mg_key = os.environ.get('MAILGUN_API_KEY')
    mg_domain = os.environ.get('MAILGUN_DOMAIN')
    if not mg_key or not mg_domain:
        print('MAILGUN_API_KEY and MAILGUN_DOMAIN must be set in environment or .env')
        sys.exit(2)

    api_from = os.environ.get('API_FROM') or os.environ.get('FLASKY_MAIL_SENDER') or f'no-reply@{os.environ.get("HOSTNAME", "localhost")}'

    recipients = [r.strip() for r in args.to.split(',') if r.strip()]

    mg_url = f'https://api.mailgun.net/v3/{mg_domain}/messages'
    data = {
        'from': api_from,
        'to': recipients,
        'subject': args.subject,
        'html': args.html,
    }

    print('Sending via Mailgun to', recipients)
    r = requests.post(mg_url, auth=('api', mg_key), data=data)
    print('Status:', r.status_code)
    try:
        print('Response:', r.json())
    except Exception:
        print('Response text:', r.text)
    r.raise_for_status()


if __name__ == '__main__':
    main()
