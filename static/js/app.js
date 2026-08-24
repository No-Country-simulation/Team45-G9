/* ═══════════════════════════════════════════════════════════
   VólticvS — app.js v9.0  |  BOLETA ENERGÉTICA + RESET TOTAL
   Engine del Wizard, Avatar, Factura de Impresión
   ═══════════════════════════════════════════════════════════ */

'use strict';

let currentStep = 1;
const TOTAL_STEPS = 4;
let _paisesCache = null;
const PAIS_DEFAULT = 'CL';

/* ── Todos los contadores arrancan en 0 al iniciar/resetear ── */
const COUNTER_ZEROS = {
  inputDormitorios: 0,
  inputVentanas:    0,
  inputMayores:     0,
  inputMenores:     0,
  lavadoFrecuencia: 0,
  refrigerador:     0,
  freezer:          0,
  tv:               0,
  tvFrecuencia:     0,
  inputLucesExterior:     0,
  inputLucesInterior:     0,
  inputCargadoresVampiro: 0
};

/* Lista de equipos con toggle para construir el desglose */
const EQUIPOS_TOGGLE = [
  { id: 'aireAcondicionado',    payloadKey: 'aire_acondicionado',       nombre: 'Aire Acondicionado / Climatización', detalle: 'Equipos de refrigeración o calefacción eléctrica' },
  { id: 'calefaccionElectrica', payloadKey: 'calefaccion_electrica',    nombre: 'Calefacción Eléctrica',              detalle: 'Estufas, radiadores, calefactores' },
  { id: 'aguaCalienteElectrica',payloadKey: 'agua_caliente_electrica',  nombre: 'Calentador de Agua / Termotanque (Eléctrico)', detalle: 'Uso de electricidad para calentar agua' },
  { id: 'secarropasElectrico',  payloadKey: 'secarropas_electrico',     nombre: 'Secarropas Eléctrico',               detalle: 'Secado de prendas' },
  { id: 'hornoElectrico',       payloadKey: 'horno_electrico',          nombre: 'Horno / Anafe Eléctrico',            detalle: 'Cocción eléctrica' }
];

// ── 1. DOM REFERENCES ───────────────────────────────────────
const wizardSteps    = document.querySelectorAll('.wizard-step');
const progressSteps  = document.querySelectorAll('.progress-step');
const progressFill   = document.getElementById('progressFill');
const voltiFrame     = document.getElementById('voltiFrame');
const voltiAvatarImg = document.getElementById('voltiAvatarImg');
const voltiBubble    = document.getElementById('voltiBubble');
const voltiBubbleText= document.getElementById('voltiBubbleText');
const voltiMood      = document.getElementById('voltiMood');
const resultadosSeccion = document.getElementById('resultados');

// ── 2. ESTADOS DEL PANEL LATERAL (antes "Volti", ahora Denji) ──
// Nota: saludando.png no existe en el proyecto; usamos impatado.png para el inicio.
const VOLTI_ASSETS = {
  1:       '/static/img/volti/impatado.png',
  2:       '/static/img/volti/preguntas.png',
  3:       '/static/img/volti/bien.png',
  4:       '/static/img/volti/bien.png',
  submit:  '/static/img/volti/preguntas.png',
  results: '/static/img/volti/felicidades.png',
  error:   '/static/img/volti/error.png'
};

const VOLTI_MESSAGES = {
  // NOTA: estos 7 textos NO pasan por el sistema de idiomas (_t()) — se
  // escriben directo al DOM en updateVoltiMessage() más abajo. Sea cual sea
  // el idioma elegido, esta burbuja siempre sale en español. Es un gap
  // real, independiente del cambio de nombre — señalado para decidir si se
  // conecta al i18n en otra vuelta.
  1:       '¡Hola! Soy <strong>Denji</strong>, tu asesor energético. Indícame tu ubicación y tarifa para comenzar.',
  2:       '¡Excelente! Ahora cuéntame sobre tu tipo de vivienda y la cantidad de habitantes.',
  3:       'Selecciona los artefactos de mayor consumo que utilizas en tu hogar.',
  4:       'Indica la frecuencia con la que usas tus electrodomésticos.',
  submit:  '⚡ Calculando tu consumo estimado... ¡Dame un momento!',
  results: '¡Aquí están tus resultados! Revisa las recomendaciones para ahorrar más.',
  error:   'Oops, parece que faltan algunos datos. Por favor, revisa la información.'
};

const VOLTI_MOODS = {
  1: 'Saludando', 2: 'Analizando', 3: 'Atento', 4: 'Entusiasmado',
  submit: 'Calculando', results: 'Celebrando', error: 'Preocupado'
};

// ── 3. AVATAR ────────────────────────────────────────────────
function _t(key) {
  return (window.DenjiI18n ? window.DenjiI18n.t(key) : key);
}

let _ultimoKeyVolti = 1;
let _ultimoMensajeOverride = null;

function updateVoltiMessage(key, mensajeOverride) {
  _ultimoKeyVolti = key;
  _ultimoMensajeOverride = mensajeOverride || null;
  const claveTraduccion = 'volti_msg_' + key;
  const traducido = _t(claveTraduccion);
  // Si window.DenjiI18n no existe o la clave no está en el diccionario,
  // t() devuelve la clave misma tal cual ("volti_msg_1") en vez de un
  // valor vacío — hay que detectar ese caso explícito para caer bien al
  // mensaje en español, no mostrar la clave literal en pantalla.
  // mensajeOverride manda cuando existe: antes, cualquier error de
  // validación mostraba la misma frase genérica ("Oops, parece que faltan
  // algunos datos"), sin decir CUÁL — mientras el error específico y real
  // aparecía chico, en rojo, junto al campo. Ahora Denji dice lo mismo.
  const message = mensajeOverride || ((traducido !== claveTraduccion) ? traducido : (VOLTI_MESSAGES[key] || VOLTI_MESSAGES[1]));
  const imgSrc  = VOLTI_ASSETS[key]   || VOLTI_ASSETS[1];
  const claveMood = 'volti_mood_' + key;
  const moodTraducido = _t(claveMood);
  const mood = (moodTraducido !== claveMood) ? moodTraducido : (VOLTI_MOODS[key] || VOLTI_MOODS[1]);

  if (voltiAvatarImg) {
    voltiAvatarImg.style.opacity = '0';
    setTimeout(() => {
      voltiAvatarImg.src = imgSrc;
      voltiAvatarImg.style.opacity = '1';
    }, 150);
  }
  if (voltiFrame) {
    voltiFrame.classList.remove('pop');
    void voltiFrame.offsetWidth;
    voltiFrame.classList.add('pop');
    setTimeout(() => voltiFrame.classList.remove('pop'), 400);
  }
  if (voltiBubble && voltiBubbleText) {
    voltiBubble.classList.remove('pulse');
    void voltiBubble.offsetWidth;
    voltiBubble.classList.add('pulse');
    voltiBubbleText.innerHTML = message;
    setTimeout(() => voltiBubble.classList.remove('pulse'), 450);
  }
  if (voltiMood) voltiMood.textContent = mood;
}

