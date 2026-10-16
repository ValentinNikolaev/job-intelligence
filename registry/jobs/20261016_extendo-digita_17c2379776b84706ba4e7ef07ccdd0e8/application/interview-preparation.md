## Recruiter / HR Screening

Preparare una risposta breve sul perché Extendo Digital: l’annuncio unisce PHP, API REST, prestazioni e integrazioni; il sito descrive system integration ed e-commerce. Spiegare l’interesse per PHP dopo i lavori recenti in Go usando la consulenza PHP di CRURATED come esperienza concreta; formulare personalmente la motivazione. Se emerge la precedente candidatura, riferire solo fatti noti sul proprio invio, senza supporre che Extendo l’abbia valutata.

Ripassare la sequenza: Simple.life termina nel CV con il solo anno 2026; CRURATED fu consulenza part-time parallela da agosto 2024 a gennaio 2026. Preparare le ragioni dei cambi di lavoro e spiegare anche la sovrapposizione Sixt/PDFfiller. Chiedere la frequenza a Fondi prima di indicare disponibilità agli spostamenti. Autorizzazione al lavoro, preavviso, data utile, retribuzione e italiano richiedono risposte personali confermate. Concordare formato e riservatezza di portfolio e case history.

## Culture Fit / Behavioral Interview

Preparare risposte STAR concise, distinguendo situazione, compito personale, azioni e risultato documentato.

1. «Quando hai dovuto bilanciare velocità e sicurezza?» Usare la telefonia Simple.life: architettura backend, verifica di sicurezza e rilascio in produzione. Chiarire il contributo distinto di frontend e SRE.
2. «Come hai gestito un’interfaccia fra sistemi diversi?» Usare il gateway Intercom/Zendesk e i contratti API, distinguendo decisioni proprie e condivise.
3. «Racconta un miglioramento della stabilità sotto carico.» In airSlate ho ridotto il carico di picco del database principale rimuovendo colli di bottiglia e redistribuendo il lavoro. Descrivere diagnosi e verifica senza introdurre percentuali.
4. «Come hai mantenuto compatibilità durante un cambiamento?» Usare la pubblicazione parallela delle versioni degli eventi CRURATED, confermata in produzione.
5. «Come hai collaborato con figure non backend?» Usare la pianificazione airSlate con Product Management e Development, distinguendo influenza tecnica e decisione di prodotto.
6. «Come hai gestito una scadenza di rilascio?» Usare Hyprr dal prototipo alla beta chiusa; non attribuirsi da solo il risultato di tutta la squadra.
7. «Quando hai cambiato un processo ripetitivo?» Usare il motore Snowflake–Intercom e spiegare cambiamento e verifica.
8. «Come hai gestito dati sensibili?» Usare il numero di telefono non esposto all’interfaccia e i controlli sulle chiamate di Simple.life, evitando dettagli interni superflui.

## Technical Interview

**Alta priorità — PHP, API e integrazione frontend.** Aspettarsi un esercizio su endpoint REST: validazione, errori, autenticazione, paginazione, idempotenza, test e compatibilità dei contratti. Preparare un esempio PHP CRURATED, distinguendo responsabilità tecnica da scrittura di ogni componente. Spiegare come un contratto API viene concordato e modificato. Il gateway Simple.life era in Go.

**Alta priorità — SQL, prestazioni e scalabilità.** Ripassare indici, `EXPLAIN`, transazioni, lock, query lente e misure prima/dopo. Per airSlate descrivere colli di bottiglia osservati e intervento personale, senza cifre non ancorate. Distinguere MySQL, PostgreSQL ed Elasticsearch da una competenza generale NoSQL. In system design, trattare cache, code e rilascio graduale come ipotesi progettuali.

**Media priorità — rilascio, test e infrastruttura.** Preparare la pipeline CI/CD airSlate, una strategia di test API/database, casi di errore e rollback. GitHub Actions è nel CV; chiarire l’uso effettivo di Git. Linux, Nginx e Redis sono nello stack aziendale ma non nel CV verificato: studiarne il ruolo e dichiarare il livello d’uso reale.

**Bassa priorità — frontend e dominio.** Conoscere il ruolo di Twig e React nelle API, senza rivendicare sviluppo frontend. Il prodotto assegnato resta sconosciuto.

## CV Deep-Dive Questions

Per CRURATED, spiegare chi definì schema, versionamento e verifiche; quali funzioni Crutrade furono rilasciate; quale risultato si può dimostrare. Per Simple.life, il titolo resta Software Developer e il CV usa solo l’anno finale 2026: il mese di fine rapporto e il titolo più recente restano da chiarire. PHP compare soltanto nella sua riga Technologies, senza un risultato PHP attribuito.

Sul gateway Go, distinguere la prima demo B2B dall’adozione commerciale non documentata. Sull’agente AI, identificare le azioni implementate personalmente. Per Snowflake–Intercom, spiegare l’effetto sulle riletture storiche, senza contare righe di codice. Per airSlate, sostenere separatamente database e CI/CD; la migrazione ECS–Kubernetes non è confermata. Per PDFfiller, spiegare il ruolo nel servizio email; se emerge un vecchio CV, correggere il volume ordinario senza rivendicare una crescita personale non documentata.

## Company-Specific Preparation

Rileggere annuncio e pagine aziendali. Extendo si descrive come agenzia di sviluppo focalizzata su marketing, system integration ed e-commerce. Termoservice è presentato come gestione ordini B2B integrata con Zucchetti: usarlo per chiedere come Extendo governa contratti API, sincronizzazione ed errori. Fattura.it è software cloud di fatturazione elettronica. Non presumere che questi siano i prodotti assegnati al ruolo.

## Preparation Plan

**Da preparare subito:** confermare Fondi, diritto al lavoro, italiano, preavviso e aspettativa economica. Scegliere case history condivisibili su PHP/API CRURATED e prestazioni o integrazione. Allinearle al CV finale.

**Prima del colloquio tecnico:** provare API REST PHP e MySQL, ripassare diagnosi query, disegnare flusso eventi CRURATED e gateway Simple.life. Chiarire l’uso reale di Git, Linux, Nginx, Redis e test. Preparare un rilascio e un problema in produzione, precisando la responsabilità personale.

**Prima del finale/cultura:** provare le storie STAR ad alta voce. Rivedere motivazione, collaborazione e disponibilità pratica dopo aver chiarito i punti personali.

## Questions to Ask

1. Quale prodotto o cliente seguirebbe questa posizione nei primi mesi?
2. Quali problemi di API o integrazione frontend/backend hanno oggi la priorità?
3. Come misurate prestazioni e regressioni delle query MySQL in produzione?
4. Dove usate Elasticsearch e quali altri database NoSQL richiedono esperienza diretta?
5. Quali parti di Nginx e Redis sono di competenza quotidiana del backend developer?
6. Quali controlli automatici, test e passaggi di rilascio usate attualmente?
7. Come sono distribuite le decisioni tecniche tra developer, frontend, prodotto e responsabile tecnico?
8. Quanti giorni e con quale frequenza è richiesta la presenza a Fondi?
9. Quale formato e livello di dettaglio preferite per portfolio e case history, considerata la riservatezza?
10. Come valutate il successo della persona scelta dopo i primi tre mesi?
