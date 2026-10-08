import { useState } from 'react'
import Incidencia from './Incidencia'
import './App.css'

const incidenciasMock = [
  { maquina: 'Torno CNC-01', descripcion: 'Se detiene durante el cambio automático de herramienta.' },
  { maquina: 'Prensa hidráulica-02', descripcion: 'Pérdida de presión durante el ciclo de trabajo.' },
  { maquina: 'Banda transportadora-03', descripcion: 'Ruido anormal en el motor.' },
]

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <h1>Incidencias (investigación TCI)</h1>

      {incidenciasMock.map((incidencia) => (
        <Incidencia
          key={incidencia.maquina}
          maquina={incidencia.maquina}
          descripcion={incidencia.descripcion}
        />
      ))}

      <button type="button" onClick={() => setCount((count) => count + 1)}>
        Incidencias cargadas: {count}
      </button>
    </>
  )
}

export default App
