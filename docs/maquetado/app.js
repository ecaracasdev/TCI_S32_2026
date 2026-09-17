console.log("app.js cargado ✅");
const form = document.querySelector("#form-incidencia");

form.addEventListener("submit", (event) => {
  event.preventDefault(); // evita que el form haga un submit real y recargue la página
  console.log("submit del form");
  const incidencia = {
    codigoMaquina: document.querySelector("#codigo-maquina").value,
    descripcion: document.querySelector("#descripcion").value,
    turno: document.querySelector("#turno").value,
  };
  renderizarPreview(incidencia);
  console.table(incidencia);
});

// leerFormulario()  →  devuelve el objeto { codigoMaquina, descripcion, turno }
function renderizarPreview(payload) {
  const feedBack = document.querySelector("#preview-incidencia");
  feedBack.hidden = false;
  feedBack.textContent = `Turno: ${payload.turno}`;
  console.log("turno:", payload.turno);
}

// handler del submit  →  event.preventDefault(); leerFormulario(); renderizarPreview(); form.reset()
