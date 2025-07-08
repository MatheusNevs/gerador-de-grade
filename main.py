import re
from ortools.linear_solver import pywraplp

def coletar_configuracoes():
    print("--- Configuração da Otimização ---")
    
    while True:
        resposta_dist = input("Deseja centralizar as aulas em menos dias (s/n)? ").lower().strip()
        if resposta_dist == 's':
            dist_centralizada = True
            break
        elif resposta_dist == 'n':
            dist_centralizada = False
            break
        else:
            print("Erro: Resposta inválida. Por favor, digite 's' para sim ou 'n' para não.")
            
    while True:
        try:
            ch_max = int(input("Digite a carga horária máxima total (ex: 390): ").strip())
            break
        except ValueError:
            print("Erro: Por favor, insira um número inteiro.")

    print("\nDigite os pesos para a função objetivo (valores de 0 a 100).")
    
    while True:
        try:
            p_pref_100 = float(input("Peso para MAXIMIZAR preferências (0-100): ").strip())
            if 0.0 <= p_pref_100 <= 100.0:
                break
            print("Erro: O peso deve estar entre 0 e 100.")
        except ValueError:
            print("Erro: Por favor, insira um número.")
            
    while True:
        try:
            p_buracos_100 = float(input("Peso para MINIMIZAR buracos (0-100): ").strip())
            if 0.0 <= p_buracos_100 <= 100.0:
                break
            print("Erro: O peso deve estar entre 0 e 100.")
        except ValueError:
            print("Erro: Por favor, insira um número.")

    while True:
        try:
            p_dias_100 = float(input("Peso para a quantidade de dias (0-100): ").strip())
            if 0.0 <= p_dias_100 <= 100.0:
                break
            print("Erro: O peso deve estar entre 0 e 100.")
        except ValueError:
            print("Erro: Por favor, insira um número.")
            
    soma_pesos = p_pref_100 + p_buracos_100 + p_dias_100
    
    if soma_pesos == 0:
        print("Aviso: Todos os pesos são 0. A otimização não terá um objetivo claro.")
        p_pref_norm, p_buracos_norm, p_dias_norm = 0.0, 0.0, 0.0
    else:
        p_pref_norm = p_pref_100 / soma_pesos
        p_buracos_norm = p_buracos_100 / soma_pesos
        p_dias_norm = p_dias_100 / soma_pesos
        
    return dist_centralizada, ch_max, p_pref_norm, p_buracos_norm, p_dias_norm


D = 6 
H = 15
DIA_MAP = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5}
HORARIO_MAP = {
    'M1': 0, 'M2': 1, 'M3': 2, 'M4': 3, 'M5': 4,
    'T1': 5, 'T2': 6, 'T3': 7, 'T4': 8, 'T5': 9, 'T6': 10,
    'N1': 11, 'N2': 12, 'N3': 13, 'N4': 14,
}
HORARIO_DISPLAY_LABELS = [
    'M1 08:00 - 08:55 ',
    'M2 08:55 - 09:50 ',
    'M3 10:00 - 10:55',
    'M4 10:55 - 11:50',
    'M5 12:00 - 12:55',
    'T1 13:00 - 13:50',
    'T2 14:00 - 14:55',
    'T3 14:55 - 15:50',
    'T4 16:00 - 16:55',
    'T5 16:55 - 17:50',
    'T6 18:00 - 18:50',
    'N1 19:00 - 19:50',
    'N2 19:50 - 20:40',
    'N3 20:50 - 21:40',
    'N4 21:40 - 22:30',
]

def parse_horario(horario_str):
    horarios_finais = []
    partes = horario_str.strip().strip('()').split()
    for parte in partes:
        match = re.match(r'(\d+)([MTN])(\d+)', parte, re.IGNORECASE)
        if not match:
            print(f"AVISO: Formato de horário inválido ignorado: '{parte}'")
            continue
        dias_str, turno, horarios_str = match.groups()
        turno = turno.upper()
        for dia_char in dias_str:
            if dia_char not in DIA_MAP:
                print(f"AVISO: Dia inválido '{dia_char}' na parte '{parte}' foi ignorado.")
                continue
            dia_idx = DIA_MAP[dia_char]
            for horario_char in horarios_str:
                chave_horario = turno + horario_char
                if chave_horario not in HORARIO_MAP:
                    print(f"AVISO: Horário inválido '{chave_horario}' na parte '{parte}' foi ignorado.")
                    continue
                horario_idx = HORARIO_MAP[chave_horario]
                if (dia_idx, horario_idx) not in horarios_finais:
                    horarios_finais.append((dia_idx, horario_idx))
    return horarios_finais

