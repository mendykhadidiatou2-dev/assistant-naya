# Naya : assistante personnelle IA (RAG, Agent, Gemini et n8n)

Naya est mon assistante personnelle accessible depuis une interface web et depuis Telegram. Son rôle est
d'explorer mes données privées (documents administratifs, calendrier Google, boîte Gmail)
grâce à une architecture combinant **RAG local** et **agent autonome à base d'outils**, avec
une génération de réponses assurée par l'**API Gemini** (function calling). Elle **garde le fil de
la conversation** (mémoire des échanges récents). Chaque matin, un workflow **n8n** lui demande de
rédiger un brief motivant, envoyé sur **Telegram**.

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
- **Mémoire de conversation** : elle comprend les questions de suivi (« résume le premier »)
  grâce à l'historique des derniers échanges, renvoyé au modèle à chaque question.
- **Brief matinal automatique** : chaque jour à 8 h, un scénario n8n appelle l'API de Naya, qui
  rédige un message chaleureux (agenda, mails, focus du jour) envoyé sur Telegram.

---

## Architecture modulaire

Le projet repose sur plusieurs couches bien étanches, garantissant un code propre et la possibilité
de faire évoluer chaque module sans casser le reste.

| Couche | Rôle | Emplacement |
|---|---|---|
| **Outils** | Fonctions pures et prévisibles (fichiers, agenda, boîte mail) | `src/tools/`, `src/rag/` |
| **Agent** | Boucle de raisonnement : choix de l'outil, exécution et rédaction | `src/agent/` |
| **Interface** | Espace de discussion interactif développé avec Streamlit | `src/web/` |
| **API** | Point d'entrée HTTP (`GET /brief`) pour l'automatisation | `src/api.py` |
| **Automatisation** | Workflow n8n : déclencheur 8 h, appel de l'API, envoi Telegram | n8n |

### Le cheminement d'une question

1. L'utilisateur pose sa question (l'interface y joint l'historique récent).
2. L'agent construit les messages : consigne système, historique, question.
3. Le modèle Gemini décide d'appeler un outil ou de répondre directement.
4. Le code exécute l'outil demandé (lecture locale ou appel d'API) et renvoie le résultat au modèle.
5. La boucle se répète (5 tours maximum), puis le modèle rédige une synthèse claire et sourcée.

### Le cheminement du brief matinal

```
n8n (Schedule 8 h) ──► API FastAPI  GET /brief ──► Agent (agenda + mails) ──► n8n ──► Telegram
```

La recherche documentaire reste entièrement confinée sur ma machine grâce à ChromaDB et au
modèle d'embeddings : aucun document personnel n'est envoyé à l'extérieur. Seuls les extraits
indispensables et la question finale transitent brièvement par l'API Gemini pour produire la
réponse.

---

## Mémoire de conversation

Une API de modèle de langage est **sans état** : le modèle ne se souvient de rien d'un appel à l'autre.
La mémoire de Naya repose donc sur un principe simple.

- L'interface Streamlit conserve les échanges dans `st.session_state.messages`.
- À chaque question, elle transmet à l'agent les **10 derniers messages** (fenêtre glissante),
  sans le message d'accueil, via le paramètre `historique`.
- L'agent assemble : consigne système, puis historique, puis nouvelle question, et renvoie le tout au modèle.

Pourquoi limiter à 10 messages ? Chaque message renvoyé est relu (et compté en tokens) à chaque appel.
Plus l'historique grandit, plus les appels coûtent et plus le quota est vite consommé. La fenêtre
glissante garde le contexte utile tout en maîtrisant le coût.

---

## Stack technique retenue

| Besoin | Solution | Justification |
|---|---|---|
| Extraction de documents | `pdfplumber` et OCR (`pytesseract`, Poppler) | Prise en charge des textes natifs comme des scans |
| Embeddings | `intfloat/multilingual-e5-base` (`sentence-transformers`) | Compréhension fine du français, exécuté en local |
| Base vectorielle | ChromaDB en local | Solution persistante, légère et respectueuse de la vie privée |
| Modèle de génération | API Gemini (famille Flash), via le client `openai` et l'endpoint compatible | Function calling fiable, quotas plus confortables |
| Logique agentique | Function calling | Sélection dynamique de la bonne fonction par le modèle |
| Interface web | Streamlit | Chat ergonomique, léger et simple à mettre en cache |
| API | FastAPI + Uvicorn | Expose le brief à n8n |
| Automatisation | n8n + bot Telegram | Brief quotidien planifié |
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
  Compréhension du partage des rôles : le modèle demande l'outil, c'est le code qui l'exécute.
- **Mémoire de conversation** : conception d'une fenêtre glissante sur un modèle sans état,
  avec compromis entre cohérence du dialogue et coût en tokens.
- **Gestion des tokens et des quotas** : fenêtre de contexte, `max_tokens` (plafond de sortie,
  vérification de `finish_reason`), limites par minute et par jour. Compréhension de ce qui fait
  grossir le coût d'un appel : consigne système, description des outils, résultats d'outils et
  historique, renvoyés à chaque tour de boucle. Une erreur 429 sur le quota quotidien m'a conduite
  à migrer de Groq vers Gemini en changeant seulement le client et le modèle.
