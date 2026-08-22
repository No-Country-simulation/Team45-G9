/**
 * accesibilidad.js — Panel flotante de accesibilidad para Denji
 *
 * Funcionalidades:
 *   · Tamaño de letra (5 niveles)
 *   · Modos de color (deuteranopia, tritanopia, alto contraste)
 *   · Narración por voz TTS — activa/desactiva la voz de Volti/Denji
 *   · Indicador de estado del micrófono (refleja lo que hace denji.js)
 *
 * Autocontenido: inyecta sus propios estilos y markup al cargar.
 * Persistencia: guarda las preferencias en localStorage.
 * Sin dependencias externas — funciona antes y después de denji.js.
 *
 * Para activarlo: añadir al final de <body> en index.html:
 *   <script src="/static/js/accesibilidad.js"></script>
 *
 * Integración TTS: debe cargarse ANTES que denji.js para poder interceptar
 * speechSynthesis.speak() y respetar la preferencia del usuario.
 */
(function () {
  'use strict';

  // ── Constantes ─────────────────────────────────────────────────────────────
  const PREFS_KEY = 'volticvs_acces';

  const NIVELES_FUENTE = [
    { label: 'Muy pequeña', px: 13 },
    { label: 'Pequeña',     px: 15 },
    { label: 'Normal',      px: 16 },
    { label: 'Grande',      px: 19 },
    { label: 'Muy grande',  px: 22 },
  ];
  const NIVEL_DEFAULT = 2; // "Normal"

  const MODOS_COLOR = [
    { id: 'normal',         label: 'Normal',                   emoji: '🎨' },
    { id: 'deuteranopia',   label: 'Rojo-verde (deuteranopia)', emoji: '👁️' },
    { id: 'tritanopia',     label: 'Azul-amarillo (tritanopia)',emoji: '👁️' },
    { id: 'alto-contraste', label: 'Alto contraste',            emoji: '◑'  },
  ];

  // ── Persistencia ───────────────────────────────────────────────────────────
  function cargarPrefs() {
    try { return JSON.parse(localStorage.getItem(PREFS_KEY) || '{}'); }
    catch { return {}; }
  }
  function guardarPrefs(p) {
    try { localStorage.setItem(PREFS_KEY, JSON.stringify(p)); } catch {}
  }

  const prefs = cargarPrefs();
  let nivelFuente = typeof prefs.nivelFuente === 'number' ? prefs.nivelFuente : NIVEL_DEFAULT;
  let modoColor   = prefs.modoColor  ?? 'normal';
  let ttsActivo   = prefs.ttsActivo  ?? true;
  let msgsVisibles = prefs.msgsVisibles ?? true;

  // ── Interceptar TTS lo antes posible ──────────────────────────────────────
  // Debe ejecutarse ANTES de que denji.js llame a speechSynthesis.speak(),
  // por eso este script va antes de denji en el HTML.
  if ('speechSynthesis' in window) {
    const _speakOriginal = speechSynthesis.speak.bind(speechSynthesis);
    speechSynthesis.speak = function (utterance) {
      if (ttsActivo) _speakOriginal(utterance);
    };
  }

  // ── Aplicar al DOM ─────────────────────────────────────────────────────────
  function aplicarFuente(nivel) {
    document.documentElement.style.fontSize = NIVELES_FUENTE[nivel].px + 'px';
  }

  function aplicarColor(modo) {
    MODOS_COLOR.forEach(m => document.body.classList.remove('acces-' + m.id));
    if (modo !== 'normal') document.body.classList.add('acces-' + modo);
  }

  // ── CSS ────────────────────────────────────────────────────────────────────
  const CSS = /* css */`
    /* ── Botón flotante ────────────────────────────────────────── */
    #acces-fab {
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      z-index: 9990;
      width: 3rem;
      height: 3rem;
      border-radius: 50%;
      background: var(--azul-oscuro);
      color: #fff;
      border: none;
      cursor: pointer;
      font-size: 1.35rem;
      line-height: 1;
      box-shadow: 0 4px 16px rgba(30,58,95,.35);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s var(--ease, ease), background 0.2s;
    }
    #acces-fab:hover,
    #acces-fab:focus-visible { transform: scale(1.1); outline: 3px solid var(--amarillo); }
    #acces-fab[aria-expanded="true"] { background: var(--verde-dark); }

    /* ── Panel ─────────────────────────────────────────────────── */
    #acces-panel {
      position: fixed;
      bottom: 5.5rem;
      right: 1.5rem;
      z-index: 9989;
      width: 290px;
      background: var(--white, #fff);
      border: 2px solid var(--azul, #2F80ED);
      border-radius: var(--r-lg, 16px);
      box-shadow: 0 8px 32px rgba(30,58,95,.2);
      font-family: var(--font, sans-serif);
      font-size: 0.875rem;
      transform-origin: bottom right;
      transition: opacity 0.2s, transform 0.2s;
    }
    #acces-panel.acces-oculto {
      opacity: 0;
      transform: scale(0.88);
      pointer-events: none;
    }
    .acces-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.7rem 1rem;
      background: var(--azul-oscuro, #1E3A5F);
      color: #fff;
      border-radius: calc(var(--r-lg, 16px) - 2px) calc(var(--r-lg, 16px) - 2px) 0 0;
    }
    .acces-header h2 {
      margin: 0;
      font-size: 0.875rem;
      font-weight: 700;
    }
    .acces-cerrar {
      background: none;
      border: none;
      color: #fff;
      font-size: 1.1rem;
      cursor: pointer;
      padding: 0 0.2rem;
      line-height: 1;
    }
    .acces-cerrar:focus-visible { outline: 2px solid var(--amarillo, #FFC83D); border-radius: 4px; }

    /* ── Secciones ─────────────────────────────────────────────── */
    .acces-seccion {
      padding: 0.7rem 1rem;
      border-bottom: 1px solid var(--gris, #D9D9D9);
    }
    .acces-seccion:last-child { border-bottom: none; }
    .acces-seccion-titulo {
      font-weight: 700;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--azul, #2F80ED);
      margin-bottom: 0.55rem;
    }

    /* ── Tamaño de letra ───────────────────────────────────────── */
    .acces-fuente-fila {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .acces-fuente-fila button {
      width: 2rem;
      height: 2rem;
      border-radius: var(--r-sm, 8px);
      border: 1.5px solid var(--azul, #2F80ED);
      background: #fff;
      color: var(--azul, #2F80ED);
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s;
    }
    .acces-fuente-fila button:hover:not(:disabled) { background: var(--p-azul, #E8F1FD); }
    .acces-fuente-fila button:disabled { opacity: 0.35; cursor: default; }
    .acces-fuente-label {
      flex: 1;
      text-align: center;
      font-size: 0.78rem;
      color: var(--carbon, #333);
    }

    /* ── Modos de color ────────────────────────────────────────── */
    .acces-colores {
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
    }
    .acces-color-opcion {
      display: flex;
      align-items: center;
      gap: 0.45rem;
      cursor: pointer;
      font-size: 0.82rem;
      color: var(--carbon, #333);
    }
    .acces-color-opcion input[type="radio"] {
      accent-color: var(--azul, #2F80ED);
      width: 1rem;
      height: 1rem;
      cursor: pointer;
    }

    /* ── Voz ───────────────────────────────────────────────────── */
    .acces-voz { display: flex; flex-direction: column; gap: 0.5rem; }

    .acces-toggle-fila {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .acces-toggle-label { font-size: 0.82rem; color: var(--carbon, #333); }

    /* Toggle switch */
    .acces-toggle {
      position: relative;
      width: 2.6rem;
      height: 1.4rem;
      background: var(--gris, #D9D9D9);
      border-radius: var(--r-full, 9999px);
      border: none;
      cursor: pointer;
      transition: background 0.2s;
      flex-shrink: 0;
    }
    .acces-toggle[aria-checked="true"] { background: var(--verde, #009E73); }
    .acces-toggle::after {
      content: '';
      position: absolute;
      top: 0.15rem;
      left: 0.15rem;
      width: 1.1rem;
      height: 1.1rem;
      border-radius: 50%;
      background: #fff;
      box-shadow: 0 1px 4px rgba(0,0,0,.2);
      transition: transform 0.2s var(--spring, ease);
    }
    .acces-toggle[aria-checked="true"]::after { transform: translateX(1.2rem); }
    .acces-toggle:focus-visible { outline: 2px solid var(--azul, #2F80ED); }

    /* Estado del micrófono */
    .acces-mic-estado {
      font-size: 0.76rem;
      color: var(--azul, #2F80ED);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }
    .acces-mic-punto {
      width: 0.5rem;
      height: 0.5rem;
      border-radius: 50%;
      background: var(--gris, #D9D9D9);
      display: inline-block;
      flex-shrink: 0;
      transition: background 0.3s;
    }
    .acces-mic-punto.disponible  { background: var(--verde, #009E73); }
    .acces-mic-punto.escuchando  { background: var(--naranja, #F2994A); animation: acces-pulso 0.8s infinite; }
    @keyframes acces-pulso { 0%,100%{opacity:1} 50%{opacity:.25} }

    /* ── Overrides de paleta por modo de color ─────────────────── */

    /* Deuteranopia: sustituye verdes y naranjas por tonos azul/violeta,
       que son discriminables para personas con daltonismo rojo-verde. */
    body.acces-deuteranopia {
      --verde:       #0072B2;
      --verde-dark:  #005a8e;
      --s-glow:      0 0 18px rgba(0,114,178,.3);
      --naranja:     #CC4400;
      --amarillo:    #DDAA00;
    }

    /* Tritanopia: sustituye azules y amarillos por rojo/verde,
       que son discriminables para personas con daltonismo azul-amarillo. */
    body.acces-tritanopia {
      --azul:        #CC3300;
      --azul-oscuro: #881100;
      --verde:       #009966;
      --amarillo:    #009966;
      --p-azul:      #FFE0D9;
    }

    /* Alto contraste: máxima legibilidad, sin sombras decorativas. */
    body.acces-alto-contraste {
      --verde:        #006600;
      --verde-dark:   #004400;
      --azul:         #0000CC;
      --azul-oscuro:  #000066;
      --hueso:        #FFFFFF;
      --carbon:       #000000;
      --gris:         #888888;
      --naranja:      #993300;
      --amarillo:     #886600;
      --white:        #FFFFFF;
      --s-sm: 0 0 0 1.5px #000;
      --s-md: 0 0 0 2px   #000;
      --s-lg: 0 0 0 3px   #000;
      --s-glow: none;
    }
    body.acces-alto-contraste * {
      letter-spacing: 0.01em;
    }
  `;

  // ── HTML del panel ─────────────────────────────────────────────────────────
  function construirPanel() {
    const tieneSTT = !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    const tieneTTS = 'speechSynthesis' in window;

    const panel = document.createElement('div');
    panel.id = 'acces-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'false');
    panel.setAttribute('aria-label', 'Panel de accesibilidad');
    panel.classList.add('acces-oculto');

    // Helper para obtener traducción si i18n está disponible
    const _t = (key, fallback) => window.DenjiI18n ? window.DenjiI18n.t(key) : fallback;
    const currentLang = window.DenjiI18n ? window.DenjiI18n.lang : 'es';

    panel.innerHTML = `
      <div class="acces-header">
        <h2 data-i18n="acces_title">♿ ${_t('acces_title', 'Accesibilidad')}</h2>
        <button class="acces-cerrar" aria-label="Cerrar panel de accesibilidad">✕</button>
      </div>

      <div class="acces-seccion">
        <div class="acces-seccion-titulo" data-i18n="acces_lang">${_t('acces_lang', 'Idioma')}</div>
        <div class="acces-idiomas" role="radiogroup" aria-label="Idioma">
          <label class="acces-color-opcion">
            <input type="radio" name="acces-lang" value="es" ${currentLang === 'es' ? 'checked' : ''}>
            🇪🇸 Español
          </label>
          <label class="acces-color-opcion">
            <input type="radio" name="acces-lang" value="en" ${currentLang === 'en' ? 'checked' : ''}>
            🇬🇧 English
          </label>
          <label class="acces-color-opcion">
            <input type="radio" name="acces-lang" value="pt" ${currentLang === 'pt' ? 'checked' : ''}>
            🇧🇷 Português
          </label>
        </div>
      </div>

      <div class="acces-seccion">
        <div class="acces-seccion-titulo" data-i18n="acces_font">${_t('acces_font', 'Tamaño de letra')}</div>
        <div class="acces-fuente-fila">
          <button id="acces-f-menos" aria-label="Reducir tamaño de letra">A−</button>
          <span class="acces-fuente-label" id="acces-f-desc">${NIVELES_FUENTE[nivelFuente].label}</span>
          <button id="acces-f-mas"   aria-label="Aumentar tamaño de letra">A+</button>
        </div>
      </div>

      <div class="acces-seccion">
        <div class="acces-seccion-titulo" data-i18n="acces_color">${_t('acces_color', 'Modo de color')}</div>
        <div class="acces-colores" role="radiogroup" aria-label="Modo de color">
          ${MODOS_COLOR.map(m => `
            <label class="acces-color-opcion">
              <input type="radio" name="acces-color" value="${m.id}"
                     ${modoColor === m.id ? 'checked' : ''}>
              ${m.emoji} ${m.label}
            </label>
          `).join('')}
        </div>
      </div>

      <div class="acces-seccion">
        <div class="acces-seccion-titulo" data-i18n="acces_assistant">${_t('acces_assistant', 'Asistente')}</div>
        <div class="acces-toggle-fila">
          <span class="acces-toggle-label" data-i18n="acces_hide_msgs">${_t('acces_hide_msgs', '💬 Mensajes de Volti')}</span>
          <button class="acces-toggle"
                  id="acces-msgs-btn"
                  role="switch"
                  aria-checked="${msgsVisibles}"
                  aria-label="Mostrar u ocultar mensajes del asistente">
          </button>
        </div>
      </div>

      <div class="acces-seccion">
        <div class="acces-seccion-titulo" data-i18n="acces_voice">${_t('acces_voice', 'Voz')}</div>
        <div class="acces-voz">
          ${tieneTTS ? `
          <div class="acces-toggle-fila">
            <span class="acces-toggle-label" data-i18n="acces_tts">${_t('acces_tts', '🔊 Narración de Volti')}</span>
            <button class="acces-toggle"
                    id="acces-tts-btn"
                    role="switch"
                    aria-checked="${ttsActivo}"
                    aria-label="Activar o desactivar narración por voz">
            </button>
          </div>` : ''}
          <div class="acces-mic-estado">
            <span class="acces-mic-punto ${tieneSTT ? 'disponible' : ''}"
                  id="acces-mic-punto"></span>
            <span data-i18n="${tieneSTT ? 'acces_mic_available' : 'acces_mic_unsupported'}">${tieneSTT
              ? _t('acces_mic_available', '🎤 Micrófono disponible — úsalo desde el asistente')
              : _t('acces_mic_unsupported', '🎤 Tu navegador no soporta reconocimiento de voz')}</span>
          </div>
        </div>
      </div>
    `;

    return panel;
  }

  // ── Lógica del panel ───────────────────────────────────────────────────────
  function init() {
    // Estilos
    const styleEl = document.createElement('style');
    styleEl.textContent = CSS;
    document.head.appendChild(styleEl);

    // Aplicar prefs guardadas
    aplicarFuente(nivelFuente);
    aplicarColor(modoColor);

    // Botón flotante
    const fab = document.createElement('button');
    fab.id = 'acces-fab';
    fab.setAttribute('aria-label', 'Abrir panel de accesibilidad');
    fab.setAttribute('aria-expanded', 'false');
    fab.setAttribute('aria-controls', 'acces-panel');
    fab.setAttribute('title', 'Accesibilidad');
    fab.textContent = '♿';
    document.body.appendChild(fab);

    // Panel
    const panel = construirPanel();
    document.body.appendChild(panel);

    // Abrir / cerrar
    function abrir() {
      panel.classList.remove('acces-oculto');
      fab.setAttribute('aria-expanded', 'true');
      panel.querySelector('.acces-cerrar').focus();
    }
    function cerrar() {
      panel.classList.add('acces-oculto');
      fab.setAttribute('aria-expanded', 'false');
      fab.focus();
    }

    fab.addEventListener('click', () =>
      panel.classList.contains('acces-oculto') ? abrir() : cerrar()
    );
    panel.querySelector('.acces-cerrar').addEventListener('click', cerrar);
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && !panel.classList.contains('acces-oculto')) cerrar();
    });

    // ── Selector de idioma ─────────────────────────────────────────────────
    panel.querySelectorAll('input[name="acces-lang"]').forEach(radio => {
      radio.addEventListener('change', () => {
        if (window.DenjiI18n) {
          window.DenjiI18n.setLang(radio.value);
        }
      });
    });

    // ── Tamaño de letra ──────────────────────────────────────────────────────
    const btnMenos = panel.querySelector('#acces-f-menos');
    const btnMas   = panel.querySelector('#acces-f-mas');
    const descEl   = panel.querySelector('#acces-f-desc');

    function sincronizarFuente() {
      aplicarFuente(nivelFuente);
      descEl.textContent      = NIVELES_FUENTE[nivelFuente].label;
      btnMenos.disabled       = nivelFuente <= 0;
      btnMas.disabled         = nivelFuente >= NIVELES_FUENTE.length - 1;
      prefs.nivelFuente       = nivelFuente;
      guardarPrefs(prefs);
    }
    btnMenos.addEventListener('click', () => { if (nivelFuente > 0) { nivelFuente--; sincronizarFuente(); } });
    btnMas.addEventListener('click',   () => { if (nivelFuente < NIVELES_FUENTE.length - 1) { nivelFuente++; sincronizarFuente(); } });
    sincronizarFuente();

    // ── Modo de color ────────────────────────────────────────────────────────
    panel.querySelectorAll('input[name="acces-color"]').forEach(radio => {
      radio.addEventListener('change', () => {
        modoColor       = radio.value;
        prefs.modoColor = modoColor;
        aplicarColor(modoColor);
        guardarPrefs(prefs);
      });
    });

    // ── TTS toggle ───────────────────────────────────────────────────────────
    const ttsBtn = panel.querySelector('#acces-tts-btn');
    if (ttsBtn) {
      ttsBtn.addEventListener('click', () => {
        ttsActivo = !ttsActivo;
        ttsBtn.setAttribute('aria-checked', String(ttsActivo));
        // Cortar la síntesis en curso si se desactiva
        if (!ttsActivo && 'speechSynthesis' in window) speechSynthesis.cancel();
        prefs.ttsActivo = ttsActivo;
        guardarPrefs(prefs);
      });
    }

    // ── Toggle mensajes del asistente ──────────────────────────────────────────
    const msgsBtn = panel.querySelector('#acces-msgs-btn');
    function aplicarVisibilidadMsgs() {
      // Oculta/muestra la burbuja de Volti y el HUD de Denji
      const voltiSpeech = document.getElementById('voltiSpeech');
      const denjiCard   = document.getElementById('denji-card');
      const denjiHud    = document.getElementById('denji-hud');
      if (voltiSpeech) voltiSpeech.style.display = msgsVisibles ? '' : 'none';
      if (denjiCard)   denjiCard.style.display   = msgsVisibles ? '' : 'none';
      if (denjiHud)    denjiHud.style.display     = msgsVisibles ? '' : 'none';
    }
    if (msgsBtn) {
      msgsBtn.addEventListener('click', () => {
        msgsVisibles = !msgsVisibles;
        msgsBtn.setAttribute('aria-checked', String(msgsVisibles));
        aplicarVisibilidadMsgs();
        prefs.msgsVisibles = msgsVisibles;
        guardarPrefs(prefs);
      });
    }
    // Aplicar preferencia guardada al arrancar
    if (!msgsVisibles) aplicarVisibilidadMsgs();
    // Re-aplicar cuando denji.js cargue (crea #denji-hud después)
    new MutationObserver(() => { if (!msgsVisibles) aplicarVisibilidadMsgs(); })
      .observe(document.body, { childList: true, subtree: true });

    // ── Estado del micrófono ─────────────────────────────────────────────────
    // Observa cambios en el DOM para detectar cuando denji.js activa el micro.
    // El texto del botón de denji pasa a "Escuchando…" mientras graba.
    const puntoEl = panel.querySelector('#acces-mic-punto');
    if (puntoEl && 'MutationObserver' in window) {
      const obs = new MutationObserver(() => {
        const escuchando = Array.from(document.querySelectorAll('button')).some(b =>
          b.textContent.includes('Escuchando') || b.textContent.includes('Cancelar escucha')
        );
        puntoEl.className = 'acces-mic-punto ' + (escuchando ? 'escuchando' : 'disponible');
      });
      obs.observe(document.body, { subtree: true, childList: true, characterData: true });
    }
  }

  // Esperar al DOM si aún no está listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
