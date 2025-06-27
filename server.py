from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/gerar-grade', methods=['GET'])
def gerar_grade():
  dados = request.get_json()

  # Função para converter código de horário para lista de tuplas (dia, horário)
  def converter_codigo_horario(codigo):
    resultado = []
    # Exemplo de código: 24M34
    match = re.match(r"([2-6]+)([MT])([1-5]+)", codigo)
    if not match:
      return resultado
    dias_str, turno, horarios_str = match.groups()
    # Mapear turno para offset de horário
    turno_offset = {"M": 0, "T": 4}
    for dia_char in dias_str:
      dia = int(dia_char) - 2  # 2->0, 3->1, ..., 6->4
      for h in horarios_str:
        horario = int(h)
        # Ignorar horários inválidos
        if turno == "M" and horario == 5:
          continue  # Não usamos o 5 da manhã
        if turno == "T" and horario == 1:
          continue  # Não usamos o 1 da tarde
        if turno not in turno_offset:
          continue
        # Ajustar horário para índice global
        if turno == "M":
          horario_idx = horario - 1  # manhã: 1-4 -> 0-3
        elif turno == "T":
          horario_idx = 4 + (horario - 2)  # tarde: 2-5 -> 4-7
        else:
          continue
        resultado.append((dia, horario_idx))
    return resultado

  # Monta entradas_txt
  entradas_txt = []
  entradas_txt.append(str(dados["dias"]))
  entradas_txt.append(str(dados["horarios"]))
  entradas_txt.append(str(dados["carga_horaria_maxima"]))
  entradas_txt.append(str(dados["peso_preferencia"]))
  entradas_txt.append(str(dados["peso_buracos"]))
  entradas_txt.append(str(dados["peso_dias"]))
  entradas_txt.append("s" if dados.get("centralizado", False) else "n")
  for turma in dados["turmas"]:
    horarios_turma = converter_codigo_horario(turma["codigo_horario"])
    horarios_str = '[' + ','.join([f'({dia},{horario})' for dia, horario in horarios_turma]) + ']'
    linha = f'{turma["id_turma"]} {turma["cod_disciplina"]} {horarios_str} {turma["preferencia"]}'
    entradas_txt.append(linha)
  entradas_txt.append(" ")
  entradas_txt_str = "\n".join(entradas_txt)


  # Executa o main.py simulando entrada do usuário
  try:
    resultado = subprocess.run(
      ["python3", "main.py"],
      input=entradas_txt_str.encode(),
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      timeout=60
    )
    saida = resultado.stdout.decode()
    erro = resultado.stderr.decode()
    if erro:
      return jsonify({"erro": erro}), 200
    else:
      return jsonify({"saida": saida}), 200
  except Exception as e:
    return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
  app.run(debug=True)

