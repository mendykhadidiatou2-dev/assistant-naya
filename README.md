# Naya : assistante personnelle IA (RAG, Agent et Groq)

Naya est mon assistante personnelle accessible depuis une interface web. Son rôle est
d'explorer mes données privées (documents administratifs, calendrier Google, boîte Gmail)
grâce à une architecture combinant **RAG local** et **agent autonome à base d'outils**, avec
une génération de réponses accélérée par l'**API Groq**.

---

## Ce que Naya prend en charge

- **Documents administratifs** : elle extrait les réponses clés au cœur de mes PDF
  (attestations, titre de séjour, contrats d'assurance) et cite systématiquement le document source.
- **Agenda** : elle consulte mes créneaux et mes cours, toutes sources confondues, y compris
  mon planning d'école synchronisé via iCal.
- **Gestion des e-mails** : elle identifie les messages non lus et urgents en extrayant
  l'expéditeur, l'objet et un court résumé.
- **Prise de décision autonome** : dotée d'une logique d'agent, elle sélectionne elle-même le
  bon outil en fonction du besoin détecté dans la question.
- **Évolution prévue** : un récapitulatif matinal envoyé chaque jour à 8 h grâce à un scénario
  automatisé n8n.

---

## Architecture modulaire

Le projet repose sur trois couches bien étanches, garantissant un code propre et la possibilité
de faire évoluer chaque module sans casser le reste.

| Couche | Rôle | Emplacement |
|---|---|---|
| **Outils** | Fonctions pures et prévisibles (fichiers, agenda, boîte mail) | `src/tools/`, `src/rag/` |
| **Agent** | Boucle de raisonnement : choix de l'outil, exécution et rédaction | `src/agent/` |
| **Interface** | Espace de discussion interactif développé avec Streamlit | `src/web/` |

### Le cheminement d'une question

1. L'utilisateur pose sa question.
2. L'agent propulsé par Groq identifie et appelle l'outil approprié.
3. Le code exécute l'action demandée (lecture locale ou appel d'API).
4. Le modèle rédige une synthèse claire et contextualisée.

La recherche documentaire reste entièrement confinée sur ma machine grâce à ChromaDB et au
modèle d'embeddings : aucun document personnel n'est envoyé à l'extérieur. Seuls les extraits
indispensables et la question finale transitent brièvement par l'API Groq pour produire la
réponse à la vitesse de l'éclair.

---

## Stack technique retenue

| Besoin | Solution | Justification |
|---|---|---|
| Extraction de documents | `pdfplumber` et OCR (`pytesseract`, Poppler) | Prise en charge des textes natifs comme des scans |
| Embeddings | `intfloat/multilingual-e5-base` | Compréhension fine du français et des nuances sémantiques |
| Base vectorielle | ChromaDB en local | Solution persistante, légère et respectueuse de la vie privée |
| Modèle de génération | API Groq (`openai/gpt-oss-120b`) | Temps de réponse instantané, gratuité et bon raisonnement |
| Logique agentique | Function calling via Groq | Sélection dynamique de la bonne fonction par le modèle |
| Interface web | Streamlit | Chat ergonomique, léger et simple à mettre en cache |
| Services Google | Calendar et Gmail en lecture seule (OAuth 2.0) | Respect strict du principe de moindre privilège |

---

## Compétences techniques approfondies

- **Chaîne RAG complète** : extraction de texte, découpage intelligent (chunking),
  vectorisation, stockage en base vectorielle, récupération ciblée et génération ancrée.
- **Découpage contextuel** : un fichier court correspond à un segment unique, ajout de préfixes
  pour tracer l'origine et métadonnées complètes pour faciliter les filtres.
- **Gestion des embeddings** : conversion du sens en vecteurs mathématiques, calculs de
  similarité et séparation nette entre les préfixes de requêtes (`query:`) et de documents (`passage:`).
