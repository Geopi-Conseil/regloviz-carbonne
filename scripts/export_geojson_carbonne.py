"""
Export des donnees QGIS vers les GeoJSON utilises par la webmap - Carbonne.

Adaptation directe de scripts/export_geojson.py (Septemes) : meme structure,
mais lit les couches enrichies du projet Carbonne et TRADUIT les champs
snake_case ecrits par le moteur de regles (adaptation_carbonne/
regles_carbonne.py, applique via le projet QGIS) vers le meme schema
camelCase que celui deja consomme par src/js/app.js (zoneCode, zoneLabel,
zoneColor, regime, diagnostic, zoneRefuge, refugeCategorie, eligibiliteFprnm,
typologie, typologieSource, etagePresent, etageSource, nbLogements,
hauteurM, id...).

Choix retenu (a valider avec l'equipe avant mise en prod) : plutot que
d'adapter tout app.js a un nouveau nommage par commune, on garde app.js
INCHANGE (a l'exception de CONFIG : center, codeInsee, zoneOrder,
zoneShortNames, zoneColors) et c'est ce script d'export qui absorbe toute
la traduction de schema, exactement dans l'esprit de la section
"Reproduire pour une autre commune" de docs/METHODOLOGIE.md (etape 6 :
"Adapter scripts/export_geojson.py ... Mettre a jour CONFIG ... dans
src/js/app.js" - rien d'autre). Consequence directe : si vous adoptez ce
choix, le fichier adaptation_carbonne/correction_block_carbonne.js doit etre
remplace par adaptation_carbonne/correction_block_carbonne_camelcase.js
(meme dossier), qui suppose ce schema camelCase plutot que le schema
snake_case brut issu de QGIS.

Deux differences de contenu avec Septemes, a garder en tete :
  - Carbonne a DEUX textes de regime distincts (constructions nouvelles /
    constructions existantes) la ou Septemes n'en a qu'un seul (regime) :
    on les combine ici en un seul champ `regime` pour rester compatible
    avec renderBuildingPanel() sans le modifier. Le detail des deux volets
    reste consultable dans les "Details techniques" via zonesIntersectees
    et, si besoin plus tard, en exposant deux champs supplementaires.
  - l'obligation d'etude geotechnique G2 (zones mouvement de terrain,
    absente a Septemes) est repercutee comme une phrase supplementaire dans
    `regime` (pour rester visible sans toucher app.js) ET comme un champ
    brut `etudeGeotechniqueG2` (bool), disponible pour un futur usage
    (ex. tuile de tableau de bord dediee).

A executer dans la console Python de QGIS, projet carbonne_ppri.qgz charge,
de preference via le bouton "Executer le script" de l'editeur Python (fichier
.py ouvert depuis scripts/export_geojson_carbonne.py dans le depot Carbonne) :
OUTPUT_DIR se deduit alors automatiquement du dossier data/ voisin. Un repli
sur un chemin connu en dur est prevu si le script est colle directement dans
la console interactive plutot qu'execute depuis un fichier (voir _here
ci-dessous, a adapter si le dossier du depot venait a changer).
"""

import json
import os

from qgis.core import (
    NULL,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsProject,
    QgsSpatialIndex,
)

# ---------------------------------------------------------------------------
# Configuration : adapter les noms de couches / chemin de sortie si besoin
# ---------------------------------------------------------------------------

LAYER_BATI = "Batiments BD TOPO - Carbonne (clip commune, enrichi BDNB)"
LAYER_ZONAGE = "Zonage PPRN - Carbonne (clip commune)"
LAYER_ERP = "ERP BD TOPO - Carbonne (clip commune, rattaches batiment)"

# __file__ n'existe que si ce script est execute via le bouton "Executer le
# script" de l'editeur Python de QGIS (fichier .py ouvert depuis le disque).
# Si vous collez son contenu directement dans la console Python interactive,
# __file__ n'est pas defini : on retombe alors sur le chemin connu du depot
# Carbonne. Adaptez cette ligne si le dossier venait a changer.
try:
    _here = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _here = r"C:\Users\33632\Desktop\GEOPI\PROJETS_WEB\PPRI_WEB\PAPI-AGGLO-TOULOUSE\CARBONNE\depot-git\scripts"

OUTPUT_DIR = os.path.join(_here, "..", "data")

