// ════════════════════════════════════════════════════════════
//  VólticvS — app.js (Arquitectura ≤ 2 llamadas LLM/sesión)
//  Módulos: TipoInmueble, SelectorKwh, Electrodomésticos, Submit
// ════════════════════════════════════════════════════════════

const formulario       = document.getElementById("formularioEnergia");
const resultadosSeccion = document.getElementById("resultados");
const meterValue        = document.getElementById("meterValue");

// ── Estado del módulo ──────────────────────────────────────────────────────────
let _paisesCache     = null;
const PAIS_DEFAULT   = "CL";
const TARIFA_FALLBACK = 0.75;

// Estado: tipo de inmueble (asignado directamente por botón, sin LLM)
let _tipoInmueble        = "Casa";
let _textoOtroInmueble   = "";   // Texto libre del campo "Otro"

// Estado: consumo kWh (prioridad: exacto > rango > calculado > fallback)
let _kwhRangoSeleccionado = null;   // Valor numérico del rango elegido (null = no elegido)
let _kwhRango             = "ninguno"; // Etiqueta del rango ("bajo","medio","alto","nose","boleta")
const KWH_FALLBACK        = 250;    // Promedio estándar cuando el usuario no sabe

// ── Validación HTML5 en español ────────────────────────────────────────────────
document.addEventListener("invalid", (e) => {
  const campo = e.target;
  if (campo.tagName !== "INPUT" || campo.type !== "number") return;
  const val = parseFloat(campo.value);
  const max = parseFloat(campo.getAttribute("max"));
  const min = parseFloat(campo.getAttribute("min") ?? "-Infinity");
  if (!isNaN(max) && val > max) {
    campo.setCustomValidity(`El valor debe ser menor o igual a ${max} horas.`);
  } else if (!isNaN(min) && val < min) {
    campo.setCustomValidity(`El valor debe ser mayor o igual a ${min}.`);
  } else if (campo.validity.valueMissing) {
    campo.setCustomValidity("Este campo es obligatorio.");
  } else {
    campo.setCustomValidity("Valor no válido.");
  }
}, true);

document.addEventListener("input", (e) => {
  const campo = e.target;
  if (campo.tagName === "INPUT" && campo.type === "number") {
    campo.setCustomValidity("");
  }
}, true);

// Agregar "veces por semana" a artefactos con horas de uso
document.querySelectorAll(".item.item--con-horas").forEach((item) => {
  const campos = item.querySelector(".item__fields");
  if (campos && !item.querySelector(".veces-semana")) {
    const etiqueta = document.createElement("label");
    etiqueta.innerHTML = 'Veces por semana <input type="number" min="1" max="7" value="7" class="veces-semana">';
    campos.appendChild(etiqueta);
  }
});

// ════════════════════════════════════════════════════════════
//  MÓDULO 1: PAÍSES Y TARIFA
// ════════════════════════════════════════════════════════════

async function cargarPaises() {
  const selectPais = document.getElementById("selectPais");
  try {
    const respuesta = await fetch("/api/paises");
    const paises    = await respuesta.json();
    _paisesCache    = paises;
    selectPais.innerHTML = "";
    Object.entries(paises).forEach(([codigo, datos]) => {
      const opcion = document.createElement("option");
      opcion.value = codigo;
      opcion.textContent = `${datos.nombre} (${datos.moneda})`;
      selectPais.appendChild(opcion);
    });
    selectPais.value = PAIS_DEFAULT;
    actualizarTarifaPorPais(paises, PAIS_DEFAULT);
    selectPais.addEventListener("change", () => actualizarTarifaPorPais(paises, selectPais.value));
  } catch (error) {
    selectPais.innerHTML = '<option value="">No se pudo cargar la lista de países</option>';
  }
}

function actualizarTarifaPorPais(paises, codigo) {
  const datos       = paises[codigo];
  if (!datos) return;
  const campoTarifa = document.getElementById("tarifaClp");
  const fuenteTexto = document.getElementById("fuenteTarifa");
  const labelMoneda = document.getElementById("labelMoneda");
  const hintTarifa  = document.getElementById("hintTarifa");
  const tarifa      = datos.tarifa_kwh_referencial ?? TARIFA_FALLBACK;
  campoTarifa.value = tarifa;
  const simbolo = datos.simbolo || "";
  const moneda  = datos.moneda  || "";
  if (labelMoneda) {
    labelMoneda.textContent = moneda
      ? `(${simbolo ? simbolo + " · " : ""}${moneda})`
      : "";
  }
  window._monedaActiva  = moneda;
  window._simboloActivo = simbolo;
  window._paisActivo    = codigo;
  if (hintTarifa) {
    const monedaLabel = simbolo ? `${simbolo} (${moneda})` : (moneda || "moneda local");
    hintTarifa.textContent = datos.fuente
      ? `Tarifa referencial en ${monedaLabel} — Fuente: ${datos.fuente}. Súbela tu boleta para mayor exactitud.`
      : `Tarifa referencial en ${monedaLabel}. Súbela tu boleta para mayor exactitud.`;
  }
  if (fuenteTexto) fuenteTexto.textContent = datos.fuente
    ? `Fuente: ${datos.fuente}. Verifica el valor vigente ahí o usa el de tu boleta.`
    : "";
}
cargarPaises();

