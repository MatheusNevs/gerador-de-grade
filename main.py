from ortools.linear_solver import pywraplp

# Configurações via input
D = int(input())
H = int(input())
CARGA_HORARIA_MAXIMA = int(input())

# Pesos para o objetivo
PESO_MAXIMIZAR_PREFERENCIA = float(input())
PESO_MINIMIZAR_BURACOS = float(input())
PESO_QUANTIDADE_DIAS = float(input())

# Preferências
DISTRIBUICAO_CENTRALIZADA = input().strip().lower() == "s"

# Entrada: (id_turma, cod_disciplina, horarios, peso)
entrada = []
while True:
    linha = input()
    if not linha.strip():
        break
    try:
        partes = linha.split(maxsplit=3)
        turma_id = partes[0]
        cod_disciplina = partes[1]
        horarios = eval(partes[2])
        preferencia = float(partes[3])
        entrada.append((turma_id, cod_disciplina, horarios, preferencia))
    except Exception as e:
        print("Entrada inválida. Tente novamente.")
        exit()

# Solver
solver = pywraplp.Solver.CreateSolver("SCIP")

# Variáveis de decisão: x[turma_id] = 1 se a turma for alocada, 0 caso contrário
x = {}
for turma_id, _, _, _ in entrada:
    x[turma_id] = solver.IntVar(0, 1, turma_id)

# Variáveis de decisão auxiliares, ocupação na grade: ocupado[d][h] = 1 se qualquer turma ocupar (d, h)
ocupado = {}
for d in range(D):
    for h in range(H):
        ocupado[(d, h)] = solver.IntVar(0, 1, f"ocupado_{d}_{h}")

# Ligar x[turma] ↔ ocupado[d][h]
for d in range(D):
    for h in range(H):
        turmas_aqui = [t for t, _, hs, _ in entrada if (d, h) in hs]
        soma_x = solver.Sum(x[t] for t in turmas_aqui)
        solver.Add(ocupado[(d, h)] >= soma_x)
        solver.Add(ocupado[(d, h)] <= soma_x)

# Restrição 1: conflito de horários
ocupacao = {}
for turma_id, _, horarios, _ in entrada:
    for d, h in horarios:
        if (d, h) not in ocupacao:
            ocupacao[(d, h)] = []
        ocupacao[(d, h)].append(turma_id)

for turmas_mesmo_horario in ocupacao.values():
    solver.Add(solver.Sum(x[t] for t in turmas_mesmo_horario) <= 1)

# Restrição 2: uma turma por disciplina
disciplinas = {}
for turma_id, cod_disciplina, _, _ in entrada:
    if cod_disciplina not in disciplinas:
        disciplinas[cod_disciplina] = []
    disciplinas[cod_disciplina].append(turma_id)

for turmas_disciplina in disciplinas.values():
    solver.Add(solver.Sum(x[t] for t in turmas_disciplina) <= 1)

# Restrição 3: carga horária
solver.Add(
    solver.Sum(15 * len(hs) * x[t] for t, _, hs, _ in entrada) <= CARGA_HORARIA_MAXIMA
)

# Função objetivo 1: minimizar buracos
# Um buraco ocorre quando existe um horário livre (ocupado == 0) entre dois horários ocupados no mesmo dia
antes, depois = {}, {}
for d in range(D):
    for h in range(H):
        antes[(d, h)] = solver.IntVar(0, 1, f"antes_{d}_{h}")
        depois[(d, h)] = solver.IntVar(0, 1, f"depois_{d}_{h}")

# Condições de fronteira
for d in range(D):
    solver.Add(antes[(d, 0)] == 0)
    solver.Add(depois[(d, H - 1)] == 0)

# Propagação de ‘antes’
for d in range(D):
    for h in range(1, H):
        solver.Add(antes[(d, h)] >= ocupado[(d, h - 1)])
        solver.Add(antes[(d, h)] >= antes[(d, h - 1)])
        solver.Add(antes[(d, h)] <= ocupado[(d, h - 1)] + antes[(d, h - 1)])

# Propagação de ‘depois’
for d in range(D):
    for h in range(H - 2, -1, -1):
        solver.Add(depois[(d, h)] >= ocupado[(d, h + 1)])
        solver.Add(depois[(d, h)] >= depois[(d, h + 1)])
        solver.Add(depois[(d, h)] <= ocupado[(d, h + 1)] + depois[(d, h + 1)])

# Definição de buracos
buracos_list = []
for d in range(D):
    for h in range(1, H - 1):
        b = solver.IntVar(0, 1, f"buraco_{d}_{h}")
        solver.Add(b >= antes[(d, h)] + depois[(d, h)] - 1 - ocupado[(d, h)])
        solver.Add(b <= antes[(d, h)])
        solver.Add(b <= depois[(d, h)])
        solver.Add(b <= 1 - ocupado[(d, h)])
        buracos_list.append(b)
buracos = solver.Sum(buracos_list)

# Funcao objetivo 2: maximizar preferências
preferencias = solver.Sum(p * x[turma_id] for turma_id, _, _, p in entrada)

# Funcao objetivo 3: distribuir turmas de forma mais uniforme ou centralizada
dias_ocupados = []
for d in range(D):
    dia_ocupado = solver.IntVar(0, 1, f"dia_ocupado_{d}")
    # Se qualquer ocupado[(d, h)] == 1, então dia_ocupado deve ser 1
    for h in range(H):
        solver.Add(dia_ocupado >= ocupado[(d, h)])
    # Se todos ocupado[(d, h)] == 0, então dia_ocupado deve ser 0
    solver.Add(dia_ocupado <= solver.Sum([ocupado[(d, h)] for h in range(H)]))
    dias_ocupados.append(dia_ocupado)
quantidade_dias = solver.Sum(dias_ocupados)

# Se centralizado,quantidade_dias é o número de dias não ocupados
if DISTRIBUICAO_CENTRALIZADA:
    quantidade_dias = D - quantidade_dias

solver.Maximize(
    PESO_MAXIMIZAR_PREFERENCIA * preferencias
    - PESO_MINIMIZAR_BURACOS * buracos
    + PESO_QUANTIDADE_DIAS * quantidade_dias
)

# Solve
status = solver.Solve()

# Resultado
if status == pywraplp.Solver.OPTIMAL:
    # Inicializa matriz do calendário (horários como linhas, dias como colunas)
    calendario = [["-" for _ in range(D)] for _ in range(H)]
    for turma_id, _, hs, _ in entrada:
        if x[turma_id].solution_value() == 1:
            for d, h in hs:
                calendario[h][d] = turma_id
    print(calendario)
else:
    print("❌ Nenhuma solução ótima encontrada.")
