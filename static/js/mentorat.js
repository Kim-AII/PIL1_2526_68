/* ═══════════════════════════════════════════════════════
   MENTORAT — Logique JS (offres.html)
═══════════════════════════════════════════════════════ */

// ── État global ──
let offresData   = [];   // données chargées depuis l'API
let activeTab    = 'offre';  // 'offre' | 'demande' | 'mes'
let filterFiliere = '';
let filterNiveau  = '';
let filterComp    = '';

// ── Références DOM ──
const grid        = document.getElementById('ment-grid');
const mesPubsWrap = document.getElementById('mes-pubs-wrap');


// ═══════════════════════════════
//  CHARGEMENT DES DONNÉES
// ═══════════════════════════════

async function loadOffres() {
  showSpinner();
  const params = new URLSearchParams({ type: activeTab });
  if (filterFiliere) params.set('filiere', filterFiliere);
  if (filterNiveau)  params.set('niveau',  filterNiveau);
  if (filterComp)    params.set('competence_id', filterComp);

  try {
    const res  = await fetch('/api/mentorat/offres?' + params);
    offresData = await res.json();
    renderOffres(offresData);
  } catch (e) {
    showToast('Erreur lors du chargement.', 'error');
  }
}

async function loadMesPublications() {
  if (!mesPubsWrap) return;
  mesPubsWrap.innerHTML = '<div class="ment-spinner"><div class="spinner-ring"></div> Chargement…</div>';
  try {
    const res   = await fetch('/api/mentorat/mes-publications');
    const pubs  = await res.json();
    renderMesPublications(pubs);
  } catch (e) {
    mesPubsWrap.innerHTML = '<p style="color:var(--sub);text-align:center;padding:2rem">Erreur de chargement.</p>';
  }
}


// ═══════════════════════════════
//  RENDU — Grille d'offres
// ═══════════════════════════════

function renderOffres(offres) {
  if (!grid) return;
  if (!offres.length) {
    const type = activeTab === 'offre' ? 'offres de mentorat' : 'demandes de mentorat';
    grid.innerHTML = `
      <div class="empty-ment">
        <span class="em-ico"><i class="fa-solid fa-hand-holding-hand"></i></span>
        <h3>Aucune ${type} disponible</h3>
        <p>Il n'y a actuellement aucune publication dans cette catégorie.<br>
           Soyez le premier à en publier une !</p>
      </div>`;
    return;
  }

  grid.innerHTML = offres.map((o, i) => offreCard(o, i)).join('');
}

