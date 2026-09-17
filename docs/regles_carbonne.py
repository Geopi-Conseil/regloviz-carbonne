"""
Moteur de règles PPRi/PPRN - Carbonne (31)

Traduit en code le décodage du règlement PPRN "Bassin versant de la Garonne
moyenne" (approuvé le 21/06/2022, DDT Haute-Garonne, ARTELIA / Alp'Géorisques)
livré dans Carbonne_PPRi_decodage_zones.md. Ce module est le pendant, pour
Carbonne, des champs qui pour Septèmes-les-Vallons sont pré-calculés en amont
de scripts/export_geojson.py (regime_pprin, diagnostic_vuln, zone_refuge,
refuge_categorie, obligations_typologie, eligibilite_fprnm...).

Différences structurelles avec Septèmes, à garder en tête (cf.
ADAPTATION_CARBONNE.md) :
  - le PPRN de Carbonne combine DEUX familles d'aléa (inondation ET
    mouvements de terrain), avec des codes de zone combinés (Rig, Rie) déjà
    présents tels quels comme valeurs de codezonere - on ne les reconstitue
    pas ici, on les reconnaît directement ;
  - la zone refuge n'est pas liée à un seuil de logements comme à Septèmes,
    mais à une clause d'« impossibilité fonctionnelle » d'implanter le
    plancher au-dessus des PHEC, laissée à l'appréciation du pétitionnaire
    et non déductible avec certitude des seules données BD TOPO/BDNB : le
    champ zoneRefuge reste donc ici une information CONDITIONNELLE
    ("si vous ne pouvez pas caler le plancher au-dessus des PHEC"), pas un
    verdict binaire ;
  - le diagnostic de vulnérabilité obligatoire ne concerne, dans le
    règlement de Carbonne, que les établissements sensibles (enseignement,
    soin, santé, secours) en zone inondable, pas l'ensemble du bâti : il
    dépend donc du champ is_erp / erp_type_principal, pas seulement de la
    zone ;
  - une étude géotechnique G2 (norme NF P 94-500) est exigée dans toutes les
    zones mouvement de terrain (sauf liste d'exceptions ponctuelles,
    entretien courant, clôtures, très petits abris) : ce n'existe pas côté
    Septèmes (PPRi inondation seul) et mérite un champ dédié plutôt que
    d'être noyé dans "regime".

Comme pour Septèmes (docs/METHODOLOGIE.md §8), ce module ne modélise que les
obligations relatives aux BIENS EXISTANTS (extensions, aménagements) ; les
règles applicables aux projets neufs (permis de construire sur terrain vierge)
ne sont pas modélisées ici, elles requièrent un projet précis. Toutes les
sorties sont indicatives et n'ont pas de valeur réglementaire opposable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional


# ---------------------------------------------------------------------------
# 1. Zones : ordre de contrainte, couleurs, libellés
# ---------------------------------------------------------------------------

# Du moins contraignant au plus contraignant. Sert à choisir la zone "à
# retenir" (zonePprin) quand un bâtiment intersecte plusieurs polygones de
# zone (chevauchement en limite de zonage), sur le même principe que
# Septèmes (docs/METHODOLOGIE.md §2) : on retient la zone la plus
# contraignante parmi celles touchées, en listant les autres dans
# zonesIntersectees à titre de traçabilité.
#
# Cet ordre combine deux familles d'aléa distinctes (inondation, mouvement
# de terrain) : il n'existe pas de hiérarchie officielle unique entre les
# deux dans le règlement, ce classement est un choix éditorial (sévérité de
# la restriction de construction), à faire valider par un technicien avant
# mise en production.
ZONE_ORDER = [
    "GHg",   # aggravation potentielle glissement, pas de restriction d'usage
    "GHi",   # remblai hors d'eau, pas de restriction d'usage
    "Bg",    # bleue mouvement de terrain, aléa faible, constructible sous étude G2
    "Bi",    # bleue inondation, aléa faible à moyen, constructible sous prescriptions
    "BFg",   # bleue foncée mouvement de terrain, aléa moyen, gel des constructions nouvelles
    "BFe",   # bleue foncée mouvement de terrain (recul de berge), idem
    "RHg",   # rouge hachurée mouvement de terrain, aléa faible, habitat nouveau interdit
    "RHi",   # rouge hachurée inondation, champ d'expansion des crues
    "Rg",    # rouge mouvement de terrain, aléa fort (glissement)
    "Re",    # rouge mouvement de terrain, aléa fort (recul de berge/effondrement)
    "Ri",    # rouge inondation, aléa fort
    "Rie",   # cumul Ri + Re
    "Rig",   # cumul Ri + Rg
]

ZONE_COLORS = {
    "Ri": "#E2001A",
    "Rig": "#B0001C",
    "Rie": "#C81E3A",
    "RHi": "#E2001A",  # même teinte que Ri, distinguée par la trame côté QGIS/print ; sur la webmap (couleur pleine, pas de hachure), on l'assombrit légèrement pour rester lisible
    "Rg": "#E2001A",
    "Re": "#D62839",
    "RHg": "#E2001A",
    "BFe": "#0033A0",
    "BFg": "#0033A0",
    "Bi": "#4FA8E0",
    "Bg": "#7EC8E3",
    "GHi": "#8A8A8A",
    "GHg": "#6E6E6E",
}

ZONE_SHORT_NAMES = {
    "Ri": "Rouge inondation",
    "Rig": "Rouge inondation + mouvement de terrain",
    "Rie": "Rouge inondation + recul de berge",
    "RHi": "Rouge hachurée inondation",
    "Rg": "Rouge mouvement de terrain (glissement)",
    "Re": "Rouge mouvement de terrain (recul de berge)",
    "RHg": "Rouge hachurée mouvement de terrain",
    "BFe": "Bleue foncée mouvement de terrain",
    "BFg": "Bleue foncée mouvement de terrain",
    "Bi": "Bleue inondation",
    "Bg": "Bleue mouvement de terrain",
    "GHi": "Grise hachurée inondation (remblai)",
    "GHg": "Grise hachurée (aggravation glissement)",
}

INONDATION_ZONES = {"Ri", "RHi", "Bi", "GHi", "Rig", "Rie"}
MOUVEMENT_TERRAIN_ZONES = {"Rg", "Re", "RHg", "BFe", "BFg", "Bg", "GHg", "Rig", "Rie"}
ZONES_ETUDE_G2_OBLIGATOIRE = {"Rg", "Re", "RHg", "BFe", "BFg", "Bg", "Rig", "Rie"}

# Étage : seuil de hauteur (m) utilisé en repli quand nombre_d_etages/
# bdnb_nb_niveau sont absents. Repris tel quel de la méthode Septèmes
# (docs/METHODOLOGIE.md §3) : calibré empiriquement sur un bâti comparable
# (maison individuelle méridionale), à recalibrer si le bâti de Carbonne
# s'avère significativement différent (à vérifier terrain, cf. limites).
SEUIL_HAUTEUR_ETAGE_M = 5.30

# Emprise au sol minimale (m²) pour considérer un seuil de travaux fiable
# (même valeur et même justification que Septèmes, docs/METHODOLOGIE.md §5).
SEUIL_EMPRISE_FIABLE_M2 = 10.0

# Lettres de type ERP (arrêté du 25/06/1980) correspondant à un
# établissement sensible au sens du règlement de Carbonne (enseignement,
# soin, santé, secours) - cf. Carbonne_PPRi_decodage_zones.md §7 et annexe 2
# du règlement ("établissements sensibles"). Liste indicative : R
# (enseignement), U (sanitaire), J (structures d'accueil pour personnes
# âgées/handicapées) ; à confirmer/affiner avec le service urbanisme, la
# nomenclature ERP ne recoupe pas exactement la notion réglementaire PPRi.
TYPES_ERP_SENSIBLES = {"R", "U", "J"}


# ---------------------------------------------------------------------------
# 2. Table des obligations par zone (issue de Carbonne_PPRi_decodage_zones.md)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ZoneRule:
    regime_construction_nouvelle: str
    regime_construction_existante: str
    etude_geotechnique_g2: bool
    zone_refuge_applicable: bool  # zone inondable où la clause PHEC/refuge existe
    zone_refuge_note: str = ""


ZONE_RULES: dict[str, ZoneRule] = {
    "Ri": ZoneRule(
        regime_construction_nouvelle=(
            "Interdites, sauf exceptions très limitées (accès de sécurité, "
            "abris légers <20 m² une fois, locaux techniques agricoles, "
            "serres tunnel...)."
        ),
        regime_construction_existante=(
            "Extension limitée à 20 % de l'emprise existante, une seule "
            "fois depuis le 06/02/2018, plancher au-dessus des PHEC."
        ),
        etude_geotechnique_g2=False,
        zone_refuge_applicable=True,
    ),
    "RHi": ZoneRule(
        regime_construction_nouvelle=(
            "Très limitées (abris, locaux techniques, serres, bâtiments "
            "agricoles) : champ d'expansion des crues à préserver."
        ),
        regime_construction_existante=(
            "Extension limitée à 20 % de l'emprise existante, une seule "
            "fois depuis le 06/02/2018, plancher au-dessus des PHEC."
        ),
        etude_geotechnique_g2=False,
        zone_refuge_applicable=True,
    ),
    "Bi": ZoneRule(
        regime_construction_nouvelle=(
            "Autorisées sous prescriptions (plancher au-dessus des PHEC, "
            "transparence hydraulique, matériaux les moins vulnérables)."
        ),
        regime_construction_existante=(
            "Extension jusqu'à 30 % de l'emprise existante, une seule fois "
            "depuis le 06/02/2018."
        ),
        etude_geotechnique_g2=False,
        zone_refuge_applicable=True,
    ),
    "GHi": ZoneRule(
        regime_construction_nouvelle=(
            "Autorisées : zone de remblai hors d'eau non soumise au risque "
            "pour la crue centennale."
        ),
        regime_construction_existante="Autorisées, sans restriction d'usage particulière.",
        etude_geotechnique_g2=False,  # étude géotechnique spécifique remblai (G2 AVP), pas la même obligation que mouvement de terrain "classique" ; voir note fondations dans obligations_typologie
        zone_refuge_applicable=False,
    ),
    "Rg": ZoneRule(
        regime_construction_nouvelle=(
            "Interdites, sauf travaux d'infrastructure publique et "
            "exceptions mesurées (extension RDC <20 m² une fois, structures "
            "garage/annexe <20 m²)."
        ),
        regime_construction_existante=(
            "Extension <20 m² une fois depuis le 06/02/2018, pas de "
            "terrassement créant un dénivelé >0,5 m."
        ),
        etude_geotechnique_g2=True,
        zone_refuge_applicable=False,
    ),
    "Re": ZoneRule(
        regime_construction_nouvelle=(
            "Interdites, sauf travaux d'infrastructure publique et "
            "exceptions mesurées (extension RDC <20 m² une fois, structures "
            "garage/annexe <20 m²)."
        ),
        regime_construction_existante=(
            "Extension <20 m² une fois depuis le 06/02/2018, pas de "
            "terrassement créant un dénivelé >0,5 m."
        ),
        etude_geotechnique_g2=True,
        zone_refuge_applicable=False,
    ),
    "RHg": ZoneRule(
        regime_construction_nouvelle="Construction de bâtiments nouveaux à usage d'habitation interdite.",
        regime_construction_existante=(
            "Extension RDC <50 m² une fois depuis le 06/02/2018 sans étude "
            "si dénivelé <0,5 m ; au-delà, étude géotechnique G2 requise."
        ),
        etude_geotechnique_g2=True,
        zone_refuge_applicable=False,
    ),
    "BFe": ZoneRule(
        regime_construction_nouvelle="Interdites (seules les adaptations de l'existant sont possibles).",
        regime_construction_existante=(
            "Extension RDC <50 m² une fois depuis le 06/02/2018, "
            "changement de destination/aménagement sans augmenter la "
            "capacité d'accueil."
        ),
        etude_geotechnique_g2=True,
        zone_refuge_applicable=False,
    ),
    "BFg": ZoneRule(
        regime_construction_nouvelle="Interdites (seules les adaptations de l'existant sont possibles).",
        regime_construction_existante=(
            "Extension RDC <50 m² une fois depuis le 06/02/2018, "
            "changement de destination/aménagement sans augmenter la "
            "capacité d'accueil."
        ),
        etude_geotechnique_g2=True,
        zone_refuge_applicable=False,
    ),
    "Bg": ZoneRule(
        regime_construction_nouvelle="Autorisées (aucune interdiction d'occupation du sol).",
        regime_construction_existante="Autorisées, sous réserve de l'étude géotechnique G2.",
        etude_geotechnique_g2=True,
        zone_refuge_applicable=False,
    ),
    "GHg": ZoneRule(
        regime_construction_nouvelle=(
            "Autorisées, sous prescriptions de gestion des eaux (pas de "
            "nouveaux rejets infiltrés, réseaux étanches)."
        ),
        regime_construction_existante=(
            "Prescriptions identiques : maîtrise des rejets, étanchéité en "
            "cas de mise en charge des réseaux."
        ),
        etude_geotechnique_g2=False,
        zone_refuge_applicable=False,
    ),
}

# Zones combinées : cumul des deux règlements simples, le plus restrictif
# prévalant en cas de conflit (légende du règlement). Le régime affiché est
# celui, déjà très restrictif, de la composante inondation (Ri), complété
# par l'exigence d'étude géotechnique de la composante mouvement de terrain.
ZONE_RULES["Rig"] = ZoneRule(
    regime_construction_nouvelle=(
        ZONE_RULES["Ri"].regime_construction_nouvelle
        + " Cumul avec le régime Rg : étude géotechnique G2 exigée en plus "
        "pour les rares travaux autorisés."
    ),
    regime_construction_existante=(
        ZONE_RULES["Ri"].regime_construction_existante
        + " Cumul avec les prescriptions Rg (étude géotechnique G2, pas de "
        "terrassement >0,5 m)."
    ),
    etude_geotechnique_g2=True,
    zone_refuge_applicable=True,
)
ZONE_RULES["Rie"] = ZoneRule(
    regime_construction_nouvelle=(
        ZONE_RULES["Ri"].regime_construction_nouvelle
        + " Cumul avec le régime Re : interdiction des voies nouvelles en "
        "zone de recul de berge sauf impossibilité technique ; étude "
        "géotechnique G2 exigée en plus pour les rares travaux autorisés."
    ),
    regime_construction_existante=(
        ZONE_RULES["Ri"].regime_construction_existante
        + " Cumul avec les prescriptions Re (étude géotechnique G2). Le "
        "tracé de la zone rouge effondrement peut être contesté par relevé "
        "de géomètre en crête de berge de la Garonne."
    ),
    etude_geotechnique_g2=True,
    zone_refuge_applicable=True,
)


# ---------------------------------------------------------------------------
# 3. Étage, typologie, emprise (même méthode que Septèmes, cf. docs/
#    METHODOLOGIE.md §3, adaptée aux noms de champs Carbonne)
# ---------------------------------------------------------------------------


def determine_etage(
    nombre_d_etages: Optional[int],
    bdnb_nb_niveau: Optional[int],
    hauteur_m: Optional[float],
) -> tuple[str, str]:
    """Retourne (etagePresent, etageSource). Voir docs/METHODOLOGIE.md §3
    pour la justification de la méthode et de ses limites (non reprises en
    détail ici, cf. ADAPTATION_CARBONNE.md)."""
    niveau = None
    source = None
    if bdnb_nb_niveau is not None:
        niveau = bdnb_nb_niveau
        source = f"connu (BDNB Fichiers Fonciers nb_niveau={bdnb_nb_niveau})"
    elif nombre_d_etages is not None:
        niveau = nombre_d_etages
        source = "connu (BD TOPO nombre_d_etages)"

    if niveau is not None:
        etage = "Oui" if niveau >= 2 else "Non"
        if etage == "Non" and hauteur_m is not None and hauteur_m > SEUIL_HAUTEUR_ETAGE_M:
            return (
                "Oui",
                f"étage retenu par prudence ({niveau} niveau(x) déclaré(s), "
                f"incohérent avec la hauteur mesurée {hauteur_m:.1f} m > "
                f"seuil {SEUIL_HAUTEUR_ETAGE_M:.2f} m)",
            )
        return etage, source

    if hauteur_m is not None:
        etage = "Oui" if hauteur_m > SEUIL_HAUTEUR_ETAGE_M else "Non"
        return etage, f"estimé par la hauteur du bâti ({hauteur_m:.1f} m), fiabilité modérée"

    return "Inconnu", "aucune donnée disponible"


def determine_typologie(
    usage_1: Optional[str],
    bdnb_usage_niveau_1: Optional[str],
    nombre_de_logements: Optional[int],
    bdnb_nb_log: Optional[int],
) -> tuple[str, Optional[str]]:
    """Retourne (typologieOccupation, typologieSource). Reprend les trois
    grandes catégories déjà utilisées pour Septèmes (docs/METHODOLOGIE.md
    §10) : Habitation / Activité économique / Annexe non habitée."""
    source = None
    usage = usage_1
    nb_log = nombre_de_logements

    if not usage or usage in ("Indifférencié", ""):
        if bdnb_usage_niveau_1:
            usage = bdnb_usage_niveau_1
            nb_log = bdnb_nb_log if bdnb_nb_log is not None else nombre_de_logements
            source = "BDNB (Fichiers Fonciers)"

    if not usage or usage in ("Indifférencié", ""):
        return "Typologie indéterminée (donnée absente ou non exploitable)", source

    usage_lower = usage.lower()
    if any(k in usage_lower for k in ["résidentiel", "residentiel", "habitation", "secondaire"]):
        if nb_log and nb_log > 1:
            return f"Logement collectif ({nb_log} logements)", source
        return "Maison individuelle", source
    if any(k in usage_lower for k in ["dépendance", "dependance", "annexe"]):
        return "Annexe (non habitée)", source
    return "Activité économique", source


def compute_emprise(aire_m2: float) -> tuple[float, str]:
    if aire_m2 < SEUIL_EMPRISE_FIABLE_M2:
        return round(aire_m2, 1), f"Non (emprise <{SEUIL_EMPRISE_FIABLE_M2:.0f} m², annexe/abri probable)"
    return round(aire_m2, 1), "Oui"


# ---------------------------------------------------------------------------
# 4. Zone refuge, diagnostic, éligibilité FPRNM
# ---------------------------------------------------------------------------


def compute_zone_refuge(zone_code: Optional[str]) -> tuple[str, str]:
    """Contrairement à Septèmes (seuil >2 logements, zone indifférente), la
    zone refuge de Carbonne est une clause conditionnelle : elle ne
    s'applique QUE si le pétitionnaire ne peut pas caler son plancher
    au-dessus des PHEC ("impossibilité fonctionnelle"), et seulement dans
    les zones inondables. On ne peut pas trancher cette impossibilité
    depuis les seules données BD TOPO/BDNB : le champ reste donc une
    information conditionnelle, pas un verdict."""
    if not zone_code or zone_code not in INONDATION_ZONES:
        return (
            "Non applicable (zone hors risque inondation).",
            "Non applicable",
        )
    return (
        "Conditionnelle : si le plancher ne peut pas être calé au-dessus "
        "des PHEC (impossibilité fonctionnelle dûment justifiée), un "
        "niveau refuge adapté est exigé (20 m² minimum pour une "
        "habitation, hauteur 1,80 m minimum, un refuge par logement/local, "
        "pas de refuge \"collectif\").",
        "Conditionnelle (impossibilité fonctionnelle à justifier)",
    )


def compute_diagnostic(zone_code: Optional[str], is_erp: bool, erp_types: Iterable[str]) -> str:
    """Le diagnostic de vulnérabilité obligatoire (délai 1 an après
    approbation, 06/2022) ne concerne, dans le règlement de Carbonne, que
    les établissements sensibles (enseignement, soin, santé, secours) en
    zone inondable - pas l'ensemble du bâti, à la différence de Septèmes où
    un auto-diagnostic est simplement recommandé pour toute habitation."""
    if not zone_code or zone_code not in INONDATION_ZONES:
        return "Non concerné (hors zone inondable)."
    if is_erp and set(erp_types) & TYPES_ERP_SENSIBLES:
        return (
            "OBLIGATOIRE (établissement sensible en zone inondable, art. "
            "4.2 du règlement) : étude de vulnérabilité dans un délai d'un "
            "an, mesures mises en œuvre sous 5 ans si aléa fort, dans la "
            "limite de 10 % de la valeur vénale du bien (art. R562-5 du "
            "code de l'environnement)."
        )
    if is_erp:
        return (
            "Non explicitement obligatoire pour ce type d'ERP (à vérifier "
            "sur site) ; auto-diagnostic de vulnérabilité recommandé."
        )
    return "Non obligatoire pour l'habitat ; auto-diagnostic de vulnérabilité recommandé (à la charge du propriétaire)."


def compute_eligibilite_fprnm(typologie: str) -> str:
    """Reprend la même règle nationale, déjà utilisée pour Septèmes
    (docs/METHODOLOGIE.md §6), le règlement de Carbonne ne fixant rien de
    spécifique à ce sujet (cf. Carbonne_PPRi_decodage_zones.md §6).
    Indicatif uniquement, sous réserve d'un bien existant avant
    l'approbation du PPRN (21/06/2022) et d'instruction par la DDT."""
    t = typologie.lower()
    if "maison individuelle" in t or "logement collectif" in t:
        return (
            "Éligible - habitation : Fonds Barnier (FPRNM) à 80 % des "
            "travaux de prévention prescrits par le PPRN, plafond légal "
            "national, sous réserve d'un bien existant avant le 21/06/2022."
        )
    if "activité économique" in t:
        return (
            "Potentiellement éligible - activité : Fonds Barnier (FPRNM) à "
            "20 % des travaux prescrits si moins de 20 salariés (effectif "
            "non déductible des données géographiques, à vérifier), sous "
            "réserve d'un bien existant avant le 21/06/2022."
        )
    return "Non déterminé - typologie non qualifiée en l'état, à vérifier sur site."


# ---------------------------------------------------------------------------
# 5. Sélection de la zone la plus contraignante
# ---------------------------------------------------------------------------


def pick_most_restrictive_zone(zone_codes: Iterable[str]) -> Optional[str]:
    codes = [c for c in zone_codes if c]
    if not codes:
        return None
    return max(codes, key=lambda c: ZONE_ORDER.index(c) if c in ZONE_ORDER else -1)


# ---------------------------------------------------------------------------
# 6. Point d'entrée : calcule l'ensemble des champs pour un bâtiment
# ---------------------------------------------------------------------------


@dataclass
class BuildingInput:
    zone_codes: list[str] = field(default_factory=list)  # zones intersectées par le bâtiment (codezonere)
    emprise_sol_m2: float = 0.0
    nombre_d_etages: Optional[int] = None
    bdnb_nb_niveau: Optional[int] = None
    hauteur_m: Optional[float] = None
    usage_1: Optional[str] = None
    bdnb_usage_niveau_1: Optional[str] = None
    nombre_de_logements: Optional[int] = None
    bdnb_nb_log: Optional[int] = None
    is_erp: bool = False
    erp_type_principal: list[str] = field(default_factory=list)  # ex. ["M"], ["R", "U"]...


def compute_obligations(b: BuildingInput) -> dict:
    zone_code = pick_most_restrictive_zone(b.zone_codes)
    zones_intersectees = ";".join(sorted(set(b.zone_codes))) if b.zone_codes else None

    if zone_code is None:
        return {
            "zonePprin": None,
            "zoneLabel": "Hors zonage réglementaire PPRN",
            "zoneColor": None,
            "concerne": False,
        }

    rule = ZONE_RULES[zone_code]
    etage_present, etage_source = determine_etage(b.nombre_d_etages, b.bdnb_nb_niveau, b.hauteur_m)
    typologie, typologie_source = determine_typologie(
        b.usage_1, b.bdnb_usage_niveau_1, b.nombre_de_logements, b.bdnb_nb_log
    )
    emprise, emprise_fiable = compute_emprise(b.emprise_sol_m2)
    zone_refuge, refuge_categorie = compute_zone_refuge(zone_code)
    diagnostic = compute_diagnostic(zone_code, b.is_erp, b.erp_type_principal)
    eligibilite = compute_eligibilite_fprnm(typologie)

    out = {
        "zonePprin": zone_code,
        "zoneLabel": ZONE_SHORT_NAMES.get(zone_code, zone_code),
        "zoneColor": ZONE_COLORS.get(zone_code, "#9E9E9E"),
        "concerne": True,
        "zonesIntersectees": zones_intersectees,
        "regimeConstructionNouvelle": rule.regime_construction_nouvelle,
        "regimeConstructionExistante": rule.regime_construction_existante,
        "etudeGeotechniqueG2": rule.etude_geotechnique_g2,
        "etagePresent": etage_present,
        "etageSource": etage_source,
        "typologie": typologie,
        "typologieSource": typologie_source,
        "empriseSolM2": emprise,
        "empriseFiable": emprise_fiable,
        "zoneRefuge": zone_refuge,
        "refugeCategorie": refuge_categorie,
        "diagnostic": diagnostic,
        "eligibiliteFprnm": eligibilite,
    }
    return {k: v for k, v in out.items() if v is not None}


# ---------------------------------------------------------------------------
# 7. Auto-test minimal (exécuter : python3 regles_carbonne.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cases = [
        BuildingInput(zone_codes=[], emprise_sol_m2=80),
        BuildingInput(
            zone_codes=["Ri"],
            emprise_sol_m2=95,
            nombre_d_etages=1,
            hauteur_m=4.2,
            usage_1="Résidentiel",
            nombre_de_logements=1,
        ),
        BuildingInput(
            zone_codes=["Ri", "RHg"],
            emprise_sol_m2=210,
            nombre_d_etages=2,
            usage_1="Indifférencié",
            bdnb_usage_niveau_1="Résidentiel collectif",
            bdnb_nb_log=6,
            bdnb_nb_niveau=2,
        ),
        BuildingInput(
            zone_codes=["Bi"],
            emprise_sol_m2=340,
            usage_1="Commercial et services",
            is_erp=True,
            erp_type_principal=["M"],
        ),
        BuildingInput(
            zone_codes=["Bi"],
            emprise_sol_m2=420,
            usage_1="Enseignement",
            is_erp=True,
            erp_type_principal=["R"],
        ),
        BuildingInput(zone_codes=["Bg"], emprise_sol_m2=150, hauteur_m=6.1),
        BuildingInput(zone_codes=["GHg"], emprise_sol_m2=6, hauteur_m=2.5),
    ]
    for i, c in enumerate(cases, 1):
        print(f"--- cas {i} ---")
        for k, v in compute_obligations(c).items():
            print(f"  {k}: {v}")
        print()