# Repris de regles_carbonne.py (ZONE_COLORS / ZONE_SHORT_NAMES) : a garder
# strictement synchronise avec ce module si l'un des deux evolue.
ZONE_COLORS = {
    "Ri": "#E2001A", "Rig": "#B0001C", "Rie": "#C81E3A", "RHi": "#E2001A",
    "Rg": "#E2001A", "Re": "#D62839", "RHg": "#E2001A", "BFe": "#0033A0",
    "BFg": "#0033A0", "Bi": "#4FA8E0", "Bg": "#7EC8E3", "GHi": "#8A8A8A",
    "GHg": "#6E6E6E",
}
ZONE_LABELS = {
    "Ri": "Rouge inondation", "Rig": "Rouge inondation + mouvement de terrain",
    "Rie": "Rouge inondation + recul de berge", "RHi": "Rouge hachurée inondation",
    "Rg": "Rouge mouvement de terrain (glissement)", "Re": "Rouge mouvement de terrain (recul de berge)",
    "RHg": "Rouge hachurée mouvement de terrain", "BFe": "Bleue foncée mouvement de terrain",
    "BFg": "Bleue foncée mouvement de terrain", "Bi": "Bleue inondation",
    "Bg": "Bleue mouvement de terrain", "GHi": "Grise hachurée inondation (remblai)",
    "GHg": "Grise hachurée (aggravation glissement)",
}
INONDATION_ZONES = {"Ri", "RHi", "Bi", "GHi", "Rig", "Rie"}
TYPES_ERP_SENSIBLES = {"R", "U", "J"}

# ---------------------------------------------------------------------------

proj = QgsProject.instance()
_tr = QgsCoordinateTransform(
    QgsCoordinateReferenceSystem("EPSG:2154"),
    QgsCoordinateReferenceSystem("EPSG:4326"),
    proj,
)


def clean(v):
    return None if (v is None or v == NULL or v == "") else v


def geom_to_geojson(geom, ndigits=6, simplify_tol=None):
    g = QgsGeometry(geom)
    if simplify_tol:
        g = g.simplify(simplify_tol)
    g.transform(_tr)
    gj = json.loads(g.asJson())

    def round_coords(c):
        if isinstance(c[0], list):
            return [round_coords(x) for x in c]
        return [round(c[0], ndigits), round(c[1], ndigits)]

    gj["coordinates"] = round_coords(gj["coordinates"])
    return gj


def find_layer(name):
    matches = [l for l in proj.mapLayers().values() if l.name() == name]
    if not matches:
        raise RuntimeError(f"Couche introuvable : {name}")
    return matches[0]


