(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const form = $('#query-form'), input = $('#question'), send = $('#send-button');
  const chatArea = $('#chat-area'), welcome = $('#welcome-screen'), messages = $('#message-list');
  const errorBox = $('#composer-error'), recent = $('#recent-list'), sidebar = $('#sidebar');
  const overlay = $('#sidebar-overlay'), menu = $('#menu-button');
  let busy = false, started = false, sessionQuestions = [];

  const timeNow = () => new Intl.DateTimeFormat('en-IN', {hour: '2-digit', minute: '2-digit'}).format(new Date());
  const scrollLatest = () => requestAnimationFrame(() => { chatArea.scrollTop = chatArea.scrollHeight; });
  function resizeInput() { input.style.height = 'auto'; input.style.height = `${Math.min(input.scrollHeight, 136)}px`; }
  function startConversation() { if (!started) { started = true; welcome.hidden = true; messages.hidden = false; } }
  function addMessage(role, text) {
    const item = document.createElement('article'); item.className = `message ${role}`;
    const body = document.createElement('div'); body.className = 'message-body';
    const content = document.createElement('p'); content.className = 'message-text'; content.textContent = text;
    const timestamp = document.createElement('time'); timestamp.dateTime = new Date().toISOString(); timestamp.textContent = timeNow();
    body.append(content, timestamp);
    if (role === 'assistant') { const icon = document.createElement('span'); icon.className = 'assistant-avatar'; icon.setAttribute('aria-hidden', 'true'); icon.textContent = '✦'; item.append(icon); }
    item.append(body); messages.append(item); scrollLatest(); return item;
  }
  function reasons(value) {
    if (!value) return []; if (Array.isArray(value)) return value.flatMap(reasons);
    if (typeof value === 'object') return Object.values(value).flatMap(reasons);
    return [String(value).replace(/[_-]+/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase())];
  }
  function addMetadata(item, data) {
    const body = item.querySelector('.message-body'), metadata = document.createElement('div'); metadata.className = 'response-meta'; let visible = false;
    if (data.grounded === true) { const tag = document.createElement('span'); tag.className = 'meta-item grounded'; tag.textContent = '✓ Based on university information'; metadata.append(tag); visible = true; }
    if (typeof data.source_document === 'string' && data.source_document.trim()) { const tag = document.createElement('span'); tag.className = 'meta-item source'; tag.textContent = `Source: ${data.source_document}`; metadata.append(tag); visible = true; }
    if (data.escalated === true) { const note = document.createElement('div'); note.className = 'escalation-note'; const title = document.createElement('strong'); title.textContent = '⚠ This question may require additional assistance.'; note.append(title); const values = reasons(data.escalation_reasons); if (values.length) { const detail = document.createElement('span'); detail.textContent = values.join(' • '); note.append(detail); } metadata.append(note); visible = true; }
    if (visible) body.insertBefore(metadata, body.querySelector('time'));
  }
  function showTyping() { const typing = document.createElement('article'); typing.className = 'message assistant typing-message'; typing.id = 'typing-message'; typing.innerHTML = '<span class="assistant-avatar" aria-hidden="true">✦</span><div class="message-body"><div class="typing-dots" aria-label="AI is thinking"><i></i><i></i><i></i></div><span>AI is thinking...</span></div>'; messages.append(typing); scrollLatest(); }
  const removeTyping = () => $('#typing-message')?.remove();
  function updateRecent(query) {
    sessionQuestions = [query, ...sessionQuestions.filter(item => item !== query)].slice(0, 6); recent.replaceChildren();
    sessionQuestions.forEach(question => { const button = document.createElement('button'); button.type = 'button'; button.className = 'recent-item'; button.title = question; const label = document.createElement('span'); label.textContent = question; button.append(label); button.addEventListener('click', () => { input.value = question; resizeInput(); input.focus(); closeSidebar(); }); recent.append(button); });
  }
  function setBusy(value) { busy = value; send.disabled = value; input.disabled = value; send.classList.toggle('is-loading', value); send.setAttribute('aria-label', value ? 'Sending message' : 'Send message'); }
  async function submitQuery(query) {
    if (busy || !query.trim()) return;
    errorBox.textContent = ''; startConversation(); addMessage('user', query); updateRecent(query); input.value = ''; resizeInput(); setBusy(true); showTyping();
    try {
      const response = await fetch('/query', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({query})});
      const data = await response.json().catch(() => null);
      if (!response.ok || !data || typeof data !== 'object') throw new Error(data?.error || 'The Admissions Helpdesk is unavailable right now.');
      if (typeof data.answer !== 'string' || !data.answer.trim()) throw new Error('The Admissions Helpdesk returned an unexpected response.');
      removeTyping(); const answer = addMessage('assistant', data.answer); addMetadata(answer, data);
    } catch (error) { console.error('Admissions Helpdesk request failed:', error); removeTyping(); addMessage('assistant', "Sorry, I couldn't connect to the Admissions Helpdesk right now. Please try again."); errorBox.textContent = 'Your message could not be processed. Please try again.'; }
    finally { setBusy(false); input.focus(); scrollLatest(); }
  }
  function closeSidebar() { sidebar.classList.remove('is-open'); overlay.hidden = true; menu.setAttribute('aria-expanded', 'false'); }
  form.addEventListener('submit', event => { event.preventDefault(); submitQuery(input.value); });
  input.addEventListener('input', resizeInput);
  input.addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); } });
  document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => submitQuery(button.dataset.question || '')));
  $('#new-chat').addEventListener('click', () => { messages.replaceChildren(); welcome.hidden = false; messages.hidden = true; started = false; errorBox.textContent = ''; input.value = ''; resizeInput(); input.focus(); closeSidebar(); });
  menu.addEventListener('click', () => { const opening = !sidebar.classList.contains('is-open'); sidebar.classList.toggle('is-open', opening); overlay.hidden = !opening; menu.setAttribute('aria-expanded', String(opening)); }); overlay.addEventListener('click', closeSidebar);
  $('#theme-toggle').addEventListener('click', event => { const dark = document.body.classList.toggle('dark-theme'); event.currentTarget.textContent = dark ? '☀' : '☾'; event.currentTarget.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme'); });
  $('#support-button').addEventListener('click', () => { errorBox.textContent = 'Support contact details are not configured in this helpdesk.'; input.focus(); });
  resizeInput();
})();
