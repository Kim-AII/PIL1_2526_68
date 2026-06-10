/* ================================================================
   messages.js — Logique de la messagerie IFRI_MentorLink
   La variable CURRENT_USER_ID est définie dans messages.html
================================================================ */

/* ─ État global ─ */
  let activeConvId  = null;
  let activeUserId  = null;
  let pollTimer     = null;
  const ME = window.CURRENT_USER_ID;

  /* ─ Ouvrir une conversation ─ */
  async function openConv(userId, name, filiere, niveau) {
    activeUserId = userId;

    /* Sélectionner visuellement */
    document.querySelectorAll('.conv-item').forEach(el => el.classList.remove('active'));
    const item = document.querySelector(`.conv-item[data-user-id="${userId}"]`);
    if (item) item.classList.add('active');

    /* Afficher le chat */
    document.getElementById('chat-placeholder').style.display = 'none';
    const chatActive = document.getElementById('chat-active');
    chatActive.style.display = 'flex';

    /* Header */
    const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    document.getElementById('chat-hava').textContent  = initials;
    document.getElementById('chat-hname').textContent = name;
    document.getElementById('chat-hmeta').textContent = [filiere.replace('_','&'), niveau].filter(Boolean).join(' · ') || 'IFRI';

    /* Charger les messages */
    document.getElementById('chat-messages').innerHTML =
      '<div class="chat-loading"><div class="spinner"></div> Chargement…</div>';

    try {
      const r    = await fetch(`/api/messages/conversation/${userId}`);
      const data = await r.json();
      activeConvId = data.conversation_id;
      renderMessages(data.messages);

      /* Supprimer badge non lus */
      if (item) { const d = item.querySelector('.conv-unread'); if (d) d.remove(); }

      /* Polling toutes les 4s */
      clearInterval(pollTimer);
      pollTimer = setInterval(pollMessages, 4000);
    } catch {
      document.getElementById('chat-messages').innerHTML =
        '<div class="chat-loading" style="color:#f87171">Erreur de chargement.</div>';
    }
  }

  /* ─ Afficher les messages ─ */
  function renderMessages(msgs) {
    const container = document.getElementById('chat-messages');
    if (!msgs.length) {
      container.innerHTML = '<div class="chat-loading" style="margin-top:2rem">Aucun message. Dites bonjour !</div>';
      return;
    }
    let lastDate = '';
    container.innerHTML = msgs.map(m => {
      const sent = m.user_id === ME;
      const dt   = new Date(m.date_envoi);
      const date = dt.toLocaleDateString('fr-FR', { day:'numeric', month:'short' });
      const time = dt.toLocaleTimeString('fr-FR', { hour:'2-digit', minute:'2-digit' });
      let sep = '';
      if (date !== lastDate) { sep = `<div class="date-sep">${date}</div>`; lastDate = date; }
      return `${sep}<div class="msg-bubble ${sent ? 'msg-sent' : 'msg-recv'}">
        ${escHtml(m.contenu)}<span class="msg-time">${time}</span>
      </div>`;
    }).join('');
    container.scrollTop = container.scrollHeight;
  }

  /* ─ Polling nouveaux messages ─ */
  async function pollMessages() {
    if (!activeUserId) return;
    try {
      const r    = await fetch(`/api/messages/conversation/${activeUserId}`);
      const data = await r.json();
      renderMessages(data.messages);
    } catch {}
  }

  /* ─ Envoyer un message ─ */
  async function sendMsg() {
    const inp  = document.getElementById('chat-input');
    const text = inp.value.trim();
    if (!text || !activeConvId) return;

    inp.value = ''; autoResize(inp);
    document.getElementById('btn-send').disabled = true;

    /* Affichage optimiste */
    const container = document.getElementById('chat-messages');
    const tmp = document.createElement('div');
    tmp.className = 'msg-bubble msg-sent';
    tmp.innerHTML = `${escHtml(text)}<span class="msg-time">Envoi…</span>`;
    if (container.querySelector('.chat-loading')) container.innerHTML = '';
    container.appendChild(tmp);
    container.scrollTop = container.scrollHeight;

    try {
      const r = await fetch('/api/messages/envoyer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: activeConvId, contenu: text })
      });
      const d = await r.json();
      if (d.succes) {
        const now = new Date().toLocaleTimeString('fr-FR', { hour:'2-digit', minute:'2-digit' });
        tmp.querySelector('.msg-time').textContent = now;
      } else {
        tmp.style.opacity = '.5';
        tmp.querySelector('.msg-time').textContent = '⚠ Erreur';
      }
    } catch {
      tmp.style.opacity = '.5';
      tmp.querySelector('.msg-time').textContent = '⚠ Erreur réseau';
    }
    document.getElementById('btn-send').disabled = false;
    inp.focus();
  }

  /* ─ Filtrer la liste ─ */
  function filterConvs(q) {
    document.querySelectorAll('.conv-item').forEach(el => {
      el.style.display = el.dataset.name.toLowerCase().includes(q.toLowerCase()) ? '' : 'none';
    });
  }

  /* ─ Auto-resize textarea ─ */
  function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  }

  /* ─ Échappement HTML ─ */
  function escHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
  }

  /* ─ Ouvrir depuis l'URL (ex: /messages?user=5) ─ */
  const params = new URLSearchParams(window.location.search);
  const autoUser = params.get('user');
  if (autoUser) {
    const item = document.querySelector(`.conv-item[data-user-id="${autoUser}"]`);
    if (item) {
      item.click();
    } else {
      /* Pas encore de conversation : on récupère l'utilisateur puis on ouvre le chat */
      fetch(`/api/utilisateur/${autoUser}`)
        .then(r => r.json())
        .then(u => openConv(Number(autoUser), `${u.prenom} ${u.nom}`, u.filiere || '', u.niveau || ''))
        .catch(() => {});
    }
  }

  /* ─ Nettoyage polling ─ */
  window.addEventListener('beforeunload', () => clearInterval(pollTimer));