"""
Italian Workflow Phase Templates
Comprehensive templates based on Italian bureaucratic processes for renewable energy plants
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from app.core.italian_compliance_documents import ComplianceEntity, get_required_documents


def get_gse_rid_activation_phases() -> List[Dict[str, Any]]:
    """GSE RID (Ritiro Dedicato) Activation Workflow Phases"""
    return [
        {
            "name": "Raccolta Documenti Identificativi e Anagrafici",
            "description": "Raccolta documenti identificativi e anagrafici del produttore",
            "order": 1,
            "estimated_days": 5,
            "responsible_entity": ComplianceEntity.GSE.value,
            "practice_type": "RID Activation - Document Collection",
            "required_documents": [
                "Company Registration Documents (Visura Camerale)",
                "Tax Code Certificate (Codice Fiscale)",
                "VAT Registration (Partita IVA)",
                "PEC Email Certificate (Postnominata Certificata)",
                "Bank Account Details (IBAN)",
            ],
            "official_form_fields": {
                "produttore_denominazione": "Denominazione/Ragione sociale",
                "produttore_cf_piva": "Codice fiscale/P.IVA",
                "produttore_indirizzo": "Indirizzo sede legale",
                "produttore_pec": "Indirizzo PEC",
                "produttore_telefono": "Telefono",
                "rappresentante_legale": "Nome rappresentante legale",
                "iban": "Codice IBAN per accrediti",
            },
            "checklist_items": [
                "Verifica validità Visura Camerale (non superiore a 90 giorni)",
                "Controllo PEC attiva e verificata",
                "Validazione IBAN",
                "Verifica corrispondenza dati anagrafici",
            ],
            "instructions": "Raccogliere tutti i documenti identificativi e anagrafici. La Visura Camerale deve essere rilasciata non più di 90 giorni prima della presentazione. Verificare che la PEC sia attiva e funzionante.",
            "portal_url": "https://www.gse.it/portale-gse",
            "portal_login_url": "https://portale.gse.it/",
            "required_credentials": "SPID/CIE/CNS",
            "submission_method": "Portal upload",
            "requires_human_auth": True,
            "external_resources": [
                "https://www.gse.it/documenti_site/Documenti%20GSE/Servizi%20per%20te/Tecnologie/Fotovoltaico/GSE_Guida_RID.pdf",
            ],
        },
        {
            "name": "Raccolta Documenti Tecnici Impianto",
            "description": "Raccolta documentazione tecnica dell'impianto",
            "order": 2,
            "estimated_days": 7,
            "responsible_entity": ComplianceEntity.GSE.value,
            "practice_type": "RID Activation - Technical Documentation",
            "required_documents": [
                "Plant Technical Specifications (Scheda Tecnica Impianto)",
                "Technical Connection Document (TICA)",
                "Electrical Diagram (Schema Elettrico)",
                "Meter Configuration Data",
            ],
            "official_form_fields": {
                "potenza_impianto_kwp": "Potenza nominale impianto (kWp)",
                "tipologia_impianto": "Tipologia impianto",
                "codice_censimp": "Codice CENSIMP",
                "tipo_connessione": "Tipo connessione",
                "data_entrata_esercizio": "Data entrata in esercizio",
                "coordinate_geografiche": "Coordinate geografiche impianto",
            },
            "checklist_items": [
                "Verifica firma tecnico abilitato su documenti tecnici",
                "Controllo completezza Scheda Tecnica",
                "Validazione TICA valido",
                "Verifica corrispondenza dati tecnici con GAUDÌ",
            ],
            "instructions": "Tutti i documenti tecnici devono essere firmati da professionista abilitato. La Scheda Tecnica deve contenere tutti i dati richiesti dal GSE. Verificare che i dati corrispondano a quelli registrati su GAUDÌ.",
            "requires_physical_signature": True,
            "external_resources": [
                "https://www.gse.it/documenti_site/Documenti%20GSE/Servizi%20per%20te/Tecnologie/Fotovoltaico/GSE_Guida_RID.pdf",
            ],
        },
        {
            "name": "Dichiarazione Antimafia",
            "description": "Compilazione e presentazione Dichiarazione Antimafia (se richiesta)",
            "order": 3,
            "estimated_days": 3,
            "responsible_entity": ComplianceEntity.GSE.value,
            "practice_type": "RID Activation - Anti-Mafia Declaration",
            "required_documents": [
                "Anti-Mafia Declaration (Dichiarazione Antimafia)",
            ],
            "official_form_fields": {
                "richiedente_denominazione": "Denominazione richiedente",
                "richiedente_cf": "Codice fiscale",
                "richiedente_qualifica": "Qualifica del dichiarante",
                "dichiarazione_data": "Data dichiarazione",
            },
            "checklist_items": [
                "Verifica se obbligatoria (incentivi >€150k/anno)",
                "Compilazione modulo dichiarazione",
                "Firma dichiarante",
            ],
            "instructions": "La Dichiarazione Antimafia è obbligatoria se gli incentivi superano €150.000/anno. Compilare il modulo ufficiale GSE e farlo firmare dal legale rappresentante.",
            "regulatory_deadline": None,  # No specific deadline, but required before activation
            "deadline_type": "ordinary",
            "requires_physical_signature": True,
            "external_resources": [
                "https://www.gse.it/documenti_site/Documenti%20GSE/Servizi%20per%20te/Tecnologie/Fotovoltaico/GSE_Guida_RID.pdf",
            ],
        },
        {
            "name": "Caricamento Documentazione su Portale GSE",
            "description": "Upload di tutta la documentazione sul portale GSE",
            "order": 4,
            "estimated_days": 2,
            "responsible_entity": ComplianceEntity.GSE.value,
            "practice_type": "RID Activation - Portal Upload",
            "required_documents": [
                "All previous documents",
            ],
            "checklist_items": [
                "Accesso portale GSE con SPID/CIE",
                "Verifica completezza documenti",
                "Conversione formato PDF (se necessario)",
                "Upload documenti sul portale",
                "Conferma ricezione GSE",
            ],
            "instructions": "Accedere al portale GSE con credenziali SPID/CIE/CNS. Verificare che tutti i documenti siano in formato PDF e non superino le dimensioni massime consentite. Caricare tutti i documenti nella sezione dedicata.",
            "portal_url": "https://portale.gse.it/",
            "portal_login_url": "https://portale.gse.it/",
            "required_credentials": "SPID/CIE/CNS",
            "submission_method": "Portal upload",
            "requires_human_auth": True,
            "external_resources": [
                "https://portale.gse.it/",
            ],
        },
        {
            "name": "Attesa Risposta e Attivazione RID",
            "description": "Attesa risposta GSE e attivazione contratto RID",
            "order": 5,
            "estimated_days": 45,
            "responsible_entity": ComplianceEntity.GSE.value,
            "practice_type": "RID Activation - Contract Activation",
            "required_documents": [
                "RID Contract (Convenzione RID)",
            ],
            "checklist_items": [
                "Monitoraggio stato pratica su portale",
                "Verifica eventuali richieste integrazione",
                "Firma Convenzione RID",
                "Conferma attivazione contratto",
            ],
            "instructions": "Il GSE ha 45 giorni per rispondere. Monitorare lo stato della pratica sul portale. In caso di richieste di integrazione, rispondere tempestivamente. Una volta approvata, firmare la Convenzione RID.",
            "regulatory_deadline": None,  # GSE has 45 days to respond
            "deadline_type": "ordinary",
            "deadline_consequences": "Ritardo nell'attivazione degli incentivi",
            "external_resources": [
                "https://portale.gse.it/",
            ],
        },
    ]


def get_terna_gaudi_registration_phases() -> List[Dict[str, Any]]:
    """Terna GAUDÌ Plant Registration Workflow Phases"""
    return [
        {
            "name": "Raccolta Documenti Connessione",
            "description": "Raccolta documentazione tecnica di connessione",
            "order": 1,
            "estimated_days": 5,
            "responsible_entity": ComplianceEntity.TERNA.value,
            "practice_type": "GAUDÌ Registration - Connection Documents",
            "required_documents": [
                "Technical Connection Document (TICA)",
                "Electrical Diagram (Schema Elettrico)",
                "Production Unit Specifications",
                "Meter Configuration Data",
            ],
            "official_form_fields": {
                "codice_utente": "Codice utente GAUDÌ",
                "impianto_codice": "Codice impianto",
                "potenza_nominale": "Potenza nominale (kW)",
                "tipologia_impianto": "Tipologia impianto",
                "tipo_connessione": "Tipo connessione",
                "codice_censimp": "Codice CENSIMP",
            },
            "checklist_items": [
                "Verifica TICA valido",
                "Controllo completezza schema elettrico",
                "Validazione dati unità di produzione",
                "Verifica configurazione contatori",
            ],
            "instructions": "Raccogliere tutti i documenti tecnici di connessione. Il TICA deve essere valido e non scaduto. Lo schema elettrico deve essere completo e firmato da tecnico abilitato.",
            "requires_physical_signature": True,
            "external_resources": [
                "https://gaudi.terna.it/",
            ],
        },
        {
            "name": "Registrazione Anagrafica su GAUDÌ",
            "description": "Registrazione anagrafica produttore su portale GAUDÌ",
            "order": 2,
            "estimated_days": 2,
            "responsible_entity": ComplianceEntity.TERNA.value,
            "practice_type": "GAUDÌ Registration - Producer Registration",
            "required_documents": [
                "Company Registration Documents",
                "Tax Code Certificate",
            ],
            "official_form_fields": {
                "produttore_denominazione": "Denominazione produttore",
                "produttore_cf_piva": "Codice fiscale/P.IVA",
                "produttore_indirizzo": "Indirizzo",
                "produttore_pec": "PEC",
            },
            "checklist_items": [
                "Accesso portale GAUDÌ",
                "Inserimento dati anagrafici",
                "Upload documenti identificativi",
                "Conferma registrazione",
            ],
            "instructions": "Accedere al portale GAUDÌ e registrare l'anagrafica del produttore. Inserire tutti i dati richiesti e caricare i documenti identificativi.",
            "portal_url": "https://gaudi.terna.it/",
            "portal_login_url": "https://gaudi.terna.it/",
            "required_credentials": "SPID/CIE/CNS",
            "submission_method": "Portal upload",
            "requires_human_auth": True,
            "external_resources": [
                "https://gaudi.terna.it/",
            ],
        },
        {
            "name": "Registrazione Impianto e Richiesta CENSIMP",
            "description": "Registrazione impianto su GAUDÌ e richiesta codice CENSIMP",
            "order": 3,
            "estimated_days": 3,
            "responsible_entity": ComplianceEntity.TERNA.value,
            "practice_type": "GAUDÌ Registration - Plant Registration",
            "required_documents": [
                "Plant Technical Sheet (Scheda Tecnica Impianto GAUDÌ)",
                "All connection documents",
            ],
            "official_form_fields": {
                "impianto_denominazione": "Denominazione impianto",
                "impianto_indirizzo": "Indirizzo impianto",
                "potenza_nominale_kw": "Potenza nominale (kW)",
                "tipologia_impianto": "Tipologia",
                "codice_pod": "Codice POD",
                "coordinate_geografiche": "Coordinate geografiche",
            },
            "checklist_items": [
                "Inserimento dati tecnici impianto",
                "Upload Scheda Tecnica",
                "Richiesta codice CENSIMP",
                "Verifica generazione codice",
            ],
            "instructions": "Registrare l'impianto sul portale GAUDÌ inserendo tutti i dati tecnici. Caricare la Scheda Tecnica completa. Richiedere il codice CENSIMP che verrà generato automaticamente.",
            "regulatory_deadline": None,  # Must be done within 30 days of connection
            "deadline_type": "peremptory",
            "deadline_consequences": "Mancata registrazione comporta sanzioni",
            "external_resources": [
                "https://gaudi.terna.it/",
            ],
        },
        {
            "name": "Verifica e Riconciliazione Dati",
            "description": "Verifica correttezza dati e riconciliazione con DSO",
            "order": 4,
            "estimated_days": 5,
            "responsible_entity": ComplianceEntity.TERNA.value,
            "practice_type": "GAUDÌ Registration - Data Reconciliation",
            "required_documents": [],
            "checklist_items": [
                "Verifica corrispondenza dati con DSO",
                "Controllo configurazione contatori",
                "Validazione dati produzione",
                "Conferma riconciliazione",
            ],
            "instructions": "Verificare che tutti i dati registrati su GAUDÌ corrispondano a quelli del DSO. In caso di discrepanze, aggiornare i dati sul portale.",
            "external_resources": [
                "https://gaudi.terna.it/",
            ],
        },
    ]


def get_dso_tica_request_phases() -> List[Dict[str, Any]]:
    """DSO TICA Request Workflow Phases"""
    return [
        {
            "name": "Raccolta Documenti Tecnici",
            "description": "Raccolta documentazione tecnica per richiesta TICA",
            "order": 1,
            "estimated_days": 7,
            "responsible_entity": ComplianceEntity.DSO.value,
            "practice_type": "TICA Request - Technical Documents",
            "required_documents": [
                "Progetto e Schema Unifilare (firmato da tecnico abilitato)",
                "Disposizione moduli fotovoltaici",
                "Schema inverter e quadri elettrici",
                "Schema collegamenti elettrici",
            ],
            "official_form_fields": {
                "progettista_nome": "Nome e cognome progettista",
                "progettista_albo": "Numero iscrizione albo professionale",
                "progettista_provincia": "Provincia albo",
                "potenza_impianto_kwp": "Potenza nominale impianto (kWp)",
                "n_moduli": "Numero moduli fotovoltaici",
                "n_inverter": "Numero inverter",
            },
            "checklist_items": [
                "Verifica firma tecnico abilitato",
                "Controllo completezza progetto",
                "Validazione schema unifilare",
            ],
            "instructions": "Tutti i documenti tecnici devono essere firmati da professionista abilitato. Il progetto deve essere completo e conforme alle normative vigenti.",
            "requires_physical_signature": True,
            "external_resources": [],
        },
        {
            "name": "Raccolta Documentazione Anagrafica e Catastale",
            "description": "Raccolta documenti anagrafici e catastali del richiedente",
            "order": 2,
            "estimated_days": 3,
            "responsible_entity": ComplianceEntity.DSO.value,
            "practice_type": "TICA Request - Identity Documents",
            "required_documents": [
                "Copia ultima bolletta elettrica",
                "Documento identità intestatario (fronte/retro)",
                "Mappa catastale (rilascio non anteriore a 6 mesi)",
                "Codice IBAN per accrediti",
            ],
            "checklist_items": [
                "Verifica validità documento identità",
                "Controllo data rilascio mappa catastale",
                "Validazione IBAN",
            ],
            "instructions": "La mappa catastale deve essere rilasciata non più di 6 mesi prima della presentazione. Verificare che il documento di identità sia valido.",
            "external_resources": [],
        },
        {
            "name": "Inserimento Anagrafica Produttore su Portale DSO",
            "description": "Registrazione anagrafica del produttore sul portale DSO",
            "order": 3,
            "estimated_days": 2,
            "responsible_entity": ComplianceEntity.DSO.value,
            "practice_type": "TICA Request - Producer Registration",
            "required_documents": [
                "Copia ultima bolletta elettrica",
                "Documento identità intestatario",
                "Mappa catastale",
                "Codice IBAN",
            ],
            "official_form_fields": {
                "produttore_denominazione": "Denominazione/Ragione sociale",
                "produttore_cf_piva": "Codice fiscale/P.IVA",
                "produttore_indirizzo": "Indirizzo sede legale",
                "produttore_pec": "Indirizzo PEC",
                "produttore_telefono": "Telefono",
                "rappresentante_legale": "Nome rappresentante legale",
            },
            "checklist_items": [
                "Accesso portale DSO",
                "Inserimento dati anagrafici",
                "Upload documentazione",
                "Conferma registrazione",
            ],
            "instructions": "Accedere al portale del DSO (es. E-Distribuzione) e registrare l'anagrafica del produttore. Inserire tutti i dati richiesti e caricare i documenti.",
            "portal_url": "https://www.e-distribuzione.it/",
            "portal_login_url": "https://www.e-distribuzione.it/area-riservata",
            "required_credentials": "Email registration",
            "submission_method": "Portal upload",
            "external_resources": [
                "https://www.e-distribuzione.it/",
            ],
        },
        {
            "name": "Inserimento Anagrafica Impianto",
            "description": "Inserimento dati tecnici dell'impianto sul portale",
            "order": 4,
            "estimated_days": 2,
            "responsible_entity": ComplianceEntity.DSO.value,
            "practice_type": "TICA Request - Plant Registration",
            "required_documents": [
                "Dati tecnici impianto",
                "Coordinate geografiche",
                "POD di riferimento (se esistente)",
            ],
            "official_form_fields": {
                "potenza_nominale": "Potenza nominale",
                "dati_ubicazione": "Dati ubicazione",
                "tipologia_connessione": "Tipologia connessione",
            ],
            "checklist_items": [
                "Inserimento potenza nominale",
                "Inserimento dati ubicazione",
                "Selezione tipologia connessione",
            ],
            "instructions": "Inserire tutti i dati tecnici dell'impianto sul portale DSO. Verificare che i dati corrispondano a quelli del progetto tecnico.",
            "external_resources": [],
        },
        {
            "name": "Caricamento Documentazione Completa",
            "description": "Upload di tutta la documentazione sul portale DSO",
            "order": 5,
            "estimated_days": 2,
            "responsible_entity": ComplianceEntity.DSO.value,
            "practice_type": "TICA Request - Document Upload",
            "required_documents": [
                "All previous documents",
            ],
            "checklist_items": [
                "Verifica completezza documenti",
                "Conversione formato PDF",
                "Upload sul portale",
                "Conferma ricezione DSO",
            ],
            "instructions": "La documentazione deve essere caricata in formato PDF. Verificare che tutti i documenti siano presenti prima del caricamento.",
            "submission_method": "Portal upload",
            "external_resources": [],
        },
        {
            "name": "Attesa Risposta e Ricezione TICA",
            "description": "Attesa risposta DSO e ricezione TICA",
            "order": 6,
            "estimated_days": 45,
            "responsible_entity": ComplianceEntity.DSO.value,
            "practice_type": "TICA Request - TICA Reception",
            "required_documents": [
                "TICA (Technical Connection Document)",
            ],
            "checklist_items": [
                "Monitoraggio stato pratica",
                "Verifica eventuali richieste integrazione",
                "Ricezione TICA",
                "Verifica validità TICA",
            ],
            "instructions": "Il DSO ha 45 giorni per rispondere. Monitorare lo stato della pratica sul portale. Una volta ricevuto il TICA, verificare che sia valido e completo.",
            "regulatory_deadline": None,  # DSO has 45 days to respond
            "deadline_type": "ordinary",
            "deadline_consequences": "Ritardo nella connessione dell'impianto",
            "external_resources": [],
        },
    ]


def get_adm_utf_license_phases() -> List[Dict[str, Any]]:
    """ADM UTF License Application Workflow Phases (for plants >20kW)"""
    return [
        {
            "name": "Raccolta Documentazione UTF",
            "description": "Raccolta documentazione per richiesta licenza UTF",
            "order": 1,
            "estimated_days": 10,
            "responsible_entity": ComplianceEntity.ADM.value,
            "practice_type": "UTF License - Document Collection",
            "required_documents": [
                "UTF License Application (Domanda Licenza UTF)",
                "Photo of Meter Group (Foto Gruppo di Misura) - With model and serial number",
                "Workshop Declaration (Denuncia Attività di Officina Elettrica)",
                "General Site Plan (Planimetria Generale Officina)",
                "Technical Report (Relazione Tecnica) - By licensed technician",
                "Single-Line Electrical Diagram (Schema Unifilare Impianto Elettrico)",
                "Compliance Declaration (Dichiarazione Conformità)",
            ],
            "official_form_fields": {
                "richiedente_denominazione": "Denominazione richiedente",
                "richiedente_cf_piva": "Codice fiscale/P.IVA",
                "impianto_indirizzo": "Indirizzo impianto",
                "potenza_nominale_kw": "Potenza nominale (kW)",
                "modello_contatore": "Modello contatore",
                "numero_seriale_contatore": "Numero seriale contatore",
            },
            "checklist_items": [
                "Verifica potenza impianto (>20kW)",
                "Foto gruppo di misura con modello e seriale",
                "Relazione tecnica firmata da tecnico abilitato",
                "Controllo completezza documentazione",
            ],
            "instructions": "La licenza UTF è obbligatoria per impianti con potenza superiore a 20kW. La foto del gruppo di misura deve mostrare chiaramente modello e numero seriale. La relazione tecnica deve essere firmata da tecnico abilitato.",
            "requires_physical_signature": True,
            "external_resources": [
                "https://www.adm.gov.it/",
            ],
        },
        {
            "name": "Caricamento Documentazione su Portale ADM",
            "description": "Upload documentazione sul portale ADM",
            "order": 2,
            "estimated_days": 2,
            "responsible_entity": ComplianceEntity.ADM.value,
            "practice_type": "UTF License - Portal Upload",
            "required_documents": [
                "All previous documents",
            ],
            "checklist_items": [
                "Accesso portale ADM",
                "Verifica formato documenti (PDF)",
                "Upload documentazione",
                "Conferma ricezione",
            ],
            "instructions": "Accedere al portale ADM e caricare tutta la documentazione. Verificare che i documenti siano in formato PDF.",
            "portal_url": "https://www.adm.gov.it/",
            "portal_login_url": "https://www.adm.gov.it/",
            "required_credentials": "SPID/CIE/CNS",
            "submission_method": "Portal upload",
            "requires_human_auth": True,
            "external_resources": [
                "https://www.adm.gov.it/",
            ],
        },
        {
            "name": "Attesa Risposta e Ricezione Licenza",
            "description": "Attesa risposta ADM e ricezione licenza UTF",
            "order": 3,
            "estimated_days": 60,
            "responsible_entity": ComplianceEntity.ADM.value,
            "practice_type": "UTF License - License Reception",
            "required_documents": [
                "UTF License (Licenza UTF)",
            ],
            "checklist_items": [
                "Monitoraggio stato pratica",
                "Verifica eventuali richieste integrazione",
                "Ricezione licenza UTF",
                "Verifica validità licenza",
            ],
            "instructions": "L'ADM ha 60 giorni per rispondere. Monitorare lo stato della pratica. Una volta ricevuta la licenza, verificare che sia valida e conservarla per gli adempimenti annuali.",
            "regulatory_deadline": None,  # ADM has 60 days to respond
            "deadline_type": "ordinary",
            "deadline_consequences": "Impossibilità di esercizio legale dell'impianto",
            "external_resources": [],
        },
    ]


def get_comune_authorization_phases(power_kw: float) -> List[Dict[str, Any]]:
    """Comune Authorization Workflow Phases (varies by power)"""
    if power_kw < 20:
        # CILA (Comunicazione Inizio Lavori Asseverata)
        return [
            {
                "name": "Raccolta Documentazione CILA",
                "description": "Raccolta documentazione per CILA (<20kW)",
                "order": 1,
                "estimated_days": 5,
                "responsible_entity": ComplianceEntity.COMUNE.value,
                "practice_type": "CILA - Document Collection",
                "required_documents": [
                    "CILA Form (Modulo CILA)",
                    "Technical Report (Relazione Tecnica)",
                    "Site Plan (Planimetria)",
                    "Project Drawings (Disegni Progetto)",
                ],
                "official_form_fields": {
                    "richiedente_nome": "Nome richiedente",
                    "richiedente_cf": "Codice fiscale",
                    "impianto_indirizzo": "Indirizzo impianto",
                    "potenza_kw": "Potenza impianto (kW)",
                },
                "checklist_items": [
                    "Verifica potenza <20kW",
                    "Compilazione modulo CILA",
                    "Relazione tecnica completa",
                ],
                "instructions": "Per impianti <20kW è sufficiente la CILA. Compilare il modulo ufficiale e allegare la documentazione tecnica.",
                "external_resources": [],
            },
        ]
    elif power_kw < 200:
        # PAS (Procedura Abilitativa Semplificata)
        return [
            {
                "name": "Raccolta Documentazione PAS",
                "description": "Raccolta documentazione per PAS (20-200kW)",
                "order": 1,
                "estimated_days": 15,
                "responsible_entity": ComplianceEntity.COMUNE.value,
                "practice_type": "PAS - Document Collection",
                "required_documents": [
                    "PAS Application (Domanda PAS)",
                    "Environmental Impact Assessment (Valutazione Impatto Ambientale)",
                    "Technical Documentation (Documentazione Tecnica Completa)",
                    "Building Permit (Permesso di Costruire)",
                ],
                "official_form_fields": {
                    "richiedente_denominazione": "Denominazione richiedente",
                    "impianto_indirizzo": "Indirizzo impianto",
                    "potenza_kw": "Potenza impianto (kW)",
                    "superficie_utilizzata": "Superficie utilizzata (mq)",
                },
                "checklist_items": [
                    "Verifica potenza 20-200kW",
                    "Valutazione impatto ambientale",
                    "Documentazione tecnica completa",
                ],
                "instructions": "Per impianti 20-200kW è richiesta la PAS. Includere la valutazione di impatto ambientale e la documentazione tecnica completa.",
                "requires_site_inspection": True,
                "external_resources": [],
            },
        ]
    else:
        # AU (Autorizzazione Unica Regionale)
        return [
            {
                "name": "Raccolta Documentazione AU",
                "description": "Raccolta documentazione per AU (>200kW)",
                "order": 1,
                "estimated_days": 30,
                "responsible_entity": ComplianceEntity.COMUNE.value,
                "practice_type": "AU - Document Collection",
                "required_documents": [
                    "AU Application (Domanda Autorizzazione Unica)",
                    "Environmental Impact Study (Studio Impatto Ambientale)",
                    "Landscape Impact Assessment (Valutazione Impatto Paesaggistico)",
                    "Complete Technical Documentation (Documentazione Tecnica Completa)",
                ],
                "official_form_fields": {
                    "richiedente_denominazione": "Denominazione richiedente",
                    "impianto_indirizzo": "Indirizzo impianto",
                    "potenza_kw": "Potenza impianto (kW)",
                    "superficie_utilizzata": "Superficie utilizzata (mq)",
                },
                "checklist_items": [
                    "Verifica potenza >200kW",
                    "Studio impatto ambientale completo",
                    "Valutazione impatto paesaggistico",
                    "Documentazione tecnica completa",
                ],
                "instructions": "Per impianti >200kW è richiesta l'Autorizzazione Unica Regionale. Includere studio di impatto ambientale completo e valutazione di impatto paesaggistico.",
                "requires_site_inspection": True,
                "external_resources": [],
            },
        ]


def get_all_italian_workflow_templates() -> Dict[str, List[Dict[str, Any]]]:
    """Get all Italian workflow phase templates"""
    return {
        "gse_rid_activation": get_gse_rid_activation_phases(),
        "terna_gaudi_registration": get_terna_gaudi_registration_phases(),
        "dso_tica_request": get_dso_tica_request_phases(),
        "adm_utf_license": get_adm_utf_license_phases(),
        "comune_authorization_20kw": get_comune_authorization_phases(15),
        "comune_authorization_100kw": get_comune_authorization_phases(100),
        "comune_authorization_300kw": get_comune_authorization_phases(300),
    }