function offreCard(o, idx) {
  const avaIdx   = idx % 4;
  const score    = o.score_compat || 0;
  const scCls    = score >= 70 ? 'score-high' : score >= 40 ? 'score-mid' : 'score-low';
  const type_cls = o.type_publication === 'offre' ? 'type-offre' : 'type-demande';
  const type_lbl = o.type_publication === 'offre'
    ? '<i class="fa-solid fa-chalkboard-user"></i> Offre'
    : '<i class="fa-solid fa-hand-raised"></i> Demande';

  const deja     = o.ma_candidature;
  const postulBtnLabel = deja
    ? '<i class="fa-solid fa-check"></i> Déjà postulé'
    : '<i class="fa-solid fa-paper-plane"></i> Postuler';

  const places_pct = Math.round((o.places_restantes / o.max_places) * 100);
  const date_fmt   = new Date(o.date_creation).toLocaleDateString('fr-FR', { day:'numeric', month:'short' });

  let tags = '';
  if (o.competence) tags += `<span class="oc-tag tag-comp"><i class="fa-solid fa-bolt"></i> ${o.competence.nom}</span>`;
  if (o.niveau_cible)  tags += `<span class="oc-tag tag-niv">${o.niveau_cible}</span>`;
  if (o.filiere_cible) tags += `<span class="oc-tag tag-fil">${o.filiere_cible.replace('_','&')}</span>`;

  const prenom = o.auteur.prenom || '';
  const nom    = o.auteur.nom    || '';
  const initiales = (prenom[0]||'').toUpperCase() + (nom[0]||'').toUpperCase();

  return `
  <div class="offre-card" id="offre-${o.id}">
    <div style="display:flex;align-items:center;justify-content:space-between;gap:.5rem">
      <span class="type-badge ${type_cls}">${type_lbl}</span>
      <span style="font-size:.72rem;color:var(--dim)">${date_fmt}</span>
    </div>

    <div class="oc-head">
      <div class="oc-ava oc-ava-${avaIdx}">${initiales}</div>
      <div class="oc-meta">
        <div class="oc-auteur">${prenom} ${nom}</div>
        <div class="oc-infos">${o.auteur.filiere || '—'}${o.auteur.niveau ? ' · '+o.auteur.niveau : ''}</div>
      </div>
      <div class="oc-score">
        <span class="score-val ${scCls}">${score}%</span>
        <span class="score-lbl">match</span>
      </div>
    </div>

    <div class="oc-titre">${escHtml(o.titre)}</div>
    ${o.description ? `<div class="oc-desc">${escHtml(o.description)}</div>` : ''}

    ${tags ? `<div class="oc-tags">${tags}</div>` : ''}

    <div class="oc-places">
      <div class="places-bar">
        <div class="places-fill" style="width:${places_pct}%"></div>
      </div>
      <span>${o.places_restantes}/${o.max_places} place${o.max_places>1?'s':''}</span>
    </div>

    <div class="oc-actions">
      <button
        class="btn-postuler ${deja ? 'deja-postule' : ''}"
        onclick="openPostuler(${o.id})"
        ${deja ? 'disabled' : ''}
        id="btn-post-${o.id}"
      >${postulBtnLabel}</button>
    </div>
  </div>`;
}


// ═══════════════════════════════
//  RENDU — Mes publications
// ═══════════════════════════════

function renderMesPublications(pubs) {
  if (!mesPubsWrap) return;
  if (!pubs.length) {
    mesPubsWrap.innerHTML = `
      <div class="empty-ment">
        <span class="em-ico"><i class="fa-solid fa-file-circle-plus"></i></span>
        <h3>Aucune publication</h3>
        <p>Publiez une offre ou une demande de mentorat pour commencer.</p>
      </div>`;
    return;
  }
  mesPubsWrap.innerHTML = `<div class="mes-pubs-list">${pubs.map(pubCard).join('')}</div>`;
}

function pubCard(p) {
  const type_cls = p.type_publication === 'offre' ? 'type-offre' : 'type-demande';
  const type_lbl = p.type_publication === 'offre' ? 'Offre' : 'Demande';
  const candsPending = p.candidatures.filter(c => c.statut === 'en_attente');
  const candsAccepted = p.candidatures.filter(c => c.statut === 'acceptee');

  const btnFermer = p.statut === 'ouverte'
    ? `<button class="btn-fermer-pub" onclick="fermerPublication(${p.id})">Fermer</button>`
    : '';

  const candsHtml = p.candidatures.length
    ? p.candidatures.map(c => candidatureRow(c, p)).join('')
    : `<div class="no-cand"><i class="fa-regular fa-clock"></i> Aucune candidature reçue.</div>`;

  return `
  <div class="pub-card" id="pub-${p.id}">
    <div class="pub-card-head" onclick="toggleCands('pub-cands-${p.id}')">
      <span class="type-badge ${type_cls}">${type_lbl}</span>
      <div class="pub-titre-wrap">
        <div class="pub-titre">${escHtml(p.titre)}</div>
        <div class="pub-sub">${candsAccepted.length} acceptée(s) · ${candsPending.length} en attente</div>
      </div>
      <div class="pub-actions-head">
        <span class="pub-statut ${p.statut}">${p.statut}</span>
        ${btnFermer}
        <i class="fa-solid fa-chevron-down" style="color:var(--dim);font-size:.8rem"></i>
      </div>
    </div>
    <div class="pub-candidatures" id="pub-cands-${p.id}">
      ${candsHtml}
    </div>
  </div>`;
}

