from ortools.linear_solver import pywraplp

###### CONFIGURAÇÃO DO PROBLEMA E ENTRADAS (PARA TESTE) ######

# Configurações
D = 5  # dias da semana
H = 8  # horários por dia
CARGA_HORARIA_MAXIMA = 390  # carga horária máxima total pedida (em horas)

# Pesos para o objetivo (ajustáveis conforme a preferência do usuário)
PESO_MAXIMIZAR_PREFERENCIA = 0.5  # Peso referente à maximização de preferências
PESO_MINIMIZAR_BURACOS = 0.2
PESO_QUANTIDADE_DIAS = (
    0.3  # Peso referente à distribuição mais uniforme ou centralizada
)

# Preferências
DISTRIBUICAO_CENTRALIZADA = (
    False  # Se True, distribui turmas de forma mais centralizada
)

# Entrada: (id_turma, cod_disciplina, horarios, peso)
entrada = [
    ("MAT101-T1", "MAT101", [(0, 0), (0, 1)], 0.9),
    ("MAT101-T2", "MAT101", [(1, 2), (1, 3)], 0.85),
    ("FIS102-T1", "FIS102", [(0, 4), (0, 5)], 0.8),
    ("BIO104-T1", "BIO104", [(2, 0), (2, 1)], 0.6),
    ("QUI105-T1", "QUI105", [(2, 2), (2, 3), (2, 4)], 0.7),
    ("HIS110-T1", "HIS110", [(3, 5), (3, 6)], 0.5),
    ("GEO120-T1", "GEO120", [(3, 0), (3, 1), (3, 2)], 0.65),
    ("MAT101-T3", "MAT101", [(4, 6), (4, 7)], 0.8),
    ("FIS102-T2", "FIS102", [(1, 4), (1, 5)], 0.75),
    ("BIO104-T2", "BIO104", [(4, 0), (4, 1)], 0.55),
    ("QUI105-T2", "QUI105", [(0, 6), (0, 7)], 0.6),
    ("HIS110-T2", "HIS110", [(1, 6), (1, 7)], 0.45),
    ("GEO120-T2", "GEO120", [(2, 6), (2, 7)], 0.5),
    ("MAT201-T1", "MAT201", [(1, 0), (1, 1)], 0.7),
    ("MAT201-T2", "MAT201", [(3, 3), (3, 4)], 0.65),
    ("FIS202-T1", "FIS202", [(2, 4), (2, 5)], 0.6),
    ("FIS202-T2", "FIS202", [(4, 2), (4, 3)], 0.55),
    ("BIO204-T1", "BIO204", [(0, 2), (0, 3)], 0.8),
    ("BIO204-T2", "BIO204", [(3, 7), (4, 5)], 0.75),
    ("QUI205-T1", "QUI205", [(1, 5), (1, 6)], 0.7),
    ("QUI205-T2", "QUI205", [(2, 3), (2, 4)], 0.65),
    ("HIS210-T1", "HIS210", [(0, 5), (1, 7)], 0.6),
    ("HIS210-T2", "HIS210", [(4, 4), (4, 5)], 0.55),
    ("GEO220-T1", "GEO220", [(3, 3), (3, 4), (3, 5)], 0.7),
    ("GEO220-T2", "GEO220", [(1, 1), (1, 2)], 0.6),
    ("MAT301-T1", "MAT301", [(2, 7), (3, 6)], 0.8),
    ("FIS302-T1", "FIS302", [(0, 4), (1, 4)], 0.75),
    ("BIO304-T1", "BIO304", [(4, 0), (4, 2)], 0.7),
    ("QUI305-T1", "QUI305", [(2, 5), (2, 6)], 0.65),
]

###### FIM DA CONFIGURAÇÃO DO PROBLEMA ######

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

# 1. Normalização das Preferências
solver.Maximize(preferencias)
max_preferencias = solver.Solve()

if max_preferencias == pywraplp.Solver.OPTIMAL:
    max_preferencia_real = solver.Objective().Value()
else:
    print(
        "❌ Não foi possível encontrar uma solução viável na Fase 1. A grade pode ser impossível."
    )
    exit()

objetivo_preferencias_norm = (
    preferencias / max_preferencia_real if max_preferencia_real > 0 else 0
)

# 2. Normalização dos Buracos
max_buracos_possivel = D * (H - 2) if H > 2 else 1  # Evita divisão por zero se H<=2
objetivo_buracos_norm = (
    buracos / max_buracos_possivel if max_buracos_possivel > 0 else 0
)

# 3. Normalização da Quantidade de Dias
objetivo_dias_norm = quantidade_dias / D if D > 0 else 0

# Definindo a função objetivo final
solver.Maximize(
    PESO_MAXIMIZAR_PREFERENCIA * objetivo_preferencias_norm
    - PESO_MINIMIZAR_BURACOS * objetivo_buracos_norm
    + PESO_QUANTIDADE_DIAS * objetivo_dias_norm
)

# Solve
status = solver.Solve()

# Resultado
if status == pywraplp.Solver.OPTIMAL:
    # Inicializa matriz do calendário (horários como linhas, dias como colunas)
    calendario = [["-" for _ in range(D)] for _ in range(H)]
    carga_horaria_total = 0
    for turma_id, _, hs, _ in entrada:
        if x[turma_id].solution_value() == 1:
            carga_horaria_total += 15 * len(hs)
            for d, h in hs:
                calendario[h][d] = turma_id
    # Imprime cabeçalho
    col_width = max(len(turma_id) for turma_id, _, _, _ in entrada) + 2
    print("     " + "".join(f"D{d}".center(col_width) for d in range(D)))
    for h in range(H):
        linha = "".join(f"{calendario[h][d]:^{col_width}}" for d in range(D))
        print(f"H{h}: {linha}")
    print(f"\nCarga horária total alocada: {carga_horaria_total}")
else:
    print("❌ Nenhuma solução ótima encontrada.")