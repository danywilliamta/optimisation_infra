# Système d'optimisation Infra

## Description

J'ai choisi de développer cette application en **Python** car c'est un langage flexible et adapté au traitement de données volumineuses ainsi qu'à l'intégration avec des modèles de langage (LLM).

Mon approche a été de partir de fichiers **JSON** où les logs de performance sont sauvegardés, et de les ingérer dans une **base de données PostgreSQL**. PostgreSQL permet de stocker et de requêter facilement des données de type JSON.

Le traitement se fait comme suit :

- Chaque fichier est traité dans un **dossier connu**.
- Les logs sont traités par **batchs de n log metrics**, en utilisant des **générateurs** pour ne pas surcharger la mémoire.
- Grâce à la bibliothèque **ijson**, nous pouvons éviter de charger tout un fichier JSON en mémoire, et traiter le fichier **ligne par ligne**.
- Pour chaque batch de n log metrics, nous faisons un **appel à un LLM** pour générer “on the fly” les **analyses et recommandations** correspondantes.
- Le modèle de la **réponse attendue** est passé au LLM, et le **schéma de l'objet retourné est vérifié**.
- Les résultats sont ensuite **stockés dans la base de données**, en associant le batch de logs et la génération d’analyses et de recommandations.

Résultat:

![alt text](/result/image.png)

![alt text](/result/image-1.png)

