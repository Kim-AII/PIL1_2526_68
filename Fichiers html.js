// edit_profile.js - Logique de l'application de Matching

/* ─── DONNÉES STATIQUES ─── */
const MATIERES = [
    "Algorithmique", "Structures de données", "Base de données",
    "Réseaux", "Statistiques", "Analyse", "Algèbre",
    "Python", "Java", "Développement Web", "Cybersécurité", "Machine Learning"
];

const DISPOS = [
    "Lundi Matin", "Lundi Aprem", "Mardi Matin", "Mardi Soir",
    "Mercredi Aprem", "Jeudi Matin", "Vendredi Matin", "Samedi Matin"
];

const MENTORS = [
    { id: 1, nom: "Amara Touré", filiere: "Informatique", initiales: "AT", matieres_maitrisees: ["Algorithmique", "Structures de données", "Python", "Base de données"], disponibilites: ["Lundi Matin", "Mercredi Aprem", "Samedi Matin"], note: 4.8, couleur: "#2563eb" },
    { id: 2, filiere: "IA", nom: "Fatou Diallo", initiales: "FD", matieres_maitrisees: ["Statistiques", "Analyse", "Algèbre", "Machine Learning"], disponibilites: ["Mardi Matin", "Mardi Soir", "Jeudi Matin"], note: 4.6, couleur: "#8b5cf6" },
    { id: 3, filiere: "Réseaux", nom: "Kwame Asante", initiales: "KA", matieres_maitrisees: ["Réseaux", "Base de données", "Cybersécurité", "Python"], disponibilites: ["Lundi Matin", "Lundi Aprem", "Vendredi Matin"], note: 4.4, couleur: "#10b981" },
    { id: 4, filiere: "Informatique", nom: "Léa Konan", initiales: "LK", matieres_maitrisees: ["Développement Web", "Java", "Analyse", "Statistiques"], disponibilites: ["Mardi Soir", "Mercredi Aprem", "Samedi Matin"], note: 4.7, couleur: "#f59e0b" },
    { id: 5, filiere: "Sécurité", nom: "Cheikh Ndiaye", initiales: "CN", matieres_maitrisees: ["Cybersécurité", "Réseaux", "Statistiques", "Algèbre"], disponibilites: ["Lundi Aprem", "Jeudi Matin", "Vendredi Matin"], note: 4.5, couleur: "#0ea5e9" }
];

/* ─── INITIALISATION DU DOM ─── */
document.addEventListener('DOMContentLoaded', () => {
    
    // Remplir les matières
    const lacGrid = document.getElementById('lacunes-grid');
    if(lacGrid) {
        MATIERES.forEach(m => {
            lacGrid.innerHTML += `
                <div class="col-md-6 col-lg-4">
                    <label class="checkbox-card w-100">
                        <input type="checkbox" name="lacune" value="${m}">
                        <span class="cb-box"><span class="material-symbols-outlined" style="font-size: 14px;">check</span></span>
                        <span class="cb-label">${m}</span>
                    </label>
                </div>`;
        });
    }

    // Remplir les disponibilités
    const disGrid = document.getElementById('dispos-grid');
    if(disGrid) {
        DISPOS.forEach(d => {
            disGrid.innerHTML += `
                <label class="chip-btn" onclick="toggleChip(this)">
                    <input type="checkbox" name="dispo" value="${d}">
                    <span class="material-symbols-outlined me-1 fs-6">schedule</span> ${d}
                </label>`;
        });
    }
});

function toggleChip(el) {
    setTimeout(() => {
        const cb = el.querySelector('input');
        el.classList.toggle('selected', cb.checked);
    }, 10);
}

/* ─── ALGORITHME DE MATCHING ─── */
function computeMatches(student) {
    const results = [];

    MENTORS.forEach(mentor => {
        const communMatieres = mentor.matieres_maitrisees.filter(m => student.lacunes.includes(m));
        if (communMatieres.length === 0) return; // Le mentor ne maitrise aucune lacune de l'étudiant = on l'élimine

        let score = communMatieres.length * 10;
        if (mentor.filiere === student.filiere) score += 5;

        const communDispos = mentor.disponibilites.filter(d => student.disponibilites.includes(d));
        score += communDispos.length * 2;

        results.push({ ...mentor, score, communMatieres, communDispos });
    });

    // Trier du meilleur score au plus faible
    results.sort((a, b) => b.score - a.score);
    return results;
}

