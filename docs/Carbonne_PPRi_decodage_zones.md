# Décodage du règlement PPRi de Carbonne (31) pour REGLOVIZ

PPRN "Bassin versant de la Garonne moyenne", approuvé le 21 juin 2022, DDT Haute-Garonne, bureaux d'études ARTELIA et Alp'Géorisques. Document source : Reglement_Carbonne.pdf (65 pages).

Ce document synthétise, zone par zone, les obligations réglementaires applicables afin d'alimenter le modèle de données REGLOVIZ (régime de construction, seuils sur l'existant, zone refuge, diagnostic de vulnérabilité, éligibilité indicative Fonds Barnier), sur le même principe que ce qui a été fait pour Septèmes-les-Vallons.

## 1. Légende de la nomenclature des zones

Les codes de zone se construisent ainsi :

- 1ère lettre (majuscule) = couleur : R = rouge, B = bleu, G = gris
- 2ème lettre (majuscule, optionnelle) = trame : H = hachurée, F = foncée
- lettre(s) minuscule(s) = aléa : i = inondation, g = glissement de terrain, e = escarpement / effondrement de berge

Quand un code combine deux aléas (ex. Rig, Rie), les règlements des deux zones simples s'appliquent de façon cumulative, et la règle la plus restrictive prévaut en cas de contradiction.

13 codes présents dans le zonage de Carbonne, avec leur fréquence dans la couche "Zonage PPRN - Carbonne (clip commune)" (210 entités) :

