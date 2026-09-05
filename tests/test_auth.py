def test_registrar_usuario(client):
    resposta = client.post(
        "/auth/registrar",
        json={"email": "novo@exemplo.com", "senha": "senha12345"},
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == "novo@exemplo.com"
    assert "senha" not in corpo
    assert "senha_hash" not in corpo


def test_nao_permite_email_duplicado(client):
    payload = {"email": "duplicado@exemplo.com", "senha": "senha12345"}
    client.post("/auth/registrar", json=payload)
    resposta = client.post("/auth/registrar", json=payload)
    assert resposta.status_code == 409


def test_registrar_senha_curta_e_rejeitada(client):
    resposta = client.post(
        "/auth/registrar",
        json={"email": "curta@exemplo.com", "senha": "123"},
    )
    assert resposta.status_code == 422


def test_login_com_sucesso(client):
    client.post(
        "/auth/registrar",
        json={"email": "login@exemplo.com", "senha": "senha12345"},
    )
    resposta = client.post(
        "/auth/login",
        data={"username": "login@exemplo.com", "password": "senha12345"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert "access_token" in corpo
    assert corpo["token_type"] == "bearer"


def test_login_com_senha_errada(client):
    client.post(
        "/auth/registrar",
        json={"email": "senhaerrada@exemplo.com", "senha": "senha12345"},
    )
    resposta = client.post(
        "/auth/login",
        data={"username": "senhaerrada@exemplo.com", "password": "senhaincorreta"},
    )
    assert resposta.status_code == 401


def test_login_usuario_inexistente(client):
    resposta = client.post(
        "/auth/login",
        data={"username": "naoexiste@exemplo.com", "password": "qualquer123"},
    )
    assert resposta.status_code == 401