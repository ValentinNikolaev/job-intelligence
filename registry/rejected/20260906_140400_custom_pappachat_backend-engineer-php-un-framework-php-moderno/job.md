# Backend Engineer (PHP / un framework PHP moderno)

Posted: 2026-08-05

## Rejection

- Category: stale
- Reason: published_at 2026-08-05 is older than 7 days

Il backend di PappaChat è un'applicazione un framework PHP moderno multi-tenant che riceve messaggi da WhatsApp, Instagram, Messenger, Telegram, email e telefono, li porta all'assistente, conserva le conversazioni e ne ricava prenotazioni, contatti e notifiche. È in produzione, con clienti che pagano, e il traffico non aspetta il deploy.

Cerchiamo qualcuno a suo agio con webhook che arrivano fuori ordine, code che devono essere idempotenti e fornitori che rispondono con un errore proprio nel momento peggiore. Il codice è pulito e documentato, ma è un prodotto vero: ci sono anche gli angoli scomodi.

### Cosa farai

- Progettare e mantenere le API del pannello e le integrazioni con le piattaforme di messaggistica, la telefonia, i pagamenti e i calendari.
- Tenere in piedi il livello a code: ingest della base di conoscenza, invii, promemoria e monitor, con retry e idempotenza dove servono.
- Lavorare sul modello dati multi-tenant e sulle query che diventano lente quando il volume di messaggi cresce.
- Scrivere test sulle parti che, se si rompono, costano soldi: fatturazione, quote, permessi e consegna dei messaggi.
- Occuparti degli eventi di piattaforma e della diagnostica: quando un canale smette di consegnare deve accorgersene il sistema, non il cliente.
- Fare code review, deploy e, quando capita, leggere i log alle otto di sera perché qualcosa in produzione si comporta male.

### Cosa serve

- Almeno tre anni su PHP moderno e almeno un'applicazione un framework PHP moderno seria portata in produzione e poi mantenuta.
- un database relazionale a livello di piani di esecuzione, indici e transazioni, non solo di ORM.
- Esperienza reale con code, job falliti, retry e lavori pianificati.
- Capacità di integrare API di terze parti leggendo la documentazione, compresi i pezzi che la documentazione non dice.
- Attenzione a permessi e isolamento dei dati: in un prodotto multi-tenant una query senza scope è un incidente, non un bug.
- Italiano o inglese fluente per lavorare in un team piccolo e distribuito.

### Cosa aiuta, ma non è obbligatorio

- Integrazioni con piattaforme di messaggistica basate su webhook.
- la piattaforma di pagamenti: abbonamenti, cambi di piano, webhook di fatturazione.
- Ricerca semantica, embedding e ricerca ibrida.
- Code di lavoro, tempo reale su WebSocket, OAuth 2.1.
- Esperienza di gestione di incidenti o di reperibilità.

### I primi 90 giorni

- **Primi 30 giorni**: Metti in piedi l'ambiente locale, leggi la mappa del codice in docs/ e chiudi una serie di bug reali scelti apposta per farti attraversare tutto il sistema. Il primo deploy in produzione lo fai nella prima settimana.
- **Giorni 31-60**: Prendi in carico un'area intera (per esempio le prenotazioni, o un canale di messaggistica) e ne diventi la persona di riferimento: correzioni, evoluzioni e documentazione.
- **Giorni 61-90**: Progetti e consegni una funzionalità chiesta dai clienti, dal modello dati alla API, con i test e la documentazione che serviranno a chi verrà dopo di te.
