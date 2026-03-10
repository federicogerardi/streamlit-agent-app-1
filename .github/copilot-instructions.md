<memory_persistence_protocol>
  <setup_directives>
    - **Inizializzazione**: Se la cartella `/memories/` non esiste, creala e aggiungila immediatamente al `.gitignore`.
  </setup_directives>

  <memory_scopes>
    - **User memory** (`/memories/`): Preferenze persistenti, pattern comuni, comandi frequenti e insights generali (primo caricamento: 200 righe).
    - **Session memory** (`/memories/session/`): Note per la sessione corrente. Archivia contesto task-specifico, note in progress e stato di lavoro temporaneo.
    - **Repository memory** (`/memories/repo/`): Fatti specifici del repository. Archivia convenzioni del codebase, comandi di build, struttura del progetto e pratiche verificate.
  </memory_scopes>

  <allowed_files_whitelist>
    - **L'agente ha il permesso di scrivere ESCLUSIVAMENTE sui seguenti file**:
      1. `PROJECT.md` (nella root del progetto): Per stack tecnologico, specifiche tecniche e analisi funzionali.
      2. `/memories/[MMDDYYYY].md` (nella root del progetto): Per log giornalieri, modifiche e info acquisite.
      3. `/memories/repo/*.md` (nella root del progetto): Per fatti specifici del repository e convenzioni del codebase.
      4. `/memories/session/*.md` (nella root del progetto): Per note della sessione corrente.
    - **Regola di Consolidamento**: Qualsiasi analisi, sintesi, riepilogo visuale o documento di progettazione DEVE essere integrato all'interno di `PROJECT.md`. Non è permessa la frammentazione in file multipli.
  </allowed_files_whitelist>

  <strict_file_creation_ban>
    - ### DIVIETO ASSOLUTO ###
    - È vietata la creazione autonoma di qualsiasi altro file con estensione `.md` (es. `ANALYSIS.md`, `SUMMARY.md`, `FUNCTIONAL_DOC.md`, ecc.).
    - Ogni nuova informazione deve "trovare casa" in uno dei percorsi sopra citati.
    - **Eccezione**: La creazione di nuovi file (di codice o documentazione) è consentita SOLO se esplicitamente richiesta dall'utente tramite comando diretto.
    - **Ratio**: Questo vincolo è mandatorio per prevenire la proliferazione di file ridondanti, ottimizzare il contesto e azzerare lo spreco di token e crediti derivanti da generazioni non necessarie.
  </strict_file_creation_ban>

  <daily_log_logic>
    - **Naming**: `/memories/[MMDDYYYY].md` (es. `/memories/03102026.md`).
    - **Append Mode**: Se il file del giorno esiste, aggiungi in coda. Se non esiste, crea il nuovo indice sequenziale.
  </daily_log_logic>

  <validation_step_before_writing>
    - Prima di creare un nuovo file, l'agente deve porsi questa domanda: "L'utente mi ha chiesto esplicitamente di creare QUESTO specifico file?". 
    - Se la risposta è NO, l'informazione va inserita in `PROJECT.md`, nel log giornaliero (`/memories/[MMDDYYYY].md`), o nei file di memoria appropriati.
  </validation_step_before_writing>
</memory_persistence_protocol>