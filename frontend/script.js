function basculer(onglet) {
    // Cacher les deux sections
    document.getElementById('connexion').style.display = 'none';
    document.getElementById('inscription').style.display = 'none';
    
    // Afficher la section choisie
    document.getElementById(onglet).style.display = 'block';
    
    // Changer l'apparence des onglets
    const onglets = document.querySelectorAll('.onglet');
    onglets.forEach(function(btn) {
        btn.classList.remove('actif');
    });
    
    // Activer le bon onglet
    if (onglet === 'connexion') {
        onglets[0].classList.add('actif');
    } else {
        onglets[1].classList.add('actif');
    }
}

// Afficher le bon formulaire au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('connexion').style.display = 'block';
    document.getElementById('inscription').style.display = 'none';
});

function connecter() {
    const email = document.getElementById('email-connexion').value;
    const mdp = document.getElementById('mdp-connexion').value;
    
    if (!email || !mdp) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    // li sa au backend Django
    fetch('http://127.0.0.1:8001/api/connexion/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            mot_de_passe: mdp
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Connexion réussie ! Bonjour ' + data.user.prenom);
            // Rediriger vers la liste des utilisateurs
            window.location.href = 'utilisateurs.html';
        } else {
            alert('❌ ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('❌ Erreur : Vérifiez que Django est lancé sur le port 8001');
    });
}function inscrire() {
    const nom = document.getElementById('nom').value;
    const prenom = document.getElementById('prenom').value;
    const email = document.getElementById('email-inscription').value;
    const telephone = document.getElementById('telephone').value;
    const filiere = document.getElementById('filiere').value;
    const niveau = document.getElementById('niveau').value;
    const mdp = document.getElementById('mdp-inscription').value;
    const disponibilite = document.getElementById('disponibilite').value;
    const statut = document.getElementById('statut').value;
    
    if (!nom || !prenom || !email || !telephone || !filiere || !niveau || !mdp || !disponibilite || !statut) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    // Envoi au backend Django
    fetch('http://127.0.0.1:8001/api/inscription/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nom: nom,
            prenom: prenom,
            email: email,
            telephone: telephone,
            filiere: filiere,
            niveau: niveau,
            mot_de_passe: mdp,
            disponibilite: disponibilite,
            statut: statut
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Inscription réussie ! Vous pouvez vous connecter.');
            basculer('connexion');
            document.getElementById('email-connexion').value = email;
        } else {
            alert('❌ Erreur : ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('❌ Erreur : Vérifiez que Django est lancé sur le port 8001');
    });
}