function candidatureRow(c, pub) {
  const prenom = c.candidat.prenom || '';
  const nom    = c.candidat.nom    || '';
  const init   = (prenom[0]||'').toUpperCase() + (nom[0]||'').toUpperCase();

  let btns = '';
  if (c.statut === 'en_attente') {
    btns = `
      <div class="cand-btns">
        <button class="btn-acc" onclick="repondreCand(${c.id}, 'accepter', ${pub.id})"><i class="fa-solid fa-check"></i> Accepter</button>
        <button class="btn-ref" onclick="repondreCand(${c.id}, 'refuser',  ${pub.id})"><i class="fa-solid fa-xmark"></i> Refuser</button>
      </div>`;
  } else {
    const badgeCls = c.statut === 'acceptee' ? 'acceptee' : 'refusee';
    const badgeLbl = c.statut === 'acceptee' ? '✓ Acceptée' : '✗ Refusée';
    btns = `<span class="cand-statut-badge ${badgeCls}">${badgeLbl}</span>`;
  }

  return `
  <div class="cand-row" id="cand-row-${c.id}">
    <div class="cand-ava">${init}</div>
    <div class="cand-info">
      <div class="cand-nom">${prenom} ${nom}</div>
      <div class="cand-msg">${c.message ? escHtml(c.message) : '<em>Pas de message</em>'}</div>
    </div>
    ${btns}
  </div>`;
}


// ═══════════════════════════════
//  ONGLETS & FILTRES
// ═══════════════════════════════

function setTab(tab) {
  activeTab = tab;
  // Activer le bon bouton
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tab);
  });
  // Afficher/masquer les sections
  const gridSection   = document.getElementById('section-grid');
  const mesPubSection = document.getElementById('section-mes');
  if (tab === 'mes') {
    gridSection   && (gridSection.style.display   = 'none');
    mesPubSection && (mesPubSection.style.display = 'block');
    loadMesPublications();
  } else {
    gridSection   && (gridSection.style.display   = 'block');
    mesPubSection && (mesPubSection.style.display = 'none');
    loadOffres();
  }
}

function applyFilter(type, val) {
  if (type === 'filiere')       filterFiliere = val;
  else if (type === 'niveau')   filterNiveau  = val;
  else if (type === 'comp')     filterComp    = val;
  if (activeTab !== 'mes') loadOffres();
}

function toggleCands(id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle('hidden');
}


// ═══════════════════════════════
//  MODALE — Publier
// ═══════════════════════════════

const pubModal = document.getElementById('modal-publier');

function openPublier() {
  pubModal && pubModal.classList.add('open');
}
function closePublier() {
  pubModal && pubModal.classList.remove('open');
  document.getElementById('form-publier') && document.getElementById('form-publier').reset();
}

async function submitPublier(e) {
  e.preventDefault();
  const form    = document.getElementById('form-publier');
  const btn     = document.getElementById('btn-submit-pub');
  const typeVal = document.querySelector('input[name="type_publication"]:checked');

  if (!typeVal) { showToast('Choisissez un type (Offre ou Demande).', 'error'); return; }

  const data = {
    type_publication: typeVal.value,
    titre:            form.titre.value.trim(),
    description:      form.description.value.trim(),
    competence_id:    form.competence_id.value || null,
    niveau_cible:     form.niveau_cible.value || null,
    filiere_cible:    form.filiere_cible.value || null,
    max_places:       parseInt(form.max_places.value) || 1
  };

  if (!data.titre) { showToast('Le titre est requis.', 'error'); return; }

  btn.disabled = true; btn.textContent = 'Publication…';
  try {
    const res = await fetch('/api/mentorat/offres', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.erreur || 'Erreur');
    showToast('Publication créée avec succès !', 'success');
    closePublier();
    setTab('mes');
  } catch(err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'Publier';
  }
}


// ═══════════════════════════════
//  MODALE — Postuler
// ═══════════════════════════════