// Si cambia el idioma a mitad de camino (vía el panel de accesibilidad), la
// burbuja se refresca en el sitio con el mismo estado que ya mostraba —
// nada se pierde, nada se reinicia.
window.addEventListener('denji-lang-change', function () {
  updateVoltiMessage(_ultimoKeyVolti, _ultimoMensajeOverride);
});

// ── 4. WIZARD Y PROGRESS BAR ─────────────────────────────────
function updateProgressBar() {
  const percent = ((currentStep - 1) / (TOTAL_STEPS - 1)) * 100;
  if (progressFill) progressFill.style.width = percent + '%';

  progressSteps.forEach((step, index) => {
    const stepNum = index + 1;
    step.classList.remove('progress-step--active', 'progress-step--done');
    if (stepNum === currentStep)       step.classList.add('progress-step--active');
    else if (stepNum < currentStep)    step.classList.add('progress-step--done');
  });
}

function showStep(stepNumber) {
  // Bug real encontrado: Denji llama a window.showStep() directo para saltar
  // visualmente de página (sincronizarPasoJC en denji.js), pero antes de este
  // arreglo eso NUNCA actualizaba `currentStep` — la variable que usa el
  // botón real "Siguiente" para saber en qué paso está. Resultado: Denji
  // mueve la vista al paso 3, la persona llena los campos ahí, aprieta
  // "Siguiente", y nextStep() valida un paso viejo (el que currentStep
  // todavía recordaba) y aterriza en el paso equivocado. Centralizar la
  // sincronización acá adentro hace que cualquiera que llame a showStep()
  // —Denji, los clics de la barra de progreso, o el propio wizard— deje
  // currentStep siempre correcto, sin tener que acordarse de hacerlo en
  // cada lugar por separado.
  currentStep = stepNumber;
  // Expuesto para que Denji (denji.js) pueda resincronizar su propio
  // contador interno de preguntas cuando la persona avanza usando el
  // formulario real directo (no a través de Denji) — sin esto, Denji se
  // queda mostrando preguntas de un paso anterior mientras la página real
  // ya avanzó, y "Confirmar" queda desconectado de lo que se ve en pantalla.
  window.wizardPasoActual = stepNumber;
  wizardSteps.forEach(step => {
    step.classList.toggle('wizard-step--active', parseInt(step.dataset.step) === stepNumber);
  });
  if (resultadosSeccion) resultadosSeccion.hidden = true;
  ocultarErrorGlobal();
  updateProgressBar();
  updateVoltiMessage(stepNumber);
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ── 4B. VALIDACIÓN ──────────────────────────────────────────
function clearError(el) {
  if (!el) return;
  el.classList.remove('input-error', 'shake');
  el.parentNode?.querySelector('.error-msg')?.remove();
}

// El mensaje genérico de Denji ("Oops, parece que faltan algunos datos")
// no decía QUÉ estaba mal — se veía distinto al error específico y rojo que
// sí aparece junto al campo, así que la persona tenía que encontrarlo por su
// cuenta. Estas dos funciones guardan el primer mensaje real acá, para que
// Denji lo use en vez de su frase genérica.
let _primerMensajeError = null;

function showError(el, mensaje) {
  if (!el) return;
  if (!_primerMensajeError) _primerMensajeError = mensaje;
  el.classList.add('input-error', 'shake');
  let msg = el.parentNode?.querySelector('.error-msg');
  if (!msg && el.parentNode) {
    msg = document.createElement('span');
    msg.className = 'error-msg';
    el.parentNode.appendChild(msg);
  }
  if (msg) msg.textContent = mensaje;
  setTimeout(() => el.classList.remove('shake'), 400);
}

/**
 * Aviso de error a nivel de página, para fallos que no pertenecen a ningún
 * campo del formulario (la API no responde, se agotó el tiempo, 429…).
 * Antes estos fallos solo cambiaban la cara del asistente: el usuario veía a
 * Denji poner gesto de error sin saber qué había pasado ni qué hacer.
 */
function mostrarErrorGlobal(mensaje) {
  if (!_primerMensajeError) _primerMensajeError = mensaje;
  let aviso = document.getElementById('avisoGlobal');
  if (!aviso) {
    aviso = document.createElement('div');
    aviso.id = 'avisoGlobal';
    aviso.className = 'aviso-global';
    aviso.setAttribute('role', 'alert');
    document.getElementById('btnSubmit')?.closest('.step-card')?.appendChild(aviso);
  }
  aviso.textContent = mensaje;
  aviso.hidden = false;
}

function ocultarErrorGlobal() {
  const aviso = document.getElementById('avisoGlobal');
  if (aviso) aviso.hidden = true;
}

function validarPaso(pasoActual) {
  let valido = true;
  _primerMensajeError = null;
  document.querySelector(`.wizard-step[data-step="${pasoActual}"]`)
    ?.querySelectorAll('.input-error').forEach(clearError);
  ocultarErrorGlobal();

  if (pasoActual === 1) {
    const sel = document.getElementById('pais') || document.getElementById('selectPais');
    if (sel && sel.hasAttribute('required') && !sel.value?.trim()) {
      showError(sel, 'Por favor, selecciona un país.');
      valido = false;
    }
    // La ubicación completa (país + provincia/estado) es la única sección que
    // no puede quedar en blanco — el modelo de eficiencia la necesita para
    // la tarifa, el clima, y los coeficientes de regresión por región.
    const provincia = document.getElementById('selectProvincia');
    if (provincia && !provincia.value?.trim()) {
      showError(provincia, 'Indica tu provincia, estado o región — el cálculo de eficiencia lo necesita.');
      valido = false;
    }
  }

  if (pasoActual === 3) {
    const skip = document.getElementById('skipStep3')?.checked;
    if (!skip) {
      const algunoActivo = Array.from(document.querySelectorAll('#step3 .equip-toggle'))
        .some(el => el.checked);
      if (!algunoActivo) {
        mostrarErrorGlobal('Selecciona al menos un artefacto, o marca "Ninguno de estos equipos está en mi vivienda".');
        valido = false;
      }
    }
  }

  if (pasoActual === 4) {
    const skip = document.getElementById('skipStep4')?.checked;
    if (!skip) {
      const ids = ['lavadoFrecuencia', 'refrigerador', 'freezer', 'tv'];
      const algunoMayorACero = ids.some(id => {
        const n = parseInt(document.getElementById(id)?.value, 10);
        return !isNaN(n) && n > 0;
      });
      if (!algunoMayorACero) {
        mostrarErrorGlobal('Indica al menos una cantidad mayor a 0, o marca "No quiero responder esta sección".');
        valido = false;
      }
    }
    // El campo ya tenía min="0" max="24" en el HTML, pero eso no bloquea
    // que alguien escriba 25 a mano — los navegadores no impiden tipear
    // fuera de rango en <input type="number">, solo afectan las flechitas.
    const tvFrecuenciaEl = document.getElementById('tvFrecuencia');
    if (tvFrecuenciaEl) {
      const horas = parseFloat(tvFrecuenciaEl.value);
      if (!isNaN(horas) && (horas < 0 || horas > 24)) {
        showError(tvFrecuenciaEl, 'Las horas de uso diario de TV deben estar entre 0 y 24.');
        valido = false;
      }
    }
  }

  if (!valido) updateVoltiMessage('error', _primerMensajeError);
  return valido;
}

function nextStep() {
  if (currentStep >= TOTAL_STEPS) return;
  if (!validarPaso(currentStep)) return;
  currentStep++;
  showStep(currentStep);
  saveState();
}

function prevStep() {
  if (currentStep <= 1) return;
  currentStep--;
  showStep(currentStep);
}

// ── 5. INTERACTIVIDAD DE COMPONENTES ────────────────────────
let tipoInmuebleSeleccionado = 'Casa';

document.querySelectorAll('.vivienda-card').forEach(card => {
  card.addEventListener('click', () => {
    document.querySelectorAll('.vivienda-card').forEach(c => c.classList.remove('vivienda-card--active'));
    card.classList.add('vivienda-card--active');
    tipoInmuebleSeleccionado = card.dataset.value;

    // El campo libre solo aparece con "Otro": es el único caso para el que se
    // escribió /api/interpretar-campo.
    const grupoOtro = document.getElementById('grupoInmuebleOtro');
    if (grupoOtro) grupoOtro.hidden = card.dataset.value !== 'Otro';
  });
});

// ── Interpretación del tipo de inmueble descrito en texto libre ──────────────
// Se dispara al salir del campo, no en cada tecla: una llamada al modelo por
// texto ingresado, como dice el contrato del endpoint.
let ultimoTextoInterpretado = '';

document.getElementById('inputInmuebleOtro')?.addEventListener('blur', async (e) => {
  const texto = e.target.value.trim();
  const estado = document.getElementById('inmuebleOtroEstado');

  if (!texto || texto === ultimoTextoInterpretado) return;
  ultimoTextoInterpretado = texto;

  if (estado) estado.textContent = 'Interpretando…';

  try {
    const res = await fetchConTimeout('/api/interpretar-campo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ campo: 'tipo_inmueble', texto })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const { valor_mapeado } = await res.json();
    tipoInmuebleSeleccionado = valor_mapeado;
    if (estado) estado.textContent = `Lo clasificamos como: ${valor_mapeado}`;
  } catch (error) {
    console.error('No se pudo interpretar el tipo de inmueble:', error);
    // Se conserva "Otro" como valor: es un miembro válido de la lista y no
    // inventa una clasificación que el usuario no dio.
    tipoInmuebleSeleccionado = 'Otro';
    if (estado) estado.textContent = 'No pudimos interpretarlo; lo dejamos como "Otro".';
  }
});

// ── 5B. SUBIDA DE BOLETA ────────────────────────────────────
// El endpoint /api/subir-boleta existía desde el principio (pdfplumber, regex
// y modelo de visión, ~145 líneas) pero no había forma de invocarlo: no
// existía ningún <input type="file"> en toda la interfaz.
document.getElementById('inputBoleta')?.addEventListener('change', async (e) => {
  const archivo = e.target.files?.[0];
  const estado = document.getElementById('boletaEstado');
  if (!archivo || !estado) return;

  const pintar = (texto, clase) => {
    estado.hidden = false;
    estado.textContent = texto;
    estado.className = `boleta-estado boleta-estado--${clase}`;
  };

  pintar('Leyendo tu boleta…', 'cargando');
  e.target.disabled = true;

  const cuerpo = new FormData();
  cuerpo.append('boleta', archivo);
  cuerpo.append('pais', document.getElementById('pais')?.value || window._paisActivo || 'CL');

  try {
    // Más margen que el resto: implica subir el archivo y analizarlo.
    const res = await fetchConTimeout('/api/subir-boleta', { method: 'POST', body: cuerpo }, 30000);
    const datos = await res.json().catch(() => ({}));

    if (!res.ok) {
      pintar(datos.error || 'No pudimos leer la boleta. Prueba con otra foto o ingresa el consumo a mano.', 'error');
      return;
    }

    const partes = [];

    if (datos.kwh_mes != null) {
      const campoConsumo = document.getElementById('inputConsumo');
      if (campoConsumo) campoConsumo.value = Math.round(datos.kwh_mes);

      // Una boleta informa el período facturado, que es mensual: hay que
      // desmarcar el interruptor de consumo anual o el backend lo dividiría por 12.
      const flagAnual = document.getElementById('flagAnual');
      if (flagAnual?.checked) {
        flagAnual.checked = false;
        flagAnual.dispatchEvent(new Event('change'));
      }
      partes.push(`consumo: ${Math.round(datos.kwh_mes)} kWh`);
    }

    if (datos.tarifa_kwh != null) {
      window._tarifaBoleta = datos.tarifa_kwh;
      partes.push(`tarifa: ${datos.simbolo || ''}${datos.tarifa_kwh} ${datos.moneda || ''}`.trim());
    }

    if (!partes.length) {
      pintar('No encontramos el consumo en la boleta. Ingrésalo a mano más abajo.', 'error');
      return;
    }

    const confianza = datos.confianza ? ` (confianza ${datos.confianza})` : '';
    pintar(`✓ Cargado en "Consumo eléctrico mensual" — ${partes.join(' · ')}${confianza}. Revisa que coincida con tu boleta antes de continuar.`, 'ok');
  } catch (error) {
    const esTimeout = error.name === 'AbortError';
    console.error('Error al subir la boleta:', error);
    pintar(esTimeout
      ? 'La lectura está tardando demasiado. Ingresa el consumo a mano.'
      : 'No pudimos conectar con el servidor. Ingresa el consumo a mano.', 'error');
  } finally {
    e.target.disabled = false;
  }
});

document.querySelectorAll('.equip-toggle').forEach(toggle => {
  toggle.addEventListener('change', e => {
    e.target.closest('.equip-item')
      ?.classList.toggle('equip-item--on', e.target.checked);
  });
});

document.querySelectorAll('.counter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = document.getElementById(btn.dataset.target);
    if (!input) return;
    let val = parseInt(input.value) || 0;
    const min = parseInt(input.min) || 0;
    const max = parseInt(input.max) || 999;
    if (btn.classList.contains('counter-btn--plus') && val < max) val++;
    else if (btn.classList.contains('counter-btn--minus') && val > min) val--;
    input.value = val;
    clearError(input);
  });
});