def coletar_entradas():
    entradas = []
    print("\n--- Cadastro de Disciplinas para Otimização ---")
    print("Insira os dados de cada turma. Digite 'fim' no código da disciplina para terminar.")
    while True:
        while True:
            cod_disciplina = input("\nDigite o código da disciplina (ex: CIC0105) ou 'fim': ").strip().upper()
            if cod_disciplina == 'FIM':
                break
            if len(cod_disciplina) == 7:
                break
            else:
                print("Erro: O código da disciplina deve ter exatamente 7 caracteres.")
        
        if cod_disciplina == 'FIM':
            break
        
        while True:
            turma_input = input(f"Digite a turma para {cod_disciplina} (01 a 99): ").strip()
            if turma_input.isdigit():
                turma_num = int(turma_input)
                if 1 <= turma_num <= 99:
                    turma = f"{turma_num:02d}"
                    break
                else:
                    print("Erro: O número da turma deve estar entre 1 e 99.")
            else:
                print("Erro: A turma deve ser um número.")

        while True:
            horario_str = input(f"Digite o(s) horário(s) para {cod_disciplina}-{turma} (ex: 35M12): ")
            horarios = parse_horario(horario_str)
            if horarios:
                break
            else:
                print("Erro: O horário fornecido não resultou em nenhuma aula válida. Verifique o formato e tente novamente.")

        while True:
            try:
                peso_str = input(f"Digite o peso/preferência para esta turma (0 a 100): ").strip()
                peso = float(peso_str)
                if 0 <= peso <= 100:
                    break
                else:
                    print("Erro: O peso deve ser um número entre 0 e 100.")
            except ValueError:
                print("Erro: Por favor, insira um valor numérico para o peso.")

        turma_id = f"{cod_disciplina}-{turma}"
        peso_normalizado = peso / 100.0
        entradas.append((turma_id, cod_disciplina, horarios, peso_normalizado))
        print(f"✅ Turma '{turma_id}' adicionada com sucesso.")
    return entradas


DISTRIBUICAO_CENTRALIZADA, CARGA_HORARIA_MAXIMA, PESO_MAXIMIZAR_PREFERENCIA, PESO_MINIMIZAR_BURACOS, PESO_QUANTIDADE_DIAS = coletar_configuracoes()
entrada = coletar_entradas()

if not entrada:
    print("\nNenhuma turma foi inserida. Encerrando o programa.")
    exit()

print("\n--- Iniciando Otimização com as Configurações e Turmas Fornecidas ---")


solver = pywraplp.Solver.CreateSolver("SCIP")

x = {}
for turma_id, _, _, _ in entrada:
    x[turma_id] = solver.IntVar(0, 1, turma_id)

ocupado = {}
for d in range(D):
    for h in range(H):
        ocupado[(d, h)] = solver.IntVar(0, 1, f"ocupado_{d}_{h}")

for d in range(D):
    for h in range(H):
        turmas_aqui = [t for t, _, hs, _ in entrada if (d, h) in hs]
        soma_x = solver.Sum(x[t] for t in turmas_aqui)
        solver.Add(ocupado[(d, h)] == soma_x)

ocupacao = {}
for turma_id, _, horarios, _ in entrada:
    for d, h in horarios:
        if (d, h) not in ocupacao:
            ocupacao[(d, h)] = []
        ocupacao[(d, h)].append(turma_id)

for turmas_mesmo_horario in ocupacao.values():
    solver.Add(solver.Sum(x[t] for t in turmas_mesmo_horario) <= 1)

disciplinas = {}
for turma_id, cod_disciplina, _, _ in entrada:
    if cod_disciplina not in disciplinas:
        disciplinas[cod_disciplina] = []
    disciplinas[cod_disciplina].append(turma_id)

for turmas_disciplina in disciplinas.values():
    solver.Add(solver.Sum(x[t] for t in turmas_disciplina) <= 1)

solver.Add(
    solver.Sum(len(hs) * x[t] for t, _, hs, _ in entrada) * 15 <= CARGA_HORARIA_MAXIMA
)

antes, depois = {}, {}
for d in range(D):
    for h in range(H):
        antes[(d, h)] = solver.IntVar(0, 1, f"antes_{d}_{h}")
        depois[(d, h)] = solver.IntVar(0, 1, f"depois_{d}_{h}")

for d in range(D):
    solver.Add(antes[(d, 0)] == 0)
    solver.Add(depois[(d, H - 1)] == 0)

