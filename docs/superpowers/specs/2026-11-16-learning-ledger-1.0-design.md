# learning-ledger 1.0.0: design

Data: 2026-11-16. Stato: da approvare.

## Intento e perché

Fabio usa l'AI per scrivere in fretta classi e sistemi, ma per certe parti vuole capire ciò che è stato scritto: deve poterlo raccontare (colloqui, lavoro) e giudicare se la scelta è quella giusta o se c'erano alternative. Oggi il plugin (0.2.2) registra bene le prove di apprendimento (quiz, practice, ledger con livelli limitati dall'evidenza), ma non ha niente che accompagni chi costruisce: né spiegazioni del codice già scritto, né un affiancamento passo per passo mentre si scrive.

La 1.0.0 aggiunge due modi di lavorare, entrambi collegati al ledger esistente.

## Obiettivi

1. **`explain`**: l'AI scrive (o ha già scritto), l'utente capisce. Spiega il codice reale del progetto decisione per decisione.
2. **`pair`**: l'utente scrive, l'AI fa ragionare con domande e contesta le scelte deboli.
3. Entrambe finiscono nel ledger con evidenza onesta, senza modifiche alle regole di `ledger.py`.
4. Versione stabile 1.0.0: documentazione, test, CHANGELOG, promessa di compatibilità dello schema dei file del ledger.

## Non-obiettivi

- Nessuna modifica alla logica di livelli e intervalli di `ledger.py`.
- Nessuna sincronizzazione, account o rete.
- Nessun commit o push fatto dalle skill.
- `explain` e `pair` non sostituiscono `quiz` e `practice`; le completano.

## Anti-obiettivi (sarebbe un fallimento anche se tutto funziona)

- Un muro di testo che spiega tutto senza che l'utente debba mai pensare.
- Un tutor accondiscendente che approva scelte deboli.
- Un registro in cui "ho letto la spiegazione" fa salire il livello.

## Approcci considerati

| | Descrizione | Esito |
|---|---|---|
| A | Due skill separate, `explain` e `pair`, accanto a `practice` | **Scelto da Fabio** |
| B | Una skill `mentor` con modalità | Scartato: SKILL.md lungo, cambio modalità confuso |
| C | Una "manopola" su quanto scrive l'AI | Scartato: difficile da far rispettare al modello |

## Design

### `explain`

Due ingressi nella stessa skill, scelti da quello che l'utente chiede:

1. **Spiegare codice esistente** ("perché c'è il filtro JWT?", "spiegami cosa ha scritto Claude"). Se l'utente parla di ciò che è appena stato scritto, parte dal diff (`git diff` / `git status`) senza modificarlo.
2. **Generare spiegando** ("scrivimi X e spiegami"). Prima di scrivere elenca le decisioni principali con alternative e una raccomandazione; poi scrive e spiega ogni pezzo; alla fine indica come verificare che funzioni (test, comando, caso limite).

Per ogni decisione, in ordine di esecuzione a runtime: cosa fa; perché esiste (che problema risolve); come funziona dentro (cosa succede a una richiesta vera); alternative e trade-off; cosa si rompe se lo togli; come verificarlo.

Regole di contenuto:
- Ancorata al codice del progetto (`file:riga`), non a un esempio generico.
- **Critica onesta**: se una scelta è debole, lo dice e la classifica come *bug / rischio / miglioramento facoltativo / stile*; se è corretta, lo dice senza inventare difetti.
- Per API e versioni di librerie usa uno strumento di documentazione (per esempio Context7) quando c'è, e marca come *non verificato* ciò che non ha controllato.
- Livello di dettaglio adattato: parte dalla decisione, approfondisce dove l'utente chiede o sbaglia.
- Chiude con **"come lo racconteresti"**: una versione di 4-5 frasi da dire a voce, e poi chiede all'utente di rifarla con parole sue (*teach-back*) su 1-3 punti, valutando con la rubrica di `quiz` (30 punti).
- Sola lettura: non modifica file (nel ramo "generare" scrive solo ciò che l'utente ha chiesto di generare).

Registrazione: la spiegazione data prima della verifica è un aiuto forte. Quindi la sessione si registra con `support: full_solution`, `evidence: observed_answers` (solo se c'è stato il teach-back; altrimenti non si propone la registrazione). Lo script porta già al massimo `with_support`: per salire serve tornare dopo giorni con `quiz` o `pair`. Nessuna modifica a `ledger.py`.

### `pair`

L'utente scrive il codice. Cicli brevi:

1. Chiarire l'obiettivo e il criterio di successo (una domanda).
2. Chiedere all'utente il prossimo passo e il perché, **una domanda di ragionamento alla volta** ("che cosa succede se il token è scaduto qui?", "cosa succede con due richieste insieme?").
3. L'utente scrive; Claude rivede quel pezzo: classifica i problemi (bug / rischio / miglioramento / stile), dice dove e perché. Se la scelta è discutibile, la **contesta con un'alternativa e un trade-off** e chiede all'utente di difenderla.
4. Scala di aiuto, la più piccola possibile: domanda guida, indizio, esempio minimo, soluzione parziale, soluzione completa. Si ricorda l'aiuto massimo dato.
5. A ogni traguardo l'utente riassume in due righe cosa ha fatto e perché.

Regole: non scrive nei file dell'utente salvo richiesta esplicita (e allora vale `full_solution`); non decide l'architettura al posto suo; esegue i test quando l'ambiente lo permette e riporta ciò che è stato davvero eseguito.

Differenza con `practice`: `practice` dà un brief e rivede alla fine; `pair` accompagna durante la scrittura.

Registrazione: `evidence: observed_exercise` o `reviewed_code`, `support` = aiuto massimo effettivo; il tipo sessione è `exercise`.

### Interventi sulle skill esistenti

- `study-today`: tra i passi successivi consiglia anche `explain` (per capire codice) e `pair` (per costruire).
- `practice`: una riga che rimanda a `pair` per chi vuole essere accompagnato durante.
- `log-session`: due righe che dicono come registrare le sessioni `explain` e `pair`.
- Nuovo pacchetto di argomenti `examples/spring-security-topics.json` (filtro JWT, validazione token, refresh token, password encoding, autorizzazione per metodo, CORS/CSRF, rate limiting), perché è il campo di Fabio e collega i due plugin. Il builder sceglie il numero di argomenti (circa 10-12).

### Convenzioni valide per tutte le skill

- Rispondono nella lingua dell'utente.
- Spiegano prima di mostrare, senza tono motivazionale, senza elogi automatici.
- Mai segreti nelle spiegazioni o nei riassunti.

## Vincoli

- Solo Python 3 standard library per lo script; le skill trovano Python come oggi (`python3`, `python`, `py`).
- Compatibilità con ledger esistenti: formato di `topics.json`, `sessions.jsonl`, `config.json` invariato.
- Niente commit: i file restano nel working tree finché Fabio non autorizza.

## Cosa resta al builder

- Testo preciso dei SKILL.md (descrizioni con trigger chiari, in inglese come le altre).
- Test strutturali: ogni `skills/<nome>/SKILL.md` ha frontmatter con `name` uguale alla cartella e `description` non vuota; il pacchetto di argomenti nuovo passa `topic import`; i test esistenti restano verdi.
- Versione 1.0.0 in `plugin.json`, CHANGELOG, README (tabella skill, esempio d'uso), `marketplace.json` se contiene la versione.
- Scelta delle decisioni di esempio nel README.

## Scelte mie (da controllare)

- `explain` si registra sempre come `full_solution`: è la lettura più prudente; se vuoi più generosità va cambiata a mano.
- I nomi `explain` e `pair` sono miei.
- Il pacchetto di argomenti di sicurezza è un'aggiunta mia, non richiesta.
