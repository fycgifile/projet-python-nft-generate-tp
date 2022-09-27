import json
import os
import numpy as np
import random
from PIL import Image

glob_datas = []  # Data configuration
glob_characters = []  # Character List
glob_metadatas = []  # Character List


def check_configuration():
    print('Vérification du fichier de configuration en cours ...')
    for dt in glob_datas['configuration']:
        dt_path = os.path.join('images', dt['path'])
        # Récupération de fichiers img dans le dossier selon dt_path
        characters = sorted(
            [character for character in os.listdir(dt_path) if character[0] != '.'])
        if dt['require'] == "false":  # Si dans configuration, blocs require = false ajout d'un character None a la liste des characters pour ajouter le fait de ne rien pouvoir avoir si cette couche
            characters = [None] + characters
        # Création d'une liste de la longeur du nbr de charactere par dossier
        characters_statistic = [1 for x in characters]
        # Conversion via NumPy des stats pour que la somme total d'un character de caractere soit égale à 1
        characters_statistic = np.array(
            characters_statistic) / sum(characters_statistic)
        # Retourne la somme cumulée des éléments via NumPy 1, 1+2, 1+2+3, 1+2+3+4, etc
        dt['characters_statistic'] = np.cumsum(characters_statistic)
        dt['characters'] = characters
    print('Vérification terminée ✔️')


def get_index(characters_statistic, rand):
    # [0.2, 0.4, 0.6, 0.8, 1.0] / 0.8188532614967073
    # [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    characters_statistic = [0] + list(characters_statistic)
    for i in range(len(characters_statistic) - 1):
        if rand >= characters_statistic[i] and rand <= characters_statistic[i+1]:
            return i


def generate(paths, filename):
    # Création de la base de l'image
    bg = Image.open(os.path.join('images', paths[0]))
    # Boucle autant de fois qu'il y a de path
    for filepath in paths[1:]:
        if filepath.endswith('.png'):  # Si extension est png
            # Ouverture de l'image charactere selon le path
            img = Image.open(os.path.join('images', filepath))
            # Collage de l'image recupéré sur l'image créer
            bg.paste(img, (0, 0), img)
    bg.save(filename)  # Enregistrement de l'image
    global glob_metadatas
    # Ajout du nom de fichier a la list des path d'une image
    paths.append(filename)
    datas_item = []
    for path in paths:
        path_split = path.split("/")
        item_name = str(path_split[0])
        item_value = str(path_split[1])
        if item_name == "images_generate":
            item = {"image": str(path_split[3])}
        else:
            item = {item_name: item_value}
        datas_item.append(item)
    # Ajout de la liste des path dans la list globale pour metadonnée
    glob_metadatas.append(datas_item)


def pre_generate(images_collection_name, images_total_number):
    print("Pré-génération des images en cours ...")
    # Création d'un path vers le dossier images_generate/Collection + images_collection_name
    os_path = os.path.join('images_generate', 'collection_' +str(images_collection_name), 'images')

    if not os.path.exists(os_path):  # Permet de vérifier si le dossier existe ou non
        os.makedirs(os_path)  # Permet de créer le dossier si il n'existe pas
    # Boucle pour lancer la génération des X images demandés
    for n in range(images_total_number):
        # Nom de l'image qu'on definit avec n
        name = str(n + 1) + '.png'
        character_paths = []  # Liste des path des photos des caracteristique de l'image
        for dt in glob_datas['configuration']:
            # Selectionne un index au hasard
            idx = get_index(dt['characters_statistic'], random.random())
            # Ajoute le path de l'image du charactere choisi dans la liste character_paths
            if dt['characters'][idx] is not None:  # Si le characters existe
                # Récupération du path du charactere
                character_path = os.path.join(dt['path'], dt['characters'][idx])
                character_paths.append(character_path)  # Ajout a la liste
        # Génération de l'image, avec les conditions généré par hasard
        generate(character_paths, os.path.join(os_path, name))
    # Enregistrement de métadonnées
    om_path = os.path.join('images_generate', 'collection_' +str(images_collection_name), 'metadata')
    if not os.path.exists(om_path):  # Permet de vérifier si le dossier existe ou non
        os.makedirs(om_path)  # Permet de créer le dossier si il n'existe pas
    # Boucle la liste des metadonnées

    for metadata in glob_metadatas:
        name = metadata[-1]  # Récupération du dernier element de la liste
        # Enlever l'extension .png du nom du fichier
        name = os.path.splitext(name['image'])[0]
        # Nouveau path du fichier de metadonné
        path = om_path + "/" + str(name)
        with open(path, 'w') as f:
            item = {
                "attributes": metadata,
                "description": name,
                "external_url": "https://example.com/?token_id="+name,
                "image": path,
                "name": name
            }
            json.dump(item, f, indent=2)


def main():
    print('Récupération de la configuration en cours ...')
    f = open('configuration.json')  # Récupération de la configuration
    global glob_datas
    glob_datas = json.load(f)  # Défini glob_datas avec contenu de la config
    check_configuration()  # Verification du fichier de config
    # Question prompt pour le nombre d'image à générer
    images_total_number = int(input("Combien voulez-vous générer d'images ? "))
    # Question prompt pour le nom de la collection
    images_collection_name = input(
        "Comment voulez-vous nommer cette collection ? ")
    # Pré-génération et génération des images
    pre_generate(images_collection_name, images_total_number)
    print("Génération terminé ✔️")


# Fonction main()
main()