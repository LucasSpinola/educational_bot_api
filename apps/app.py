from typing import Union
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Form
import requests
import json
from pydantic import BaseModel
import logging
import httpx

app = FastAPI()

BD_FIRE = ""

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/cria_pergunta/")
async def cria_pergunta(pergunta: str = Form(...), resposta: str = Form(...)):
    # Cria um dicionário com a pergunta e a resposta
    dicionario_pergunta = {'pergunta': pergunta, 'resposta': resposta}

    # Transforma o dicionário em json
    json_pergunta = json.dumps(dicionario_pergunta)

    # Faz a requisição do tipo post na API
    requisicao = requests.post(f'{BD_FIRE}/perguntas/.json', data=json_pergunta)

    # Verifica se a requisição foi bem sucedida (200)
    if requisicao.status_code == 200:
        return {"mensagem": "Pergunta criada com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao criar a pergunta")

@app.put("/edita_pergunta/{id}/")
async def edita_pergunta(
    id: str,
    pergunta: str = Form("pergunta padrão"),
    resposta: str = Form("resposta padrão")
    ):
    # Cria um dicionário com a pergunta e a resposta
    if pergunta == 'pergunta padrão':
        dicionario_pergunta = {'resposta': resposta}
    elif resposta == 'resposta padrão':
        dicionario_pergunta = {'pergunta': pergunta}
    else:
        dicionario_pergunta = {'pergunta': pergunta, 'resposta': resposta}

    # Transforma o dicionário em json
    json_pergunta = json.dumps(dicionario_pergunta)

    # Faz a requisição do tipo patch na API
    requisicao = requests.patch(f'{BD_FIRE}/perguntas/{id}/.json', data=json_pergunta)

    # Verifica se a requisição foi bem sucedida (200)
    if requisicao.status_code == 200:
        return {"mensagem": "Pergunta editada com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao editar a pergunta")
    
@app.delete("/deleta_pergunta/{id}/")
async def deleta_pergunta(id: str):
    # Verifica se o ID existe no banco de dados fazendo uma requisição GET
    get_request = requests.get(f'{BD_FIRE}/perguntas/{id}/.json')

    if get_request.status_code == 200:
        resposta = get_request.json()
        if resposta is not None:
            # A pergunta existe, então podemos prosseguir com a exclusão
            delete_request = requests.delete(f'{BD_FIRE}/perguntas/{id}/.json')

            # Verifica se a requisição de exclusão foi bem sucedida (status code 200)
            if delete_request.status_code == 200:
                return {"mensagem": "Pergunta deletada com sucesso"}
            else:
                raise HTTPException(status_code=500, detail="Erro ao deletar a pergunta")
    
    # Se chegamos aqui, o ID não foi encontrado no banco de dados
    raise HTTPException(status_code=404, detail="Pergunta não encontrada")

@app.get("/le_perguntas/")
async def le_perguntas():
    # Lê as perguntas do banco de dados
    requisicao = requests.get(f'{BD_FIRE}/perguntas/.json')
    
    # Verifica se a requisição foi bem-sucedida (status code 200)
    if requisicao.status_code == 200:
        perguntas = requisicao.json()
        return perguntas
    else:
        return {"mensagem": "Erro ao ler as perguntas do banco de dados"}

@app.get("/get_pergunta_id/")
async def get_pergunta_id(pergunta: str):
    # Faz uma requisição GET para ler as perguntas do banco de dados
    get_request = requests.get(f'{BD_FIRE}/perguntas/.json')
    
    # Verifica se a requisição foi bem-sucedida (status code 200)
    if get_request.status_code == 200:
        perguntas = get_request.json()
        
        # Procura o ID da pergunta no banco de dados
        for id, dados_pergunta in perguntas.items():
            if dados_pergunta.get('pergunta') == pergunta:
                return {"id": id}
        
        # Se a pergunta não for encontrada, retorna uma exceção HTTP 404
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")
    else:
        raise HTTPException(status_code=500, detail="Erro ao ler as perguntas do banco de dados")
    
class Aluno(BaseModel):
    nome: str
    matricula: int
    turma: str
    id: int

@app.post("/cria_aluno/")
async def cria_aluno(aluno: Aluno):
    # Transforma o objeto Aluno em um dicionário
    dicionario_aluno = aluno.dict()

    # Transforma o dicionário em JSON
    json_aluno = json.dumps(dicionario_aluno)

    # Faz a requisição do tipo POST na API para criar o aluno
    requisicao = requests.post(f'{BD_FIRE}/alunos/.json', data=json_aluno)

    # Verifica se a requisição foi bem-sucedida (status code 200)
    if requisicao.status_code == 200:
        return {"mensagem": "Aluno criado com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao criar o aluno")

