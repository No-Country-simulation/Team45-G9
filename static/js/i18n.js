/**
 * i18n.js — Sistema de internacionalización para Denji (Energy Advisor).
 *
 * Idiomas soportados: ES (español), EN (inglés), PT (portugués).
 * Carga ANTES que bienvenida.js, accesibilidad.js y denji.js.
 *
 * API global:
 *   window.DenjiI18n.lang        — idioma actual ('es'|'en'|'pt')
 *   window.DenjiI18n.t(key)      — traducción de una clave
 *   window.DenjiI18n.setLang(l)  — cambia idioma y refresca el DOM
 *   window.DenjiI18n.apply()     — aplica traducciones al DOM actual
 *
 * Convención en el HTML:
 *   data-i18n="key"              — reemplaza textContent
 *   data-i18n-html="key"         — reemplaza innerHTML (para markup)
 *   data-i18n-placeholder="key"  — reemplaza placeholder
 *
 * Autor: Héctor Acuña — rama feature/panel-accesibilidad
 */
(function () {
  'use strict';

  // ── Diccionario completo ──────────────────────────────────────────────

  var DICT = {
    // ─── APP GLOBAL ───
    app_name:       { es: 'Denji', en: 'Denji', pt: 'Denji' },
    app_tagline:    { es: 'Asesor energético', en: 'Energy advisor', pt: 'Consultor energético' },
    header_tagline: { es: 'Tu asesor energético inteligente', en: 'Your smart energy advisor', pt: 'Seu consultor energético inteligente' },
    volti_name:     { es: 'Volti', en: 'Volti', pt: 'Volti' },
    footer_text:    { es: 'Denji © 2026 — Asesor energético · Equipo Volti', en: 'Denji © 2026 — Energy advisor · Team Volti', pt: 'Denji © 2026 — Consultor energético · Equipe Volti' },

    // ─── BIENVENIDA ───
    bvn_title_generic: { es: '¿Te gustaría ahorrar en tu factura de luz?', en: 'Would you like to save on your electricity bill?', pt: 'Gostaria de economizar na sua conta de luz?' },
    bvn_subtitle:      { es: 'Revisa la eficiencia energética de tu hogar', en: 'Check your home\'s energy efficiency', pt: 'Verifique a eficiência energética da sua casa' },
    bvn_firma:         { es: 'Yo, Volti, te asesoro.', en: 'I, Volti, will guide you.', pt: 'Eu, Volti, te assessoro.' },
    bvn_start:         { es: 'Comenzar', en: 'Start', pt: 'Começar' },
    bvn_save_prefix:   { es: '¿Te gustaría ahorrar hasta', en: 'Would you like to save up to', pt: 'Gostaria de economizar até' },
    bvn_save_suffix:   { es: ' al mes?', en: ' per month?', pt: ' por mês?' },

    // ─── VOLTI SIDEBAR ───
    volti_greeting: {
      es: '¡Hola! Soy <strong>Volti</strong>, tu asesor energético. Te guiaré paso a paso para calcular tu consumo.',
      en: 'Hi! I\'m <strong>Volti</strong>, your energy advisor. I\'ll guide you step by step to calculate your consumption.',
      pt: 'Olá! Sou o <strong>Volti</strong>, seu consultor energético. Vou te guiar passo a passo para calcular seu consumo.'
    },

    // ─── PROGRESS STEPS ───
    step_location:  { es: 'Ubicación', en: 'Location', pt: 'Localização' },
    step_housing:   { es: 'Vivienda', en: 'Housing', pt: 'Moradia' },
    step_equipment: { es: 'Equipamiento', en: 'Equipment', pt: 'Equipamento' },
    step_routines:  { es: 'Rutinas', en: 'Routines', pt: 'Rotinas' },

    // ─── STEP 1: UBICACIÓN ───
    s1_title: { es: 'Ubicación & Tarifa', en: 'Location & Rate', pt: 'Localização & Tarifa' },
    s1_desc:  { es: 'Indica dónde resides e ingresa tu consumo si lo conoces.', en: 'Tell us where you live and enter your consumption if known.', pt: 'Indique onde mora e insira seu consumo se souber.' },
    s1_badge: { es: 'Paso 1 de 4', en: 'Step 1 of 4', pt: 'Passo 1 de 4' },
    label_country:    { es: 'País', en: 'Country', pt: 'País' },
    loading_countries:{ es: 'Cargando países…', en: 'Loading countries…', pt: 'Carregando países…' },
    label_province:   { es: 'Provincia / Estado / Región', en: 'Province / State / Region', pt: 'Província / Estado / Região' },
    ph_province:      { es: 'Ej: Santiago, Buenos Aires, CDMX…', en: 'E.g.: New York, California, London…', pt: 'Ex.: São Paulo, Lisboa, Rio…' },
    hint_province:    { es: 'Ayuda a estimar variaciones de clima local.', en: 'Helps estimate local climate variations.', pt: 'Ajuda a estimar variações climáticas locais.' },
    label_consumption:{ es: 'Consumo eléctrico mensual (kWh)', en: 'Monthly electricity consumption (kWh)', pt: 'Consumo elétrico mensal (kWh)' },
    ph_consumption:   { es: 'Ej: 250  —  déjalo vacío para que Volti lo calcule', en: 'E.g.: 250  —  leave empty for Volti to estimate', pt: 'Ex.: 250  —  deixe vazio para Volti calcular' },
    label_monthly:    { es: 'El consumo es mensual', en: 'Consumption is monthly', pt: 'O consumo é mensal' },
    label_schedule:   { es: '¿En qué horarios usas mayoritariamente la electricidad?', en: 'When do you primarily use electricity?', pt: 'Em quais horários você mais usa eletricidade?' },
    hint_schedule:    { es: 'Marca uno o varios — nos ayuda a saber si tu consumo cae en horario pico.', en: 'Check one or more — helps us know if your usage falls in peak hours.', pt: 'Marque um ou mais — nos ajuda a saber se seu consumo é em horário de pico.' },
    hr_dawn:          { es: '00:00 – 06:00 (madrugada)', en: '00:00 – 06:00 (dawn)', pt: '00:00 – 06:00 (madrugada)' },
    hr_early_morning: { es: '06:00 – 09:00 (mañana temprano)', en: '06:00 – 09:00 (early morning)', pt: '06:00 – 09:00 (manhã cedo)' },
    hr_morning:       { es: '09:00 – 13:00 (mañana)', en: '09:00 – 13:00 (morning)', pt: '09:00 – 13:00 (manhã)' },
    hr_midday:        { es: '13:00 – 15:00 (mediodía)', en: '13:00 – 15:00 (midday)', pt: '13:00 – 15:00 (meio-dia)' },
    hr_afternoon:     { es: '15:00 – 18:00 (tarde)', en: '15:00 – 18:00 (afternoon)', pt: '15:00 – 18:00 (tarde)' },
    hr_peak_night:    { es: '18:00 – 22:00 (noche, horario pico)', en: '18:00 – 22:00 (night, peak hours)', pt: '18:00 – 22:00 (noite, horário de pico)' },
    hr_late_night:    { es: '22:00 – 00:00 (noche tardía)', en: '22:00 – 00:00 (late night)', pt: '22:00 – 00:00 (noite tardia)' },
    label_upload_bill:{ es: '¿Prefieres subir tu boleta?', en: 'Prefer to upload your bill?', pt: 'Prefere enviar sua conta?' },
    hint_upload_bill: { es: 'Leemos el consumo y la tarifa por ti. Acepta JPG, PNG, WEBP o PDF.', en: 'We read the consumption and rate for you. Accepts JPG, PNG, WEBP or PDF.', pt: 'Lemos o consumo e a tarifa por você. Aceita JPG, PNG, WEBP ou PDF.' },

    // ─── STEP 2: VIVIENDA ───
    s2_title: { es: 'Mi Vivienda', en: 'My Home', pt: 'Minha Moradia' },
    s2_desc:  { es: 'Selecciona tu tipo de hogar y estructura familiar.', en: 'Select your home type and family structure.', pt: 'Selecione o tipo de moradia e estrutura familiar.' },
    s2_badge: { es: 'Paso 2 de 4', en: 'Step 2 of 4', pt: 'Passo 2 de 4' },
    label_property_type: { es: 'Tipo de Inmueble', en: 'Property Type', pt: 'Tipo de Imóvel' },
    type_house:     { es: 'Casa', en: 'House', pt: 'Casa' },
    type_apartment: { es: 'Departamento / Piso', en: 'Apartment / Flat', pt: 'Apartamento' },
    type_rv:        { es: 'Casilla / Casa Rodante / RV', en: 'Trailer / RV / Mobile Home', pt: 'Trailer / Casa Móvel' },
    type_other:     { es: 'Otro', en: 'Other', pt: 'Outro' },
    label_describe: { es: 'Descríbelo en tus palabras', en: 'Describe it in your own words', pt: 'Descreva com suas palavras' },
    hint_describe:  { es: 'Volti lo interpretará para clasificar tu vivienda.', en: 'Volti will interpret it to classify your home.', pt: 'Volti interpretará para classificar sua moradia.' },

    // ─── STEP 3: EQUIPAMIENTO ───
    s3_title: { es: 'Equipamiento Principal', en: 'Main Equipment', pt: 'Equipamento Principal' },
    s3_desc:  { es: 'Indica cuáles de estos artefactos utilizas en tu hogar.', en: 'Indicate which of these appliances you use at home.', pt: 'Indique quais destes aparelhos você usa em casa.' },
    s3_badge: { es: 'Paso 3 de 4', en: 'Step 3 of 4', pt: 'Passo 3 de 4' },
    eq_ac:          { es: 'Aire Acondicionado / Climatización', en: 'Air Conditioning / HVAC', pt: 'Ar Condicionado / Climatização' },
    eq_ac_desc:     { es: 'Equipos de refrigeración o calefacción eléctrica', en: 'Cooling or electric heating equipment', pt: 'Equipamentos de refrigeração ou aquecimento elétrico' },
    eq_heating:     { es: 'Calefacción Eléctrica', en: 'Electric Heating', pt: 'Aquecimento Elétrico' },
    eq_heating_desc:{ es: 'Estufas, radiadores, calefactores', en: 'Heaters, radiators, space heaters', pt: 'Estufas, radiadores, aquecedores' },
    eq_water:       { es: 'Calentador de Agua / Termotanque (Eléctrico)', en: 'Water Heater / Electric Tank', pt: 'Aquecedor de Água / Boiler (Elétrico)' },
    eq_water_desc:  { es: 'Uso de electricidad para calentar agua', en: 'Using electricity to heat water', pt: 'Uso de eletricidade para aquecer água' },
    eq_dryer:       { es: 'Secarropas Eléctrico', en: 'Electric Dryer', pt: 'Secadora Elétrica' },
    eq_dryer_desc:  { es: 'Secado de prendas', en: 'Clothes drying', pt: 'Secagem de roupas' },
    eq_oven:        { es: 'Horno o Anafe Eléctrico', en: 'Electric Oven or Stove', pt: 'Forno ou Fogão Elétrico' },
    eq_oven_desc:   { es: 'Cocción eléctrica', en: 'Electric cooking', pt: 'Cozinha elétrica' },
    eq_ext_lights:      { es: 'Luces en el exterior de la vivienda', en: 'Outdoor lights', pt: 'Luzes no exterior da residência' },
    eq_int_lights:      { es: 'Luces interiores encendidas al menos 4 horas al día', en: 'Indoor lights on at least 4 hours a day', pt: 'Luzes internas acesas pelo menos 4 horas por dia' },
    eq_int_lights_hint: { es: 'Solo las que quedan prendidas por 4 horas o más — no todas las de la casa.', en: 'Only the ones left on for 4+ hours — not all the lights in the house.', pt: 'Apenas as que ficam acesas por 4 horas ou mais — não todas as da casa.' },
    skip_section:   { es: 'No quiero responder esta sección', en: 'I don\'t want to answer this section', pt: 'Não quero responder esta seção' },
    skip_equipment_section: { es: 'Ninguno de estos equipos está en mi vivienda', en: 'None of these appliances are in my home', pt: 'Nenhum destes equipamentos está na minha residência' },

    // ─── STEP 4: RUTINAS ───
    s4_title: { es: 'Electrodomésticos & Rutinas', en: 'Appliances & Routines', pt: 'Eletrodomésticos & Rotinas' },
    s4_desc:  { es: 'Indica la frecuencia de uso diario y semanal.', en: 'Indicate daily and weekly usage frequency.', pt: 'Indique a frequência de uso diário e semanal.' },
    s4_badge: { es: 'Paso 4 de 4', en: 'Step 4 of 4', pt: 'Passo 4 de 4' },
    label_laundry:  { es: 'Lavados semanales', en: 'Weekly washes', pt: 'Lavagens semanais' },
    label_fridge:   { es: 'Refrigerador / Heladera', en: 'Refrigerator / Fridge', pt: 'Geladeira / Refrigerador' },
    label_freezer:  { es: 'Freezer independiente', en: 'Standalone freezer', pt: 'Freezer independente' },
    hint_freezer:   { es: 'Congelador separado del refrigerador', en: 'Freezer separate from the fridge', pt: 'Congelador separado da geladeira' },
    label_tv:       { es: 'Televisores', en: 'Televisions', pt: 'Televisores' },
    label_tv_hours: { es: 'Horas promedio de uso diario de TV', en: 'Average daily TV usage hours', pt: 'Horas médias de uso diário de TV' },
    hint_tv_hours:  { es: 'Ingresa las horas de uso al día por televisor.', en: 'Enter the daily usage hours per TV.', pt: 'Insira as horas de uso diário por televisor.' },

    // ─── NAVIGATION BUTTONS ───
    btn_next:     { es: 'Siguiente', en: 'Next', pt: 'Próximo' },
    btn_prev:     { es: 'Anterior', en: 'Previous', pt: 'Anterior' },
    btn_calculate:{ es: 'Calcular Consumo y Ahorro', en: 'Calculate Consumption & Savings', pt: 'Calcular Consumo e Economia' },

    // ─── RESULTS ───
    results_title:   { es: 'Análisis de Consumo', en: 'Consumption Analysis', pt: 'Análise de Consumo' },
    results_desc:    { es: 'Proyección estimada por Volti para tu hogar', en: 'Estimated projection by Volti for your home', pt: 'Projeção estimada por Volti para sua casa' },
    metric_consumption: { es: 'Consumo Mensual', en: 'Monthly Consumption', pt: 'Consumo Mensal' },
    metric_savings:  { es: 'Ahorro Estimado a 1 año', en: 'Estimated Savings per Year', pt: 'Economia Estimada em 1 ano' },
    metric_action:   { es: 'Acción Principal', en: 'Main Action', pt: 'Ação Principal' },
    metric_cost:     { es: 'Costo Estimado', en: 'Estimated Cost', pt: 'Custo Estimado' },
    metric_potential:{ es: 'Ahorro Potencial', en: 'Potential Savings', pt: 'Economia Potencial' },
    recs_title:      { es: 'Recomendaciones de Volti', en: 'Volti\'s Recommendations', pt: 'Recomendações do Volti' },
    chart_title:     { es: 'Consumo por categoría', en: 'Consumption by category', pt: 'Consumo por categoria' },
    efficiency_title: { es: 'Etiquetado de eficiencia energética', en: 'Energy efficiency label', pt: 'Etiquetagem de eficiência energética' },
    btn_new_calc:    { es: 'Nuevo Cálculo', en: 'New Calculation', pt: 'Novo Cálculo' },
    btn_print:       { es: 'Imprimir Reporte', en: 'Print Report', pt: 'Imprimir Relatório' },

    // ─── REPORT (FACTURA) ───
    report_title:   { es: 'REPORTE ENERGÉTICO', en: 'ENERGY REPORT', pt: 'RELATÓRIO ENERGÉTICO' },
    report_tagline: { es: 'Asesor energético · Equipo Volti', en: 'Energy advisor · Team Volti', pt: 'Consultor energético · Equipe Volti' },
    rpt_s1:         { es: '1 · Datos del Inmueble', en: '1 · Property Data', pt: '1 · Dados do Imóvel' },
    rpt_s2:         { es: '2 · Desglose de Consumo & Equipamiento', en: '2 · Consumption & Equipment Breakdown', pt: '2 · Detalhamento de Consumo & Equipamento' },
    rpt_s3:         { es: '3 · Diagnóstico Energético', en: '3 · Energy Diagnosis', pt: '3 · Diagnóstico Energético' },
    rpt_recs_title: { es: '💡 Recomendaciones de Volti', en: '💡 Volti\'s Recommendations', pt: '💡 Recomendações do Volti' },
    rpt_disclaimer: { es: 'Este reporte es orientativo. Los valores son estimaciones basadas en los datos ingresados por el usuario.', en: 'This report is for guidance only. Values are estimates based on user-provided data.', pt: 'Este relatório é orientativo. Os valores são estimativas baseadas nos dados informados pelo usuário.' },

    // ─── ACCESSIBILITY PANEL ───
    acces_title:      { es: '♿ Accesibilidad', en: '♿ Accessibility', pt: '♿ Acessibilidade' },
    acces_font:       { es: 'Tamaño de letra', en: 'Font size', pt: 'Tamanho da fonte' },
    acces_color:      { es: 'Modo de color', en: 'Color mode', pt: 'Modo de cor' },
    acces_assistant:   { es: 'Asistente', en: 'Assistant', pt: 'Assistente' },
    acces_hide_msgs:   { es: '💬 Mensajes de Volti', en: '💬 Volti messages', pt: '💬 Mensagens do Volti' },
    acces_voice:      { es: 'Voz', en: 'Voice', pt: 'Voz' },
    acces_tts:        { es: '🔊 Narración de Volti', en: '🔊 Volti narration', pt: '🔊 Narração do Volti' },
    acces_mic_available: { es: '🎤 Micrófono disponible — úsalo desde el asistente', en: '🎤 Microphone available — use it from the assistant', pt: '🎤 Microfone disponível — use-o no assistente' },
    acces_mic_unsupported: { es: '🎤 Tu navegador no soporta reconocimiento de voz', en: '🎤 Your browser doesn\'t support speech recognition', pt: '🎤 Seu navegador não suporta reconhecimento de voz' },
    acces_lang:       { es: 'Idioma', en: 'Language', pt: 'Idioma' },

    // Accessibility font level labels
    font_very_small: { es: 'Muy pequeña', en: 'Very small', pt: 'Muito pequena' },
    font_small:      { es: 'Pequeña', en: 'Small', pt: 'Pequena' },
    font_normal:     { es: 'Normal', en: 'Normal', pt: 'Normal' },
    font_large:      { es: 'Grande', en: 'Large', pt: 'Grande' },
    font_very_large: { es: 'Muy grande', en: 'Very large', pt: 'Muito grande' },

    // Color mode labels
    color_normal:          { es: 'Normal', en: 'Normal', pt: 'Normal' },
    color_deuteranopia:    { es: 'Rojo-verde (deuteranopia)', en: 'Red-green (deuteranopia)', pt: 'Vermelho-verde (deuteranopia)' },
    color_tritanopia:      { es: 'Azul-amarillo (tritanopia)', en: 'Blue-yellow (tritanopia)', pt: 'Azul-amarelo (tritanopia)' },
    color_high_contrast:   { es: 'Alto contraste', en: 'High contrast', pt: 'Alto contraste' },

    // ─── DENJI.JS ASSISTANT DIALOGUE ───
    dj_consent: {
      es: '¿Quieres que el asistente Volti te acompañe hablando y moviéndose por la pantalla mientras completas el formulario, o prefieres hacerlo tú mismo, sin voz ni animaciones?',
      en: 'Would you like the assistant Volti to guide you with voice and animations while you fill out the form, or would you prefer to do it yourself, without voice or animations?',
      pt: 'Gostaria que o assistente Volti te acompanhe falando e se movendo pela tela enquanto preenche o formulário, ou prefere fazer sozinho, sem voz nem animações?'
    },
    dj_yes_guide:     { es: 'Sí, quiero que me guíe', en: 'Yes, guide me', pt: 'Sim, quero que me guie' },
    dj_no_solo:       { es: 'No, prefiero el formulario solo', en: 'No, I prefer the form alone', pt: 'Não, prefiro o formulário sozinho' },
    dj_hello:         { es: '¡Hola! Soy Volti. Detecté que tu sistema tiene ', en: 'Hi! I\'m Volti. I detected that your system has ', pt: 'Olá! Sou Volti. Detectei que seu sistema tem ' },
    dj_keep_config:   { es: 'Sí, mantenerla', en: 'Yes, keep it', pt: 'Sim, manter' },
    dj_default_config:{ es: 'No, usar valores por defecto', en: 'No, use defaults', pt: 'Não, usar padrões' },
    dj_confirm:       { es: 'Confirmar', en: 'Confirm', pt: 'Confirmar' },
    dj_skip:          { es: 'No quiero responder', en: 'I don\'t want to answer', pt: 'Não quero responder' },
    dj_yes:           { es: 'Sí', en: 'Yes', pt: 'Sim' },
    dj_no:            { es: 'No', en: 'No', pt: 'Não' },
    dj_correct:       { es: 'Sí, es correcto', en: 'Yes, that\'s correct', pt: 'Sim, está correto' },
    dj_fix:           { es: 'No, corregir', en: 'No, fix it', pt: 'Não, corrigir' },
    dj_activate:      { es: 'Activar asistente Volti', en: 'Activate assistant Volti', pt: 'Ativar assistente Volti' },
    dj_calculating:   { es: 'Listo, ya tengo todo. Voy a calcular tu consumo, dame un segundo.', en: 'All set! I\'m going to calculate your consumption, one moment.', pt: 'Pronto, já tenho tudo. Vou calcular seu consumo, um momento.' },
    dj_results_ready: { es: 'Listo, aquí está tu resultado.', en: 'Done! Here are your results.', pt: 'Pronto, aqui estão seus resultados.' },
    dj_detecting:     { es: 'Detectando tu ubicación…', en: 'Detecting your location…', pt: 'Detectando sua localização…' },
    dj_no_location:   { es: 'No pude acceder a tu ubicación. Vamos a ingresarla manualmente.', en: 'Couldn\'t access your location. Let\'s enter it manually.', pt: 'Não consegui acessar sua localização. Vamos inserir manualmente.' },
    dj_country_q:     { es: '¿En qué país te encuentras?', en: 'What country are you in?', pt: 'Em que país você está?' },
    dj_state_q:       { es: '¿En qué estado o provincia?', en: 'What state or province?', pt: 'Em qual estado ou província?' },
    dj_city_q:        { es: '¿En qué comuna o ciudad?', en: 'What city or district?', pt: 'Em que cidade ou distrito?' },
    dj_continue:      { es: 'Continuar', en: 'Continue', pt: 'Continuar' },
    dj_skip_confirm:  { es: '¿Estás seguro de que quieres enviar sin responder esta pregunta? Quedará como que no la respondiste.', en: 'Are you sure you want to submit without answering this question? It will be marked as unanswered.', pt: 'Tem certeza de que quer enviar sem responder esta pergunta? Ficará como não respondida.' },
    dj_skip_no:       { es: 'No, quiero responderla', en: 'No, I want to answer it', pt: 'Não, quero responder' },
    dj_skip_yes:      { es: 'Sí, omitirla', en: 'Yes, skip it', pt: 'Sim, pular' },
    dj_detected:      { es: 'Detecté que estás en ', en: 'I detected you\'re in ', pt: 'Detectei que você está em ' },
    dj_is_correct:    { es: '. ¿Es correcto?', en: '. Is that correct?', pt: '. Está correto?' },
    dj_timeout:       { es: 'El cálculo está tardando más de lo normal. Revisa la pantalla, puede que haya un error.', en: 'The calculation is taking longer than usual. Check the screen, there may be an error.', pt: 'O cálculo está demorando mais do que o normal. Verifique a tela, pode haver um erro.' },
    dj_consumption_label: { es: 'Consumo:', en: 'Consumption:', pt: 'Consumo:' },
    dj_savings_label: { es: 'Ahorro:', en: 'Savings:', pt: 'Economia:' },
    dj_your_consumption: { es: ' Tu consumo estimado es ', en: ' Your estimated consumption is ', pt: ' Seu consumo estimado é ' },
    dj_your_savings:  { es: ' Tu ahorro potencial es ', en: ' Your potential savings is ', pt: ' Sua economia potencial é ' },
    dj_my_recs:       { es: ' Mis recomendaciones: ', en: ' My recommendations: ', pt: ' Minhas recomendações: ' },
    dj_form_hint:     { es: 'Puedes llenar el formulario tú mismo, sin el asistente. Si cambias de opinión:', en: 'You can fill out the form yourself, without the assistant. If you change your mind:', pt: 'Você pode preencher o formulário sozinho, sem o assistente. Se mudar de ideia:' },
    dj_not_number:    { es: ', que no es un número; usa los botones', en: ', which is not a number; use the buttons', pt: ', que não é um número; use os botões' },
    dj_say_yes_no:    { es: '; di sí o no, o usa los botones', en: '; say yes or no, or use the buttons', pt: '; diga sim ou não, ou use os botões' },
    dj_not_option:    { es: ', que no es una de las opciones', en: ', which is not one of the options', pt: ', que não é uma das opções' },
    dj_understood:    { es: 'entendí "', en: 'I understood "', pt: 'entendi "' },
    dj_no_answer_btn: { es: 'No quiero responder', en: 'I don\'t want to answer', pt: 'Não quero responder' },
    dj_unanswered:    { es: 'Sin responder (click para volver a responder)', en: 'Unanswered (click to answer again)', pt: 'Sem resposta (clique para responder)' },
    dj_summary:       { es: 'Te hago el resumen.', en: 'Here\'s a summary.', pt: 'Faço um resumo.' },
    dj_cancel_listen: { es: 'escucha cancelada, usa los botones si prefieres', en: 'listening cancelled, use the buttons if you prefer', pt: 'escuta cancelada, use os botões se preferir' },
    dj_extend_q:      { es: 'Con esto ya puedo darte una estimación. ¿Quieres continuar con la versión extendida para afinar el resultado?', en: 'I can already give you an estimate. Would you like to continue with the extended version for a more accurate result?', pt: 'Já posso te dar uma estimativa. Quer continuar com a versão estendida para refinar o resultado?' },

    // ─── DENJI.JS QUESTIONS (steps array) ───
    q_dormitorios:   { es: '¿Cuántos dormitorios tiene la vivienda? Si es un monoambiente, responde cero.', en: 'How many bedrooms does the home have? If it\'s a studio, answer zero.', pt: 'Quantos quartos tem a moradia? Se for um estúdio, responda zero.' },
    q_ventanas:      { es: '¿Cuántas ventanas y puertas balcón tiene la vivienda en total?', en: 'How many windows and balcony doors does the home have in total?', pt: 'Quantas janelas e portas de sacada a moradia tem no total?' },
    q_mayores:       { es: '¿Cuántos habitantes de 18 años o más viven en la vivienda?', en: 'How many people aged 18 or older live in the home?', pt: 'Quantos moradores de 18 anos ou mais vivem na moradia?' },
    q_menores:       { es: '¿Cuántos habitantes de 17 años o menos viven en la vivienda?', en: 'How many people aged 17 or younger live in the home?', pt: 'Quantos moradores de 17 anos ou menos vivem na moradia?' },
    q_ac:            { es: '¿La vivienda tiene aire acondicionado?', en: 'Does the home have air conditioning?', pt: 'A moradia tem ar condicionado?' },
    q_calef:         { es: '¿La calefacción principal de la vivienda es eléctrica?', en: 'Is the main heating in the home electric?', pt: 'O aquecimento principal da moradia é elétrico?' },
    q_agua:          { es: '¿El agua caliente para ducha y lavado de platos se calienta principalmente con electricidad?', en: 'Is hot water for showers and dishes mainly heated with electricity?', pt: 'A água quente para banho e louça é aquecida principalmente com eletricidade?' },
    q_secarropas:    { es: '¿La vivienda tiene secarropas eléctrico?', en: 'Does the home have an electric dryer?', pt: 'A moradia tem secadora elétrica?' },
    q_horno:         { es: '¿El horno principal de la vivienda es eléctrico?', en: 'Is the main oven in the home electric?', pt: 'O forno principal da moradia é elétrico?' },
    q_extendida:     { es: 'Con esto ya puedo darte una estimación. ¿Quieres continuar con la versión extendida para afinar el resultado?', en: 'I can already give you an estimate. Would you like to continue with the extended version for a more accurate result?', pt: 'Já posso te dar uma estimativa. Quer continuar com a versão estendida para refinar o resultado?' },
    q_lavado:        { es: '¿Cuántas veces por semana lava la ropa?', en: 'How many times per week do you do laundry?', pt: 'Quantas vezes por semana lava a roupa?' },
    q_refrigerador:  { es: '¿Cuántos refrigeradores tiene la vivienda?', en: 'How many refrigerators does the home have?', pt: 'Quantas geladeiras a moradia tem?' },
    q_freezer:       { es: '¿Cuántos freezers independientes del refrigerador tiene la vivienda?', en: 'How many standalone freezers does the home have?', pt: 'Quantos freezers independentes a moradia tem?' },
    q_tv:            { es: '¿Cuántos televisores tiene la vivienda?', en: 'How many TVs does the home have?', pt: 'Quantas televisões a moradia tem?' },
    q_tv_freq:       { es: '¿Cuántas horas al día está encendido el televisor principal?', en: 'How many hours per day is the main TV on?', pt: 'Quantas horas por dia a TV principal fica ligada?' },

    // Voice recognition errors
    voice_no_speech: { es: 'No escuché nada, intenta de nuevo.', en: 'I didn\'t hear anything, try again.', pt: 'Não ouvi nada, tente novamente.' },
    voice_no_mic:    { es: 'No encontré un micrófono conectado.', en: 'No microphone found.', pt: 'Nenhum microfone encontrado.' },

    // ─── MISC / SHARED ───
    saludando: { es: 'Saludando', en: 'Greeting', pt: 'Cumprimentando' }
  };

  // ── Idioma actual ─────────────────────────────────────────────────────
  var lang = 'es';
  try {
    var saved = localStorage.getItem('denji_lang');
    if (saved && DICT.app_name[saved]) lang = saved;
  } catch (e) {}

  // ── API pública ───────────────────────────────────────────────────────
  function t(key) {
    var entry = DICT[key];
    if (!entry) return key;
    return entry[lang] || entry.es || key;
  }

  function apply() {
    // data-i18n → textContent
    var els = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < els.length; i++) {
      var key = els[i].getAttribute('data-i18n');
      var val = t(key);
      if (val !== key) els[i].textContent = val;
    }
    // data-i18n-html → innerHTML
    var htmlEls = document.querySelectorAll('[data-i18n-html]');
    for (var j = 0; j < htmlEls.length; j++) {
      var hkey = htmlEls[j].getAttribute('data-i18n-html');
      var hval = t(hkey);
      if (hval !== hkey) htmlEls[j].innerHTML = hval;
    }
    // data-i18n-placeholder → placeholder
    var phEls = document.querySelectorAll('[data-i18n-placeholder]');
    for (var k = 0; k < phEls.length; k++) {
      var pkey = phEls[k].getAttribute('data-i18n-placeholder');
      var pval = t(pkey);
      if (pval !== pkey) phEls[k].placeholder = pval;
    }
    // Update html lang attribute
    document.documentElement.lang = lang === 'es' ? 'es' : lang === 'pt' ? 'pt' : 'en';
  }

  function setLang(newLang) {
    if (!DICT.app_name[newLang]) return;
    lang = newLang;
    try { localStorage.setItem('denji_lang', lang); } catch (e) {}
    apply();
    // Emit event for other scripts (denji.js, accesibilidad.js)
    window.dispatchEvent(new CustomEvent('denji-lang-change', { detail: { lang: lang } }));
  }

  window.DenjiI18n = {
    get lang() { return lang; },
    t: t,
    setLang: setLang,
    apply: apply,
    DICT: DICT
  };

  // Apply on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', apply);
  } else {
    apply();
  }
})();
