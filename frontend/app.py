from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os

app = Flask(__name__)

# Definindo as variáveis de ambiente
API_BASE_URL = "http://backend:8000"

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para exibir o formulário de cadastro
@app.route('/cadastro', methods=['GET'])
def inserir_jogo_form():
    return render_template('cadastro.html')

# Rota para enviar os dados do formulário de cadastro para a API
@app.route('/inserir', methods=['POST'])
def inserir_jogo():
    nome = request.form['nome']
    plataforma = request.form['plataforma']
    quantidade = request.form['quantidade']
    preco = request.form['preco']

    payload = {
        'nome': nome,
        'plataforma': plataforma,
        'quantidade' : quantidade,
        'preco' : preco
    }

    response = requests.post(f'{API_BASE_URL}/api/v1/jogos/', json=payload)
    
    if response.status_code == 201:
        return redirect(url_for('listar_jogos'))
    else:
        return "Erro ao inserir jogo", 500

# Rota para listar todos os jogos
@app.route('/estoque', methods=['GET'])
def listar_jogos():
    response = requests.get(f'{API_BASE_URL}/api/v1/jogos/')
    try:
        jogos = response.json()
    except:
        jogos = []
    return render_template('estoque.html', jogos=jogos)

# Rota para exibir o formulário de edição de jogo
@app.route('/atualizar/<int:jogo_id>', methods=['GET'])
def atualizar_jogo_form(jogo_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/jogos/")
    #filtrando apenas o jogo correspondente ao ID
    jogos = [jogo for jogo in response.json() if jogo['id'] == jogo_id]
    if len(jogos) == 0:
        return "jogo não encontrado", 404
    jogo = jogos[0]
    return render_template('atualizar.html', jogo=jogo)

# Rota para enviar os dados do formulário de edição de jogo para a API
@app.route('/atualizar/<int:jogo_id>', methods=['POST'])
def atualizar_jogo(jogo_id):
    nome = request.form['nome']
    plataforma = request.form['plataforma']
    quantidade = request.form['quantidade']
    preco = request.form['preco']

    payload = {
        'id': jogo_id,
        'nome': nome,
        'plataforma': plataforma,
        'quantidade' : quantidade,
        'preco' : preco
    }

    response = requests.patch(f"{API_BASE_URL}/api/v1/jogos/{jogo_id}", json=payload)
    
    if response.status_code == 200:
        return redirect(url_for('listar_jogos'))
    else:
        return "Erro ao atualizar jogo", 500

# Rota para exibir o formulário de edição de jogo
@app.route('/vender/<int:jogo_id>', methods=['GET'])
def vender_jogo_form(jogo_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/jogos/")
    #filtrando apenas o jogo correspondente ao ID
    jogos = [jogo for jogo in response.json() if jogo['id'] == jogo_id]
    if len(jogos) == 0:
        return "jogo não encontrado", 404
    jogo = jogos[0]
    return render_template('vender.html', jogo=jogo)

# Rota para vender um jogo
@app.route('/vender/<int:jogo_id>', methods=['POST'])
def vender_jogo(jogo_id):
    quantidade = request.form['quantidade']

    payload = {
        'quantidade': quantidade
    }

    response = requests.put(f"{API_BASE_URL}/api/v1/jogos/{jogo_id}/vender/", json=payload)
    
    if response.status_code == 200:
        return redirect(url_for('listar_jogos'))
    else:
        return "Erro ao vender jogo", 500

# Rota para listar todas as vendas
@app.route('/vendas', methods=['GET'])
def listar_vendas():
    response = requests.get(f"{API_BASE_URL}/api/v1/vendas/")
    try:
        vendas = response.json()
    except:
        vendas = []
    #salvando nomes dos jogos vendidos
    total_vendas = 0
    for venda in vendas:
        total_vendas += float(venda['valor_venda'])
    return render_template('vendas.html', vendas=vendas, total_vendas=total_vendas)

# Rota para excluir um jogo
@app.route('/excluir/<int:jogo_id>', methods=['POST'])
def excluir_jogo(jogo_id):
    response = requests.delete(f"{API_BASE_URL}/api/v1/jogos/{jogo_id}")
    
    if response.status_code == 200  :
        return redirect(url_for('listar_jogos'))
    else:
        return "Erro ao excluir jogo", 500

#Rota para resetar o database
@app.route('/reset-database', methods=['GET'])
def resetar_database():
    response = requests.delete(f"{API_BASE_URL}/api/v1/jogos/")
    
    if response.status_code == 200  :
        return render_template('confirmacao.html')
    else:
        return "Erro ao resetar o database", 500


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')