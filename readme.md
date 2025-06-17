# Projeto Final - Tópicos Avançados em Computadores

Este projeto foi desenvolvido para a disciplina de **Tópicos Avançados em Computadores** da Universidade de Brasília (UnB), com foco em **Pesquisa Operacional**.

## Tema

O tema do projeto é um **Gerador de Grade Ótima**. O sistema recebe turmas de usuários, cada uma com um peso diferente baseado no desejo do usuário, e gera uma grade ótima considerando as restrições do problema.

## Descrição

O objetivo é criar uma grade de horários que maximize a satisfação dos usuários, levando em conta:

- Pesos diferentes para cada turma, conforme o desejo do usuário.
- Restrições detalhadas nos comentários do arquivo `main.py`, como:
  - Carga horária máxima informada pelo usuário.
  - Associação completa das aulas de uma determinada turma.
  - No máximo uma turma para cada disciplina.
  - Conflitos de horários entre disciplinas.
  - Evitar/minimizar buracos.
  - Distribuição espalhada/centralizada das turmas pelos dias.

O algoritmo utiliza técnicas de pesquisa operacional e faz uso da biblioteca **OR-Tools** do Google para programação linear, a fim de encontrar a melhor solução possível respeitando todas as restrições impostas.

## Como usar

1. Instale as dependências necessárias, incluindo a biblioteca `ortools` (veja os comentários em `main.py`).
2. Execute o arquivo `main.py` para gerar a grade ótima.

Para mais detalhes sobre as restrições e funcionamento, consulte os comentários no arquivo `main.py`.