| Code | Effectif | Signification |
|---|---|---|
| Ri | 16 | Rouge inondation (aléa fort) |
| RHi | 4 | Rouge hachurée inondation (urbanisation diffuse, aléa faible à moyen, ou remblais hors d'eau) |
| Bi | 8 | Bleue inondation (zone urbanisée, aléa faible à moyen) |
| GHi | 5 | Grise hachurée inondation (remblai hors d'eau, zone de crue historique) |
| Rig | 21 | Rouge inondation + rouge mouvement de terrain (cumul) |
| Rie | 25 | Rouge inondation + rouge escarpement/recul de berge (cumul) |
| Rg | 35 | Rouge mouvement de terrain, aléa fort glissement |
| Re | 20 | Rouge mouvement de terrain, aléa fort recul de berge/effondrement |
| RHg | 46 | Rouge hachurée mouvement de terrain (zone non urbanisée, aléa faible) |
| BFe | 11 | Bleue foncée mouvement de terrain, aléa moyen (secteur recul de berge) |
| BFg | 9 | Bleue foncée mouvement de terrain, aléa moyen (glissement) |
| Bg | 7 | Bleue mouvement de terrain, aléa faible |
| GHg | 3 | Grise hachurée glissement de terrain (zone d'aggravation potentielle) |

Rg et Re d'une part, BFe et BFg d'autre part, partagent le même règlement (seul le nom de la zone/aléa change) ; ils sont donc traités ensemble ci-dessous.

## 2. Tableau de synthèse par zone

| Code | Type de zone | Constructions nouvelles | Constructions existantes | Étude géotechnique G2 obligatoire | Niveau refuge | Régime |
|---|---|---|---|---|---|---|
| Ri | Rouge inondation, aléa fort, urbanisée ou non | Interdites (hors exceptions très limitées : accès sécurité, abris légers <20 m² une fois, locaux techniques agricoles, serres tunnel...) | Autorisées sous conditions strictes : extension limitée à 20 % une seule fois depuis le 06/02/2018, plancher au-dessus des PHEC, transparence/ombre hydraulique | Non (spécifique inondation, pas mouvement de terrain) | Oui, si impossibilité fonctionnelle de caler le plancher au-dessus des PHEC | Zone d'interdiction quasi-totale |
| RHi | Rouge hachurée inondation, urbanisation diffuse, aléa faible à moyen, ou remblais hors d'eau | Très limitées (mêmes types qu'en Ri : abris, locaux techniques, serres, bâtiments agricoles) | Autorisées sous conditions : extension 20 % une fois, plancher au-dessus des PHEC (refuge si impossibilité) | Non | Oui, si impossibilité fonctionnelle | Champ d'expansion des crues à préserver |
| Bi | Bleue inondation, zone urbanisée, aléa faible à moyen | Autorisées sous prescriptions (plancher au-dessus des PHEC, transparence hydraulique, matériaux les moins vulnérables) | Autorisées : extension jusqu'à 30 % du bâtiment existant (une fois depuis 06/02/2018) | Non | Oui, si impossibilité fonctionnelle (obligatoire sans dérogation pour établissements sensibles) | Zone constructible sous prescriptions |
| GHi | Grise hachurée inondation, remblai hors d'eau, zone de crue historique | Autorisées, non soumises au risque pour la crue centennale | Autorisées | Oui, spécifique remblai (étude géotechnique G2 AVP pour le dimensionnement des fondations) | Non mentionné | Zone de vigilance (précaution sur remblai, pas de restriction d'usage) |
| Rg / Re | Rouge mouvement de terrain, aléa fort glissement ou recul de berge, ou zone non urbanisée aléa moyen | Interdites, sauf travaux d'infrastructure publique (voirie, réseaux) et quelques exceptions mesurées (extension RDC <20 m² une fois, structures garage/annexe <20 m²) | Autorisées sous réserve : extension <20 m² une fois, pas de terrassement >0,5 m de dénivelé, pas d'aggravation | Oui, systématique (norme NF P 94-500, type G2 AVP), sauf liste d'exceptions (entretien courant, clôtures, abris <20 m² sans fondation) | Non mentionné (zone mouvement de terrain, pas de PHEC) | Zone d'interdiction, dérogations très encadrées |
| RHg | Rouge hachurée mouvement de terrain, zone non urbanisée, aléa faible | Interdiction spécifique : construction de bâtiments nouveaux à usage d'habitation | Autres occupations/aménagements autorisés sous étude géotechnique G2 ; extension RDC <50 m² une fois sans étude si dénivelé <0,5 m | Oui (sauf exceptions listées : entretien, clôtures, réseaux secs, abris <50 m²) | Non mentionné | Zone à risque faible mais non urbanisable pour l'habitat nouveau |
| BFe / BFg | Bleue foncée mouvement de terrain, zone urbanisée, aléa moyen | Interdites (seules les adaptations de l'existant sont possibles) | Autorisées : extension RDC <50 m² une fois, changement de destination/aménagement sans augmenter la capacité d'accueil | Oui (mêmes exceptions que RHg) | Non mentionné | Zone urbanisée mais non extensible (gel des nouvelles constructions) |
| Bg | Bleue mouvement de terrain, zone urbanisée ou non, aléa faible | Autorisées (aucune interdiction d'occupation du sol) | Autorisées | Oui, systématique (mêmes exceptions que RHg/BFe/BFg) | Non mentionné | Zone constructible sous étude géotechnique |
| GHg | Grise hachurée glissement de terrain, zone d'aggravation potentielle (plateau/amont de pentes sensibles) | Autorisées, prescriptions sur la gestion des eaux (pas de nouveaux rejets infiltrés, réseaux étanches) | Prescriptions identiques (maîtrise des rejets, étanchéité en cas de mise en charge) | Non (prescriptions hydrauliques, pas géotechniques) | Non mentionné | Zone sans restriction d'usage, prescriptions de gestion des eaux |
| Rig | Cumul Ri + Rg | Régime Ri (le plus restrictif) et étude géotechnique G2 en plus pour les rares travaux autorisés | Cumul des deux jeux de prescriptions, la plus restrictive prévaut | Oui, en plus du régime Ri | Oui (volet inondation) | Interdiction quasi-totale, double contrainte |
| Rie | Cumul Ri + Re | Régime Ri, plus interdiction des nouvelles voies en zone de recul de berge (sauf impossibilité technique) | Cumul des deux jeux de prescriptions | Oui, en plus du régime Ri | Oui (volet inondation) | Interdiction quasi-totale, double contrainte, possibilité de contester le tracé de la zone rouge effondrement par relevé de géomètre |

## 3. Règlement commun à toutes les zones inondables (Ri, RHi, Bi, GHi, Rig, Rie)

Les zones inondables partagent un socle réglementaire commun (chapitre "Règlement applicable à toutes les zones inondables", pages 1 à 20 du PDF) avant les dispositions propres à chaque zone : interdictions générales, prescriptions détaillées pour les aménagements et infrastructures, pour les utilisations du sol (dont stockage de matières dangereuses), pour les stations d'épuration, les aires d'accueil des gens du voyage et les centrales photovoltaïques au sol. Ce socle est systématiquement rappelé dans chaque règlement de zone inondable via la mention "se reporter à la partie Règlement applicable à toutes les zones inondables".

## 4. Mesures de prévention, de protection, de sauvegarde et recommandations (chapitre 4)

Ces mesures s'appliquent en complément du régime de construction, avec des délais réglementaires à compter de l'approbation du PPRN (06/02/2018 pour la prescription, 21/06/2022 pour l'approbation) :

- Plan Communal de Sauvegarde : obligatoire pour la commune dans un délai de 2 ans si elle n'en dispose pas, ou mise à jour dans un délai d'1 an si elle en dispose déjà.
- Diagnostic de vulnérabilité pour les établissements sensibles existants en zone inondable (enseignement, soin, santé, secours) : obligatoire dans un délai d'1 an à la charge du gestionnaire. Mise en œuvre des mesures définies dans un délai de 5 ans, mais uniquement pour les zones d'aléa fort et dans la limite de 10 % de la valeur vénale du bien (art. R562-5 du code de l'environnement).
- Mesures pour les biens et activités existants en zone inondable : mise hors d'eau des stockages de produits dangereux, dispositifs anti-dispersion, mise hors d'eau/étanchéité des équipements à fonctionnement autonome (délai 5 ans) ; balisage des piscines existantes (délai 2 ans) ; signalisation des aires de stationnement inondables (délai 6 mois).
- Réseaux publics : tampons verrouillés, postes électriques et équipements de télécommunication mis hors d'eau ou protégés (délai 2 ans).
- Zones de mouvement de terrain : évacuation directe des eaux pluviales vers un exutoire naturel et interdiction des dispositifs d'infiltration en zone rouge (délai 2 ans), entretien des systèmes de drainage en zones rouge et bleue.
- Information préventive : le maire informe la population au moins une fois tous les 2 ans (réunions publiques, affichage dans les ERP) sur les risques, l'alerte et la conduite à tenir.

## 5. Notions clés utiles au moteur de règles REGLOVIZ (annexe 2 et glossaire)

- PHEC : Plus Hautes Eaux Connues, correspondant à la crue de référence (en général la crue de 1875 pour la Garonne en Haute-Garonne).
- Premier plancher au-dessus des PHEC : règle par défaut sauf abris légers, garages et annexes n'accueillant pas de population permanente ; en l'absence d'isocote, des niveaux par défaut sont fixés par zone.
- Niveau refuge adapté : surface protégée accessible depuis l'intérieur et depuis l'extérieur pour les secours. Surface minimale 20 m² pour une habitation ; pour un ERP ou une activité, 20 m² + 6 m² + 1 m²/personne au-delà de 15 personnes de capacité. Hauteur minimale 1,80 m. Le refuge est attaché à chaque entité du bâtiment (un logement, un commerce) : il n'existe pas de zone refuge "collective".
- Impossibilité fonctionnelle : doit être justifiée par une notice explicative du pétitionnaire.
- Extension : mesurée, limitée à 30 % de la surface de plancher existante au sens du Conseil d'État ; distincte d'une annexe (construction secondaire, dimensions réduites, lien fonctionnel mais pas d'accès direct depuis la construction principale).
- Ombre hydraulique : continuité du bâti dans le sens de l'écoulement des eaux (en amont ou en aval), sans être forcément attenant.
- Sens d'écoulement des eaux : parallèle au lit majeur du cours d'eau en crue, ou perpendiculaire à la ligne d'isocote de référence.
- Dent creuse : parcelle non bâtie entourée de parcelles bâties ou de voirie à la date de prescription du PPRN (06/02/2018) ; une seule construction à usage d'habitation y est autorisée.
- Matériaux les moins vulnérables à l'eau : isolation insensible à l'eau, matériaux traités hydrofuges/anti-corrosifs, revêtements non sensibles à l'action de l'eau, sous la cote de référence.

## 6. Éligibilité indicative au Fonds Barnier (FPRNM)

Le règlement de Carbonne ne détaille pas de barème d'éligibilité au Fonds Barnier propre à la commune : il rappelle seulement (page 48, en référence à l'article R562-5 du code de l'environnement) que les travaux de prévention imposés à des biens construits conformément aux règles d'urbanisme avant l'approbation du PPRN ne peuvent porter que sur des aménagements dont le coût est inférieur à 10 % de la valeur vénale ou estimée du bien. C'est cette même règle nationale, déjà utilisée pour Septèmes, qui doit être reprise pour Carbonne : l'éligibilité affichée par REGLOVIZ reste une estimation indicative fondée sur le caractère "prescrit" (et non recommandé) de la mesure, le statut du bien (habitation ou usage mixte, ou petite entreprise de moins de 20 salariés) et le plafond des 10 %, et non sur une disposition spécifique au PPRi de Carbonne.

## 7. Points de vigilance pour l'adaptation du moteur de règles

- La logique "code = couleur + trame + aléa" est différente de celle de Septèmes (bleu foncé / bleu clair / orange / rouge / violet) : il faut un décodeur de code à deux ou trois caractères plutôt qu'une simple correspondance couleur-régime.
- Les codes combinés (Rig, Rie, et potentiellement d'autres combinaisons non présentes à Carbonne mais possibles ailleurs sur ce même PPRN Garonne moyenne) nécessitent une résolution par cumul des deux règlements simples, avec la règle du plus restrictif en cas de conflit : le moteur de règles doit donc pouvoir décomposer un code combiné en ses composantes avant d'appliquer les règles.
- L'étude géotechnique G2 (norme NF P 94-500) est une obligation transversale à toutes les zones mouvement de terrain (Rg, Re, RHg, BFe, BFg, Bg), avec une liste d'exceptions récurrente (entretien courant, clôtures, réseaux secs, petits abris sans fondation) qu'il est possible de factoriser dans le modèle plutôt que de la dupliquer zone par zone.
- Le niveau refuge n'est mentionné que dans les zones inondables (Ri, RHi, Bi et leurs combinaisons avec Rg/Re) ; il n'a pas de sens dans les zones mouvement de terrain pures.
- Le diagnostic de vulnérabilité obligatoire (délai 1 an) ne concerne que les établissements sensibles (enseignement, soin, santé, secours), pas l'ensemble des bâtiments d'habitation : à distinguer dans le modèle de données bâtiment (probablement via le champ usage_1/usage_2 de BD TOPO ou l'usage BDNB) plutôt que de l'appliquer uniformément par zone.

## 8. Prochaine étape suggérée

Traduire ce tableau en fichier de configuration structuré (JSON ou équivalent) sur le même schéma que celui utilisé pour Septèmes-les-Vallons, avec un champ "décodage du code de zone" en amont pour gérer les codes combinés. Cela permettra de brancher directement les 6 132 bâtiments enrichis (BD TOPO + BDNB) de Carbonne sur le moteur de règles REGLOVIZ une fois le zonage spatialement croisé avec la couche bâtiments.
