/*
 * Bienvenida — pantalla de inicio de VólticvS.
 *
 * Splash screen que se muestra al cargar la app, antes de que el usuario
 * interactúe con nada. Muestra el avatar de Denji, un estimado de ahorro
 * en la divisa del usuario (detectada por geolocalización) y un botón
 * "Comenzar" que revela la app con una transición suave.
 *
 * Autocontenido: inyecta su propio CSS y HTML, no depende de ningún otro
 * script. Se carga ANTES que app.js, accesibilidad.js y denji.js.
 *
 * Autor: Héctor Acuña — rama feature/panel-accesibilidad
 */
(function () {
  'use strict';
  function _t(key) {
    return (window.DenjiI18n ? window.DenjiI18n.t(key) : key);
  }

  // ── Datos de ahorro por país (tarifa_kwh * 50 kWh de ahorro moderado) ──
  // Extraídos de data/consumo_referencia.json. El "50 kWh" es conservador:
  // corresponde al consumo fantasma + buenas prácticas mínimas.
  var AHORRO_POR_PAIS = {
    CL: { simbolo: '$',   monto: '7.500',   moneda: 'CLP', nombre: 'Chile' },
    AR: { simbolo: '$',   monto: '4.250',   moneda: 'ARS', nombre: 'Argentina' },
    PE: { simbolo: 'S/',  monto: '31',      moneda: 'PEN', nombre: 'Peru' },
    CO: { simbolo: '$',   monto: '41.000',  moneda: 'COP', nombre: 'Colombia' },
    MX: { simbolo: '$',   monto: '60',      moneda: 'MXN', nombre: 'Mexico' },
    ES: { simbolo: '€',  monto: '13',  moneda: 'EUR', nombre: 'Espana' },
    BR: { simbolo: 'R$',  monto: '37',      moneda: 'BRL', nombre: 'Brasil' },
    EC: { simbolo: '$',   monto: '5',       moneda: 'USD', nombre: 'Ecuador' },
    UY: { simbolo: '$U',  monto: '425',     moneda: 'UYU', nombre: 'Uruguay' },
    VE: { simbolo: 'Bs.', monto: '5',       moneda: 'VES', nombre: 'Venezuela' },
    BO: { simbolo: 'Bs.', monto: '30',      moneda: 'BOB', nombre: 'Bolivia' },
    PY: { simbolo: '₲',  monto: '9.250',moneda: 'PYG', nombre: 'Paraguay' },
    GT: { simbolo: 'Q',   monto: '85',      moneda: 'GTQ', nombre: 'Guatemala' },
    CR: { simbolo: '₡',  monto: '7.250',moneda: 'CRC', nombre: 'Costa Rica' },
    PA: { simbolo: '$',   monto: '8',       moneda: 'USD', nombre: 'Panama' },
    DO: { simbolo: 'RD$', monto: '625',     moneda: 'DOP', nombre: 'Rep. Dominicana' },
    US: { simbolo: '$',   monto: '8',       moneda: 'USD', nombre: 'Estados Unidos' },
    HN: { simbolo: 'L',   monto: '175',     moneda: 'HNL', nombre: 'Honduras' },
    SV: { simbolo: '$',   monto: '9',       moneda: 'USD', nombre: 'El Salvador' },
    NI: { simbolo: 'C$',  monto: '375',     moneda: 'NIO', nombre: 'Nicaragua' },
    PR: { simbolo: '$',   monto: '11',      moneda: 'USD', nombre: 'Puerto Rico' },
    CU: { simbolo: '$',   monto: '4',       moneda: 'CUP', nombre: 'Cuba' },
    HT: { simbolo: 'G',   monto: '7',       moneda: 'HTG', nombre: 'Haiti' },
    JM: { simbolo: 'J$',  monto: '17',      moneda: 'JMD', nombre: 'Jamaica' }
  };

  // ── CSS inyectado (prefijo "bvn-" para no chocar) ──────────────────────
  var css = '\
    #bvn-overlay {\
      position: fixed; inset: 0; z-index: 100000;\
      display: flex; flex-direction: column;\
      align-items: center; justify-content: center;\
      background: linear-gradient(160deg, #1E3A5F 0%, #0d2240 60%, #091a30 100%);\
      font-family: "Atkinson Hyperlegible", "Inter", sans-serif;\
      color: #F8F9F4;\
      opacity: 1; transition: opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1);\
      padding: 24px;\
      overflow: hidden;\
    }\
    #bvn-overlay.bvn-salir {\
      opacity: 0; pointer-events: none;\
    }\
    \
    /* Particulas de energia decorativas */\
    .bvn-particula {\
      position: absolute; border-radius: 50%;\
      background: rgba(0, 158, 115, 0.15);\
      pointer-events: none;\
      animation: bvn-flotar 6s ease-in-out infinite;\
    }\
    .bvn-particula:nth-child(2) { animation-delay: -2s; animation-duration: 8s; }\
    .bvn-particula:nth-child(3) { animation-delay: -4s; animation-duration: 7s; }\
    @keyframes bvn-flotar {\
      0%, 100% { transform: translateY(0) scale(1); opacity: 0.3; }\
      50%      { transform: translateY(-30px) scale(1.1); opacity: 0.6; }\
    }\
    \
    /* Avatar */\
    .bvn-avatar {\
      width: 180px; height: 180px;\
      border-radius: 50%;\
      border: 4px solid #009E73;\
      object-fit: contain;\
      background: rgba(255,255,255,0.08);\
      box-shadow: 0 0 40px rgba(0, 158, 115, 0.3), 0 8px 32px rgba(0,0,0,0.3);\
      animation: bvn-aparecer 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) both;\
      margin-bottom: 28px;\
    }\
    @keyframes bvn-aparecer {\
      0%   { opacity: 0; transform: scale(0.5) translateY(30px); }\
      100% { opacity: 1; transform: scale(1) translateY(0); }\
    }\
    \
    /* Textos */\
    .bvn-titulo {\
      font-size: 1.6rem; font-weight: 700;\
      text-align: center; line-height: 1.35;\
      margin-bottom: 8px;\
      animation: bvn-subir 0.7s 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) both;\
    }\
    .bvn-titulo .bvn-monto {\
      color: #FFC83D;\
      font-size: 2rem;\
      display: block;\
      margin-top: 4px;\
    }\
    .bvn-subtitulo {\
      font-size: 1.05rem;\
      text-align: center;\
      opacity: 0.85;\
      margin-bottom: 6px;\
      animation: bvn-subir 0.7s 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) both;\
    }\
    .bvn-firma {\
      font-size: 0.95rem;\
      text-align: center;\
      opacity: 0.7;\
      font-style: italic;\
      margin-bottom: 32px;\
      animation: bvn-subir 0.7s 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both;\
    }\
    @keyframes bvn-subir {\
      0%   { opacity: 0; transform: translateY(20px); }\
      100% { opacity: 1; transform: translateY(0); }\
    }\
    \
    /* Boton Comenzar */\
    .bvn-comenzar {\
      background: #009E73;\
      color: #fff;\
      border: none;\
      padding: 14px 48px;\
      font-size: 1.1rem;\
      font-weight: 700;\
      font-family: "Atkinson Hyperlegible", "Inter", sans-serif;\
      border-radius: 12px;\
      cursor: pointer;\
      box-shadow: 0 4px 20px rgba(0, 158, 115, 0.4);\
      position: relative;\
      overflow: hidden;\
      animation: bvn-subir 0.7s 0.75s cubic-bezier(0.34, 1.56, 0.64, 1) both;\
      transition: background 0.25s, transform 0.2s, box-shadow 0.25s;\
    }\
    .bvn-comenzar:hover {\
      background: #007a59;\
      transform: translateY(-2px);\
      box-shadow: 0 6px 28px rgba(0, 158, 115, 0.5);\
    }\
    .bvn-comenzar:active { transform: translateY(0); }\
    /* Brillo animado sobre el boton */\
    .bvn-comenzar::after {\
      content: "";\
      position: absolute; top: 0; left: -100%;\
      width: 50%; height: 100%;\
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);\
      animation: bvn-brillo 2.5s 1.5s ease-in-out infinite;\
    }\
    @keyframes bvn-brillo {\
      0%   { left: -100%; }\
      40%  { left: 150%; }\
      100% { left: 150%; }\
    }\
    \
    /* Logo pequeno arriba */\
    .bvn-logo-nombre {\
      font-size: 0.8rem;\
      letter-spacing: 3px;\
      text-transform: uppercase;\
      opacity: 0.5;\
      margin-bottom: 20px;\
      animation: bvn-subir 0.7s 0.1s cubic-bezier(0.34, 1.56, 0.64, 1) both;\
    }\
    \
    /* Responsive */\
    @media (max-width: 480px) {\
      .bvn-avatar { width: 140px; height: 140px; }\
      .bvn-titulo { font-size: 1.3rem; }\
      .bvn-titulo .bvn-monto { font-size: 1.6rem; }\
      .bvn-comenzar { padding: 12px 36px; font-size: 1rem; }\
      #bvn-lang { max-width: 92vw; }\
      .bvn-lang-texto { font-size: 0.78rem; }\
      .bvn-lang-fila { flex-direction: column; width: 100%; }\
      .bvn-lang-btn { width: 100%; padding: 10px 16px; font-size: 0.82rem; }\
    }\
    #bvn-lang {\
      margin-top: 18px; display: none; flex-direction: column;\
      align-items: center; gap: 10px; max-width: 340px; width: 100%;\
      box-sizing: border-box;\
    }\
    .bvn-lang-texto {\
      font-size: 0.85rem; text-align: center; opacity: 0.9; margin: 0;\
    }\
    .bvn-lang-fila {\
      display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;\
      width: 100%;\
    }\
    .bvn-lang-btn {\
      background: rgba(255,255,255,0.12); color: #F8F9F4;\
      border: 1px solid rgba(255,255,255,0.3); border-radius: 999px;\
      padding: 8px 16px; font-size: 0.8rem; cursor: pointer;\
      transition: background 0.2s ease;\
      box-sizing: border-box;\
    }\
    .bvn-lang-btn:hover {\
      background: rgba(255,255,255,0.22);\
    }\
    .bvn-lang-btn--primario {\
      background: #F0E442; color: #1E3A5F; font-weight: 700;\
      border-color: #F0E442;\
    }\
  ';

  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ── Construir el overlay ───────────────────────────────────────────────
  var overlay = document.createElement('div');
  overlay.id = 'bvn-overlay';

  // Particulas decorativas
  var particulas = [
    { w: 120, h: 120, top: '10%', left: '5%' },
    { w: 80, h: 80, top: '70%', right: '8%' },
    { w: 60, h: 60, top: '25%', right: '15%' }
  ];
  particulas.forEach(function (p) {
    var el = document.createElement('div');
    el.className = 'bvn-particula';
    el.style.width = p.w + 'px';
    el.style.height = p.h + 'px';
    if (p.top) el.style.top = p.top;
    if (p.left) el.style.left = p.left;
    if (p.right) el.style.right = p.right;
    overlay.appendChild(el);
  });

  // Logo
  var logo = document.createElement('div');
  logo.className = 'bvn-logo-nombre';
  logo.textContent = '⚡ VólticvS';
  overlay.appendChild(logo);

  // Avatar
  var avatar = document.createElement('img');
  avatar.className = 'bvn-avatar';
  avatar.src = '/static/img/volti/bien.png';
  avatar.alt = 'Denji — tu asesor energético';
  overlay.appendChild(avatar);

  // Titulo (se actualiza si la geo detecta el pais)
  var titulo = document.createElement('h2');
  titulo.className = 'bvn-titulo';
  titulo.innerHTML = _t('bvn_titulo');
  overlay.appendChild(titulo);

  // Subtitulo
  var subtitulo = document.createElement('p');
  subtitulo.className = 'bvn-subtitulo';
  subtitulo.textContent = _t('bvn_subtitulo');
  overlay.appendChild(subtitulo);

  // Firma Denji
  var firma = document.createElement('p');
  firma.className = 'bvn-firma';
  firma.textContent = _t('bvn_firma');
  overlay.appendChild(firma);
  // Selector de idioma (se muestra solo si la geolocalizacion detecta el
  // pais y el usuario todavia no eligio idioma en una visita anterior)
  var langBox = document.createElement('div');
  langBox.id = 'bvn-lang';
  overlay.appendChild(langBox);

  // Boton
  var boton = document.createElement('button');
  boton.className = 'bvn-comenzar';
  boton.textContent = _t('bvn_comenzar');
  boton.setAttribute('aria-label', 'Comenzar el análisis energético');
  overlay.appendChild(boton);

  // Insertar al principio del body
  document.body.insertBefore(overlay, document.body.firstChild);

  // ── Accion del boton ──────────────────────────────────────────────────
  boton.addEventListener('click', function () {
    overlay.classList.add('bvn-salir');
    // Remover del DOM tras la transicion para no estorbar
    setTimeout(function () {
      if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    }, 600);
  });

  // ── Deteccion de pais (best-effort, no bloquea) ───────────────────────
  // Intenta geolocalizar para personalizar el monto. Si falla por
  // cualquier razon (sin HTTPS, sin permiso, sin Nominatim), el titulo
  // generico ya funciona perfectamente.
  var ultimoCodigoPaisDetectado = null;
  function actualizarMonto(codigoPais) {
    var info = AHORRO_POR_PAIS[codigoPais];
    if (!info) return;
    ultimoCodigoPaisDetectado = codigoPais;
    titulo.innerHTML =
      _t('bvn_ahorrar_hasta') +
      '<span class="bvn-monto">' + info.simbolo + info.monto + ' ' + _t('bvn_al_mes') + '</span>';
  }

  // ── Selector de idioma sugerido por pais ──────────────────────────────
  var IDIOMAS = { es: { label: 'Español' }, en: { label: 'English' }, pt: { label: 'Português' } };
  function idiomaSugeridoPara(codigoPais) {
    if (codigoPais === 'BR') return 'pt';
    if (codigoPais === 'US') return 'en';
    return 'es';
  }
  function fijarIdioma(lang) {
    if (window.DenjiI18n) window.DenjiI18n.setLang(lang);
    try { localStorage.setItem('denji_lang_prompted', '1'); } catch (e) {}
    // Sin recargar: aunque esta pantalla es la primera que ve la persona,
    // recargar reinicia TODO (incluida la detección de ubicación en curso).
    // titulo/subtitulo/firma/boton se escribieron con textContent directo,
    // no via data-i18n, así que se repintan a mano acá.
    titulo.innerHTML = _t('bvn_titulo');
    subtitulo.textContent = _t('bvn_subtitulo');
    firma.textContent = _t('bvn_firma');
    boton.textContent = _t('bvn_comenzar');
    if (ultimoCodigoPaisDetectado) actualizarMonto(ultimoCodigoPaisDetectado);
    langBox.style.display = 'none';
  }
  function mostrarOpcionesIdioma() {
    langBox.innerHTML = '';
    var fila = document.createElement('div');
    fila.className = 'bvn-lang-fila';
    ['es', 'en', 'pt'].forEach(function (lang) {
      var btn = document.createElement('button');
      btn.className = 'bvn-lang-btn';
      btn.textContent = IDIOMAS[lang].label;
      btn.addEventListener('click', function () { fijarIdioma(lang); });
      fila.appendChild(btn);
    });
    langBox.appendChild(fila);
    langBox.style.display = 'flex';
  }
  function sugerirIdioma(codigoPais, nombrePais) {
    try { if (localStorage.getItem('denji_lang_prompted')) return; } catch (e) { return; }
    var sugerido = idiomaSugeridoPara(codigoPais);
    langBox.innerHTML = '';
    var texto = document.createElement('p');
    texto.className = 'bvn-lang-texto';
    texto.textContent = 'Detectamos que estás en ' + (nombrePais || codigoPais) + '. ¿Usamos ' + IDIOMAS[sugerido].label + '?';
    langBox.appendChild(texto);
    var fila = document.createElement('div');
    fila.className = 'bvn-lang-fila';
    var btnSi = document.createElement('button');
    btnSi.className = 'bvn-lang-btn bvn-lang-btn--primario';
    btnSi.textContent = 'Sí, usar ' + IDIOMAS[sugerido].label;
    btnSi.addEventListener('click', function () { fijarIdioma(sugerido); });
    var btnOtro = document.createElement('button');
    btnOtro.className = 'bvn-lang-btn';
    btnOtro.textContent = 'Elegir otro idioma';
    btnOtro.addEventListener('click', function () { mostrarOpcionesIdioma(); });
    fila.appendChild(btnSi);
    fila.appendChild(btnOtro);
    langBox.appendChild(fila);
    langBox.style.display = 'flex';
  }
  // ── Fallback: sugerir idioma por el idioma del navegador, sin esperar
  // el permiso de geolocalizacion (que puede tardar, fallar o ser rechazado).
  // Si despues la geolocalizacion SI responde con un pais, sugerirIdioma()
  // vuelve a evaluar y puede refinar la sugerencia (ej. sobreescribe con el
  // idioma del pais real si difiere del idioma del navegador).
  (function () {
    try {
      var navLang = (navigator.language || 'es').toLowerCase();
      var codigoAprox = navLang.startsWith('pt') ? 'BR' : navLang.startsWith('en') ? 'US' : null;
      if (codigoAprox) sugerirIdioma(codigoAprox, null);
    } catch (e) {}
  })();
  if ('geolocation' in navigator) {
    try {
      navigator.geolocation.getCurrentPosition(
        function (pos) {
          var url = '/api/ubicacion?lat=' + pos.coords.latitude + '&lon=' + pos.coords.longitude;
          fetch(url)
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (data) {
              if (data && data.pais_codigo) {
                actualizarMonto(data.pais_codigo);
                sugerirIdioma(data.pais_codigo, data.pais_nombre);
              }
            })
            .catch(function () { /* silencioso: el titulo generico queda */ });
        },
        function () { /* permiso denegado o error: generico queda bien */ },
        { timeout: 4000 }
      );
    } catch (e) {
      // Navegadores sin soporte real: nada que hacer
    }
  }
})();
