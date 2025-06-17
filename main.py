from ortools.linear_solver import pywraplp

# Configurações
D = 5  # dias da semana
H = 3  # horários por dia
CARGA_HORARIA_MAXIMA = 45  # 3 slots de 15h

# Entrada: (id_turma, cod_disciplina, horarios, peso)
entrada = [
    ("MAT101-T1", "MAT101", [(0, 0), (0, 1)], 0.9),
    ("MAT101-T2", "MAT101", [(1, 0), (1, 1)], 0.85),
    ("FIS102-T1", "FIS102", [(0, 2)], 0.8),  # cria buraco se MAT101-T1 for escolhida
    ("BIO104-T1", "BIO104", [(2, 0)], 0.6),
]

# Solver
solver = pywraplp.Solver.CreateSolver("SCIP")
x = {}  # variáveis de turma
for turma_id, _, _, _ in entrada:
    x[turma_id] = solver.IntVar(0, 1, turma_id)

# Variáveis de ocupação na grade: ocupado[d][h] = 1 se qualquer turma ocupar (d, h)
ocupado = {}
for d in range(D):
    for h in range(H):
        ocupado[(d, h)] = solver.IntVar(0, 1, f"ocupado_{d}_{h}")

# Ligar x[turma] ↔ ocupado[d][h]
for d in range(D):
    for h in range(H):
        turmas_aqui = [t for t, _, hs, _ in entrada if (d, h) in hs]
        if turmas_aqui:
            solver.Add(ocupado[(d, h)] >= solver.Sum(x[t] for t in turmas_aqui))

# Restrição: conflito de horários
ocupacao = {}
for turma_id, _, horarios, _ in entrada:
    for d, h in horarios:
        if (d, h) not in ocupacao:
            ocupacao[(d, h)] = []
        ocupacao[(d, h)].append(turma_id)

for turmas_mesmo_horario in ocupacao.values():
    solver.Add(solver.Sum(x[t] for t in turmas_mesmo_horario) <= 1)

# Restrição: uma turma por disciplina
disciplinas = {}
for turma_id, cod_disciplina, _, _ in entrada:
    if cod_disciplina not in disciplinas:
        disciplinas[cod_disciplina] = []
    disciplinas[cod_disciplina].append(turma_id)

for turmas_disciplina in disciplinas.values():
    solver.Add(solver.Sum(x[t] for t in turmas_disciplina) <= 1)

# Restrição: carga horária
solver.Add(
    solver.Sum(15 * len(hs) * x[t] for t, _, hs, _ in entrada) <= CARGA_HORARIA_MAXIMA
)

# ❗ Restrição para eliminar buracos:
for d in range(D):
    for h in range(1, H - 1):
        # Sem buraco: se há aula antes e depois, deve haver no meio também
        solver.Add(ocupado[(d, h - 1)] + ocupado[(d, h + 1)] - ocupado[(d, h)] <= 1)

# Objetivo: maximizar peso total
solver.Maximize(solver.Sum(p * x[t] for t, _, _, p in entrada))

# Solve
status = solver.Solve()

# Resultado
if status == pywraplp.Solver.OPTIMAL:
    print("Grade ótima sem buracos encontrada:")
    for turma_id, cod, hs, peso in entrada:
        if x[turma_id].solution_value() == 1:
            print(f"✓ {turma_id} ({cod}) → {hs} | peso {peso}")
    carga = sum(15 * len(hs) * x[t].solution_value() for t, _, hs, _ in entrada)
    print(f"Carga horária total: {carga}h")
else:
    print("❌ Nenhuma solução ótima encontrada.")
