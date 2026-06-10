from django.db import models

class Utilisateur(models.Model):
    STATUT_CHOICES = [
        ('mentor', 'Mentor'),
        ('mentoree', 'Mentorée'),
        ('les-deux', 'Les deux'),
    ]
    
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    telephone = models.CharField(max_length=20)
    filiere = models.CharField(max_length=10)
    niveau = models.CharField(max_length=5)
    mot_de_passe = models.CharField(max_length=255)
    disponibilite = models.CharField(max_length=255)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    est_actif = models.BooleanField(default=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'utilisateurs'  # Nom exact de votre table dans MySQL
        
    def __str__(self):
        return f"{self.prenom} {self.nom}"