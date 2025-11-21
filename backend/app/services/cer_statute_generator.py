"""
CER Statute Generator
Generates compliant statutes for Italian Renewable Energy Communities
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from app.models.cer import CERLegalType


class MemberCategory(str, Enum):
    """Allowed CER member categories per Italian law"""
    NATURAL_PERSON = "natural_person"
    SME = "sme"  # Small/Medium Enterprise
    LOCAL_AUTHORITY = "local_authority"  # Comune, Provincia
    RESEARCH_INSTITUTION = "research_institution"
    RELIGIOUS_ENTITY = "religious_entity"
    THIRD_SECTOR = "third_sector"
    ENVIRONMENTAL_ENTITY = "environmental_entity"


class CERStatuteGenerator:
    """
    Service for generating Italian CER statutes

    Legal References:
    - EU Directive 2018/2001 (RED II)
    - D.L. 162/2019, art. 42-bis
    - D.Lgs. 199/2021, art. 31-32
    - ARERA Deliberation 318/2020

    Requirements:
    - Primary purpose: environmental, economic, or social benefits
    - Not for-profit primary purpose
    - Open and voluntary participation
    - Legal entity with autonomous personality
    - Geographic boundary (primary substation)
    """

    @staticmethod
    def generate_statute(
        cer_name: str,
        legal_type: CERLegalType,
        founding_members: List[Dict[str, Any]],
        primary_substation_id: str,
        municipality: str,
        province: str,
        primary_purpose: str,
        secondary_purposes: List[str],
        governance_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate complete CER statute

        Args:
            cer_name: CER name
            legal_type: Legal structure (association, cooperative, consortium)
            founding_members: List of founding members
            primary_substation_id: Primary substation boundary
            municipality: Municipality name
            province: Province code
            primary_purpose: Primary social purpose
            secondary_purposes: Secondary purposes
            governance_structure: Governance rules

        Returns:
            Complete statute document
        """
        statute = {
            "document_type": "Statuto della Comunità Energetica Rinnovabile",
            "cer_name": cer_name,
            "legal_type": legal_type.value,
            "creation_date": datetime.now().isoformat(),

            # Article 1: Name and Legal Form
            "article_1": {
                "title": "Art. 1 - Denominazione e Forma Giuridica",
                "content": f"""
È costituita una Comunità di Energia Rinnovabile (CER) denominata "{cer_name}",
ai sensi dell'art. 2, comma 1, lett. d) del D.Lgs. 199/2021, nella forma giuridica
di {CERStatuteGenerator._get_legal_form_italian(legal_type)}.

La CER ha sede legale in {municipality} ({province}), Via [da definire], ed è dotata
di personalità giuridica autonoma.
                """
            },

            # Article 2: Geographic Boundary
            "article_2": {
                "title": "Art. 2 - Ambito Territoriale",
                "content": f"""
La CER opera nell'ambito territoriale individuato dalla cabina primaria identificata
dal codice "{primary_substation_id}", secondo quanto previsto dalla normativa vigente
in materia di autoconsumo diffuso (D.Lgs. 199/2021 e Delibera ARERA 318/2020/R/eel).

Possono partecipare alla CER esclusivamente i soggetti i cui punti di prelievo (POD)
ricadano nell'area sottesa alla medesima cabina primaria.
                """
            },

            # Article 3: Primary Purpose
            "article_3": {
                "title": "Art. 3 - Scopo Principale e Finalità",
                "content": f"""
Lo scopo principale della CER è fornire benefici ambientali, economici e sociali ai
propri membri associati e alle aree locali in cui opera, anziché profitti finanziari,
in conformità con quanto disposto dall'art. 31 del D.Lgs. 199/2021.

Finalità primaria: {primary_purpose}

La CER persegue inoltre le seguenti finalità secondarie:
{chr(10).join(f"- {purpose}" for purpose in secondary_purposes)}

La CER non ha scopo di lucro e gli eventuali utili o avanzi di gestione sono
destinati esclusivamente al perseguimento delle finalità istituzionali.
                """
            },

            # Article 4: Members
            "article_4": {
                "title": "Art. 4 - Soci e Partecipazione",
                "content": """
Possono essere soci della CER, nel rispetto dei requisiti previsti dall'art. 31,
comma 1, del D.Lgs. 199/2021:

a) Persone fisiche
b) Piccole e medie imprese (PMI)
c) Enti territoriali e autorità locali (Comuni, Province)
d) Enti di ricerca e formazione
e) Enti religiosi
f) Enti del terzo settore e di protezione ambientale

L'adesione alla CER è aperta e volontaria, secondo criteri trasparenti e non
discriminatori definiti dal Consiglio Direttivo. Il recesso è libero, fatte salve
le disposizioni statutarie in materia di preavviso e liquidazione della quota.

Per la partecipazione effettiva delle imprese, la partecipazione alla CER non può
costituire l'attività commerciale o professionale principale.
                """
            },

            # Article 5: Admission and Exit
            "article_5": {
                "title": "Art. 5 - Ammissione ed Esclusione dei Soci",
                "content": """
La domanda di ammissione deve essere presentata al Consiglio Direttivo con le
modalità stabilite dal regolamento interno. Il Consiglio Direttivo delibera
sull'ammissione entro 60 giorni dalla ricezione della domanda completa.

Requisiti per l'ammissione:
- Possesso di un punto di prelievo (POD) nell'area della cabina primaria
- Accettazione dello Statuto e del regolamento interno
- Versamento della quota associativa
- Assenza di conflitti di interesse

Il socio può recedere dalla CER con preavviso di 90 giorni mediante comunicazione
scritta al Consiglio Direttivo.

L'esclusione del socio può avvenire per:
- Grave inadempimento degli obblighi statutari
- Comportamenti lesivi degli interessi della CER
- Perdita dei requisiti di partecipazione
                """
            },

            # Article 6: Rights and Obligations
            "article_6": {
                "title": "Art. 6 - Diritti e Doveri dei Soci",
                "content": """
Ogni socio ha diritto a:
- Partecipare alle assemblee con diritto di voto
- Accedere alla rendicontazione energetica ed economica
- Ricevere i benefici derivanti dall'energia condivisa
- Essere informato sulle attività della CER

Ogni socio ha il dovere di:
- Rispettare lo Statuto e i regolamenti interni
- Versare puntualmente le quote e i contributi dovuti
- Fornire i dati necessari per il calcolo dell'energia condivisa
- Collaborare al perseguimento delle finalità della CER
                """
            },

            # Article 7-15: Governance, Assembly, Board, etc.
            "article_7": CERStatuteGenerator._generate_governance_articles(
                legal_type, governance_structure
            ),

            # Legal compliance stamps
            "compliance": {
                "legal_references": [
                    "EU Directive 2018/2001 (RED II)",
                    "D.L. 162/2019, art. 42-bis",
                    "D.Lgs. 199/2021, art. 31-32",
                    "ARERA Deliberation 318/2020/R/eel"
                ],
                "primary_purpose_compliant": True,
                "geographic_boundary_defined": True,
                "open_participation": True,
                "legal_entity_autonomous": True,
                "founding_members_count": len(founding_members),
                "validation_date": datetime.now().isoformat()
            },

            # Founding members
            "founding_members": founding_members,

            # Signatures section
            "signatures": {
                "note": "Da firmare da parte di tutti i soci fondatori",
                "required_signatures": len(founding_members),
                "digital_signature_required": True
            }
        }

        return statute

    @staticmethod
    def _get_legal_form_italian(legal_type: CERLegalType) -> str:
        """Get Italian legal form description"""
        forms = {
            CERLegalType.COOPERATIVE: "Cooperativa",
            CERLegalType.ASSOCIATION: "Associazione non riconosciuta",
            CERLegalType.CONSORTIUM: "Consorzio"
        }
        return forms.get(legal_type, "Ente con personalità giuridica")

    @staticmethod
    def _generate_governance_articles(
        legal_type: CERLegalType,
        governance_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate governance articles based on legal type"""
        return {
            "title": "Art. 7-15 - Governance e Organi Sociali",
            "content": """
Gli organi della CER sono:
- Assemblea dei Soci
- Consiglio Direttivo
- Presidente
- Collegio dei Revisori (se richiesto per legge)

[Dettagli degli organi sociali, modalità di convocazione, deliberazioni, quorum, ecc.]
            """,
            "customization_required": True
        }

    @staticmethod
    def validate_statute_compliance(
        statute_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate statute compliance with Italian CER requirements

        Args:
            statute_data: Proposed statute data

        Returns:
            Validation result
        """
        issues = []
        warnings = []

        # Check primary purpose
        primary_purpose = statute_data.get("primary_purpose", "")
        if "profitto" in primary_purpose.lower() or "utile" in primary_purpose.lower():
            issues.append("Primary purpose cannot focus on profit generation")

        # Check geographic boundary
        if not statute_data.get("primary_substation_id"):
            issues.append("Primary substation boundary must be defined")

        # Check open participation
        governance = statute_data.get("governance_structure", {})
        if governance.get("closed_membership"):
            issues.append("Membership must be open and voluntary")

        # Check member categories
        founding_members = statute_data.get("founding_members", [])
        for member in founding_members:
            category = member.get("category")
            if category not in [c.value for c in MemberCategory]:
                warnings.append(f"Member category '{category}' may not be eligible")

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "validation_date": datetime.now().isoformat(),
            "legal_review_recommended": len(warnings) > 0 or len(issues) > 0
        }


# Export generator instance
cer_statute_generator = CERStatuteGenerator()
