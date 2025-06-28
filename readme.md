# Projeto Final - Tópicos Avançados em Computadores

Este projeto foi desenvolvido para a disciplina de **Tópicos Avançados em Computadores** da Universidade de Brasília (UnB), com foco em **Pesquisa Operacional**.

## Tema

O tema do projeto é um **Gerador de Grade Ótima**. O sistema recebe um conjunto de turmas, cada uma com um peso que representa o desejo do usuário, e gera uma grade horária otimizada, respeitando diversas restrições e preferências.

## Arquitetura do Projeto

O projeto evoluiu de um script único para uma aplicação web de três camadas:

1.  **Front-end (Interface Web)**: Uma interface interativa construída com **React (Vite)**, onde o usuário pode configurar os parâmetros da otimização, gerenciar a lista de turmas e visualizar a grade gerada.
2.  **Back-end (Servidor API)**: Um servidor construído em **Flask (Python)** que expõe uma API REST. Ele recebe as configurações do front-end, atua como uma ponte para o motor de otimização e retorna o resultado de forma estruturada.
3.  **Otimizador (Motor de Otimização)**: O script original em Python (`optimizer.py`) que utiliza a biblioteca **OR-Tools** do Google. Ele é executado como um subprocesso pelo servidor Flask, garantindo que a lógica de otimização pesada seja isolada da API.

## Descrição da Funcionalidade

O objetivo é criar uma grade de horários que maximize a satisfação do usuário, levando em conta:

- **Restrições implementadas**:
  - A carga horária total alocada não pode exceder o limite máximo definido.
  - Todas as aulas de uma turma devem ser alocadas juntas.
  - No máximo uma turma pode ser escolhida para cada disciplina.
  - Não pode haver conflitos de horários entre turmas.
- **Função Objetivo Ponderada**:
  - **Maximizar** a soma dos pesos de preferência das turmas escolhidas.
  - **Minimizar** o número de "buracos" (horários livres entre aulas) na grade.
  - **Otimizar** a distribuição de aulas (seja concentrando em menos dias ou espalhando, conforme a preferência do usuário).

O algoritmo utiliza técnicas de **programação linear inteira mista**, implementadas com a biblioteca **OR-Tools**, para encontrar a melhor solução possível.

## Como Executar o Projeto Completo

Para executar a aplicação, você precisará iniciar o back-end e o front-end em terminais separados.

### Pré-requisitos

- Python 3.8+ e `pip`
- Node.js 18+ e `npm`
- Um ambiente virtual para Python (recomendado)

### 1. Configuração e Execução do Back-end

O servidor Flask é responsável por receber as requisições e orquestrar a otimização.

```bash
# 1. Navegue até a pasta raiz do projeto (onde estão server.py e optimizer.py)

# 2. Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows, use `venv\Scripts\activate`

# 3. Instale as dependências Python
# É recomendado criar um arquivo requirements.txt com o conteúdo abaixo:
# Flask
# Flask-Cors
# ortools
pip install -r requirements.txt # Ou instale individualmente

# 4. Inicie o servidor Flask
python3 server.py

# O servidor estará rodando em http://localhost:5000
```

### 2. Configuração e Execução do Front-end

A interface web permite a interação com o sistema.

```bash
# 1. Em um NOVO terminal, navegue até a pasta do seu projeto front-end

# 2. Instale as dependências do Node.js
npm install

# 3. Inicie o servidor de desenvolvimento do Vite
npm run dev

# O front-end estará acessível no endereço fornecido, geralmente http://localhost:5173
```

### 3. Utilização

Com ambos os servidores rodando, abra seu navegador e acesse a URL do front-end (ex: `http://localhost:5173`). Configure os parâmetros, adicione as turmas e clique em "Gerar Grade" para ver a mágica acontecer!

## Documentação da API

O back-end expõe um único endpoint para gerar a grade.

### Endpoint: `POST /gerar-grade`

Este endpoint recebe todos os parâmetros e a lista de turmas, executa o otimizador e retorna a grade ótima encontrada.

#### Corpo da Requisição (Request Body)

O corpo da requisição deve ser um JSON com a seguinte estrutura:

```json
{
  "dias": 5,
  "horarios": 8,
  "carga_horaria_maxima": 240,
  "peso_preferencia": 0.6,
  "peso_buracos": 0.3,
  "peso_dias": 0.3,
  "centralizado": true,
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
  ]
}
```

#### Resposta de Sucesso (200 OK)

Se uma solução for encontrada, a resposta será um JSON contendo a grade, as métricas e as turmas selecionadas.

```json
{
  "mensagem": "Solução de grade ótima encontrada!",
  "calendario": [
    ["----", "----", "----", "----", "----"],
    ["----", "----", "FIS102-102", "----", "FIS102-102"],
    ["MAT101-T1", "----", "----", "MAT101-T1", "----"],
    ["MAT101-T1", "----", "----", "MAT101-T1", "----"],
    ["----", "----", "----", "----", "----"],
    ["----", "----", "----", "----", "----"],
    ["----", "----", "----", "----", "----"],
    ["----", "----", "----", "----", "----"]
  ],
  "metricas": {
    "soma_preferencias": 8.0,
    "numero_buracos": 0,
    "dias_com_aula": 3,
    "carga_horaria_total": 120
  },
  "turmas_selecionadas": ["FIS102-102", "MAT101-T1"]
}
```

#### Resposta de Erro

Se nenhuma solução for encontrada ou ocorrer um erro, a resposta indicará o problema.

```json
{
  "erro": "Nenhuma solução ótima ou viável encontrada.",
  "mensagem": "Tente ajustar os pesos ou a carga horária máxima."
}
```