// ── 6. PAÍSES ────────────────────────────────────────────────
async function cargarPaises() {
  const selectPais = document.getElementById('pais') || document.getElementById('selectPais');
  if (!selectPais) return;
  try {
    // Con timeout: es la primera petición de la página y, sin tope, el selector
    // se queda en "Cargando países…" indefinidamente si el servidor no responde.
    const res = await fetchConTimeout('/api/paises', {}, 10000);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const paises = await res.json();
    _paisesCache = paises;

    selectPais.innerHTML = '<option value="">Selecciona un país...</option>';
    Object.entries(paises).forEach(([codigo, datos]) => {
      const opt = document.createElement('option');
      opt.value = codigo;
      opt.textContent = `${datos.nombre} (${datos.moneda})`;
      selectPais.appendChild(opt);
    });

    // Siempre aplicar default al iniciar (resetearTodo ya limpió estado)
    selectPais.value = PAIS_DEFAULT;
    actualizarInfoPais(paises, PAIS_DEFAULT);

    selectPais.addEventListener('change', () => {
      actualizarInfoPais(paises, selectPais.value);
      saveState();
    });
  } catch {
    selectPais.innerHTML = '<option value="">No se pudo cargar la lista de países</option>';
  }
}

function actualizarInfoPais(paises, codigo) {
  const datos = paises[codigo];
  if (!datos) return;
  window._monedaActiva     = datos.moneda  || '';
  window._simboloActivo    = datos.simbolo || '';
  window._paisActivo       = codigo;
  window._nombrePaisActivo = datos.nombre  || codigo;

  // Galones para sistema imperial (US, PR), Litros para métrico
  const esImperial = (codigo === 'US' || codigo === 'PR');
  window._flagGalones = esImperial ? 1 : 2;
  window._unidadAgua  = esImperial ? 'Galones' : 'Litros';

  // Actualizar dinámicamente en la UI si hay elementos de moneda o unidades
  document.querySelectorAll('.simbolo-moneda').forEach(el => (el.textContent = window._simboloActivo));
  document.querySelectorAll('.codigo-moneda').forEach(el => (el.textContent = window._monedaActiva));
  document.querySelectorAll('.unidad-agua').forEach(el => (el.textContent = window._unidadAgua));
}