def write_geojson(path, features):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(
            {"type": "FeatureCollection", "features": features},
            fh,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    print(f"  -> {path} ({len(features)} entites, {os.path.getsize(path)/1e6:.2f} Mo)")


def build_regime_text(f):
    """Combine les deux volets du reglement (nouvelles/existantes) et la
    mention d'etude geotechnique G2 en un seul texte, pour rester
    compatible avec renderBuildingPanel() de app.js (champ unique
    `regime`)."""
    parts = []
    nouv = clean(f["regime_construction_nouvelle"])
    exist = clean(f["regime_construction_existante"])
    if nouv:
        parts.append(f"Constructions nouvelles : {nouv}")
    if exist:
        parts.append(f"Constructions existantes : {exist}")
    if f["etude_geotechnique_g2"] in (True, "True", "true", 1):
        parts.append(
            "Étude géotechnique G2 (norme NF P 94-500) obligatoire avant travaux, "
            "sauf exceptions ponctuelles prévues par le règlement."
        )
    return " ".join(parts) if parts else None


def export_bati():
    lyr = find_layer(LAYER_BATI)
    feats_zone, feats_hors = [], []
    for f in lyr.getFeatures():
        zone_code = clean(f["zone_pprn"])
        if zone_code is None:
            geom = geom_to_geojson(f.geometry(), ndigits=5, simplify_tol=0.5)
            feats_hors.append(
                {"type": "Feature", "geometry": geom, "properties": {"id": clean(f["cleabs"])}}
            )
            continue

        geom = geom_to_geojson(f.geometry(), ndigits=6, simplify_tol=0.15)
        props = {
            "id": clean(f["cleabs"]),
            "zoneCode": zone_code,
            "zoneLabel": clean(f["zone_pprn_label"]),
            "zoneColor": clean(f["zone_pprn_color"]),
            "concerne": True,
            "regime": build_regime_text(f),
            "etudeGeotechniqueG2": bool(f["etude_geotechnique_g2"]) if f["etude_geotechnique_g2"] not in (None, NULL) else None,
            "diagnostic": clean(f["diagnostic_vuln"]),
            "zoneRefuge": clean(f["zone_refuge"]),
            "refugeCategorie": clean(f["refuge_categorie"]),
            "zonesIntersectees": clean(f["zones_intersectees"]),
            "etagePresent": clean(f["etage_present"]),
            "etageSource": clean(f["etage_source"]),
            "typologie": clean(f["typologie_occupation"]),
            "typologieSource": clean(f["typologie_source"]),
            "eligibiliteFprnm": clean(f["eligibilite_fprnm"]),
            "nbLogements": clean(f["nombre_de_logements"]),
            "hauteurM": clean(f["hauteur"]),
            "isErp": bool(f["is_erp"]) if f["is_erp"] not in (None, NULL) else None,
        }
        props = {k: v for k, v in props.items() if v is not None}
        feats_zone.append({"type": "Feature", "geometry": geom, "properties": props})

    write_geojson(os.path.join(OUTPUT_DIR, "batiments_ppri.geojson"), feats_zone)
    write_geojson(os.path.join(OUTPUT_DIR, "batiments_hors_zone.geojson"), feats_hors)


def export_zonage():
    lyr = find_layer(LAYER_ZONAGE)
    feats = []
    for f in lyr.getFeatures():
        code = clean(f["codezonere"])
        props = {
            "zoneCode": code,
            "zoneLabel": ZONE_LABELS.get(code, code),
            "zoneColor": ZONE_COLORS.get(code, "#9E9E9E"),
            "codeZone": clean(f["idzoneregl"]),
            "typeReg": clean(f["typereglem"]),
            "libelleZone": clean(f["libellezon"]),
        }
        geom = geom_to_geojson(f.geometry(), ndigits=6, simplify_tol=0.2)
        feats.append({"type": "Feature", "geometry": geom, "properties": props})
    write_geojson(os.path.join(OUTPUT_DIR, "zonage_pprin.geojson"), feats)


def export_erp():
    """Contrairement aux batiments, la couche ERP de Carbonne ne porte pas
    encore de champ de zone precalcule : on teste ici l'intersection avec
    le zonage directement (index spatial), plutot que d'exiger un
    pre-traitement QGIS supplementaire."""
    lyr_erp = find_layer(LAYER_ERP)
    lyr_zonage = find_layer(LAYER_ZONAGE)

    zonage_features = {f.id(): f for f in lyr_zonage.getFeatures()}
    index = QgsSpatialIndex(lyr_zonage.getFeatures())

    feats = []
    for f in lyr_erp.getFeatures():
        geom = f.geometry()
        zone_code = None
        for fid in index.intersects(geom.boundingBox()):
            zf = zonage_features.get(fid)
            if zf and zf.geometry().intersects(geom):
                zone_code = clean(zf["codezonere"])
                break

        type_principal = (clean(f["type_principal"]) or "")
        is_sensible = type_principal in TYPES_ERP_SENSIBLES
        classe_vuln = None
        if is_sensible:
            classe_vuln = "Établissement sensible (enseignement, santé ou secours)"

        props = {
            "nom": clean(f["libelle"]),
            "activite": clean(f["activite_principale"]),
            "classeVulnerabilite": classe_vuln,
            "adresse": " ".join(
                p for p in [clean(f["adresse_numero"]), clean(f["adresse_nom_1"])] if p
            ) or None,
            "zoneCode": zone_code,
            "zoneColor": ZONE_COLORS.get(zone_code, "#9E9E9E"),
            "concerne": zone_code is not None,
        }
        props = {k: v for k, v in props.items() if v is not None}
        geom_out = geom_to_geojson(geom, ndigits=6)
        feats.append({"type": "Feature", "geometry": geom_out, "properties": props})
    write_geojson(os.path.join(OUTPUT_DIR, "erp.geojson"), feats)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Export des couches Carbonne vers data/ ...")
    export_bati()
    export_zonage()
    export_erp()
    print("Termine.")
