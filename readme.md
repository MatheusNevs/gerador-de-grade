# Projeto Final - Tópicos Avançados em Computadores

Este projeto foi desenvolvido para a disciplina de **Tópicos Avançados em Computadores** da Universidade de Brasília (UnB), com foco em **Pesquisa Operacional**.

## Tema

O tema do projeto é um **Gerador de Grade Ótima**. O sistema recebe turmas de usuários, cada uma com um peso diferente baseado no desejo do usuário, e gera uma grade ótima considerando as restrições do problema e algumas preferências informadas.

## Descrição

O objetivo é criar uma grade de horários que maximize a satisfação dos usuários, levando em conta:

- Restrições implementadas:
  - Carga horária total alocada não pode exceder o limite máximo definido.
  - Todas as aulas de uma turma devem ser alocadas juntas (não é possível escolher apenas parte dos horários de uma turma).
  - No máximo uma turma pode ser escolhida para cada disciplina.
  - Não pode haver conflitos de horários entre turmas (nenhuma sobreposição de horários).
- Função objetivo:
  - Maximizar soma de pesos de turmas (informados pelo usuário).
  - Minimizar o número de buracos na grade.
  - Maximizar (ou minimizar, conforme preferência) a concentração das aulas em menos dias.
  - E, tudo junto: Maximizar a soma ponderada das preferências (as 3 acimas) dos usuários pelas turmas escolhidas, a partir de coeficientes para cada tipo de preferência informados pelo usuário.

O algoritmo utiliza técnicas de programação linear inteira mista, implementadas com a biblioteca **OR-Tools** do Google, para encontrar a melhor solução possível respeitando todas as restrições e preferências definidas.

## Como usar

1. Instale as dependências necessárias, incluindo a biblioteca `ortools` (veja os comentários em `main.py`).
2. Execute o arquivo `main.py` para gerar a grade ótima.

Para mais detalhes sobre as restrições e funcionamento, consulte os comentários no arquivo `main.py`.