@app.put("/edita_aluno/{id}/")
async def edita_aluno(id: str, novo_aluno: Aluno):
    # Faz a requisição do tipo GET para verificar se o aluno existe no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/{id}/.json')

    if get_request.status_code == 404:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # Transforma o objeto Aluno em um dicionário
    dicionario_aluno = novo_aluno.dict()

    # Transforma o dicionário em JSON
    json_aluno = json.dumps(dicionario_aluno)

    # Faz a requisição do tipo PUT na API para atualizar o aluno com o ID correspondente
    put_request = requests.put(f'{BD_FIRE}/alunos/{id}/.json', data=json_aluno)

    # Verifica se a requisição de atualização foi bem-sucedida (status code 200)
    if put_request.status_code == 200:
        return {"mensagem": "Aluno atualizado com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao atualizar o aluno")

@app.delete("/deleta_aluno/{id}/")
async def deleta_aluno(id: str):
    # Faz a requisição do tipo GET para verificar se o aluno existe no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/{id}/.json')

    if get_request.status_code == 404:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # Verifica se o aluno existe no banco de dados
    aluno_data = get_request.json()
    if aluno_data is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # Faz a requisição do tipo DELETE na API para deletar o aluno com o ID correspondente
    delete_request = requests.delete(f'{BD_FIRE}/alunos/{id}/.json')

    # Verifica se a requisição de exclusão foi bem sucedida (status code 200)
    if delete_request.status_code == 200:
        return {"mensagem": "Aluno deletado com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao deletar o aluno")

@app.get("/le_alunos/")
async def le_alunos():
    # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/.json')

    if get_request.status_code == 200:
        alunos = get_request.json()
        return alunos
    else:
        raise HTTPException(status_code=500, detail="Erro ao listar os alunos")

@app.get("/get_aluno_info/{matricula}/")
async def get_aluno_info(matricula: int):
    # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/.json')

    if get_request.status_code == 200:
        alunos = get_request.json()

        # Procura o aluno com a matrícula especificada no banco de dados
        for id, aluno_info in alunos.items():
            if aluno_info.get('matricula') == matricula:
                return aluno_info
        
        # Se a matrícula não for encontrada, retorna uma exceção HTTP 404
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    else:
        raise HTTPException(status_code=500, detail="Erro ao listar as informações do aluno")
    
@app.get("/get_aluno_id/{matricula}/")
async def get_aluno_id(matricula: int):
    # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/.json')

    if get_request.status_code == 200:
        alunos = get_request.json()

        # Procura o ID do aluno com a matrícula especificada no banco de dados
        for id, dados_aluno in alunos.items():
            if dados_aluno.get('matricula') == matricula:
                return {"id": id}
        
        # Se a matrícula não for encontrada, retorna uma exceção HTTP 404
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    else:
        raise HTTPException(status_code=500, detail="Erro ao listar o id do alunos")


@app.get("/get_aluno_matricula/{id}/")
async def get_aluno_matricula(id: str):
    # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/.json')

    if get_request.status_code == 200:
        alunos = get_request.json()

        # Procura o aluno com o ID especificado no banco de dados
        for aluno_id, aluno_info in alunos.items():
            if aluno_info.get('id') == id:
                matricula = aluno_info.get('matricula')
                if matricula is not None:
                    return {"matricula": matricula}
        
        # Se o ID não for encontrado, retorna uma exceção HTTP 404
        raise HTTPException(status_code=404, detail="ID não encontrado")

    else:
        raise HTTPException(status_code=500, detail="Erro ao listar a matricula do aluno")

@app.get("/get_aluno_turma/{matricula}/")
async def get_aluno_turma(matricula: int):
    # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/.json')

    if get_request.status_code == 200:
        alunos = get_request.json()

        # Procura o aluno com a matrícula especificada no banco de dados
        for aluno_id, aluno_info in alunos.items():
            if aluno_info.get('matricula') == matricula:
                turma = aluno_info.get('turma')
                if turma is not None:
                    return {"turma": turma}
        
        # Se a matrícula não for encontrada, retorna uma exceção HTTP 404
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")

    else:
        raise HTTPException(status_code=500, detail="Erro ao listar a turma do aluno")

@app.get("/get_aluno_nome/{matricula}/")
async def get_aluno_nome(matricula: int):
    # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/.json')

    if get_request.status_code == 200:
        alunos = get_request.json()

        # Procura o aluno com a matrícula especificada no banco de dados
        for aluno_id, aluno_info in alunos.items():
            if aluno_info.get('matricula') == matricula:
                nome = aluno_info.get('nome')
                if nome is not None:
                    return {"nome": nome}
        
        # Se a matrícula não for encontrada, retorna uma exceção HTTP 404
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")

    else:
        raise HTTPException(status_code=500, detail="Erro ao listar os alunos")