// ════════════════════════════════════════════════════════════
//  MÓDULO 1b: PASOS WIZARD — Ubicación & Tarifa
// ════════════════════════════════════════════════════════════

function initUbiSteps() {
  const step1      = document.getElementById("ubiStep1");
  const step2      = document.getElementById("ubiStep2");
  const body1      = document.getElementById("ubiStep1Body");
  const body2      = document.getElementById("ubiStep2Body");
  const toggle1    = document.getElementById("toggleStep1");
  const toggle2    = document.getElementById("toggleStep2");
  const btnSig     = document.getElementById("btnIrPaso2");
  const icon1      = toggle1 ? toggle1.querySelector(".ubi-step__toggle-icon") : null;
  const icon2      = toggle2 ? toggle2.querySelector(".ubi-step__toggle-icon") : null;

  function expandStep(step, body, toggle, icon) {
    step.classList.remove("ubi-step--collapsed");
    body.hidden = false;
    if (toggle) toggle.setAttribute("aria-expanded", "true");
    if (icon)  icon.textContent = "\u25b2";
  }

  function collapseStep(step, body, toggle, icon) {
    step.classList.add("ubi-step--collapsed");
    body.hidden = true;
    if (toggle) toggle.setAttribute("aria-expanded", "false");
    if (icon)  icon.textContent = "\u25bc";
  }

  if (toggle1) {
    toggle1.addEventListener("click", () => {
      if (body1.hidden) {
        expandStep(step1, body1, toggle1, icon1);
      } else {
        collapseStep(step1, body1, toggle1, icon1);
      }
    });
  }

  if (toggle2) {
    toggle2.addEventListener("click", () => {
      if (body2.hidden) {
        expandStep(step2, body2, toggle2, icon2);
      } else {
        collapseStep(step2, body2, toggle2, icon2);
      }
    });
  }

  if (btnSig) {
    btnSig.addEventListener("click", () => {
      collapseStep(step1, body1, toggle1, icon1);
      expandStep(step2, body2, toggle2, icon2);
      step2.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  const provinciaInput = document.getElementById("selectProvincia");
  if (provinciaInput) {
    provinciaInput.addEventListener("input", () => {
      window._provinciaActiva = provinciaInput.value.trim();
    });
  }
}
initUbiSteps();

// ════════════════════════════════════════════════════════════
//  MÓDULO 2: TIPO DE INMUEBLE (Asignación directa, sin LLM)
// ════════════════════════════════════════════════════════════

function initTipoInmueble() {
  const btns         = document.querySelectorAll(".tipo-inmueble-btn");
  const otroWrap     = document.getElementById("tipoOtroWrap");
  const otroInput    = document.getElementById("tipoOtroInput");

  if (!btns.length) return;

  btns.forEach((btn) => {
    btn.addEventListener("click", () => {
      // Desmarcar todos
      btns.forEach((b) => b.classList.remove("tipo-inmueble-btn--active"));
      // Marcar el clickeado
      btn.classList.add("tipo-inmueble-btn--active");

      const valor = btn.dataset.valor;

      if (valor === "otro") {
        // Mostrar campo de texto libre
        otroWrap.hidden = false;
        otroWrap.classList.add("selector-reveal");
        setTimeout(() => otroWrap.classList.remove("selector-reveal"), 400);
        otroInput.focus();
        // Marcar como pendiente de interpretación
        _tipoInmueble = ""; // Se resolverá en interpretarCamposLibres()
      } else {
        // Asignación directa — sin ninguna llamada a la API
        _tipoInmueble      = valor;
        _textoOtroInmueble = "";
        otroWrap.hidden    = true;
        otroInput.value    = "";
      }
    });
  });

  // Actualizar el texto libre en tiempo real
  if (otroInput) {
    otroInput.addEventListener("input", () => {
      _textoOtroInmueble = otroInput.value.trim();
    });
  }
}
initTipoInmueble();

// ════════════════════════════════════════════════════════════
//  MÓDULO 3: SELECTOR kWh POR RANGOS (Asignación directa)
// ════════════════════════════════════════════════════════════

function initSelectorKwh() {
  const btns       = document.querySelectorAll(".kwh-range-btn");
  const exactWrap  = document.getElementById("kwhExactWrap");
  const exactInput = document.getElementById("kwhExactoInput");
  const badge      = document.getElementById("kwhRangoBadge");
  const badgeText  = document.getElementById("kwhRangoBadgeText");

  if (!btns.length) return;

  const LABEL_MAP = {
    bajo:   "🟢 Bajo — ~100 kWh/mes (Depto. o mínimo)",
    medio:  "🟡 Medio — ~225 kWh/mes (Casa promedio)",
    alto:   "🟠 Alto — ~400 kWh/mes (Casa grande)",
    nose:   "🔴 No lo sé — usando 250 kWh (promedio estándar)",
    boleta: "✏️ Consumo exacto de boleta",
  };

  btns.forEach((btn) => {
    btn.addEventListener("click", () => {
      // Desmarcar todos
      btns.forEach((b) => b.classList.remove("kwh-range-btn--active"));
      btn.classList.add("kwh-range-btn--active");

      const rango = btn.dataset.rango;
      const kwh   = parseFloat(btn.dataset.kwh);
      _kwhRango   = rango;

      if (rango === "boleta") {
        // Mostrar input numérico exacto
        exactWrap.hidden = false;
        exactWrap.classList.add("selector-reveal");
        setTimeout(() => exactWrap.classList.remove("selector-reveal"), 400);
        exactInput.focus();
        _kwhRangoSeleccionado = null; // Se leerá del input al submit
        if (badge) badge.hidden = true;
      } else {
        // Asignación directa del valor de rango — sin ninguna llamada a la API
        exactWrap.hidden      = true;
        exactInput.value      = "";
        _kwhRangoSeleccionado = kwh;
        // Mostrar badge informativo
        if (badge && badgeText) {
          badgeText.textContent = LABEL_MAP[rango] || `${kwh} kWh/mes`;
          badge.hidden = false;
          badge.className = `kwh-rango-badge kwh-rango-badge--${rango}`;
        }
      }
    });
  });

  // Actualizar valor al escribir en el input exacto
  if (exactInput) {
    exactInput.addEventListener("input", () => {
      const v = parseFloat(exactInput.value);
      _kwhRangoSeleccionado = (!isNaN(v) && v > 0) ? v : null;
      if (badge && badgeText && _kwhRangoSeleccionado) {
        badgeText.textContent = `✏️ Boleta: ${_kwhRangoSeleccionado} kWh/mes`;
        badge.hidden = false;
        badge.className = "kwh-rango-badge kwh-rango-badge--boleta";
      }
    });
  }
}
initSelectorKwh();

// ════════════════════════════════════════════════════════════
//  MÓDULO 4: ELECTRODOMÉSTICOS (Checkboxes, condicionales)
// ════════════════════════════════════════════════════════════

// Habilitar/deshabilitar campos según checkbox marcado
document.querySelectorAll(".item").forEach((item) => {
  const check = item.querySelector(".chk-artefacto, .chk-iluminacion");
  if (!check) return;
  check.addEventListener("change", () => {
    item.classList.toggle("activo", check.checked);
  });
});

// Mostrar/ocultar bloques condicionales (CCTV, hervidor)
function toggleCondicional(nombreRadio, valorQueMuestra, contenedorId) {
  const contenedor = document.getElementById(contenedorId);
  document.querySelectorAll(`input[name="${nombreRadio}"]`).forEach((radio) => {
    radio.addEventListener("change", () => {
      contenedor.hidden = radio.value !== valorQueMuestra || !radio.checked;
    });
  });
}
toggleCondicional("cctv",     "si", "camposCctv");
toggleCondicional("hervidor", "si", "camposHervidor");

// Artefactos personalizados dinámicos
const listaPersonalizados    = document.getElementById("listaPersonalizados");
const templatePersonalizado  = document.getElementById("templatePersonalizado");

document.getElementById("btnAgregarPersonalizado").addEventListener("click", () => {
  const nodo  = templatePersonalizado.content.cloneNode(true);
  const fila  = nodo.querySelector(".personalizado");
  const campoWatts = fila.querySelector(".p-watts");

  fila.querySelectorAll(".btn-nivel").forEach((btn) => {
    btn.addEventListener("click", () => {
      campoWatts.value = btn.dataset.watts;
      fila.querySelectorAll(".btn-nivel").forEach((b) => b.classList.remove("activo"));
      btn.classList.add("activo");
    });
  });
  campoWatts.addEventListener("input", () => {
    fila.querySelectorAll(".btn-nivel").forEach((b) => b.classList.remove("activo"));
  });

  fila.querySelector(".btn--eliminar").addEventListener("click", () => fila.remove());
  listaPersonalizados.appendChild(nodo);

  const filaInsertada = listaPersonalizados.lastElementChild;
  filaInsertada.classList.add("personalizado--nuevo");
  setTimeout(() => filaInsertada.classList.remove("personalizado--nuevo"), 1700);
  filaInsertada.scrollIntoView({ behavior: "smooth", block: "center" });
  const campoNombre = filaInsertada.querySelector(".p-nombre");
  if (campoNombre) setTimeout(() => campoNombre.focus(), 300);
});

// ════════════════════════════════════════════════════════════
//  MÓDULO 5: RECOLECCIÓN DE DATOS
// ════════════════════════════════════════════════════════════

function recolectarElectrodomesticos() {
  const items = [];
  document.querySelectorAll(".item[data-clave]").forEach((item) => {
    const check = item.querySelector(".chk-artefacto");
    if (!check.checked) return;
    const quedaConectadoInput = item.querySelector(".queda-conectado");
    const vecesSemanaInput    = item.querySelector(".veces-semana");
    items.push({
      clave:           item.dataset.clave,
      cantidad:        parseFloat(item.querySelector(".cantidad").value) || 0,
      horas:           parseFloat(item.querySelector(".horas").value) || 0,
      queda_conectado: quedaConectadoInput ? quedaConectadoInput.checked : true,
      veces_semana:    vecesSemanaInput ? parseFloat(vecesSemanaInput.value) || 7 : 7,
    });
  });
  return items;
}

function recolectarIluminacion() {
  const items = [];
  document.querySelectorAll(".item[data-tipo]").forEach((item) => {
    const check = item.querySelector(".chk-iluminacion");
    if (!check.checked) return;
    items.push({
      tipo:     item.dataset.tipo,
      cantidad: parseFloat(item.querySelector(".cantidad").value) || 0,
      horas:    parseFloat(item.querySelector(".horas").value) || 0,
    });
  });
  return items;
}

function recolectarPersonalizados() {
  const items = [];
  listaPersonalizados.querySelectorAll(".personalizado").forEach((fila) => {
    const nombre = fila.querySelector(".p-nombre").value.trim();
    const watts  = parseFloat(fila.querySelector(".p-watts").value);
    if (!nombre || !watts) return;
    items.push({
      nombre,
      watts,
      horas:    parseFloat(fila.querySelector(".p-horas").value) || 0,
      cantidad: parseFloat(fila.querySelector(".p-cantidad").value) || 1,
    });
  });
  return items;
}

// ════════════════════════════════════════════════════════════
//  MÓDULO 6: CÁLCULO LOCAL DE CONSUMO (kWh determinista)
// ════════════════════════════════════════════════════════════

const WATTS_MAP = {
  refrigerador: 150, congeladora: 200, lavadora: 500, secadora_ropa: 2500,
  horno_electrico: 2000, microondas: 1200, olla_arrocera: 700,
  cafetera_electrica: 800, licuadora: 300, tostadora: 800,
  campana_extractora: 120, cuchillo_electrico: 100, exprimidor_electrico: 150,
  abrelatas_electrico: 60, television: 100, decodificador_tv: 15,
  computador_escritorio: 150, router_wifi: 8, cargador_celular: 5,
  cargador_tablet: 10, cargador_notebook: 65, ventilador: 50,
  calefactor_electrico: 1500, aspiradora: 1400, plancha_ropa: 1000,
  secador_pelo: 1200, porton_electrico: 300,
};
const WATTS_TIPO = {
  led: 9, incandescente: 60, fluorescente_tubo: 36,
  fluorescente_ahorro: 15, halogeno: 42, neon_exterior: 20,
};

function wattsDesdeDom(itemEl) {
  const span  = itemEl.querySelector(".item__watts");
  if (!span) return null;
  const match = span.textContent.match(/~?\s*(\d+(?:\.\d+)?)\s*W/i);
  return match ? parseFloat(match[1]) : null;
}

function calcularConsumoDesdeElectrodomesticos() {
  let total = 0;
  document.querySelectorAll(".item[data-clave]").forEach((itemEl) => {
    const check = itemEl.querySelector(".chk-artefacto");
    if (!check || !check.checked) return;
    const clave    = itemEl.dataset.clave;
    const watts    = wattsDesdeDom(itemEl) ?? WATTS_MAP[clave] ?? 100;
    const cantidad = parseFloat(itemEl.querySelector(".cantidad")?.value) || 1;
    const horas    = parseFloat(itemEl.querySelector(".horas")?.value)    || 0;
    const vecesSem = parseFloat(itemEl.querySelector(".veces-semana")?.value) || 7;
    const diasMes  = (vecesSem / 7) * 30;
    total += (watts * cantidad * horas * diasMes) / 1000;
  });
  document.querySelectorAll(".item[data-tipo]").forEach((itemEl) => {
    const check = itemEl.querySelector(".chk-iluminacion");
    if (!check || !check.checked) return;
    const tipo     = itemEl.dataset.tipo;
    const watts    = wattsDesdeDom(itemEl) ?? WATTS_TIPO[tipo] ?? 10;
    const cantidad = parseFloat(itemEl.querySelector(".cantidad")?.value) || 1;
    const horas    = parseFloat(itemEl.querySelector(".horas")?.value)    || 0;
    total += (watts * cantidad * horas * 30) / 1000;
  });
  recolectarPersonalizados().forEach((p) => {
    total += (p.watts * p.cantidad * p.horas * 30) / 1000;
  });
  return total;
}

/**
 * Determina el consumo final a enviar en el payload.
 * Prioridad estricta:
 *  1. Valor exacto de boleta ingresado por el usuario (_kwhRango === "boleta")
 *  2. Valor de rango seleccionado (_kwhRangoSeleccionado > 0)
 *  3. Consumo calculado desde electrodomésticos marcados (> 0)
 *  4. Fallback estándar 250 kWh (cuando el usuario no sabe ni marcó nada)
 */
function determinarConsumoFinal() {
  // 1. Exacto de boleta
  if (_kwhRango === "boleta" && _kwhRangoSeleccionado && _kwhRangoSeleccionado > 0) {
    return _kwhRangoSeleccionado;
  }
  // 2. Rango predefinido (bajo/medio/alto/nose)
  if (_kwhRangoSeleccionado !== null && _kwhRangoSeleccionado > 0) {
    const calculado = calcularConsumoDesdeElectrodomesticos();
    // Si el usuario marcó artefactos Y eligió un rango, usamos el mayor como referencia
    return Math.max(_kwhRangoSeleccionado, calculado > 0 ? calculado : 0);
  }
  // 3. Calculado desde electrodomésticos
  const calculado = calcularConsumoDesdeElectrodomesticos();
  if (calculado > 0) return calculado;
  // 4. Fallback estándar
  return KWH_FALLBACK;
}

// ════════════════════════════════════════════════════════════
//  MÓDULO 7: LLAMADA OPCIONAL #1 — Interpretar campo libre
//  Solo se ejecuta si el usuario escribió texto en "Otro..."
// ════════════════════════════════════════════════════════════

async function interpretarCamposLibres() {
  // Solo si el usuario eligió "Otro" y escribió algo
  if (!_textoOtroInmueble || _tipoInmueble !== "") {
    return; // Ya tiene valor directo, no necesita interpretación
  }
  try {
    const resp = await fetch("/api/interpretar-campo", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ campo: "tipo_inmueble", texto: _textoOtroInmueble }),
    });
    const data = await resp.json();
    _tipoInmueble = data.valor_mapeado || "Casa";
  } catch {
    _tipoInmueble = "Casa"; // Fallback silencioso
  }
}

