/* ================================================================
   matching.js — Filtrage des cartes de matching — IFRI_MentorLink
================================================================ */

let currentFil = '';
  function setFil(btn, fil) {
    currentFil = fil;
    document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterCards();
  }
  function filterCards() {
    const q = document.getElementById('search-inp').value.toLowerCase();
    document.querySelectorAll('.match-card').forEach(card => {
      const nameOk = card.dataset.name.toLowerCase().includes(q);
      const filOk  = !currentFil || card.dataset.fil === currentFil;
      card.style.display = (nameOk && filOk) ? '' : 'none';
    });
  }
  /* ─ Aperçu du profil (modale) ─ */
  function escHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function scoreClass(score) {
    return score >= 80 ? 'high' : (score >= 60 ? 'mid' : 'low');
  }
  function compLabel(c) {
    if (typeof c === 'string') return c;
    return (c && (c.nom || (c.competence && c.competence.nom))) || '';
  }
  function dispoLabel(d) {
    if (typeof d === 'string') return d;
    if (!d) return '';
    const deb = (d.heure_debut || '').toString().slice(0, 5);
    const fin = (d.heure_fin || '').toString().slice(0, 5);
    return [d.jour, (deb && fin) ? deb + '–' + fin : ''].filter(Boolean).join(' ');
  }

  async function openProfile(userId, score) {
    const modal = document.getElementById('profile-modal');
    const body  = document.getElementById('profile-body');
    modal.classList.add('open');
    body.innerHTML = '<div class="pm-loading"><div class="pm-spinner"></div> Chargement du profil…</div>';

    try {
      const r = await fetch('/api/utilisateur/' + userId);
      const u = await r.json();

      const initials = ((u.prenom || '')[0] || '').toUpperCase() + ((u.nom || '')[0] || '').toUpperCase();
      const meta = [(u.filiere || '').replace('_', '&'), u.niveau ? 'Niveau ' + u.niveau : '']
                     .filter(Boolean).join(' · ') || 'IFRI';
      const sCls = scoreClass(score);
      const comps  = Array.isArray(u.competences)   ? u.competences.map(compLabel).filter(Boolean)   : [];
      const dispos = Array.isArray(u.disponibilites) ? u.disponibilites.map(dispoLabel).filter(Boolean) : [];

      body.innerHTML =
        '<div class="pm-head">' +
          '<div class="pm-ava">' + (escHtml(initials) || '?') + '</div>' +
          '<div class="pm-id">' +
            '<div class="pm-name">' + escHtml(((u.prenom || '') + ' ' + (u.nom || '')).trim()) + '</div>' +
            '<div class="pm-meta">' + escHtml(meta) + '</div>' +
          '</div>' +
          '<span class="pm-score ' + sCls + '">' + score + '%<small>match</small></span>' +
        '</div>' +
        '<div class="pm-section"><div class="pm-lbl">Bio</div>' +
          (u.bio ? '<p class="pm-bio">' + escHtml(u.bio) + '</p>'
                 : '<p class="pm-empty">Aucune bio renseignée.</p>') +
        '</div>' +
        '<div class="pm-section"><div class="pm-lbl">Compétences</div><div class="pm-tags">' +
          (comps.length ? comps.map(c => '<span class="pm-tag">' + escHtml(c) + '</span>').join('')
                        : '<span class="pm-empty">Aucune compétence renseignée.</span>') +
        '</div></div>' +
        '<div class="pm-section"><div class="pm-lbl">Disponibilités</div><div class="pm-chips">' +
          (dispos.length ? dispos.map(d => '<span class="pm-chip">' + escHtml(d) + '</span>').join('')
                         : '<span class="pm-empty">Aucune disponibilité renseignée.</span>') +
        '</div></div>' +
        '<a href="/messages?user=' + userId + '" class="pm-contact"><i class="fa-solid fa-comment-dots"></i> Contacter</a>';
    } catch (e) {
      body.innerHTML = '<div class="pm-loading" style="color:#fca5a5">Impossible de charger le profil.</div>';
    }
  }

  function closeProfile() { document.getElementById('profile-modal').classList.remove('open'); }
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeProfile(); });