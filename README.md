# Amazeme

Un labyrinthe en trois dimensions, à la première personne, dans un seul fichier HTML.
Pas de dépendance, pas de serveur, pas de build : ouvrez `index.html` et marchez.

![Menu](docs/menu.jpg)

## Jouer

- **En ligne** : la version publiée se joue directement sur téléphone comme sur ordinateur.
- **Hors ligne** : téléchargez `index.html` et ouvrez-le dans Safari, Chrome ou Firefox.

Chaque niveau est le même labyrinthe pour tout le monde : la graine est dérivée du numéro du niveau.
Le **Défi du jour** change chaque jour à minuit, identique pour tous les joueurs.

## Commandes

| | Marcher | Regarder | Boussole | Survol | Fil d'Ariane | Son | Pause |
|---|---|---|---|---|---|---|---|
| Clavier | `Z Q S D` ou flèches | souris (clic pour capturer) | `C` | `M` | `F` | `N` | `Échap` |
| Tactile | pouce gauche | pouce droit | bouton | bouton | bouton | bouton | bouton |

La boussole et le survol aident à trouver la sortie, mais un temps réalisé avec une aide ne compte pas comme record.

![En jeu](docs/play.jpg)

## À l'arrivée

La caméra s'élève au-dessus du labyrinthe. Votre trajet apparaît en bleu, le chemin optimal se dessine en or,
et la fiche compare les deux : temps, nombre de cases, efficacité, meilleur temps.

![Arrivée](docs/win.jpg)

## Sous le capot

Tout tient dans `index.html` (environ 60 Ko) :

- **Génération** : backtracker récursif avec un goût pour les longs couloirs, puis ouverture d'une partie des impasses pour créer des boucles. La sortie est la cellule la plus lointaine du départ (parcours en largeur), ce qui donne aussi le chemin optimal.
- **Rendu** : WebGL 1 écrit à la main. Pierres, briques, mousse et dalles humides sont calculées dans le fragment shader, sans texture. Torche portée qui vacille, clair de lune, brouillard, ciel étoilé avec lune, colonne de lumière et étincelles à la sortie, poussière dans le faisceau de la torche.
- **Caméra** : trois modes (orbite du menu, première personne, survol) reliés par des transitions continues. Le passage du menu au jeu est un plongeon dans le labyrinthe.
- **Audio** : tout est synthétisé avec la Web Audio API. Nappe grave, vent, pas, chocs contre les murs, bourdon qui monte près de la sortie, fanfare d'arrivée, réverbération par convolution sur une impulsion générée.
- **Collisions** : cercle contre grille de blocs, glissement le long des murs.
- **Sauvegarde** : niveaux débloqués et meilleurs temps dans `localStorage`.

## Niveaux

Trente niveaux, de 8×8 à 40×40 cases. Un lien `index.html#l=12` ouvre directement le niveau 12, `#d` ouvre le défi du jour.
