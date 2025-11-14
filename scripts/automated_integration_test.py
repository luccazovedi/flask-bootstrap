"""Automated integration test (signup + login) against running dev server.

Usage: run this while the dev server is running at http://127.0.0.1:5000
"""
import re
import requests

BASE = 'http://127.0.0.1:5000'

def get_csrf(session, url):
    r = session.get(url)
    r.raise_for_status()
    m = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
    if not m:
        raise RuntimeError('CSRF token not found on %s' % url)
    return m.group(1), r.text

def register(session, email, username, password):
    reg_url = BASE + '/auth/register'
    token, _ = get_csrf(session, reg_url)
    data = {
        'csrf_token': token,
        'email': email,
        'username': username,
        'password': password,
        'password2': password,
        'submit': 'Register'
    }
    r = session.post(reg_url, data=data, allow_redirects=True)
    return r

def login(session, email_or_username, password):
    login_url = BASE + '/auth/login'
    token, _ = get_csrf(session, login_url)
    data = {
        'csrf_token': token,
        'email': email_or_username,
        'password': password,
        'remember_me': 'y',
        'submit': 'Log In'
    }
    r = session.post(login_url, data=data, allow_redirects=True)
    return r

def main():
    s = requests.Session()
    email = 'autotest+user@example.local'
    username = 'autotestuser'
    password = 'TestPass123!'

    print('Registering', email)
    r = register(s, email, username, password)
    print('Register response:', r.status_code)
    if 'A confirmation email has been sent' in r.text or r.status_code in (200, 302):
        print('Registration appears successful (server responded).')
    else:
        print('Registration may have failed; server response len:', len(r.text))

    print('Attempting login')
    r2 = login(s, email, password)
    print('Login response:', r2.status_code)
    if 'You have been logged out.' in r2.text:
        # unlikely; treat as failure
        print('Unexpected logout message present')
    # Check if authenticated by requesting index and looking for logout link or username
    r3 = s.get(BASE + '/')
    if username in r3.text or 'Logout' in r3.text:
        print('Login verified: page contains username or Logout link')
    else:
        print('Login verification ambiguous; index page length:', len(r3.text))

if __name__ == '__main__':
    main()