// ════════════════════════════════════════════════════════════
//  MÓDULO 8: ANIMACIÓN DEL MEDIDOR HERO
// ════════════════════════════════════════════════════════════

function animarMedidor(valorFinal) {
  const valorInicial = parseFloat(meterValue.textContent) || 0;
  const duracionMs   = 700;
  const inicio       = performance.now();
  function paso(ahora) {
    const progreso   = Math.min((ahora - inicio) / duracionMs, 1);
    const valorActual = valorInicial + (valorFinal - valorInicial) * progreso;
    meterValue.textContent = valorActual.toFixed(1);
    if (progreso < 1) requestAnimationFrame(paso);
  }
  requestAnimationFrame(paso);
}

// ════════════════════════════════════════════════════════════
//  MÓDULO 9: SUBMIT — Llamada Final #2 al API
//  (máximo 1 llamada LLM aquí, más la opcional anterior)
// ════════════════════════════════════════════════════════════

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();

  // ── 0. Validación de horas en español ──────────────────────────────────────
  let campoInvalido = null;
  formulario.querySelectorAll("input[type='number'][max='24']").forEach((campo) => {
    campo.setCustomValidity("");
    const val = parseFloat(campo.value);
    if (!isNaN(val) && val > 24) {
      campo.setCustomValidity("Las horas de uso diarias no pueden ser mayores a 24.");
      if (!campoInvalido) campoInvalido = campo;
    }
  });
  if (campoInvalido) {
    campoInvalido.reportValidity();
    return;
  }

  // ── 1. Recolectar datos de electrodomésticos ────────────────────────────────
  const electrodomesticos = recolectarElectrodomesticos();
  const iluminacion       = recolectarIluminacion();
  const personalizados    = recolectarPersonalizados();
  const cantidadEquipos   = electrodomesticos.length + iluminacion.length + personalizados.length;

  // ── 2. Determinar consumo final (sin LLM) ──────────────────────────────────
  const consumoFinal = Math.max(parseFloat(determinarConsumoFinal().toFixed(1)), 10);

  // ── 3. Horas alto consumo ──────────────────────────────────────────────────
  let horasAltoConsumo = 0;
  electrodomesticos.forEach((item) => {
    if (["microondas", "secadora_ropa", "horno_electrico", "calefactor_electrico"].includes(item.clave)) {
      horasAltoConsumo += item.horas;
    }
  });

  // ── 4. Llamada Opcional #1: Interpretar texto libre (solo si aplica) ───────
  const botonSubmit = formulario.querySelector(".btn--primary");
  botonSubmit.disabled    = true;
  botonSubmit.textContent = "Analizando…";

  await interpretarCamposLibres(); // Solo hace fetch si hay texto libre pendiente

  botonSubmit.textContent = "Calculando…";

  // ── 5. Payload para la API ─────────────────────────────────────────────────
  const payload = {
    consumo_kwh:        consumoFinal,
    uso_horario_pico:   horasAltoConsumo > 2,
    cantidad_equipos:   cantidadEquipos || 1,
    tipo_inmueble:      _tipoInmueble || "Casa",
    horas_alto_consumo: Math.round(horasAltoConsumo),
    rango_kwh_elegido:  _kwhRango,
    pais:               window._paisActivo || "CL",
    provincia:          window._provinciaActiva || "",
  };

  try {
    // ── 6. Llamada Final #2: Análisis energético + Narrador VólticvS ──────────
    const respuesta = await fetch("/api/analisis-energetico", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    const resultado = await respuesta.json();

    // ── 7. Mostrar resultados ──────────────────────────────────────────────────
    mostrarResultados({
      narrativa:               `Perfil energético: ${resultado.categoria} (Certeza: ${(resultado.probabilidad * 100).toFixed(0)}%)`,
      total_kwh_mes:           consumoFinal,
      total_clp_mes:           resultado.costo_estimado_mensual,
      ahorro_potencial_clp_mes: resultado.costo_estimado_mensual * 0.20,
      recomendaciones:         resultado.recomendaciones,
      proyeccion: {
        ahorro_1_mes:   resultado.costo_estimado_mensual * 0.20,
        ahorro_6_meses: (resultado.costo_estimado_mensual * 0.20) * 6,
        ahorro_1_anio:  (resultado.costo_estimado_mensual * 0.20) * 12,
        ahorro_5_anios: (resultado.costo_estimado_mensual * 0.20) * 60,
      },
      desglose: [],
    });

  } catch (error) {
    alert("Ocurrió un problema al calcular. Revisa que la API esté corriendo.");
    console.error(error);
  } finally {
    botonSubmit.disabled    = false;
    botonSubmit.textContent = "Calcular mi consumo y ahorro";
  }
});

