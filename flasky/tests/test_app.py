from flasky.app import create_app


def test_index_returns_200():
    app = create_app()
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200
