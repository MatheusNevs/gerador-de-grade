import requests

# Exemplo de corpo de requisição esperado para o endpoint /gerar-grade
# Pode ser usado em ferramentas como Postman ou curl (com -H "Content-Type: application/json")
exemplo_requisicao = {
  "dias": 5,
  "horarios": 8,
  "carga_horaria_maxima": 240,
  "peso_preferencia": 2,
  "peso_buracos": 3,
  "peso_dias": 1,
  "centralizado": True,
  "turmas": [
    {
      "id_turma": "MAT101-T1",
      "cod_disciplina": "MAT101",
      "codigo_horario": "24M34",
      "preferencia": 5
    },
    {
      "id_turma": "FIS102-102",
      "cod_disciplina": "FIS102",
      "codigo_horario": "35T25",
      "preferencia": 3
    }
  ,
    {
      "id_turma": "ICE-103",
      "cod_disciplina": "ICE",
      "codigo_horario": "24T23",
      "preferencia": 3
    }]
  
}

resp = requests.get("http://localhost:5000/gerar-grade", json=exemplo_requisicao)
print(resp.json())