// src/App.jsx

import { useState } from "react";
import "./App.css";

// Dados iniciais para facilitar o teste, baseados no seu exemplo
const initialState = {
  dias: 5,
  horarios: 8,
  carga_horaria_maxima: 240, // Carga horária em "créditos" ou "horas-aula"
  peso_preferencia: 0.6,
  peso_buracos: 0.3,
  peso_dias: 0.1,
  centralizado: true,
  turmas: [
    {
      id_turma: "MAT101-T1",
      cod_disciplina: "MAT101",
      codigo_horario: "24M34",
      preferencia: 5,
    },
    {
      id_turma: "FIS102-T2",
      cod_disciplina: "FIS102",
      codigo_horario: "35T12",
      preferencia: 8,
    },
    {
      id_turma: "PROG1-T1",
      cod_disciplina: "PROG1",
      codigo_horario: "26M12",
      preferencia: 10,
    },
    {
      id_turma: "CALC2-T4",
      cod_disciplina: "CALC2",
      codigo_horario: "35M34",
      preferencia: 7,
    },
    {
      id_turma: "HUM100-T7",
      cod_disciplina: "HUM100",
      codigo_horario: "24T12",
      preferencia: 9,
    },
  ],
};

function App() {
  // --- Estados do Formulário ---
  const [config, setConfig] = useState({
    dias: initialState.dias,
    horarios: initialState.horarios,
    carga_horaria_maxima: initialState.carga_horaria_maxima,
  });
  const [pesos, setPesos] = useState({
    peso_preferencia: initialState.peso_preferencia,
    peso_buracos: initialState.peso_buracos,
    peso_dias: initialState.peso_dias,
  });
  const [centralizado, setCentralizado] = useState(initialState.centralizado);
  const [turmas, setTurmas] = useState(initialState.turmas);

  // Estado para o formulário de nova turma
  const [novaTurma, setNovaTurma] = useState({
    id_turma: "",
    cod_disciplina: "",
    codigo_horario: "",
    preferencia: 5,
  });

  // --- Estados da Resposta da API ---
  const [resultado, setResultado] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleConfigChange = (e) => {
    const { name, value } = e.target;
    setConfig((prev) => ({ ...prev, [name]: Number(value) }));
  };

  const handlePesoChange = (e) => {
    const { name, value } = e.target;
    setPesos((prev) => ({ ...prev, [name]: parseFloat(value) }));
  };

  const handleNovaTurmaChange = (e) => {
    const { name, value, type } = e.target;
    setNovaTurma((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : value,
    }));
  };

  const handleAddTurma = (e) => {
    e.preventDefault();
    if (
      novaTurma.id_turma &&
      novaTurma.cod_disciplina &&
      novaTurma.codigo_horario
    ) {
      // Evita adicionar turmas com mesmo ID
      if (turmas.some((t) => t.id_turma === novaTurma.id_turma)) {
        alert("Já existe uma turma com este ID.");
        return;
      }
      setTurmas((prev) => [...prev, novaTurma]);
      // Limpa o formulário
      setNovaTurma({
        id_turma: "",
        cod_disciplina: "",
        codigo_horario: "",
        preferencia: 5,
      });
    } else {
      alert("Por favor, preencha todos os campos da turma.");
    }
  };

  const handleRemoveTurma = (id) => {
    setTurmas((prev) => prev.filter((turma) => turma.id_turma !== id));
  };

  const handleGerarGrade = async () => {
    setIsLoading(true);
    setError(null);
    setResultado(null);

    const requestBody = {
      ...config,
      ...pesos,
      centralizado,
      turmas,
    };

    try {
      // Usamos POST para enviar o corpo da requisição
      const response = await fetch("http://localhost:5000/gerar-grade", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Erro ${response.status}`);
      }

      const data = await response.json();
      setResultado(data.saida);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const diasDaSemana = ["SEG", "TER", "QUA", "QUI", "SEX"];
  const horariosDaSemana = [
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "14:00",
    "15:00",
    "16:00",
  ];

  return (
    <div className="container">
      <header>
        <h1>Gerador de Grade Horária</h1>
        <p>
          Preencha os parâmetros, adicione as turmas ofertadas e clique em
          "Gerar Grade" para otimizar seu horário.
        </p>
      </header>

      <main className="main-layout">
        <div className="form-section">
          {/* --- Configurações Gerais --- */}
          <fieldset>
            <legend>Configurações Gerais</legend>
            <label>
              Dias na semana:{" "}
              <input
                type="number"
                name="dias"
                value={config.dias}
                onChange={handleConfigChange}
              />
            </label>
            <label>
              Horários por dia:{" "}
              <input
                type="number"
                name="horarios"
                value={config.horarios}
                onChange={handleConfigChange}
              />
            </label>
            <label>
              Carga Horária Máx.:{" "}
              <input
                type="number"
                name="carga_horaria_maxima"
                value={config.carga_horaria_maxima}
                onChange={handleConfigChange}
              />
            </label>
          </fieldset>

          {/* --- Pesos da Otimização --- */}
          <fieldset>
            <legend>Pesos da Otimização</legend>
            <p className="info">Dica: Faça a soma dos pesos ser igual a 1.0</p>
            <label>
              Peso Preferências (0.0 a 1.0):{" "}
              <input
                type="number"
                step="0.05"
                name="peso_preferencia"
                value={pesos.peso_preferencia}
                onChange={handlePesoChange}
              />
            </label>
            <label>
              Peso Anti-Buracos (0.0 a 1.0):{" "}
              <input
                type="number"
                step="0.05"
                name="peso_buracos"
                value={pesos.peso_buracos}
                onChange={handlePesoChange}
              />
            </label>
            <label>
              Peso Distrib. Dias (0.0 a 1.0):{" "}
              <input
                type="number"
                step="0.05"
                name="peso_dias"
                value={pesos.peso_dias}
                onChange={handlePesoChange}
              />
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={centralizado}
                onChange={(e) => setCentralizado(e.target.checked)}
              />{" "}
              Centralizar aulas (minimizar dias)
            </label>
          </fieldset>

          {/* --- Cadastro de Turmas --- */}
          <fieldset>
            <legend>Adicionar Turmas Ofertadas</legend>
            <form onSubmit={handleAddTurma} className="turma-form">
              <input
                name="id_turma"
                value={novaTurma.id_turma}
                onChange={handleNovaTurmaChange}
                placeholder="ID da Turma (ex: MAT101-T1)"
              />
              <input
                name="cod_disciplina"
                value={novaTurma.cod_disciplina}
                onChange={handleNovaTurmaChange}
                placeholder="Cód. Disciplina (ex: MAT101)"
              />
              <input
                name="codigo_horario"
                value={novaTurma.codigo_horario}
                onChange={handleNovaTurmaChange}
                placeholder="Horário (ex: 24M12)"
              />
              <input
                type="number"
                name="preferencia"
                value={novaTurma.preferencia}
                onChange={handleNovaTurmaChange}
                placeholder="Preferência (1-10)"
              />
              <button type="submit">Adicionar</button>
            </form>
          </fieldset>

          {/* --- Lista de Turmas --- */}
          <div className="turmas-list">
            <h3>{turmas.length} Turmas Adicionadas</h3>
            <ul>
              {turmas.map((t) => (
                <li key={t.id_turma}>
                  <span>
                    <strong>{t.id_turma}</strong> ({t.cod_disciplina}) -
                    Horário: {t.codigo_horario} - Pref: {t.preferencia}
                  </span>
                  <button
                    onClick={() => handleRemoveTurma(t.id_turma)}
                    className="remove-btn"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="result-section">
          <button
            onClick={handleGerarGrade}
            disabled={isLoading}
            className="generate-btn"
          >
            {isLoading ? "Gerando..." : "Gerar Grade"}
          </button>

          {error && (
            <div className="error-box">
              <strong>Erro:</strong> {error}
            </div>
          )}

          {resultado && (
            <div className="resultado-container">
              <h3>{resultado.mensagem || "Resultado da Otimização"}</h3>

              {resultado.metricas && (
                <div className="metricas">
                  <h4>Métricas</h4>
                  <p>
                    <strong>Preferência Total:</strong>{" "}
                    {resultado.metricas.soma_preferencias?.toFixed(2)}
                  </p>
                  <p>
                    <strong>Buracos na Grade:</strong>{" "}
                    {resultado.metricas.numero_buracos}
                  </p>
                  <p>
                    <strong>Dias com Aula:</strong>{" "}
                    {resultado.metricas.dias_com_aula}
                  </p>
                  <p>
                    <strong>Carga Horária:</strong>{" "}
                    {resultado.metricas.carga_horaria_total}
                  </p>
                </div>
              )}

              {resultado.calendario && (
                <div className="calendario">
                  <h4>Grade Gerada</h4>
                  <table>
                    <thead>
                      <tr>
                        <th>Horário</th>
                        {diasDaSemana.slice(0, config.dias).map((dia) => (
                          <th key={dia}>{dia}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {resultado.calendario.map((linha, h) => (
                        <tr key={h}>
                          <td>{horariosDaSemana[h]}</td>
                          {linha.map((celula, d) => (
                            <td key={d}>{celula !== "----" ? celula : ""}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {resultado.turmas_selecionadas && (
                <div className="turmas-selecionadas">
                  <h4>Turmas Selecionadas</h4>
                  <p>{resultado.turmas_selecionadas.join(", ")}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