const postModal   = document.getElementById('modal-postuler');
let currentOffre  = null;

function openPostuler(offreId) {
  currentOffre = offresData.find(o => o.id === offreId);
  if (!currentOffre) return;

  const info = document.getElementById('postul-info');
  if (info) {
    info.innerHTML = `Vous postulez pour : <strong>${escHtml(currentOffre.titre)}</strong>
      de <strong>${currentOffre.auteur.prenom} ${currentOffre.auteur.nom}</strong>.`;
  }
  const msgField = document.getElementById('postul-message');
  if (msgField) msgField.value = '';
  postModal && postModal.classList.add('open');
}

function closePostuler() {
  postModal && postModal.classList.remove('open');
  currentOffre = null;
}

async function submitPostuler(e) {
  e.preventDefault();
  if (!currentOffre) return;

  const btn = document.getElementById('btn-submit-post');
  const msg = document.getElementById('postul-message').value.trim();

  btn.disabled = true; btn.textContent = 'Envoi…';
  try {
    const res = await fetch(`/api/mentorat/offres/${currentOffre.id}/postuler`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.erreur || 'Erreur');

    showToast('Candidature envoyée !', 'success');
    closePostuler();

    // Mise à jour locale du bouton
    const btnPost = document.getElementById(`btn-post-${currentOffre.id}`);
    if (btnPost) {
      btnPost.innerHTML = '<i class="fa-solid fa-check"></i> Déjà postulé';
      btnPost.classList.add('deja-postule');
      btnPost.disabled = true;
    }
    // Mettre à jour les données locales
    const idx = offresData.findIndex(o => o.id === currentOffre.id);
    if (idx >= 0) offresData[idx].ma_candidature = json.candidature;

  } catch(err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'Envoyer ma candidature';
  }
}


// ═══════════════════════════════
//  ACTIONS SUR CANDIDATURES
// ═══════════════════════════════

async function repondreCand(candId, action, pubId) {
  try {
    const res  = await fetch(`/api/mentorat/candidatures/${candId}/repondre`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.erreur || 'Erreur');

    const label = action === 'accepter' ? 'Candidature acceptée !' : 'Candidature refusée.';
    showToast(label, action === 'accepter' ? 'success' : 'error');

    // Recharger les publications
    loadMesPublications();
  } catch(err) {
    showToast(err.message, 'error');
  }
}

async function fermerPublication(offreId) {
  if (!confirm('Fermer cette publication ? Elle ne sera plus visible.')) return;
  try {
    const res  = await fetch(`/api/mentorat/offres/${offreId}`, { method: 'DELETE' });
    const json = await res.json();
    if (!res.ok) throw new Error(json.erreur || 'Erreur');
    showToast('Publication fermée.', 'success');
    loadMesPublications();
  } catch(err) {
    showToast(err.message, 'error');
  }
}


// ═══════════════════════════════
//  UTILITAIRES
// ═══════════════════════════════

function showSpinner() {
  if (grid) grid.innerHTML = `
    <div class="ment-spinner">
      <div class="spinner-ring"></div> Chargement…
    </div>`;
}

function escHtml(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

let toastTimer = null;
function showToast(msg, type='success') {
  let toast = document.getElementById('ment-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'ment-toast';
    toast.className = 'ment-toast';
    document.body.appendChild(toast);
  }
  const icon = type === 'success'
    ? '<i class="fa-solid fa-circle-check"></i>'
    : '<i class="fa-solid fa-circle-xmark"></i>';
  toast.innerHTML = icon + ' ' + escHtml(msg);
  toast.className = `ment-toast ${type}`;
  requestAnimationFrame(() => toast.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
}

// Fermer modale en cliquant sur l'overlay
pubModal  && pubModal.addEventListener('click',  e => { if (e.target === pubModal)  closePublier(); });
postModal && postModal.addEventListener('click', e => { if (e.target === postModal) closePostuler(); });

// Init
setTab('offre');