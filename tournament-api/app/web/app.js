const state = { tournaments: [], teams: [], phases: [], matches: [], tournamentId: null, activeMatch: null, mode: null, busy: false, scoreQueue: [] };
const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const tournamentPath = () => `/torneios/${state.tournamentId}`;
let toastTimer;

function toast(message) {
  const element = $('#toast');
  element.textContent = message;
  element.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => element.classList.remove('show'), 3400);
}

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
  } catch {
    throw new Error('Sem conexão com a API. Verifique se o servidor está ligado.');
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    throw new Error(typeof detail === 'string' ? detail : 'Não foi possível concluir a ação.');
  }
  return response.status === 204 ? null : response.json();
}

function currentTournament() { return state.tournaments.find(t => t.id === state.tournamentId); }
function teamName(id) { return state.teams.find(t => t.id === id)?.nome || `Time #${id}`; }
function phaseName(id) { return state.phases.find(f => f.id === id)?.nome || 'Partida'; }
function formatDate(value) { return new Intl.DateTimeFormat('pt-BR', { day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit' }).format(new Date(value)); }

async function loadTournaments() {
  state.tournaments = await api('/torneios/');
  renderTournamentList();
  const requestedId = Number(new URLSearchParams(window.location.search).get('torneio'));
  if (requestedId && state.tournaments.some(t => t.id === requestedId)) {
    await enterTournament(requestedId, false);
  } else {
    showHome(false);
  }
}

function renderTournamentList() {
  $('#home-tournament-count').textContent = state.tournaments.length;
  $('#tournament-list').innerHTML = state.tournaments.length
    ? state.tournaments.map(tournament => `<button class="tournament-card" data-tournament="${tournament.id}" aria-label="Entrar no torneio ${escapeHtml(tournament.nome)}"><span class="tournament-card-top"><span class="tournament-card-number">#${String(tournament.id).padStart(2, '0')}</span><span class="tournament-card-status">${escapeHtml(tournament.status)}</span></span><span class="tournament-card-art" aria-hidden="true">◉</span><span class="tournament-card-name">${escapeHtml(tournament.nome)}</span><span class="tournament-card-description">${escapeHtml(tournament.descricao || 'Entre para cadastrar times e acompanhar partidas.')}</span><span class="tournament-card-footer"><span>${escapeHtml(tournament.modalidade)}</span><strong>ENTRAR NO TORNEIO ↗</strong></span></button>`).join('')
    : `<div class="empty-state tournament-empty"><span class="empty-icon">◉</span><h3>Sua quadra espera por você</h3><p>Crie o primeiro torneio. Depois, entre nele para cadastrar times e partidas.</p><button class="button button-dark" data-action="tournament">Criar torneio</button></div>`;
}

function showHome(updateHistory = true) {
  const wasInTournament = state.tournamentId !== null;
  state.tournamentId = null;
  state.teams = []; state.phases = []; state.matches = [];
  $('#home-view').hidden = false;
  $('#tournament-view').hidden = true;
  $('#nav-matches').hidden = true;
  $('#nav-teams').hidden = true;
  $('#nav-tournaments').classList.add('active');
  $('#nav-matches').classList.remove('active');
  $('#nav-teams').classList.remove('active');
  $('#breadcrumb-current').textContent = 'TORNEIOS';
  if (updateHistory && wasInTournament) {
    const url = new URL(window.location.href);
    url.searchParams.delete('torneio');
    url.hash = '';
    window.history.pushState({}, '', url);
  }
  window.scrollTo(0, 0);
}

async function enterTournament(id, updateHistory = true) {
  const tournament = state.tournaments.find(item => item.id === id);
  if (!tournament) { toast('Torneio não encontrado.'); return; }
  state.tournamentId = id;
  state.teams = []; state.phases = []; state.matches = [];
  $('#home-view').hidden = true;
  $('#tournament-view').hidden = false;
  $('#nav-matches').hidden = false;
  $('#nav-teams').hidden = false;
  $('#nav-tournaments').classList.remove('active');
  $('#nav-matches').classList.add('active');
  $('#nav-teams').classList.remove('active');
  $('#breadcrumb-current').textContent = tournament.nome.toUpperCase();
  $('#detail-name').textContent = tournament.nome;
  $('#detail-description').textContent = tournament.descricao || 'Times, confrontos e cada ponto deste torneio em um só lugar.';
  $('#detail-modality').textContent = tournament.modalidade;
  $('#detail-status').textContent = tournament.status;
  $('#match-list').innerHTML = '<div class="loading-state">Carregando partidas…</div>';
  $('#team-list').innerHTML = '<div class="loading-state">Carregando times…</div>';
  $('#stat-tournament-number').textContent = `#${String(id).padStart(2, '0')}`;
  $('#stat-matches').textContent = '0';
  $('#stat-teams').textContent = '0';
  if (updateHistory) {
    const url = new URL(window.location.href);
    url.searchParams.set('torneio', String(id));
    url.hash = '';
    window.history.pushState({ torneio: id }, '', url);
  }
  window.scrollTo(0, 0);
  try { await loadSelection(); } catch (error) { toast(error.message); }
}

async function loadSelection() {
  if (!state.tournamentId) {
    state.teams = []; state.phases = []; state.matches = [];
    render();
    return;
  }
  const id = state.tournamentId;
  const [teams, phases, matches] = await Promise.all([
    api(`${tournamentPath()}/times/`),
    api(`${tournamentPath()}/fases/`),
    api(`${tournamentPath()}/partidas/`),
  ]);
  if (id !== state.tournamentId) return;
  state.teams = teams; state.phases = phases; state.matches = matches;
  render();
}

function render() {
  if (!state.tournamentId) return;
  $('#stat-matches').textContent = state.matches.length;
  $('#stat-teams').textContent = state.teams.length;
  $('#match-list').innerHTML = state.matches.length
    ? [...state.matches].sort((a,b) => new Date(b.data_partida)-new Date(a.data_partida)).map((match,index) => `<article class="match-card"><div class="match-id">#${String(index + 1).padStart(2,'0')}</div><div class="match-info"><small>${escapeHtml(phaseName(match.fase_id))} · ${formatDate(match.data_partida)}</small><div class="match-teams"><span>${escapeHtml(teamName(match.time1_id))}</span><b>${match.pontos1} : ${match.pontos2}</b><span>${escapeHtml(teamName(match.time2_id))}</span></div></div><div class="match-actions"><button class="play-button" data-match="${match.id}">▶ ABRIR PLACAR</button></div></article>`).join('')
    : `<div class="empty-state"><span class="empty-icon">⚡</span><h3>Ainda sem partidas</h3><p>Adicione dois times e marque o primeiro confronto.</p><button class="button button-dark" data-action="match">Criar partida</button></div>`;
  $('#team-list').innerHTML = state.teams.length
    ? state.teams.map(team => `<div class="team-card"><span class="team-logo">${escapeHtml(team.nome.charAt(0).toUpperCase())}</span><div><strong>${escapeHtml(team.nome)}</strong><small>${team.qtdjogadores} jogadores</small></div></div>`).join('')
    : `<div class="empty-state"><span class="empty-icon">♟</span><h3>Nenhum time escalado</h3><p>Monte o elenco do torneio.</p><button class="button button-dark" data-action="team">Adicionar time</button></div>`;
}

function field(label, name, type, extra = '') {
  return `<label class="form-field"><span>${label}</span><input name="${name}" type="${type}" ${extra} required></label>`;
}

function openForm(mode) {
  if (mode !== 'tournament' && !state.tournamentId) { toast('Crie um torneio primeiro.'); return; }
  if (mode === 'match' && state.teams.length < 2) { toast('Cadastre pelo menos dois times antes da partida.'); openForm('team'); return; }
  state.mode = mode;
  const title = { tournament:'Novo torneio', team:'Adicionar time', match:'Nova partida' }[mode];
  $('#dialog-title').textContent = title;
  $('#dialog-kicker').textContent = { tournament:'COMECE O CAMPEONATO', team:'MONTE O ELENCO', match:'BOLA EM JOGO' }[mode];
  $('#submit-dialog').textContent = { tournament:'Criar torneio', team:'Adicionar time', match:'Criar partida' }[mode];
  let fields = '';
  if (mode === 'tournament') {
    fields = field('NOME DO TORNEIO','nome','text','placeholder="Ex.: Copa da Rua" minlength="3" maxlength="50"')
      + field('MODALIDADE','modalidade','text','value="Basquete" minlength="3" maxlength="30"')
      + `<label class="form-field"><span>DESCRIÇÃO (OPCIONAL)</span><input name="descricao" type="text" placeholder="O campeonato da galera" maxlength="100"></label>`;
  } else if (mode === 'team') {
    fields = field('NOME DO TIME','nome','text','placeholder="Ex.: Tigres da Quadra" minlength="3" maxlength="50"')
      + field('NÚMERO DE JOGADORES','qtdjogadores','number','value="5" min="3"')
      + `<label class="form-field"><span>CONTATO (OPCIONAL)</span><input name="contato" type="text" placeholder="Nome ou telefone" maxlength="100"></label>`;
  } else {
    const options = state.teams.map(t => `<option value="${t.id}">${escapeHtml(t.nome)}</option>`).join('');
    const date = new Date(); date.setMinutes(date.getMinutes()-date.getTimezoneOffset());
    fields = `<label class="form-field"><span>TIME LARANJA</span><select name="time1_id" required>${options}</select></label>`
      + `<label class="form-field"><span>TIME ROXO</span><select name="time2_id" required>${options}</select></label>`
      + field('DATA E HORA','data_partida','datetime-local',`value="${date.toISOString().slice(0,16)}"`);
  }
  $('#form-fields').innerHTML = fields;
  if (mode === 'match') $('#entry-form').elements.time2_id.selectedIndex = 1;
  $('#form-dialog').showModal();
  $('#form-fields input, #form-fields select')?.focus();
}

async function submitForm(event) {
  event.preventDefault();
  const button = $('#submit-dialog');
  button.disabled = true;
  const data = Object.fromEntries(new FormData(event.currentTarget));
  try {
    if (state.mode === 'tournament') {
      const created = await api('/torneios/', { method:'POST', body:JSON.stringify({ ...data, status:'aberto', descricao:data.descricao || null }) });
      $('#form-dialog').close();
      await loadTournaments();
      document.querySelector(`[data-tournament="${created.id}"]`)?.focus();
      toast('Torneio criado! Entre nele para adicionar os times.');
    } else if (state.mode === 'team') {
      await api(`${tournamentPath()}/times/`, { method:'POST', body:JSON.stringify({ ...data, qtdjogadores:Number(data.qtdjogadores) }) });
      $('#form-dialog').close();
      await loadSelection();
      toast('Time entrou em quadra!');
    } else {
      if (data.time1_id === data.time2_id) throw new Error('Escolha dois times diferentes.');
      let phase = state.phases[0];
      if (!phase) phase = await api(`${tournamentPath()}/fases/`, { method:'POST', body:JSON.stringify({ nome:'Fase principal', ordem:1 }) });
      const match = await api(`${tournamentPath()}/partidas/`, { method:'POST', body:JSON.stringify({ fase_id:phase.id, time1_id:Number(data.time1_id), time2_id:Number(data.time2_id), data_partida:data.data_partida, pontos1:0, pontos2:0 }) });
      $('#form-dialog').close();
      await loadSelection();
      openScore(match.id);
      toast('Partida criada. É hora do jogo!');
    }
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; }
}

function showScore(match) {
  state.activeMatch = match;
  $('#score-tournament').textContent = currentTournament()?.nome || 'TORNEIO';
  $('#score-screen').classList.toggle('basketball-mode', (currentTournament()?.modalidade || '').trim().toLowerCase() === 'basquete');
  $('#score-round').textContent = phaseName(match.fase_id);
  $('#score-name1').textContent = teamName(match.time1_id);
  $('#score-name2').textContent = teamName(match.time2_id);
  $('#undo-name1').textContent = teamName(match.time1_id);
  $('#undo-name2').textContent = teamName(match.time2_id);
  $('#score-value1').textContent = match.pontos1;
  $('#score-value2').textContent = match.pontos2;
  $('#undo-left').disabled = match.pontos1 === 0;
  $('#undo-right').disabled = match.pontos2 === 0;
}

let wheelSide = null;
let wheelNegative = false;

function openPointWheel(lado, event) {
  wheelSide = lado;
  wheelNegative = false;
  const panel = $('#point-wheel-panel');
  const x = event?.clientX ?? window.innerWidth / 2;
  const y = event?.clientY ?? window.innerHeight / 2;
  panel.style.left = `${x}px`;
  panel.style.top = `${y}px`;
  panel.classList.toggle('team-orange', lado === 1);
  panel.classList.toggle('team-purple', lado === 2);
  $('#point-wheel').classList.add('open');
  $('#point-wheel').setAttribute('aria-hidden', 'false');
  $('#point-wheel-title').textContent = lado === 1 ? teamName(state.activeMatch.time1_id) : teamName(state.activeMatch.time2_id);
  updatePointWheel();
}

function updatePointWheel() {
  const sign = wheelNegative ? -1 : 1;
  document.querySelectorAll('[data-wheel-value]').forEach(button => {
    const value = Number(button.dataset.wheelValue);
    button.textContent = `${wheelNegative ? '-' : ''}${value}`;
    button.dataset.delta = String(value * sign);
  });
  $('#wheel-toggle-negative').classList.toggle('negative', wheelNegative);
  $('#wheel-toggle-negative').setAttribute('aria-label', wheelNegative ? 'Mostrar pontos positivos' : 'Mostrar pontos negativos');
}

function closePointWheel() {
  $('#point-wheel').classList.remove('open');
  $('#point-wheel').setAttribute('aria-hidden', 'true');
  wheelSide = null;
}

function openScore(id) {
  const match = state.matches.find(m => m.id === id);
  if (!match) return;
  showScore(match);
  $('#score-screen').hidden = false;
  document.body.style.overflow = 'hidden';
}

function closeScore() {
  $('#score-screen').hidden = true;
  document.body.style.overflow = '';
  if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
  state.activeMatch = null;
  loadSelection().catch(error => toast(error.message));
}

async function score(lado, delta) {
  if (!state.activeMatch) return;
  state.scoreQueue.push({ lado, delta, matchId: state.activeMatch.id });
  if (state.busy) return;
  state.busy = true;
  $('#score-screen').classList.add('busy');
  while (state.scoreQueue.length) {
    const next = state.scoreQueue.shift();
    try {
      const match = await api(`${tournamentPath()}/partidas/${next.matchId}/ponto?lado=${next.lado}&delta=${next.delta}`, { method:'POST' });
      if (state.activeMatch?.id === match.id) showScore(match);
      state.matches = state.matches.map(item => item.id === match.id ? match : item);
      render();
    } catch (error) { state.scoreQueue = []; toast(error.message); }
  }
  state.busy = false;
  $('#score-screen').classList.remove('busy');
}

$('#new-tournament-hero').addEventListener('click', () => openForm('tournament'));
$('#new-tournament').addEventListener('click', () => openForm('tournament'));
$('#new-team').addEventListener('click', () => openForm('team'));
$('#new-match').addEventListener('click', () => openForm('match'));
$('#back-to-tournaments').addEventListener('click', () => showHome());
$('#nav-tournaments').addEventListener('click', event => { event.preventDefault(); showHome(); });
$('#nav-matches').addEventListener('click', () => { $('#nav-matches').classList.add('active'); $('#nav-teams').classList.remove('active'); });
$('#nav-teams').addEventListener('click', () => { $('#nav-teams').classList.add('active'); $('#nav-matches').classList.remove('active'); });
$('#close-dialog').addEventListener('click', () => $('#form-dialog').close());
$('#cancel-dialog').addEventListener('click', () => $('#form-dialog').close());
$('#entry-form').addEventListener('submit', submitForm);
document.addEventListener('click', event => {
  const action = event.target.closest('[data-action]')?.dataset.action;
  if (action) openForm(action);
  const tournamentId = Number(event.target.closest('[data-tournament]')?.dataset.tournament);
  if (tournamentId) enterTournament(tournamentId);
  const matchId = Number(event.target.closest('[data-match]')?.dataset.match);
  if (matchId) openScore(matchId);
});
window.addEventListener('popstate', () => {
  const id = Number(new URLSearchParams(window.location.search).get('torneio'));
  if (id && state.tournaments.some(item => item.id === id)) enterTournament(id, false);
  else showHome(false);
});
$('#score-orange').addEventListener('click', event => {
  if ((currentTournament()?.modalidade || '').trim().toLowerCase() === 'basquete') openPointWheel(1, event);
  else score(1, 1);
});
$('#score-purple').addEventListener('click', event => {
  if ((currentTournament()?.modalidade || '').trim().toLowerCase() === 'basquete') openPointWheel(2, event);
  else score(2, 1);
});
$('#wheel-toggle-negative').addEventListener('click', () => { wheelNegative = !wheelNegative; updatePointWheel(); });
$('#wheel-close').addEventListener('click', closePointWheel);
document.querySelectorAll('[data-wheel-value]').forEach(button => {
  button.addEventListener('click', () => {
    if (wheelSide === null) return;
    const lado = wheelSide;
    const delta = Number(button.dataset.delta);
    closePointWheel();
    score(lado, delta);
  });
});
$('#point-wheel').addEventListener('click', event => { if (event.target === $('#point-wheel')) closePointWheel(); });
$('#undo-left').addEventListener('click', () => score(1, -1));
$('#undo-right').addEventListener('click', () => score(2, -1));
$('#close-score').addEventListener('click', closeScore);
$('#fullscreen-score').addEventListener('click', () => {
  if (document.fullscreenElement) document.exitFullscreen();
  else $('#score-screen').requestFullscreen?.().catch(() => toast('Tela cheia indisponível neste navegador.'));
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && $('#point-wheel').classList.contains('open')) closePointWheel();
  else if (event.key === 'Escape' && !$('#score-screen').hidden) closeScore();
  if ($('#score-screen').hidden || $('#form-dialog').open) return;
  if (event.key === 'ArrowLeft') score(1, 1);
  if (event.key === 'ArrowRight') score(2, 1);
});

let installPrompt = null;
const isAndroidShell = navigator.userAgent.includes('RachaAndroid');
if (isAndroidShell) {
  $('#install-app').hidden = true;
  $('#android-server').hidden = false;
  $('#android-server').addEventListener('click', () => { window.location.href = 'racha://settings'; });
} else {
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    installPrompt = event;
  });
  window.addEventListener('appinstalled', () => {
    installPrompt = null;
    $('#install-app').hidden = true;
    toast('Pontus-se instalado no dispositivo.');
  });
  $('#install-app').addEventListener('click', async () => {
    if (installPrompt) {
      await installPrompt.prompt();
      installPrompt = null;
      return;
    }
    const apple = /iPhone|iPad|iPod/.test(navigator.userAgent);
    toast(apple ? 'Use Compartilhar → Adicionar à Tela de Início.' : 'Use a opção Instalar aplicativo no menu do navegador.');
  });
  if (window.matchMedia('(display-mode: standalone)').matches) $('#install-app').hidden = true;
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
}
loadTournaments().catch(error => { render(); toast(error.message); });
