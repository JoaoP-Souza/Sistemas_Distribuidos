from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

# Função para obter a conexão com o banco de dados PostgreSQL
async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgres://postgres:postgres@db:5432/jogos") 
    return await asyncpg.connect(DATABASE_URL)

# Inicializar a aplicação FastAPI
app = FastAPI()

# Modelo para adicionar novos jogos
class jogo(BaseModel):
    id: Optional[int] = None
    nome: str
    plataforma: str
    quantidade: int
    preco: float

class jogoBase(BaseModel):
    nome: str
    plataforma: str
    quantidade: int
    preco: float

# Modelo para venda de jogos
class Vendajogo(BaseModel):
    quantidade: int

# Modelo para atualizar atributos de um jogo (exceto o ID)
class Atualizarjogo(BaseModel):
    nome: Optional[str] = None
    plataforma: Optional[str] = None
    quantidade: Optional[int] = None
    preco: Optional[float] = None

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response

# Função para verificar se o jogo existe usado plataforma e nome do jogo
async def jogo_existe(nome: str, plataforma: str, conn: asyncpg.Connection):
    try:
        query = "SELECT * FROM jogos WHERE LOWER(nome) = LOWER($1) AND LOWER(plataforma) = LOWER($2)"
        result = await conn.fetchval(query, nome, plataforma)
        return result is not None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao verificar se o jogo existe: {str(e)}")

# 1. Adicionar um novo jogo
@app.post("/api/v1/jogos/", status_code=201)
async def adicionar_jogo(jogo: jogoBase):
    conn = await get_database()
    if await jogo_existe(jogo.nome, jogo.plataforma, conn):
        raise HTTPException(status_code=400, detail="jogo já existe.")
    try:
        query = "INSERT INTO jogos (nome, plataforma, quantidade, preco) VALUES ($1, $2, $3, $4)"
        async with conn.transaction():
            result = await conn.execute(query, jogo.nome, jogo.plataforma, jogo.quantidade, jogo.preco)
            return {"message": "jogo adicionado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao adicionar o jogo: {str(e)}")
    finally:
        await conn.close()

# 2. Listar todos os jogos
@app.get("/api/v1/jogos/", response_model=List[jogo])
async def listar_jogos():
    conn = await get_database()
    try:
        # Buscar todos os jogos no banco de dados
        query = "SELECT * FROM jogos"
        rows = await conn.fetch(query)
        jogos = [dict(row) for row in rows]
        return jogos
    finally:
        await conn.close()

# 3. Buscar jogo por ID
@app.get("/api/v1/jogos/{jogo_id}")
async def listar_jogo_por_id(jogo_id: int):
    conn = await get_database()
    try:
        # Buscar o jogo por ID
        query = "SELECT * FROM jogos WHERE id = $1"
        jogo = await conn.fetchrow(query, jogo_id)
        if jogo is None:
            raise HTTPException(status_code=404, detail="jogo não encontrado.")
        return dict(jogo)
    finally:
        await conn.close()

# 4. Vender um jogo (reduzir quantidade no estoque)
@app.put("/api/v1/jogos/{jogo_id}/vender/")
async def vender_jogo(jogo_id: int, venda: Vendajogo):
    conn = await get_database()
    try:
        # Verificar se o jogo existe
        query = "SELECT * FROM jogos WHERE id = $1"
        jogo = await conn.fetchrow(query, jogo_id)
        if jogo is None:
            raise HTTPException(status_code=404, detail="jogo não encontrado.")

        # Verificar se a quantidade no estoque é suficiente
        if jogo['quantidade'] < venda.quantidade:
            raise HTTPException(status_code=400, detail="Quantidade insuficiente no estoque.")

        # Atualizar a quantidade no banco de dados
        nova_quantidade = jogo['quantidade'] - venda.quantidade
        update_query = "UPDATE jogos SET quantidade = $1 WHERE id = $2"
        await conn.execute(update_query, nova_quantidade, jogo_id)


        # Calcular o valor total da venda
        valor_venda = jogo['preco'] * venda.quantidade
        # Registrar a venda na tabela de vendas
        insert_venda_query = """
            INSERT INTO vendas (jogo_id, nome, quantidade_vendida, valor_venda) 
            VALUES ($1, $2, $3, $4)
        """
        await conn.execute(insert_venda_query, jogo_id, jogo['nome'], venda.quantidade, valor_venda)

        # Criar um novo dicionário com os dados atualizados
        jogo_atualizado = dict(jogo)
        jogo_atualizado['quantidade'] = nova_quantidade

        return {"message": "Venda realizada com sucesso!", "jogo": jogo_atualizado}
    finally:
        await conn.close()

# 5. Atualizar atributos de um jogo pelo ID (exceto o ID)
@app.patch("/api/v1/jogos/{jogo_id}")
async def atualizar_jogo(jogo_id: int, jogo_atualizacao: Atualizarjogo):
    conn = await get_database()
    try:
        # Verificar se o jogo existe
        query = "SELECT * FROM jogos WHERE id = $1"
        jogo = await conn.fetchrow(query, jogo_id)
        if jogo is None:
            raise HTTPException(status_code=404, detail="jogo não encontrado.")

        # Atualizar apenas os campos fornecidos
        update_query = """
            UPDATE jogos
            SET nome = COALESCE($1, nome),
                plataforma = COALESCE($2, plataforma),
                quantidade = COALESCE($3, quantidade),
                preco = COALESCE($4, preco)
            WHERE id = $5
        """
        await conn.execute(
            update_query,
            jogo_atualizacao.nome,
            jogo_atualizacao.plataforma,
            jogo_atualizacao.quantidade,
            jogo_atualizacao.preco,
            jogo_id
        )
        return {"message": "jogo atualizado com sucesso!"}
    finally:
        await conn.close()

# 6. Remover um jogo pelo ID
@app.delete("/api/v1/jogos/{jogo_id}")
async def remover_jogo(jogo_id: int):
    conn = await get_database()
    try:
        # Verificar se o jogo existe
        query = "SELECT * FROM jogos WHERE id = $1"
        jogo = await conn.fetchrow(query, jogo_id)
        if jogo is None:
            raise HTTPException(status_code=404, detail="jogo não encontrado.")

        # Remover o jogo do banco de dados
        delete_query = "DELETE FROM jogos WHERE id = $1"
        await conn.execute(delete_query, jogo_id)
        return {"message": "jogo removido com sucesso!"}
    finally:
        await conn.close()

# 7. Resetar banco de dados de jogos
@app.delete("/api/v1/jogos/")
async def resetar_jogos():
    init_sql = os.getenv("INIT_SQL", "db/init.sql")
    conn = await get_database()
    try:
        # Read SQL file contents
        with open(init_sql, 'r') as file:
            sql_commands = file.read()
        # Execute SQL commands
        await conn.execute(sql_commands)
        return {"message": "Banco de dados limpo com sucesso!"}
    finally:
        await conn.close()


# 8 . Listar vendas
@app.get("/api/v1/vendas/")
async def listar_vendas():
    conn = await get_database()
    try:
        # Buscar todas as vendas no banco de dados
        query = "SELECT * FROM vendas"
        rows = await conn.fetch(query)
        vendas = [dict(row) for row in rows]
        return vendas
    finally:
        await conn.close()