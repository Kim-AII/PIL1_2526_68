from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import Utilisateur
import json

@csrf_exempt
def api_inscription(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Vérifier si l'email existe déjà
            if Utilisateur.objects.filter(email=data['email']).exists():
                return JsonResponse({'success': False, 'message': 'Email déjà utilisé'})
            
            # Créer l'utilisateur
            utilisateur = Utilisateur(
                nom=data['nom'],
                prenom=data['prenom'],
                email=data['email'],
                telephone=data['telephone'],
                filiere=data['filiere'],
                niveau=data['niveau'],
                mot_de_passe=make_password(data['mot_de_passe']),
                disponibilite=data['disponibilite'],
                statut=data['statut']
            )
            utilisateur.save()
            
            return JsonResponse({'success': True, 'message': 'Inscription réussie'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@csrf_exempt
def api_connexion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            mot_de_passe = data.get('mot_de_passe')
            
            try:
                utilisateur = Utilisateur.objects.get(email=email)
                if check_password(mot_de_passe, utilisateur.mot_de_passe):
                    return JsonResponse({
                        'success': True, 
                        'message': 'Connexion réussie',
                        'user': {
                            'id': utilisateur.id,
                            'nom': utilisateur.nom,
                            'prenom': utilisateur.prenom,
                            'email': utilisateur.email
                        }
                    })
                else:
                    return JsonResponse({'success': False, 'message': 'Mot de passe incorrect'})
            except Utilisateur.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Email non trouvé'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

def api_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all().values('id', 'nom', 'prenom', 'email', 'statut')
    return JsonResponse({'utilisateurs': list(utilisateurs)})