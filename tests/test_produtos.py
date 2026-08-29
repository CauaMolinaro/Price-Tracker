def test_criar_produto(client):
    resposta = client.post(
        "/produtos/",
        json={"nome": "RTX 4070", "url": "https://exemplo.com/rtx4070", "loja": "kabum"},
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["nome"] == "RTX 4070"
    assert "id" in corpo


def test_nao_permite_url_duplicada(client):
    payload = {"nome": "RTX 4070", "url": "https://exemplo.com/rtx4070", "loja": "kabum"}
    client.post("/produtos/", json=payload)
    resposta_duplicada = client.post("/produtos/", json=payload)
    assert resposta_duplicada.status_code == 409


def test_listar_produtos_vazio(client):
    resposta = client.get("/produtos/")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_obter_produto_inexistente(client):
    resposta = client.get("/produtos/999")
    assert resposta.status_code == 404


def test_remover_produto(client):
    criado = client.post(
        "/produtos/",
        json={"nome": "Jogo X", "url": "https://exemplo.com/jogox", "loja": "kabum"},
    ).json()

    resposta = client.delete(f"/produtos/{criado['id']}")
    assert resposta.status_code == 204

    resposta_get = client.get(f"/produtos/{criado['id']}")
    assert resposta_get.status_code == 404