@app.put("/add_aluno_id/{id_banco}")
async def add_aluno_id(id_banco: str, id_discord: str):

    # Verifique se id_banco está no banco de dados Firebase
    response = requests.get(f"{BD_FIRE}/alunos/{id_banco}.json")

    # Verifique se a resposta indica que o recurso existe
    if response.status_code == 200:
        try:
            # Tente converter a resposta para um objeto JSON
            response_json = response.json()
            logging.info(f"Response JSON: {response_json}")  # Adicione um log para verificar a resposta JSON

            # Verifique se a resposta é um JSON válido e não está vazia
            if response_json and isinstance(response_json, dict) and "id" in response_json:
                # O recurso existe, prossiga com a atualização

                # Crie o dicionário de frequência
                dicionario_frequencia = {"id": id_discord}

                # Transforme o dicionário em JSON
                json_freq = json.dumps(dicionario_frequencia)

                # Faça a solicitação PATCH na API Firebase
                requisicao = requests.patch(f'{BD_FIRE}/alunos/{id_banco}.json', data=json_freq)

                # Verifique se a solicitação PATCH foi bem-sucedida
                if requisicao.status_code == 200:
                    return {"message": "ID do Discord adicionado com sucesso"}
                else:
                    raise HTTPException(status_code=500, detail="Falha na solicitação PATCH")
            else:
                raise HTTPException(status_code=404, detail="ID do banco não encontrado")
        except ValueError:
            raise HTTPException(status_code=500, detail="Erro ao processar a resposta JSON")
    else:
        raise HTTPException(status_code=500, detail="Erro ao acessar o banco de dados Firebase")
    
@app.get("/comparar_matricula_aluno/{matricula}/")
async def comparar_matricula_aluno(matricula: int):
    # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
    get_request = requests.get(f'{BD_FIRE}/alunos/.json')

    if get_request.status_code == 200:
        alunos = get_request.json()

        # Procura a matrícula especificada no banco de dados
        for aluno_id, aluno_info in alunos.items():
            if aluno_info.get('matricula') == matricula:
                return {"matricula": matricula}
        
        # Se a matrícula não for encontrada, retorna False
        return False

    else:
        return False  # Em caso de erro, também retorna False

@app.get("/comparar_id_aluno/{aluno_id}/")
async def comparar_id_aluno(aluno_id: str):
    async with httpx.AsyncClient() as client:
        # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
        get_response = await client.get(f'{BD_FIRE}/alunos/.json')

        if get_response.status_code == 200:
            alunos = get_response.json()

            # Procura o aluno com o ID especificado no banco de dados
            for aluno_key, aluno_info in alunos.items():
                if str(aluno_key) == str(aluno_id):
                    return {aluno_id}
            
            # Se o ID não for encontrado, retorna None
            return None

        else:
            return None  # Em caso de erro na requisição, também retorna None

@app.patch("/reset_aluno_id/{aluno_id}/")
async def reset_aluno_id(aluno_id: str):
    # Faz uma requisição GET para ler os dados do aluno
    aluno_ref = requests.get(f'{BD_FIRE}/alunos/{aluno_id}.json')
    aluno_data = aluno_ref.json()  # Use .json() em vez de .get()

    if aluno_ref.status_code == 200:
        if aluno_data is not None:
            # Transforma o ID em 0
            aluno_data["id"] = 0

            # Atualize os dados do aluno com uma solicitação PATCH
            patch_request = requests.patch(f'{BD_FIRE}/alunos/{aluno_id}.json', json=aluno_data)

            if patch_request.status_code == 200:
                return {"mensagem": "ID redefinido para 0 com sucesso"}
            else:
                raise HTTPException(status_code=500, detail="Erro ao atualizar os dados do aluno")
        else:
            raise HTTPException(status_code=404, detail="Aluno não encontrado no banco de dados")
    elif aluno_ref.status_code == 404:
        raise HTTPException(status_code=404, detail="Aluno não encontrado no banco de dados")
    else:
        raise HTTPException(status_code=500, detail="Erro ao acessar o banco de dados Firebase")

@app.patch("/set_presenca/{data}/{aluno_id}/")
async def set_presenca_route(data: str, aluno_id: str):
    # Faz a requisição do tipo GET para listar todos os alunos no banco de dados
    async with httpx.AsyncClient() as client:
        get_response = await client.get(f'{BD_FIRE}/alunos/.json')

    if get_response.status_code == 200:
        alunos = get_response.json()

        # Verifica se o aluno com o ID especificado está na lista
        if aluno_id in alunos:
            # Cria um dicionário de presença com a data e o valor 1
            dicionario_presenca = {data: 1}

            # Faz a requisição do tipo PATCH na API para atualizar a presença do aluno
            async with httpx.AsyncClient() as client:
                patch_response = await client.patch(f'{BD_FIRE}/alunos/{aluno_id}/frequencia.json', json=dicionario_presenca)

            # Verifica se a requisição de atualização foi bem-sucedida (status code 200)
            if patch_response.status_code == 200:
                # Após a atualização, faz uma solicitação GET para obter os dados atualizados
                async with httpx.AsyncClient() as client:
                    get_updated_response = await client.get(f'{BD_FIRE}/alunos/{aluno_id}.json')

                # Verifica o status code da resposta e o corpo da resposta
                if get_updated_response.status_code == 200:
                    updated_data = get_updated_response.json()
                    return {"mensagem": "Presença atualizada com sucesso"}
                else:
                    raise HTTPException(status_code=500, detail="Erro ao obter dados atualizados após a atualização")
            else:
                raise HTTPException(status_code=500, detail="Erro ao atualizar a presença")
        else:
            raise HTTPException(status_code=404, detail=f"Aluno com ID {aluno_id} não encontrado no banco de dados")
    else:
        raise HTTPException(status_code=500, detail="Erro ao buscar alunos no banco de dados")




