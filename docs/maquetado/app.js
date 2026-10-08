console.log("app.js cargado ✅");

const form = document.querySelector("#form-incidencia");
const codigoMaquinaInput = document.querySelector("#codigo-maquina");
const btnEscanear = document.querySelector("#btn-escanear");
const fotoInput = document.querySelector("#foto");
const fotoNombre = document.querySelector("#foto-nombre");
const btnLimpiar = document.querySelector("#btn-limpiar");
const preview = document.querySelector("#preview-incidencia");

const CODIGOS_DEMO = ["CAL-001", "FRC-014", "BND-007"];

form.addEventListener("submit", (event) => {
  event.preventDefault(); // evita que el form haga un submit real y recargue la página
  console.log("submit del form");
  const incidencia = {
    codigoMaquina: codigoMaquinaInput.value,
    descripcion: document.querySelector("#descripcion").value,
    turno: document.querySelector("#turno").value,
  };
  renderizarPreview(incidencia);
  console.table(incidencia);
});

// Simula el escaneo real de QR que llega en M3: completa el código con una animación corta.
btnEscanear.addEventListener("click", () => {
  const codigo = CODIGOS_DEMO[Math.floor(Math.random() * CODIGOS_DEMO.length)];
  codigoMaquinaInput.value = codigo;
  btnEscanear.classList.remove("escaneando");
  void btnEscanear.offsetWidth; // reinicia la animación si se clickea varias veces seguidas
  btnEscanear.classList.add("escaneando");
});

fotoInput.addEventListener("change", () => {
  const archivo = fotoInput.files[0];
  fotoNombre.textContent = archivo ? archivo.name : "Sin archivo seleccionado";
});

btnLimpiar.addEventListener("click", () => {
  form.reset();
  fotoNombre.textContent = "Sin archivo seleccionado";
  ocultarPreview();
});

function renderizarPreview(payload) {
  preview.innerHTML = `
    <h2>Incidencia cargada</h2>
    <dl>
      <dt>Máquina</dt><dd>${payload.codigoMaquina || "sin escanear"}</dd>
      <dt>Turno</dt><dd>${payload.turno}</dd>
      <dt>Descripción</dt><dd>${payload.descripcion || "sin descripción"}</dd>
    </dl>
  `;
  preview.hidden = false;
  requestAnimationFrame(() => preview.classList.add("visible"));
  console.log("turno:", payload.turno);
}

function ocultarPreview() {
  preview.classList.remove("visible");
  preview.hidden = true;
}
