# AGENTS.md

## Scopo
Plugin per Claude Code che tiene un registro locale delle prove di apprendimento. Script Python senza dipendenze (`ledger.py`) e skill.

## Fonti di verità
Il codice dello script e le skill sono la verità tecnica. `README.md` e `CHANGELOG.md` (in inglese) descrivono skill, formati dei file e versioni.

## Regole operative
- **Documentazione sempre allineata.** Ogni modifica (codice, struttura, stato, decisione, versione) aggiorna nella stessa PR tutti i documenti che la riguardano: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `docs/`, la versione nel manifest del plugin (`plugins/learning-ledger/.claude-plugin/plugin.json`), questo file e la scheda Notion del progetto. Se cambiano versione, stato, descrizione o schema del progetto, controllare anche la sua scheda nel portfolio (`fabio-zagaria-portfolio`: dati in `portfolio-angular/src/app/data`, `README.md` e `docs/CONTEXT.md`). Prima di dichiarare finito un lavoro, passare in rassegna l'elenco e dire per ciascun documento se è stato aggiornato o perché non serve. Una modifica senza documenti allineati non è Done.
- Niente commit, push, merge o deploy senza autorizzazione esplicita del proprietario.
- Nessun segreto, password o token nel repository.
