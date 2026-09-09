const $ = (selector) => document.querySelector(selector);
const historyBody = $('#history-body');
function escapeHTML(value) { return String(value ?? '').replace(/[&<>'"]/g, character => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'}[character])); }
function formatHistoryTime(value) { const date = new Date(value); return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat('en-IN', {day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'}).format(date); }
function renderHistory(interactions) {
  historyBody.innerHTML = interactions.length ? interactions.map(item => `<tr><td>${escapeHTML(item.query)}</td><td>${escapeHTML(humanIntent(item.predicted_intent))}</td><td>${item.classifier_confidence == null ? '—' : Number(item.classifier_confidence).toFixed(2)}</td><td>${escapeHTML(item.source_document || '—')}</td><td>${item.grounded == null ? '—' : (item.grounded ? 'Yes' : 'No')}</td><td class="${item.escalated ? 'yes-red' : ''}">${item.escalated ? 'Yes' : 'No'}</td><td>${formatHistoryTime(item.timestamp)}</td></tr>`).join('') : '<tr><td colspan="7">No interactions found.</td></tr>';
  $('#history-count').textContent = `Showing ${interactions.length} ${interactions.length === 1 ? 'entry' : 'entries'}`;
}
async function loadHistory() {
  historyBody.innerHTML = '<tr><td colspan="7">Loading history...</td></tr>';
  try { const response = await fetch('/history'); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Unable to load history.'); renderHistory(data.interactions || []); }
  catch (error) { historyBody.innerHTML = `<tr><td colspan="7">${escapeHTML(error.message)}</td></tr>`; }
}
function showView(name) { document.querySelectorAll('.view').forEach(v => v.classList.toggle('active', v.id === name)); document.querySelectorAll('.nav-link').forEach(b => b.classList.toggle('active', b.dataset.view === name)); if (name === 'history') loadHistory(); window.scrollTo(0, 0); }
document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => showView(button.dataset.view)));
document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => { $('#question').value = button.dataset.question; $('#question').focus(); }));
function humanIntent(value) { return (value || 'other').replaceAll('_', ' '); }
function timeNow() { return new Intl.DateTimeFormat('en-IN', {hour: '2-digit', minute: '2-digit'}).format(new Date()); }
$('#query-form').addEventListener('submit', async (event) => {
  event.preventDefault(); const query = $('#question').value.trim(); const error = $('#query-error'); const send = $('.send'); if (!query) return;
  error.textContent = ''; send.disabled = true; send.innerHTML = '… <span>Sending</span>';
  try {
    const response = await fetch('/query', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({query})}); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Unable to process your query.');
    const now = timeNow(); $('#asked-question').textContent = query; $('#asked-time').textContent = now; $('#answer-time').textContent = now; $('#answer-text').textContent = data.answer;
    $('#intent').textContent = '⌁ ' + humanIntent(data.predicted_intent); $('#source').textContent = data.source_document || 'No matching document'; $('#confidence').textContent = data.classifier_confidence.toFixed(2); $('#similarity').textContent = data.retrieval_similarity ?? '—';
    $('#escalated').textContent = data.escalated ? 'Yes' : 'No'; $('#reasons').textContent = data.escalation_reasons.join(', ') || '—'; $('#grounded').textContent = data.grounded ? 'Yes' : 'No'; $('#cleaned-query').textContent = data.cleaned_query;
    $('#confidence-tag').textContent = '◉ Confidence: ' + data.classifier_confidence.toFixed(2); $('#similarity-tag').textContent = '◌ Similarity: ' + (data.retrieval_similarity ?? '—');
    $('#grounded-tag').textContent = (data.grounded ? '✓ Grounded' : '× Not grounded'); $('#grounded-tag').className = 'tag ' + (data.grounded ? 'grounded' : 'escalated'); $('#escalated-tag').textContent = data.escalated ? '⚠ Escalated' : '✓ Not escalated'; $('#escalated-tag').style.display = data.escalated ? '' : 'none';
    showView('answer');
  } catch (err) { error.textContent = err.message; } finally { send.disabled = false; send.innerHTML = '↗ <span>Send</span>'; }
});