// ════════════════════════════════════════════════════════════
//  ── 7. RESET TOTAL (DOMContentLoaded + Nuevo Cálculo) ──
// ════════════════════════════════════════════════════════════
function resetearTodo() {
  // 1. Limpiar localStorage
  localStorage.removeItem('volticvs_state');

  // 2. Resetear todos los inputs de texto a vacío
  document.querySelectorAll('input[type="text"]').forEach(el => (el.value = ''));

  // 3. Resetear número libre (consumo kWh)
  const inputConsumo = document.getElementById('inputConsumo');
  if (inputConsumo) inputConsumo.value = '';

  // 4. Resetear select de país al default (se aplicará tras cargar países)
  const selectPais = document.getElementById('pais') || document.getElementById('selectPais');
  if (selectPais) {
    selectPais.value = PAIS_DEFAULT;
    if (_paisesCache) actualizarInfoPais(_paisesCache, PAIS_DEFAULT);
  }

  // 5. Toggle de periodo en MENSUAL, que es lo que pide la etiqueta del campo
  const flagAnual = document.getElementById('flagAnual');
  if (flagAnual) {
    flagAnual.checked = false;
    const flagAnualLabel = document.getElementById('flagAnualLabel');
    if (flagAnualLabel) flagAnualLabel.textContent = 'El consumo es mensual';
  }

  // 5B. Limpiar todo lo relativo a la boleta subida
  window._tarifaBoleta = null;
  ultimoTextoInterpretado = '';
  const inputBoleta = document.getElementById('inputBoleta');
  if (inputBoleta) inputBoleta.value = '';
  const boletaEstado = document.getElementById('boletaEstado');
  if (boletaEstado) boletaEstado.hidden = true;
  const grupoOtro = document.getElementById('grupoInmuebleOtro');
  if (grupoOtro) grupoOtro.hidden = true;
  ocultarErrorGlobal();

  // 6. TODOS los contadores a CERO
  Object.entries(COUNTER_ZEROS).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (el) el.value = val;
  });

  // 7. Desmarcar todos los checkboxes excepto flagAnual (marcado en el paso 5)
  document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
    if (cb.id !== 'flagAnual') {
      cb.checked = false;
      cb.closest('.equip-item')?.classList.remove('equip-item--on');
    }
  });

  // 8. Restablecer tipo de inmueble a "Casa"
  tipoInmuebleSeleccionado = 'Casa';
  document.querySelectorAll('.vivienda-card').forEach(card => {
    card.classList.toggle('vivienda-card--active', card.dataset.value === 'Casa');
  });

  // 9. Limpiar errores de validación
  document.querySelectorAll('.input-error').forEach(clearError);
  document.querySelectorAll('.error-msg').forEach(el => el.remove());

  // 10. Limpiar estado interno de resultados
  window._lastPayload  = null;
  window._lastResultado = null;

  // 11. Ocultar sección de resultados
  if (resultadosSeccion) {
    resultadosSeccion.hidden = true;
    resultadosSeccion.style.display = '';
  }

  // 12. Volver al Paso 1
  currentStep = 1;
  showStep(1);             // Incluye updateProgressBar() + updateVoltiMessage(1)

  // Restaurar el HUD de Denji, oculto al mostrar los resultados
  const denjiHud = document.getElementById('denji-hud');
  if (denjiHud) denjiHud.style.display = '';

  // 13. Scroll al inicio
  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (typeof window.denjiReiniciar === 'function') window.denjiReiniciar();
}