/* ─── GESTION DU FORMULAIRE ─── */
function handleSubmit() {
    const name = document.getElementById('name').value.trim();
    const filiere = document.getElementById('filiere').value;
    const lacunes = [...document.querySelectorAll('input[name="lacune"]:checked')].map(c => c.value);
    const dispos = [...document.querySelectorAll('input[name="dispo"]:checked')].map(c => c.value);

    // Validation des champs
    if (!name || !filiere || lacunes.length === 0 || dispos.length === 0) {
        alert("Veuillez remplir votre nom, filière, et sélectionner au moins une matière et un créneau.");
        return;
    }

    const student = { name, filiere, lacunes, disponibilites: dispos };

    // Mettre à jour l'indicateur d'étapes
    document.getElementById('step-1').classList.replace('active', 'done');
    document.getElementById('step-2').classList.add('active');

    // Masquer le formulaire et afficher le chargement
    document.getElementById('form-section').classList.add('d-none');
    document.getElementById('loading-section').classList.remove('d-none');

    // Reset l'animation de la barre de progression
    const fill = document.getElementById('progress-fill');
    fill.style.animation = 'none';
    fill.offsetHeight; // trigger reflow
    fill.style.animation = '';

    // Lancer le matching après un délai (pour simuler la réflexion de l'IA)
    setTimeout(() => {
        document.getElementById('loading-section').classList.add('d-none');
        document.getElementById('step-2').classList.replace('active', 'done');
        document.getElementById('step-3').classList.add('active');
        
        displayResults(student, computeMatches(student));
    }, 1800);
}

/* ─── AFFICHAGE DES RÉSULTATS ─── */
function displayResults(student, matches) {
    document.getElementById('results-section').classList.remove('d-none');
    
    document.getElementById('student-recap').innerHTML = 
        `<span class="material-symbols-outlined align-middle me-1 fs-6">verified</span> 
        ${student.name} · ${student.filiere} · ${student.lacunes.length} besoin(s) · ${student.disponibilites.length} créneau(x)`;

    const grid = document.getElementById('cards-grid');
    grid.innerHTML = '';

    if (matches.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center py-5">
                <span class="material-symbols-outlined text-muted" style="font-size: 64px;">search_off</span>
                <h4 class="fw-bold mt-3">Aucun mentor compatible</h4>
                <p class="text-muted">Essayez d'ajouter d'autres créneaux de disponibilité.</p>
            </div>`;
        return;
    }

    const maxScore = matches[0].score;

    matches.forEach((m, i) => {
        const pct = Math.round((m.score / (maxScore * 1.05)) * 100);
        const angle = Math.round(pct / 100 * 360);
        const isTop = i === 0;

        const badgeTop = isTop ? `<span class="badge bg-warning text-dark ms-2"><span class="material-symbols-outlined align-middle fs-6">star</span> Top Match</span>` : '';
        const sameFiliere = m.filiere === student.filiere ? `<span class="text-success small fw-bold ms-2">+ Bonus Filière</span>` : '';

        const matTags = m.communMatieres.map(t => `<span class="badge-tag tag-match me-1 mb-1 d-inline-block">${t}</span>`).join('');
        const disTags = m.communDispos.length > 0 
            ? m.communDispos.map(t => `<span class="badge-tag tag-time me-1 mb-1 d-inline-block">${t}</span>`).join('') 
            : `<span class="small text-muted">Aucun créneau commun exact</span>`;

        grid.innerHTML += `
            <div class="col-md-6 col-lg-12">
                <div class="mentor-card ${isTop ? 'top-match' : ''}">
                    <div class="row align-items-center">
                        <div class="col-auto text-center mb-3 mb-lg-0">
                            <div class="mentor-avatar mx-auto" style="background-color: ${m.couleur};">
                                ${m.initiales}
                                <div class="rank-badge">${i + 1}</div>
                            </div>
                        </div>
                        
                        <div class="col">
                            <div class="d-flex align-items-center mb-1">
                                <h4 class="h5 fw-bold mb-0 text-dark">${m.nom}</h4>
                                ${badgeTop}
                            </div>
                            <p class="text-muted small mb-2 d-flex align-items-center">
                                <span class="material-symbols-outlined fs-6 me-1">school</span> ${m.filiere} ${sameFiliere}
                                <span class="ms-3 text-warning fw-bold d-flex align-items-center"><span class="material-symbols-outlined fs-6 me-1">star</span> ${m.note}/5</span>
                            </p>
                            
                            <div class="row g-2 mt-2">
                                <div class="col-lg-6">
                                    <div class="small fw-bold text-muted text-uppercase mb-1">Matières partagées</div>
                                    <div>${matTags}</div>
                                </div>
                                <div class="col-lg-6">
                                    <div class="small fw-bold text-muted text-uppercase mb-1">Créneaux partagés</div>
                                    <div>${disTags}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-lg-auto mt-3 mt-lg-0 text-center border-start border-outline-variant d-none d-lg-block ps-4">
                            <div class="score-circle mx-auto mb-1" style="--pct:${angle}deg">
                                <span class="score-value">${m.score}</span>
                            </div>
                            <span class="small fw-bold text-muted text-uppercase">Score IA</span>
                        </div>
                    </div>
                </div>
            </div>`;
    });
}

/* ─── RETOUR AU FORMULAIRE ─── */
function resetForm() {
    document.getElementById('results-section').classList.add('d-none');
    document.getElementById('form-section').classList.remove('d-none');
    
    document.getElementById('step-3').classList.remove('active', 'done');
    document.getElementById('step-2').classList.remove('active', 'done');
    document.getElementById('step-1').classList.add('active');
    document.getElementById('step-1').classList.remove('done');
}