- **Ancrage (grounding)** : consignes strictes pour forcer le modèle à s'appuyer uniquement sur
  les extraits fournis ou à avouer clairement son ignorance s'il ne trouve rien.
- **Agents et function calling** : traduction des intentions en schémas JSON, déclenchement du
  code correspondant et contrôle du cycle de raisonnement avec un plafond d'itérations.
- **Sécurité OAuth 2.0** : distinction entre identifiants d'application et jetons d'accès
  utilisateur, couplée au renouvellement par jeton de rafraîchissement.
- **Culture de la mesure** : analyse des goulets d'étranglement avant d'optimiser. Le CPU
  limitait la génération, ce que l'API externe résout parfaitement sans toucher à la recherche.

---

## Arguments clés pour un échange technique

- **RAG local couplé à une API de génération** : ce compromis garantit la confidentialité totale
  des données au repos tout en offrant un confort d'utilisation immédiat, sans exiger de GPU
  dédié chez moi.
- **Agent conçu à la main plutôt qu'avec LangChain** : j'ai préféré bâtir la boucle
  d'orchestration moi-même afin de maîtriser chaque rouage sous le capot avant d'envisager un
  framework externe.
- **Un modèle unique pour plusieurs outils** : au lieu de multiplier les modèles spécialisés, un
  seul LLM performant orchestre l'ensemble grâce au function calling.
- **Abandon raisonné du reranking** : testé au départ, le reclassement s'est avéré trop lourd en
  mémoire vive et inutile pour le volume actuel de mes fichiers. La mesure a guidé ce retrait.

---

## Sécurité et données personnelles

- Scopes d'autorisation Google limités à la simple lecture.
- Fichiers sensibles, clés d'API et jetons isolés en dehors de Git via le `.gitignore`.
- Documents d'identité et base vectorielle strictement stockés en local.
- Tout contenu lu par un outil est traité comme une donnée brute, jamais comme une consigne système.

---

## Structure du dépôt

```
src/config.py    Point d'entrée unique pour la configuration et l'environnement
src/models.py    Structures de données et typage fort
src/infra/       Gestion de l'authentification Google et clients réseau
src/tools/       Fonctions dédiées à l'agenda et à la boîte mail
src/rag/         Ingestion des documents, segmentation et gestion vectorielle
src/agent/       Boucle principale et pilotage des fonctions
src/web/         Application web Streamlit
```

---

## Lancer l'application

Pour démarrer l'interface graphique :

```powershell
streamlit run src/web/app.py --server.fileWatcherType none
```

Pour exécuter et tester l'agent directement dans le terminal :

```powershell
python -m src.agent.agent
```

---

## État d'avancement

- [x] **Phase 0** — socle initial, flux OAuth et consultation de l'agenda
- [x] **Phase 1** — traitement documentaire, OCR, découpage et ajout des métadonnées
- [x] **Phase 2** — création des vecteurs sémantiques et persistance dans ChromaDB
- [x] **Phase 3** — génération factuelle ancrée et intégration de l'agent multi-outils
- [x] **Phase 4** — conception de l'interface de discussion Streamlit
- [ ] **Phase 5** — création du workflow n8n pour l'envoi du bilan matinal à 8 h

---

## Journal de bord

### 2026-09-19
- Fait : phase 0 terminée — OAuth fonctionnel, agenda lu, refresh token vérifié
- Prochaine étape : phase 1 — ingestion des documents administratifs (PDF)

### 2026-09-23
- Fait : phase 2 — recherche vectorielle fonctionnelle (ChromaDB + embeddings multilingues)
- Prochaine étape : phase 3 — le LLM qui lit les chunks et rédige la réponse

### 2026-09-30
- Fait : phases 3, 4 et début 5 — agent multi-outils (documents, agenda, mails),
  génération via Groq, interface Streamlit complète avec Naya
- Prochaine étape : phase 5 — workflow n8n pour le résumé matinal