// ── 8. EVENT LISTENERS ───────────────────────────────────────
document.getElementById('btnNext1')?.addEventListener('click', nextStep);
document.getElementById('btnNext2')?.addEventListener('click', nextStep);
document.getElementById('btnNext3')?.addEventListener('click', nextStep);
document.getElementById('btnPrev2')?.addEventListener('click', prevStep);
document.getElementById('btnPrev3')?.addEventListener('click', prevStep);
document.getElementById('btnPrev4')?.addEventListener('click', prevStep);

// ── Navegación directa por botones de progreso (directriz: desplazamiento
// entre Ubicación/Vivienda/Equipamiento/Rutinas) ────────────────────────────
progressSteps.forEach((btn) => {
  btn.style.cursor = 'pointer';
  btn.addEventListener('click', () => {
    const target = parseInt(btn.dataset.step, 10);
    if (target === currentStep) return;
    // Ir hacia atrás siempre permitido; hacia adelante valida pasos intermedios
    if (target < currentStep) {
      currentStep = target;
      showStep(currentStep);
    } else {
      for (let s = currentStep; s < target; s++) {
        if (!validarPaso(s)) return;
      }
      currentStep = target;
      showStep(currentStep);
      saveState();
    }
  });
});

document.getElementById('btnNuevoCalculo')?.addEventListener('click', resetearTodo);
document.getElementById('flagAnual')?.addEventListener('change', e => {
  const label = document.getElementById('flagAnualLabel');
  if (label) label.textContent = e.target.checked ? 'El consumo es anual' : 'El consumo es mensual';
});

// ── 8A. SUBMIT: CALCULAR CONSUMO ─────────────────────────────

const TIMEOUT_PETICION_MS = 15000;

/**
 * fetch con tope de tiempo. Sin esto el navegador espera indefinidamente:
 * si el backend tarda (o Groq se cuelga), el usuario se queda mirando un
 * botón que no responde y sin ningún aviso.
 */
async function fetchConTimeout(url, opciones = {}, ms = TIMEOUT_PETICION_MS) {
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), ms);
  try {
    return await fetch(url, { ...opciones, signal: control.signal });
  } finally {
    clearTimeout(temporizador);
  }
}

/** Extrae el mensaje de error del cuerpo JSON, con un respaldo legible. */
async function mensajeDeError(res) {
  try {
    const cuerpo = await res.json();
    if (cuerpo?.error) return cuerpo.error;
  } catch { /* el cuerpo no era JSON */ }

  if (res.status === 429) return 'Demasiadas consultas seguidas. Espera un momento e inténtalo de nuevo.';
  return 'No pudimos completar el cálculo. Inténtalo de nuevo en unos segundos.';
}

document.getElementById('btnSubmit')?.addEventListener('click', async (evento) => {
  // Bug real encontrado: este botón nunca llamaba a validarPaso() antes de
  // calcular — va directo a armar el payload y enviarlo. La validación de
  // horas de TV (0-24) vivía dentro de validarPaso(4), pero como nada la
  // invocaba acá, era código muerto: nunca se ejecutaba al apretar
  // "Calcular", solo si alguien llegaba al paso 4 vía un botón "Siguiente"
  // que ni siquiera existe en este paso (el último no tiene "Siguiente",
  // tiene "Calcular").
  if (!validarPaso(4)) return;

  updateVoltiMessage('submit');

  const boton = evento.currentTarget;
  const textoOriginal = boton.innerHTML;
  boton.disabled = true;
  boton.innerHTML = 'Calculando…';

  const v = id => document.getElementById(id);
  const horasDiariasTv = parseFloat(v('tvFrecuencia')?.value) || 0;

  const datosPayload = {
    consumo:               parseInt(v('inputConsumo')?.value || '0') || 0,
    consumo_kwh:           parseInt(v('inputConsumo')?.value || '0') || 0,
    flag_anual:            v('flagAnual')?.checked ? 1 : 0,
    pais:                  v('pais')?.value || v('selectPais')?.value || window._paisActivo || 'CL',
    estado_provincia:      v('selectProvincia')?.value || '',
    dormitorios:           parseInt(v('inputDormitorios')?.value) || 0,
    ventanas:              parseInt(v('inputVentanas')?.value) || 0,
    habitantes_mayores:    parseInt(v('inputMayores')?.value) || 0,
    habitantes_menores:    parseInt(v('inputMenores')?.value) || 0,
    aire_acondicionado:    v('aireAcondicionado')?.checked ? 1 : 0,
    calefaccion_electrica: v('calefaccionElectrica')?.checked ? 1 : 0,
    agua_caliente_electrica: v('aguaCalienteElectrica')?.checked ? 1 : 0,
    secarropas_electrico:  v('secarropasElectrico')?.checked ? 1 : 0,
    horno_electrico:       v('hornoElectrico')?.checked ? 1 : 0,
    agua_caliente_tamano:  0,
    flag_galones:          window._flagGalones || 2,
    lavado_frecuencia:     parseInt(v('lavadoFrecuencia')?.value) || 0,
    refrigerador:          parseInt(v('refrigerador')?.value) || 0,
    freezer:               parseInt(v('freezer')?.value) || 0,
    luces_exterior:        parseInt(v('inputLucesExterior')?.value) || 0,
    luces_interior:        parseInt(v('inputLucesInterior')?.value) || 0,
    cantidad_cargadores:   parseInt(v('inputCargadoresVampiro')?.value) || 0,
    tv:                    parseInt(v('tv')?.value) || 0,
    tv_frecuencia:         horasDiariasTv * 7,
    tipo_inmueble:         tipoInmuebleSeleccionado,
    rangos_horario_uso:    Array.from(document.querySelectorAll('.rango-horario:checked')).map(el => el.value),
    idioma:                (window.DenjiI18n && window.DenjiI18n.lang) || 'es'
  };

  // Tarifa leída de la boleta del usuario, si la subió. Es más exacta que la
  // referencial del país, así que el backend le da prioridad.
  if (window._tarifaBoleta) datosPayload.tarifa_kwh = window._tarifaBoleta;

  window._lastPayload = datosPayload;

  try {
    // Una sola llamada. Antes se reintentaba contra /api/calcular y /calcular
    // con este mismo payload, que tiene otra forma: /api/calcular no falla,
    // responde 200 con todo en 0 y el usuario veía "0 kWh" como si fuera un
    // resultado válido. /calcular ni siquiera existe.
    const res = await fetchConTimeout('/api/analisis-energetico', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datosPayload)
    });

    if (!res.ok) {
      mostrarErrorGlobal(await mensajeDeError(res));
      updateVoltiMessage('error', _primerMensajeError);
      return;
    }

    const resultado = await res.json();
    mostrarResultados(resultado, datosPayload);
    updateVoltiMessage('results');
  } catch (e) {
    const esTimeout = e.name === 'AbortError';
    console.error('Error conectando con la API:', e);
    mostrarErrorGlobal(esTimeout
      ? 'El cálculo está tardando más de lo normal. Revisa tu conexión e inténtalo de nuevo.'
      : 'No pudimos conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.');
    updateVoltiMessage('error', _primerMensajeError);
  } finally {
    boton.disabled = false;
    boton.innerHTML = textoOriginal;
  }
});