- **Exposition en service** : API FastAPI et automatisation n8n (déclencheur planifié, requête
  HTTP, envoi Telegram avec mise en forme HTML).
- **Sécurité OAuth 2.0** : distinction entre identifiants d'application et jetons d'accès
  utilisateur, couplée au renouvellement par jeton de rafraîchissement.
- **Culture de la mesure** : analyse des goulets d'étranglement avant d'optimiser (logs, mesure
  des durées par étape) plutôt que d'agir à l'intuition.
- **Cadre réglementaire** : notions de RGPD (minimisation, sous-traitants) et d'IA Act
  (niveaux de risque, humain dans la boucle).
- **Déploiement (notions)** : Docker (image, conteneur, `.dockerignore`) et CI/CD
  (tests, build et livraison automatiques), en préparation de l'hébergement.

---

## Arguments clés pour un échange technique

- **RAG local couplé à une API de génération** : ce compromis garantit la confidentialité des
  données au repos tout en offrant un confort d'utilisation immédiat, sans exiger de GPU
  dédié chez moi.
- **Agent conçu à la main plutôt qu'avec LangChain** : j'ai préféré bâtir la boucle
  d'orchestration moi-même afin de maîtriser chaque rouage sous le capot avant d'envisager un
  framework externe.
- **Un modèle unique pour plusieurs outils** : au lieu de multiplier les modèles spécialisés, un
  seul LLM orchestre l'ensemble grâce au function calling.
- **Fournisseur interchangeable** : l'utilisation du client `openai` avec une `base_url`
  m'a permis de passer de Groq à Gemini sans réécrire l'agent.
- **Mémoire bornée** : une fenêtre glissante de 10 messages plutôt qu'un historique illimité,
  pour garder un coût et un quota maîtrisés.
- **Abandon raisonné du reranking** : testé au départ, le reclassement s'est avéré trop lourd en
  mémoire vive et inutile pour le volume actuel de mes fichiers. La mesure a guidé ce retrait.

---

## Sécurité et données personnelles

- Scopes d'autorisation Google limités à la simple lecture.
- Fichiers sensibles, clés d'API et jetons isolés en dehors de Git via le `.gitignore`.
- Documents d'identité et base vectorielle strictement stockés en local.
- Tout contenu lu par un outil est traité comme une donnée brute, jamais comme une consigne système.
- Le token du bot Telegram est stocké dans les Credentials de n8n, jamais dans le code.

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
src/api.py       API FastAPI (endpoint /brief pour n8n)
.env.example     Modèle de configuration (sans valeur secrète)
```

---

## Configuration

Copier `.env.example` en `.env` et renseigner la clé :

```
GEMINI_API_KEY=
```

Les identifiants Google se placent dans `secrets/` (exclu de Git).

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

Pour démarrer l'API utilisée par n8n :

```powershell
uvicorn src.api:app --reload
```

---

## État d'avancement

- [x] **Phase 0** — socle initial, flux OAuth et consultation de l'agenda
- [x] **Phase 1** — traitement documentaire, OCR, découpage et ajout des métadonnées
- [x] **Phase 2** — création des vecteurs sémantiques et persistance dans ChromaDB
- [x] **Phase 3** — génération factuelle ancrée et intégration de l'agent multi-outils
- [x] **Phase 4** — conception de l'interface de discussion Streamlit
- [x] **Phase 5** — API FastAPI et workflow n8n pour l'envoi du bilan matinal à 8 h sur Telegram
- [ ] **Phase 6** — fiabilisation et mise en production
  - [x] mémoire de conversation
  - [x] évaluation de la qualité des réponses
  - [ ] tests automatisés (pytest)
  - [ ] Docker (Dockerfile, `.dockerignore`)
  - [ ] CI/CD (GitHub Actions)
  - [ ] hébergement et sécurisation de `/brief` (clé secrète)

### Limites actuelles

- Le brief du matin n'arrive que si mon ordinateur et l'API sont allumés (hébergement à venir).
- Pas encore de tests automatisés.
- La mémoire est limitée aux 10 derniers messages de la session en cours (elle ne persiste pas entre deux sessions).

### Prochaines étapes

- Tests automatisés (pytest).
- Docker (Dockerfile, `.dockerignore`).
- CI/CD avec GitHub Actions.
- Hébergement de l'application et sécurisation de `/brief` par une clé secrète.

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

### 2026-10-13
- Fait : phase 5 terminée — API FastAPI (`/brief`), workflow n8n actif (8 h → API → Telegram),
  message mis en forme en HTML ; migration Groq → Gemini après dépassement du quota quotidien
- Prochaine étape : mémoire de conversation, évaluation, puis Docker, CI/CD et hébergement

### Mi-octobre 2026
- Fait : mémoire de conversation (historique glissant de 10 messages, transmis par l'interface à l'agent) ;
  analyse de la consommation de tokens (consigne système, outils et résultats renvoyés à chaque tour) ;
  évaluation de la qualité des réponses ; README et `.env.example` mis à jour
- Prochaine étape : tests, Docker, CI/CD et hébergement