// ════════════════════════════════════════════════════════════
//  MÓDULO 10: COMPARADOR DE CATEGORÍAS
// ════════════════════════════════════════════════════════════

document.querySelectorAll(".btn--comparar").forEach((boton) => {
  boton.addEventListener("click", async () => {
    const item      = boton.closest(".item");
    const horas     = parseFloat(item.querySelector(".horas").value) || 0.1;
    const tarifa    = parseFloat(document.getElementById("tarifaClp").value) || 150;
    const contenedor = item.querySelector(".comparador-resultado");

    boton.textContent = "Comparando…";
    try {
      const respuesta = await fetch("/api/comparar", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ categoria: boton.dataset.categoria, horas_uso_diario: horas, tarifa_clp_kwh: tarifa }),
      });
      const resultado = await respuesta.json();
      if (resultado.error) {
        contenedor.innerHTML = `<p class="aviso">${resultado.error}</p>`;
      } else {
        const filas = resultado.opciones
          .map((op) => `<tr><td>${op.nombre}</td><td>${op.watts}W</td><td>${op.kwh_mes} kWh/mes</td><td>$${op.clp_mes.toLocaleString("es-CL")}/mes</td></tr>`)
          .join("");
        contenedor.innerHTML = `
          <table>
            <thead><tr><th>Opción</th><th>Potencia</th><th>Consumo</th><th>Costo</th></tr></thead>
            <tbody>${filas}</tbody>
          </table>
          <p class="aviso">⚠️ Catálogo de ejemplo — reemplazar por datos reales de retailers antes de usar como recomendación real.</p>`;
      }
      contenedor.hidden = false;
    } catch (error) {
      contenedor.innerHTML = '<p class="aviso">No se pudo comparar en este momento.</p>';
      contenedor.hidden = false;
    } finally {
      boton.textContent = "Ver alternativas más eficientes";
    }
  });
});