// ── 8B. MOSTRAR RESULTADOS EN DOM ────────────────────────────
/** Gráfico de torta en SVG puro (sin librería externa, mismo criterio que el
 * resto del proyecto: sin CDN). Recibe { "Refrigerador": 36.0, ... } y arma
 * el gráfico + una leyenda con el porcentaje real de cada categoría. */
const COLORES_TORTA = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626', '#8b5cf6', '#0891b2', '#db2777', '#65a30d', '#ea580c', '#4f46e5'];

function renderGraficoTorta(desglose, contenedorId) {
  const contenedor = document.getElementById(contenedorId);
  if (!contenedor) return;
  contenedor.innerHTML = '';

  const entradas = Object.entries(desglose || {}).filter(([, kwh]) => kwh > 0);
  if (entradas.length === 0) {
    contenedor.innerHTML = '<p style="font-size:0.82rem;color:#64748b;">Sin desglose disponible para este cálculo.</p>';
    return;
  }

  const total = entradas.reduce((suma, [, kwh]) => suma + kwh, 0);
  const cx = 90, cy = 90, r = 80;
  let anguloActual = -90; // empieza arriba, sentido horario

  const paths = entradas.map(([nombre, kwh], i) => {
    const porcentaje = kwh / total;
    const anguloBarrido = porcentaje * 360;
    const anguloInicio = anguloActual;
    const anguloFin = anguloActual + anguloBarrido;
    anguloActual = anguloFin;

    const rad = deg => (deg * Math.PI) / 180;
    const x1 = cx + r * Math.cos(rad(anguloInicio));
    const y1 = cy + r * Math.sin(rad(anguloInicio));
    const x2 = cx + r * Math.cos(rad(anguloFin));
    const y2 = cy + r * Math.sin(rad(anguloFin));
    const arcoGrande = anguloBarrido > 180 ? 1 : 0;
    const color = COLORES_TORTA[i % COLORES_TORTA.length];

    // Una sola porción == círculo completo (100%) — un arco no se puede
    // dibujar así, se dibuja un círculo directo en ese caso.
    if (entradas.length === 1) {
      return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${color}"></circle>`;
    }
    return `<path d="M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${arcoGrande} 1 ${x2},${y2} Z" fill="${color}"></path>`;
  }).join('');

  const leyenda = entradas.map(([nombre, kwh], i) => {
    const pct = Math.round((kwh / total) * 100);
    const color = COLORES_TORTA[i % COLORES_TORTA.length];
    return `<div style="display:flex;align-items:center;gap:0.4rem;font-size:0.78rem;margin:0.2rem 0;">
      <span style="width:11px;height:11px;border-radius:3px;background:${color};flex-shrink:0;"></span>
      <span style="color:#334155;">${nombre}: <strong>${pct}%</strong> (${kwh.toFixed(1)} kWh)</span>
    </div>`;
  }).join('');

  contenedor.innerHTML = `
    <div style="display:flex;gap:1.2rem;align-items:center;flex-wrap:wrap;">
      <svg viewBox="0 0 180 180" style="width:150px;height:150px;flex-shrink:0;">${paths}</svg>
      <div style="flex:1;min-width:160px;">${leyenda}</div>
    </div>`;
}

/** Escala de eficiencia energética (estilo etiquetado A++ a G), con el
 * color confirmado: verde en A++, rojo en G. Marca con una flecha en cuál
 * letra cae este hogar — igual que la imagen de referencia que mandó el líder. */
const ESCALA_LETRAS = [
  { letra: 'A++', color: '#0d7a3d' },
  { letra: 'A+',  color: '#2fa84f' },
  { letra: 'A',   color: '#6cbf3f' },
  { letra: 'B',   color: '#a9cc39' },
  { letra: 'C',   color: '#e8d631' },
  { letra: 'D',   color: '#f0ad2e' },
  { letra: 'E',   color: '#f0812e' },
  { letra: 'F',   color: '#e8501f' },
  { letra: 'G',   color: '#d92b1f' },
];

