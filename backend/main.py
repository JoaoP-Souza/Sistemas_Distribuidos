from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time

jogos = [
    {"id": 1, "nome": "Forza", "plataforma": "Xbox", "quantidade": 4, "preco": 250.0},
    {"id": 2, "nome": "God of war", "plataforma": "ps5", "quantidade": 3, "preco": 350.0},
    {"id": 2, "nome": "Zelda", "plataforma": "nintendo switch", "quantidade": 8, "preco": 300.0},
]

app = FastAPI()


class Jogo(BaseModel):
    id: Optional[int] = None
    nome: str
    plataforma: str
    quantidade: int
    preco: float

class VendaJogo(BaseModel):
    quantidade: int


class AtualizaJogo(BaseModel):
    nome: Optional[str] = None
    plataforma: Optional[str] = None
    quantidade: Optional[int] = None
    preco: Optional[float] = None

def gerar_proximo_id():
    if jogos:
        return max(Jogo['id'] for Jogo in jogos) + 1
    else:
        return 1

def buscar_Jogo_por_id(Jogo_id: int):
    for Jogo in jogos:
        if Jogo["id"] == Jogo_id:
            return Jogo
    return None

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response

@app.post("/api/v1/jogos/", status_code=201)
def adicionar_Jogo(Jogo: Jogo):
    for l in jogos:
        if l["plataforma"].lower() == Jogo.plataforma.lower() and l["nome"].lower() == Jogo.nome.lower():
            raise HTTPException(status_code=400, detail="Jogo já existe.")
    
    novo_Jogo = Jogo.dict()
    novo_Jogo['id'] = gerar_proximo_id()

    jogos.append(novo_Jogo)
    return {"message": "Jogo adicionado com sucesso!", "Jogo": novo_Jogo}

@app.get("/api/v1/jogos/", response_model=List[Jogo])
def listar_jogos():
    return jogos

@app.get("/api/v1/jogos/{Jogo_id}")
def listar_Jogo_por_id(Jogo_id: int):
    Jogo = buscar_Jogo_por_id(Jogo_id)
    if Jogo is None:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    return Jogo

@app.put("/api/v1/jogos/{Jogo_id}/vender/")
def vender_Jogo(Jogo_id: int, venda: VendaJogo):
    Jogo = buscar_Jogo_por_id(Jogo_id)
    
    if Jogo is None:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    
    if Jogo["quantidade"] < venda.quantidade:
        raise HTTPException(status_code=400, detail="Quantidade insuficiente no estoque.")
    
    Jogo["quantidade"] -= venda.quantidade
    return {"message": "Venda realizada com sucesso!", "Jogo": Jogo}

@app.patch("/api/v1/jogos/{Jogo_id}")
def atualiza_Jogo(Jogo_id: int, Jogo_atualizacao: AtualizaJogo):
    Jogo = buscar_Jogo_por_id(Jogo_id)
    if Jogo is None:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    
    if Jogo_atualizacao.nome is not None:
        Jogo["nome"] = Jogo_atualizacao.nome
    if Jogo_atualizacao.plataforma is not None:
        Jogo["plataforma"] = Jogo_atualizacao.plataforma
    if Jogo_atualizacao.quantidade is not None:
        Jogo["quantidade"] = Jogo_atualizacao.quantidade
    if Jogo_atualizacao.preco is not None:
        Jogo["preco"] = Jogo_atualizacao.preco

    return {"message": "Jogo atualizado com sucesso!", "Jogo": Jogo}


@app.delete("/api/v1/jogos/{Jogo_id}")
def remover_Jogo(Jogo_id: int):
    for i, Jogo in enumerate(jogos):
        if Jogo["id"] == Jogo_id:
            del jogos[i]
            return {"message": "Jogo removido com sucesso!"}
        

@app.delete("/api/v1/jogos/")
def resetar_jogos():
    global jogos
    jogos = [
    {"id": 1, "nome": "Forza", "plataforma": "Xbox", "quantidade": 4, "preco": 250.0},
    {"id": 2, "nome": "God of war", "plataforma": "ps5", "quantidade": 3, "preco": 350.0},
    {"id": 3, "nome": "Zelda", "plataforma": "nintendo switch", "quantidade": 8, "preco": 300.0},
    ]
    return {"message": "Repositorio limpo com sucesso!", "jogos": jogos}