// ════════════════════════════════════════════════════════════
//  MÓDULO 11: NUEVO CÁLCULO / RESETEO PROFUNDO
// ════════════════════════════════════════════════════════════

document.getElementById("btnNuevoCalculo").addEventListener("click", () => {
  formulario.reset();

  // Resetear estado del módulo
  _tipoInmueble        = "Casa";
  _textoOtroInmueble   = "";
  _kwhRangoSeleccionado = null;
  _kwhRango            = "ninguno";

  // Restablecer botones de tipo de inmueble
  document.querySelectorAll(".tipo-inmueble-btn").forEach((b) => b.classList.remove("tipo-inmueble-btn--active"));
  const btnCasa = document.getElementById("tipoBtn-casa");
  if (btnCasa) btnCasa.classList.add("tipo-inmueble-btn--active");
  const tipoOtroWrap = document.getElementById("tipoOtroWrap");
  if (tipoOtroWrap) tipoOtroWrap.hidden = true;

  // Restablecer botones de rango kWh
  document.querySelectorAll(".kwh-range-btn").forEach((b) => b.classList.remove("kwh-range-btn--active"));
  const kwhExactWrap = document.getElementById("kwhExactWrap");
  if (kwhExactWrap) kwhExactWrap.hidden = true;
  const kwhBadge = document.getElementById("kwhRangoBadge");
  if (kwhBadge) kwhBadge.hidden = true;

  // Desmarcar todos los checkboxes
  formulario.querySelectorAll("input[type='checkbox']").forEach((chk) => {
    chk.checked = false;
    chk.dispatchEvent(new Event("change", { bubbles: true }));
  });
  document.querySelectorAll(".item.activo").forEach((item) => item.classList.remove("activo"));

  // Resetear badges de pestañas
  document.querySelectorAll(".tab-btn__badge").forEach((badge) => {
    badge.textContent = "0";
    badge.hidden = true;
  });

  // Resetear medidores
  document.querySelectorAll(".meter__value").forEach((el) => { el.textContent = "000.0"; });
  document.querySelectorAll(".submit-bar__kwh").forEach((el) => { el.textContent = "000.0 kWh"; });

  // Limpiar artefactos personalizados
  listaPersonalizados.innerHTML = "";

  // Limpiar resultados comparadores
  document.querySelectorAll(".comparador-resultado").forEach((el) => {
    el.innerHTML = "";
    el.hidden = true;
  });

  // Restaurar país y tarifa
  const selectPais = document.getElementById("selectPais");
  if (selectPais && _paisesCache) {
    selectPais.value = PAIS_DEFAULT;
    actualizarTarifaPorPais(_paisesCache, PAIS_DEFAULT);
  }

  // Regresar a pestaña Ubicación
  const primerTab = document.querySelector(".tab-btn");
  if (primerTab) primerTab.click();

  // Ocultar resultados
  resultadosSeccion.hidden = true;
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// ════════════════════════════════════════════════════════════
//  MÓDULO 12: MOSTRAR RESULTADOS
// ════════════════════════════════════════════════════════════

function mostrarResultados(resultado) {
  resultadosSeccion.hidden = false;
  document.getElementById("narrativa").textContent = resultado.narrativa;
  document.getElementById("totalKwh").textContent  = `${resultado.total_kwh_mes} kWh`;

  const sim    = window._simboloActivo || "$";
  const mon    = window._monedaActiva  || "";
  const fmtMon = (v) => `${sim} ${Number(v).toLocaleString("es-CL", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}${mon ? " " + mon : ""}`;

  document.getElementById("totalClp").textContent  = fmtMon(resultado.total_clp_mes);
  document.getElementById("ahorroClp").textContent = fmtMon(resultado.ahorro_potencial_clp_mes);

  // Recomendaciones
  const listaRecomendaciones = document.getElementById("listaRecomendaciones");
  listaRecomendaciones.innerHTML = "";
  if (resultado.recomendaciones && resultado.recomendaciones.length > 0) {
    resultado.recomendaciones.forEach((frase) => {
      const li = document.createElement("li");
      li.textContent = frase;
      listaRecomendaciones.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.textContent = "No encontramos oportunidades de ahorro adicionales con lo que marcaste — ¡ya vas bien!";
    listaRecomendaciones.appendChild(li);
  }

  // Proyección en el tiempo
  if (resultado.proyeccion) {
    document.getElementById("proy1Mes").textContent   = fmtMon(resultado.proyeccion.ahorro_1_mes);
    document.getElementById("proy6Meses").textContent = fmtMon(resultado.proyeccion.ahorro_6_meses);
    document.getElementById("proy1Anio").textContent  = fmtMon(resultado.proyeccion.ahorro_1_anio);
    document.getElementById("proy5Anios").textContent = fmtMon(resultado.proyeccion.ahorro_5_anios);
  }

  // Desglose
  const cuerpo       = document.getElementById("desgloseBody");
  const tablaDesglose = cuerpo.closest("table");
  const tieneDesglose = Array.isArray(resultado.desglose) && resultado.desglose.length > 0;

  cuerpo.innerHTML = "";
  if (tieneDesglose) {
    resultado.desglose.forEach((item) => {
      const fila  = document.createElement("tr");
      const kwh   = item.kwh_mes_actual ?? item.kwh_mes_llenado_habitual ?? "—";
      const ahorro = item.ahorro_clp_mes ?? 0;
      fila.innerHTML = `<td>${item.nombre}</td><td>${kwh}</td><td>${ahorro ? fmtMon(ahorro) : "—"}</td>`;
      cuerpo.appendChild(fila);
    });
  }
  if (tablaDesglose) tablaDesglose.hidden = !tieneDesglose;

  animarMedidor(resultado.total_kwh_mes);
  resultadosSeccion.scrollIntoView({ behavior: "smooth" });
}

document.getElementById("btnImprimir").addEventListener("click", () => {
  window.print();
});

// ════════════════════════════════════════════════════════════
//  MÓDULO 13: SUBIDA DE BOLETA — Drag & Drop + IA Extracción
// ════════════════════════════════════════════════════════════

(function initBoleta() {
  const dropzone    = document.getElementById("boletaDropzone");
  const fileInput   = document.getElementById("boletaFile");
  const dropContent = document.getElementById("boletaDropContent");
  const preview     = document.getElementById("boletaPreview");
  const actionsBar  = document.getElementById("boletaActions");
  const btnAnalizar = document.getElementById("btnAnalizarBoleta");
  const btnQuitar   = document.getElementById("btnQuitarBoleta");
  const resultado   = document.getElementById("boletaResultado");
  const errorBox    = document.getElementById("boletaError");
  const btnAplicar  = document.getElementById("btnAplicarBoleta");
  const kwhRow      = document.getElementById("boletaKwhRow");
  const kwhValor    = document.getElementById("boletaKwhValor");
  const tarifaRow   = document.getElementById("boletaTarifaRow");
  const tarifaValor = document.getElementById("boletaTarifaValor");
  const notaEl      = document.getElementById("boletaNota");
  const confianzaEl = document.getElementById("boletaConfianza");

  let archivoActual  = null;
  let datosExtraidos = null;

  // Drag & Drop
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) procesarArchivo(file);
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) procesarArchivo(fileInput.files[0]);
  });

  function procesarArchivo(file) {
    const ext = file.name.split(".").pop().toLowerCase();
    if (!["png", "jpg", "jpeg", "webp", "pdf"].includes(ext)) {
      mostrarError("Solo se aceptan imágenes (PNG, JPG, WEBP) o PDF.");
      return;
    }
    archivoActual  = file;
    datosExtraidos = null;
    if (ext !== "pdf") {
      const reader = new FileReader();
      reader.onload = (e) => {
        preview.src = e.target.result;
        preview.hidden = false;
        dropContent.hidden = true;
      };
      reader.readAsDataURL(file);
    } else {
      preview.hidden = true;
      dropContent.hidden = false;
      dropContent.querySelector(".boleta-dropzone__icon").textContent = "📋";
      dropContent.querySelector(".boleta-dropzone__text").textContent = `PDF seleccionado: ${file.name}`;
      dropContent.querySelector(".boleta-dropzone__hint").textContent = "Haz clic en Analizar para extraer los datos";
    }
    dropzone.classList.add("has-file");
    actionsBar.hidden = false;
    resultado.hidden  = true;
    errorBox.hidden   = true;
  }

  btnQuitar.addEventListener("click", resetBoleta);

  function resetBoleta() {
    archivoActual  = null;
    datosExtraidos = null;
    fileInput.value = "";
    preview.src    = "";
    preview.hidden = true;
    dropContent.hidden = false;
    dropContent.querySelector(".boleta-dropzone__icon").textContent = "📄";
    dropContent.querySelector(".boleta-dropzone__text").innerHTML =
      'Arrastra tu boleta aquí o <span class="boleta-link">haz clic para seleccionar</span>';
    dropContent.querySelector(".boleta-dropzone__hint").textContent = "PNG, JPG, WEBP o PDF · Máx. 10 MB";
    dropzone.classList.remove("has-file");
    actionsBar.hidden = true;
    resultado.hidden  = true;
    errorBox.hidden   = true;
    btnAplicar.hidden = true;
  }

  btnAnalizar.addEventListener("click", async () => {
    if (!archivoActual) return;
    const pais = document.getElementById("selectPais")?.value || "CL";
    btnAnalizar.disabled = true;
    btnAnalizar.classList.add("loading");
    btnAnalizar.innerHTML = '<span class="btn-icon">⏳</span> Analizando…';
    errorBox.hidden  = true;
    resultado.hidden = true;

    const formData = new FormData();
    formData.append("boleta", archivoActual);
    formData.append("pais", pais);

    try {
      const resp = await fetch("/api/subir-boleta", { method: "POST", body: formData });
      const data = await resp.json();
      if (data.error) {
        mostrarError(data.error + (data.sugerencia ? ` 💡 ${data.sugerencia}` : ""));
        return;
      }
      datosExtraidos = data;
      mostrarResultadoBoleta(data);

      // Si la boleta tiene kWh, aplicarlo también al selector de rangos como "boleta"
      if (data.kwh_mes != null && data.kwh_mes > 0) {
        _kwhRangoSeleccionado = parseFloat(data.kwh_mes);
        _kwhRango = "boleta";
        // Marcar visualmente el botón de boleta
        document.querySelectorAll(".kwh-range-btn").forEach((b) => b.classList.remove("kwh-range-btn--active"));
        const btnBoleta = document.getElementById("kwhBtn-boleta");
        if (btnBoleta) btnBoleta.classList.add("kwh-range-btn--active");
        const badge     = document.getElementById("kwhRangoBadge");
        const badgeText = document.getElementById("kwhRangoBadgeText");
        if (badge && badgeText) {
          badgeText.textContent = `✏️ Boleta: ${_kwhRangoSeleccionado} kWh/mes`;
          badge.hidden = false;
          badge.className = "kwh-rango-badge kwh-rango-badge--boleta";
        }
      }
    } catch (err) {
      mostrarError("No se pudo conectar con el servidor. ¿Está corriendo la app?");
      console.error(err);
    } finally {
      btnAnalizar.disabled = false;
      btnAnalizar.classList.remove("loading");
      btnAnalizar.innerHTML = '<span class="btn-icon">🔍</span> Analizar boleta';
    }
  });

  function mostrarResultadoBoleta(data) {
    resultado.hidden = false;
    if (data.kwh_mes != null) {
      kwhValor.textContent = `${Number(data.kwh_mes).toLocaleString("es-CL")} kWh`;
      kwhRow.hidden = false;
    } else {
      kwhRow.hidden = true;
    }
    const simbolo = data.simbolo || data.moneda || "";
    if (data.tarifa_kwh != null) {
      tarifaValor.textContent = `${simbolo} ${Number(data.tarifa_kwh).toLocaleString("es-CL", { minimumFractionDigits: 2 })} / kWh`;
      tarifaRow.hidden = false;
    } else {
      tarifaRow.hidden = true;
    }
    notaEl.textContent = data.nota ? `💬 ${data.nota}` : "";
    const nivel = (data.confianza || "media").toLowerCase();
    confianzaEl.textContent = `Confianza: ${nivel}`;
    confianzaEl.className   = `boleta-resultado__confianza ${nivel}`;
    btnAplicar.hidden = data.tarifa_kwh == null;
  }

  btnAplicar.addEventListener("click", () => {
    if (!datosExtraidos) return;
    if (datosExtraidos.tarifa_kwh != null) {
      const campo = document.getElementById("tarifaClp");
      if (campo) {
        campo.value = datosExtraidos.tarifa_kwh;
        campo.style.transition = "box-shadow 0.3s";
        campo.style.boxShadow  = "0 0 0 3px rgba(34, 211, 168, 0.5)";
        setTimeout(() => { campo.style.boxShadow = ""; }, 1500);
      }
    }
    btnAplicar.textContent = "✅ ¡Valores aplicados!";
    btnAplicar.style.background = "linear-gradient(135deg, #059669, #10b981)";
    setTimeout(() => {
      btnAplicar.textContent = "✅ Aplicar estos valores al cálculo";
      btnAplicar.style.background = "";
    }, 2500);
  });

  function mostrarError(msg) {
    errorBox.textContent = `⚠️ ${msg}`;
    errorBox.hidden = false;
  }
})();