function renderEscalaEficiencia(letra, score, interpretacion, contenedorId) {
  const contenedor = document.getElementById(contenedorId);
  if (!contenedor) return;

  if (!letra) {
    contenedor.innerHTML = '<p style="font-size:0.82rem;color:#64748b;">Escala no disponible para este cálculo.</p>';
    return;
  }

  const barras = ESCALA_LETRAS.map(({ letra: l, color }, i) => {
    const esActual = l === letra;
    const ancho = 70 + i * 6; // más angosto arriba (A++), más ancho abajo (G) — igual que la imagen
    return `
      <div style="display:flex;align-items:center;gap:0.5rem;margin:2px 0;">
        <div style="width:${ancho}%;background:${color};color:#fff;font-weight:700;
                    padding:3px 10px;font-size:0.8rem;border-radius:2px 8px 8px 2px;
                    clip-path:polygon(0 0, 92% 0, 100% 50%, 92% 100%, 0 100%);
                    ${esActual ? 'outline:3px solid #1e3a5f;outline-offset:1px;' : ''}">
          ${l}
        </div>
        ${esActual ? '<span style="font-size:1.1rem;">◀ tu hogar</span>' : ''}
      </div>`;
  }).join('');

  contenedor.innerHTML = `
    <div style="max-width:320px;">${barras}</div>
    <p style="font-size:0.8rem;color:#334155;margin-top:0.5rem;">
      Score: <strong>${score}</strong> (rango -100 a +100) — eficiencia <strong>${interpretacion}</strong>
    </p>`;
}

function mostrarResultados(res, payload) {
  if (resultadosSeccion) resultadosSeccion.hidden = false;

  // El HUD de Denji (abajo a la izquierda) tapaba el reporte final — ya
  // cumplió su función acá (guiar el formulario, leer el resultado en voz),
  // así que se oculta al mostrar resultados. Vuelve a aparecer con "Nuevo
  // Cálculo" (resetearTodo), donde sí hace falta de nuevo.
  const denjiHud = document.getElementById('denji-hud');
  if (denjiHud) denjiHud.style.display = 'none';

  // ── Moneda: priorizar lo que devuelve el backend (ya calculado por tarifa) ──
  const simbolo = res.simbolo_moneda || res.simbolo || window._simboloActivo || '$';
  const moneda  = res.moneda         || window._monedaActiva || '';

  // ── Valores numéricos con cadena de fallback robusta ──
  const consumoVal = res.consumo_kwh
    ?? res.consumo_mensual_estimado
    ?? res.total_kwh_mes
    ?? payload?.consumo_kwh
    ?? payload?.consumo
    ?? 0;

  const costoVal = res.costo_estimado
    ?? res.costo_estimado_mensual
    ?? res.total_clp_mes
    ?? 0;

  const ahorroVal = res.ahorro_estimado
    ?? res.ahorro_potencial_clp_mes
    ?? res.ahorro_potencial
    ?? (typeof costoVal === 'number' ? Math.round(costoVal * 0.2) : 0);

  const fmt = val => (typeof val === 'number' ? val.toLocaleString('es') : val);

  const categoria = res.categoria || 'Moderado';
  let narrativa = (res.narrativa || '').replace(/CLP/g, moneda || window._monedaActiva || '');
  if (!narrativa) {
    narrativa = `Categoría: ${categoria}. Consumo estimado: ${consumoVal} kWh, costo aprox. ${simbolo} ${fmt(costoVal)} ${moneda}.`;
  }

  const sufijo = moneda ? ` ${moneda}` : '';

  // ── Narrativa LLM (oculta en pantalla, disponible para imprimir) ──
  const narrativaEl = document.getElementById('narrativa');
  if (narrativaEl) narrativaEl.textContent = narrativa;

  // ── Tarjetas de resultados (con moneda correcta) ──
  const el = id => document.getElementById(id);
  if (el('totalKwh'))  el('totalKwh').textContent  = `${consumoVal} kWh`;
  if (el('totalClp'))  el('totalClp').textContent  = `${simbolo} ${fmt(costoVal)}${sufijo}`.trim();
  if (el('ahorroClp')) el('ahorroClp').textContent = `${simbolo} ${fmt(ahorroVal)}${sufijo}`.trim();

  // ── 3 Métricas de resumen visual ──
  const ahorroAnual   = typeof ahorroVal === 'number' ? Math.round(ahorroVal * 12) : 0;
  const primeraAccion = (res.recomendaciones || [])[0]
    || 'Desconecta artefactos en stand-by para reducir tu factura.';

  if (el('metricaKwh'))    el('metricaKwh').textContent    = `${consumoVal} kWh`;
  if (el('metricaAhorro')) el('metricaAhorro').textContent = `${simbolo} ${fmt(ahorroAnual)}${sufijo}`.trim();
  if (el('metricaAccion')) el('metricaAccion').textContent = primeraAccion;

  // ── Escala de eficiencia (A++ a G) y gráfico de torta — ambos con datos reales ──
  renderEscalaEficiencia(res.letra_eficiencia, res.score_eficiencia, res.interpretacion_eficiencia, 'escalaEficiencia');
  renderGraficoTorta(res.desglose, 'graficoTortaWrap');

  // ── Lista de recomendaciones ──
  const lista = el('listaRecomendaciones');
  if (lista) {
    lista.innerHTML = '';
    (res.recomendaciones || ['Revisa los artefactos conectados en horario pico.']).forEach(r => {
      const li = document.createElement('li');
      li.textContent = r;
      lista.appendChild(li);
    });
  }

  // Guardar estado para la factura
  window._lastResultado = {
    res, consumoVal, costoVal, ahorroVal, ahorroAnual,
    categoria, simbolo, moneda, narrativa
  };

  resultadosSeccion?.scrollIntoView({ behavior: 'smooth' });
}

// ── 8C. FACTURA IMPRIMIBLE ───────────────────────────────────

/** Genera un folio único tipo #VOLT-2026-XXXX */
function generarFolio() {
  const rnd = Math.floor(1000 + Math.random() * 9000);
  return `#VOLT-2026-${rnd}`;
}

