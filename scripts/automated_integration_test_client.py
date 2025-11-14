"""Integration test using Flask test_client (register + login).

This runs without hitting the running dev server and avoids reloader issues.
"""
from flasky import create_app


def run_client_test():
    app = create_app('flasky.config.DevelopmentConfig')
    with app.test_client() as client:
        # GET register page to obtain CSRF
        reg_get = client.get('/auth/register')
        assert reg_get.status_code == 200
        # Extract csrf token
        import re
        m = re.search(r'name="csrf_token" value="([^"]+)"', reg_get.get_data(as_text=True))
        csrf = m.group(1) if m else None

        data = {
            'csrf_token': csrf,
            'email': 'clienttest+user@example.local',
            'username': 'clienttestuser',
            'password': 'ClientTest123!',
            'password2': 'ClientTest123!',
            'submit': 'Register'
        }
        reg_post = client.post('/auth/register', data=data, follow_redirects=True)
        print('Register status:', reg_post.status_code)
        if b'A confirmation email has been sent' in reg_post.data:
            print('Register: confirmation email message present')
        else:
            print('Register: response length', len(reg_post.data))

        # Now login
        login_get = client.get('/auth/login')
        m2 = re.search(r'name="csrf_token" value="([^"]+)"', login_get.get_data(as_text=True))
        csrf2 = m2.group(1) if m2 else None
        login_data = {
            'csrf_token': csrf2,
            'email': 'clienttest+user@example.local',
            'password': 'ClientTest123!',
            'remember_me': 'y',
            'submit': 'Log In'
        }
        login_post = client.post('/auth/login', data=login_data, follow_redirects=True)
        print('Login status:', login_post.status_code)
        if b'You have been logged out.' in login_post.data:
            print('Unexpected logout message in login response')
        if b'Logout' in login_post.data or b'unconfirmed' not in login_post.data:
            print('Login response ok-ish; check content length', len(login_post.data))


if __name__ == '__main__':
    run_client_test()