for d in range(D):
    for h in range(1, H):
        solver.Add(antes[(d, h)] >= ocupado[(d, h - 1)])
        solver.Add(antes[(d, h)] >= antes[(d, h - 1)])
        solver.Add(antes[(d, h)] <= ocupado[(d, h - 1)] + antes[(d, h - 1)])

for d in range(D):
    for h in range(H - 2, -1, -1):
        solver.Add(depois[(d, h)] >= ocupado[(d, h + 1)])
        solver.Add(depois[(d, h)] >= depois[(d, h + 1)])
        solver.Add(depois[(d, h)] <= ocupado[(d, h + 1)] + depois[(d, h + 1)])

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

preferencias = solver.Sum(p * x[turma_id] for turma_id, _, _, p in entrada)

dias_ocupados = []
for d in range(D):
    dia_ocupado = solver.IntVar(0, 1, f"dia_ocupado_{d}")
    solver.Add(dia_ocupado <= solver.Sum([ocupado[(d, h)] for h in range(H)]))
    for h in range(H):
        solver.Add(dia_ocupado >= ocupado[(d, h)])
    dias_ocupados.append(dia_ocupado)
quantidade_dias = solver.Sum(dias_ocupados)

if DISTRIBUICAO_CENTRALIZADA:
    quantidade_dias = D - quantidade_dias

temp_solver = pywraplp.Solver.CreateSolver("SCIP")
x_temp = {t: temp_solver.IntVar(0, 1, t) for t, _, _, _ in entrada}
disciplinas_temp = {}
for t_id, c_id, _, _ in entrada:
    if c_id not in disciplinas_temp: disciplinas_temp[c_id] = []
    disciplinas_temp[c_id].append(t_id)
for turmas_disc in disciplinas_temp.values():
    temp_solver.Add(temp_solver.Sum(x_temp[t] for t in turmas_disc) <= 1)
temp_solver.Maximize(temp_solver.Sum(p * x_temp[t] for t, _, _, p in entrada))
status_temp = temp_solver.Solve()

if status_temp == pywraplp.Solver.OPTIMAL:
    max_preferencia_real = temp_solver.Objective().Value()
else:
    max_preferencia_real = sum(p for _, _, _, p in entrada) 

objetivo_preferencias_norm = (preferencias / max_preferencia_real if max_preferencia_real > 0 else 0)
max_buracos_possivel = D * (H - 2) if H > 2 else 1
objetivo_buracos_norm = (buracos / max_buracos_possivel if max_buracos_possivel > 0 else 0)
objetivo_dias_norm = quantidade_dias / D if D > 0 else 0

solver.Maximize(
    PESO_MAXIMIZAR_PREFERENCIA * objetivo_preferencias_norm
    - PESO_MINIMIZAR_BURACOS * objetivo_buracos_norm
    + PESO_QUANTIDADE_DIAS * objetivo_dias_norm
)

status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
    print("\n--- ✅ Solução Ótima Encontrada ---")
    calendario = [['-' for _ in range(D)] for _ in range(H)]
    carga_horaria_total = 0
    turmas_selecionadas = []

    for turma_id, _, hs, _ in entrada:
        if x[turma_id].solution_value() > 0.9: 
            turmas_selecionadas.append(turma_id)
            carga_horaria_total += len(hs) * 15 
            for d, h in hs:
                calendario[h][d] = turma_id

    DIAS_SEMANA = ['Seg(2)', 'Ter(3)', 'Qua(4)', 'Qui(5)', 'Sex(6)', 'Sab(7)']
    
    label_width = 20
    col_width = max([len(t) for t in turmas_selecionadas] + [10]) + 2

    print("\n" + "Horário".ljust(label_width) + "".join(f"{dia.center(col_width)}" for dia in DIAS_SEMANA))
    print("-" * (label_width + col_width * D))

    for h in range(H):
        horario_label = HORARIO_DISPLAY_LABELS[h]
        
        if horario_label.startswith('T1') or horario_label.startswith('N1'):
             print("-" * (label_width + col_width * D))

        linha = "".join(f"{calendario[h][d]:^{col_width}}" for d in range(D))
        linha_formatada = linha.replace("-".center(col_width), " ".center(col_width))
        
        print(f"{horario_label.ljust(label_width-1)}|{linha_formatada}")

    print("-" * (label_width + col_width * D))
    print("\nTurmas Selecionadas:", ", ".join(turmas_selecionadas) if turmas_selecionadas else "Nenhuma")
    print(f"Carga horária total alocada: {carga_horaria_total} horas-aula")
    num_buracos = sum(b.solution_value() for b in buracos_list)
    print(f"Número de buracos na grade: {int(num_buracos)}")
else:
    print("\n❌ Nenhuma solução ótima encontrada.")