/** Construye las filas de desglose desde el payload */
function construirFilasDesglose(payload) {
  const filas = [];
  const addFila = (concepto, cantidad, estado = 'Activo') => filas.push({ concepto, cantidad, estado });

  if (payload.consumo_kwh > 0) addFila('Consumo Declarado', `${payload.consumo_kwh} kWh/mes`, 'Base');
  if (payload.refrigerador > 0) addFila('Refrigerador / Heladera', `${payload.refrigerador} unidad(es)`, 'Activo');
  if (payload.freezer > 0) addFila('Freezer / Congelador', `${payload.freezer} unidad(es)`, 'Activo');
  if (payload.tv > 0) {
    const hDiarias = payload.tv_frecuencia ? (payload.tv_frecuencia / 7).toFixed(1).replace('.0', '') : 0;
    addFila('Televisor', `${payload.tv} TV · ${hDiarias} h/día`, 'Activo');
  }
  if (payload.lavado_frecuencia > 0) addFila('Lavadora', `${payload.lavado_frecuencia} lavados/sem`, 'Activo');

  EQUIPOS_TOGGLE.forEach(({ payloadKey, nombre, detalle }) => {
    if (payload[payloadKey] === 1) addFila(nombre, detalle, 'Activo');
  });

  return filas;
}

/** Puebla el template #factura-print-template y llama window.print() */
function poblarFactura() {
  const payload  = window._lastPayload   || {};
  const resultado = window._lastResultado || {};
  const { res = {}, consumoVal = 0, costoVal = 0, ahorroVal = 0, categoria = '—', simbolo = '$', moneda = '', narrativa = '' } = resultado;

  const el  = id => document.getElementById(id);
  const fmt = val => (typeof val === 'number' ? val.toLocaleString() : val);

  if (el('fptFolio')) el('fptFolio').textContent = generarFolio();
  if (el('fptFecha')) {
    const ahora = new Date();
    el('fptFecha').textContent = 'Fecha: ' + ahora.toLocaleDateString('es-ES', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  // ── Barra de cliente ──
  if (el('fptPais'))         el('fptPais').textContent        = window._nombrePaisActivo || payload.pais || '—';
  if (el('fptRegion'))       el('fptRegion').textContent      = payload.estado_provincia || '(sin especificar)';
  if (el('fptInmuebleBadge')) el('fptInmuebleBadge').textContent = tipoInmuebleSeleccionado || '—';
  const totalHab = (parseInt(payload.habitantes_mayores) || 0) + (parseInt(payload.habitantes_menores) || 0);
  if (el('fptHabBadge'))     el('fptHabBadge').textContent    = `${totalHab} personas`;

  // ── Sección 1: Inmueble ──
  if (el('fptTipoVivienda'))   el('fptTipoVivienda').textContent   = tipoInmuebleSeleccionado || '—';
  if (el('fptDormitorios'))    el('fptDormitorios').textContent    = payload.dormitorios ?? '—';
  if (el('fptVentanas'))       el('fptVentanas').textContent       = payload.ventanas ?? '—';
  if (el('fptAdultosMenores')) el('fptAdultosMenores').textContent =
    `${payload.habitantes_mayores ?? 0} adultos / ${payload.habitantes_menores ?? 0} menores`;

  // ── Sección 2: Desglose dinámico ──
  const tbody = el('fptDesglose');
  if (tbody) {
    tbody.innerHTML = '';
    const filas = construirFilasDesglose(payload);

    if (filas.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="3" style="text-align:center;font-style:italic;">Sin equipos declarados</td>';
      tbody.appendChild(tr);
    } else {
      filas.forEach(({ concepto, cantidad, estado }) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${concepto}</td>
          <td>${cantidad}</td>
          <td><span class="fpt-estado-activo">${estado}</span></td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  // ── Sección 3: Totales ──
  const sufijo = moneda ? ` ${moneda}` : '';
  if (el('fptCategoria')) el('fptCategoria').textContent = categoria;
  if (el('fptKwh'))       el('fptKwh').textContent       = `${consumoVal} kWh`;
  if (el('fptCosto'))     el('fptCosto').textContent     = `${simbolo} ${fmt(costoVal)}${sufijo}`;
  if (el('fptAhorro'))    el('fptAhorro').textContent    = `${simbolo} ${fmt(ahorroVal)}${sufijo}`;

  // ── Recomendaciones ──
  // ── Narrativa del modelo ──
  // Destino real del texto que hasta ahora se generaba en cada cálculo, se
  // escribía en un div oculto y no se leía en ninguna parte: `narrativa` se
  // desestructuraba aquí arriba y no se usaba en ninguna línea de la función.
  const narrativaEl = el('fptNarrativa');
  if (narrativaEl) {
    narrativaEl.textContent = narrativa || '';
    narrativaEl.hidden = !narrativa;
  }

  const recsList = el('fptRecs');
  if (recsList) {
    recsList.innerHTML = '';
    const recs = res.recomendaciones?.length
      ? res.recomendaciones
      : ['Aplica buenas prácticas de consumo para reducir tu huella energética y ahorrar dinero.'];
    recs.forEach(r => {
      const li = document.createElement('li');
      li.textContent = r;
      recsList.appendChild(li);
    });
  }
}

// ── 8D. BOTÓN IMPRIMIR ───────────────────────────────────────
document.getElementById('btnImprimir')?.addEventListener('click', () => {
  poblarFactura();
  setTimeout(() => window.print(), 150);
});

// ── 9. PERSISTENCIA (ENTRE PASOS) ────────────────────────────
function saveState() {
  const state = {
    step: currentStep,
    tipoInmueble: tipoInmuebleSeleccionado,
    inputs: {}, checkboxes: {}
  };
  document.querySelectorAll('input[type="text"], input[type="number"], select').forEach(el => {
    if (el.id) state.inputs[el.id] = el.value;
  });
  document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
    if (cb.id) state.checkboxes[cb.id] = cb.checked;
  });
  localStorage.setItem('volticvs_state', JSON.stringify(state));
}

// Autoguardado y limpieza de errores en tiempo real
document.querySelectorAll('input, select, textarea').forEach(el => {
  const handler = e => { saveState(); clearError(e.target); };
  el.addEventListener('change', handler);
  el.addEventListener('input', handler);
});
document.querySelectorAll('.vivienda-card, .counter-btn').forEach(el => {
  el.addEventListener('click', () => setTimeout(saveState, 50));
});

// ── 10. INICIALIZACIÓN ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  /* Siempre arrancar desde cero en cada carga de página */
  resetearTodo();

  /* Cargar países (establece el select al país default) */
  await cargarPaises();

  /* Mostrar el paso 1 con el avatar de bienvenida */
  currentStep = 1;
  showStep(1);
});
