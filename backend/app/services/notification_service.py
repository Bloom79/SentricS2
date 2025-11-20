"""
Notification Service for Italian CER Operations
Handles email notifications, deadline alerts, and member communications
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of notifications"""
    # Member notifications
    WELCOME = "welcome"
    MONTHLY_REPORT = "monthly_report"
    BILLING_STATEMENT = "billing_statement"
    PAYMENT_REMINDER = "payment_reminder"
    INVOICE_AVAILABLE = "invoice_available"

    # Administrator notifications
    GSE_RESPONSE = "gse_response"
    DOCUMENT_APPROVAL_REQUIRED = "document_approval_required"
    PAYMENT_RECEIVED = "payment_received"
    SYSTEM_ALERT = "system_alert"

    # Compliance deadline alerts
    DEADLINE_30_DAYS = "deadline_30_days"
    DEADLINE_15_DAYS = "deadline_15_days"
    DEADLINE_7_DAYS = "deadline_7_days"
    DEADLINE_3_DAYS = "deadline_3_days"
    DEADLINE_1_DAY = "deadline_1_day"
    DEADLINE_OVERDUE = "deadline_overdue"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(str, Enum):
    """Communication channels"""
    EMAIL = "email"
    SMS = "sms"
    PEC = "pec"  # Italian certified email
    IN_APP = "in_app"


class NotificationService:
    """
    Service for managing notifications and alerts for CER operations

    Features:
    - Email notifications to members and administrators
    - Deadline tracking and alerts
    - Italian language templates
    - PEC (certified email) integration
    - SMS alerts (optional)
    """

    # GSE deadline - 120 days from plant commissioning
    GSE_APPLICATION_DEADLINE_DAYS = 120

    # Terna GAUDÌ deadline - 30 days from grid connection
    TERNA_REGISTRATION_DEADLINE_DAYS = 30

    # DSO response deadline - 20 working days
    DSO_RESPONSE_DEADLINE_DAYS = 20

    @staticmethod
    def send_member_welcome(
        member_email: str,
        member_name: str,
        cer_name: str,
        join_date: datetime,
        portal_url: str
    ) -> Dict[str, Any]:
        """
        Send welcome email to new CER member

        Args:
            member_email: Member email address
            member_name: Member name
            cer_name: CER name
            join_date: Date member joined
            portal_url: URL to member portal

        Returns:
            Dictionary with notification details
        """
        email_subject = f"Benvenuto in {cer_name}!"
        email_body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5282;">Benvenuto/a {member_name}!</h2>

                <p>Siamo lieti di darti il benvenuto nella <strong>{cer_name}</strong> a partire dal {join_date.strftime("%d/%m/%Y")}.</p>

                <div style="background-color: #f7fafc; border-left: 4px solid #4299e1; padding: 15px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c5282;">Cos'è una Comunità Energetica Rinnovabile (CER)?</h3>
                    <p>Una CER è un'associazione di cittadini, attività commerciali e imprese che condividono energia rinnovabile prodotta localmente. I benefici includono:</p>
                    <ul>
                        <li>Riduzione dei costi energetici</li>
                        <li>Incentivi GSE per l'energia condivisa</li>
                        <li>Contributo alla transizione energetica</li>
                        <li>Riduzione delle emissioni di CO₂</li>
                    </ul>
                </div>

                <h3 style="color: #2c5282;">Accesso al Portale</h3>
                <p>Puoi accedere al tuo portale personale per monitorare:</p>
                <ul>
                    <li>La tua produzione e consumo di energia</li>
                    <li>L'energia condivisa con la comunità</li>
                    <li>I risparmi e gli incentivi maturati</li>
                    <li>Le fatture e i pagamenti</li>
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{portal_url}" style="background-color: #4299e1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Accedi al Portale
                    </a>
                </div>

                <div style="background-color: #fff5f5; border-left: 4px solid #fc8181; padding: 15px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #c53030;">Informazioni Importanti</h4>
                    <p>Riceverai mensilmente un report dettagliato sulla tua partecipazione alla CER. Le fatture saranno disponibili nel portale e riceverai una notifica via email.</p>
                </div>

                <h3 style="color: #2c5282;">Hai Domande?</h3>
                <p>Per qualsiasi dubbio o richiesta, puoi contattarci via email. Siamo qui per aiutarti!</p>

                <p style="margin-top: 30px;">Cordiali saluti,<br>
                <strong>Il team di {cer_name}</strong></p>

                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                <p style="font-size: 12px; color: #718096;">
                    Questa è una comunicazione automatica. Per favore non rispondere a questa email.
                </p>
            </div>
        </body>
        </html>
        """

        notification = {
            "type": NotificationType.WELCOME,
            "priority": NotificationPriority.MEDIUM,
            "channel": NotificationChannel.EMAIL,
            "recipient": member_email,
            "subject": email_subject,
            "body_html": email_body_html,
            "scheduled_at": datetime.now(),
            "status": "pending",
            "metadata": {
                "member_name": member_name,
                "cer_name": cer_name,
                "join_date": join_date.isoformat()
            }
        }

        logger.info(f"Welcome notification prepared for {member_email}")
        return notification

    @staticmethod
    def send_monthly_energy_report(
        member_email: str,
        member_name: str,
        cer_name: str,
        period_start: datetime,
        period_end: datetime,
        energy_data: Dict[str, float],
        financial_data: Dict[str, float],
        portal_url: str
    ) -> Dict[str, Any]:
        """
        Send monthly energy sharing report to member

        Args:
            member_email: Member email
            member_name: Member name
            cer_name: CER name
            period_start: Period start date
            period_end: Period end date
            energy_data: Energy production/consumption data
            financial_data: Financial data (incentives, savings)
            portal_url: Portal URL

        Returns:
            Notification dictionary
        """
        month_name = period_start.strftime("%B %Y")

        email_subject = f"Report Mensile {cer_name} - {month_name}"
        email_body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5282;">Report Mensile - {month_name}</h2>

                <p>Gentile {member_name},</p>
                <p>Ecco il riepilogo della tua partecipazione alla <strong>{cer_name}</strong> per il mese di {month_name}.</p>

                <div style="background-color: #f0fff4; border: 1px solid #9ae6b4; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #22543d;">📊 Dati Energetici</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">Energia Prodotta</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">{energy_data.get('produced', 0):.2f} kWh</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">Energia Consumata</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">{energy_data.get('consumed', 0):.2f} kWh</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">Energia Condivisa</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold; color: #38a169;">{energy_data.get('shared', 0):.2f} kWh</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0;">Autoconsumo</td>
                            <td style="padding: 8px 0; text-align: right; font-weight: bold;">{energy_data.get('self_consumed', 0):.2f} kWh</td>
                        </tr>
                    </table>
                </div>

                <div style="background-color: #fffaf0; border: 1px solid #fbd38d; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #7c2d12;">💰 Benefici Economici</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">Incentivi GSE</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">€{financial_data.get('incentives', 0):.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">Risparmio Bolletta</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">€{financial_data.get('savings', 0):.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">Contributo Fondo Comune</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">-€{financial_data.get('community_fund', 0):.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-size: 18px;">Totale Mensile</td>
                            <td style="padding: 8px 0; text-align: right; font-weight: bold; font-size: 18px; color: #38a169;">€{financial_data.get('total_benefit', 0):.2f}</td>
                        </tr>
                    </table>
                </div>

                <div style="background-color: #ebf8ff; border: 1px solid #90cdf4; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e4e8c;">🌍 Impatto Ambientale</h3>
                    <p>La tua partecipazione ha evitato l'emissione di <strong>{energy_data.get('co2_avoided', 0):.2f} kg di CO₂</strong> nell'atmosfera!</p>
                    <p style="font-size: 14px; color: #4a5568;">Equivalente a piantare {energy_data.get('trees_equivalent', 0)} alberi.</p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{portal_url}" style="background-color: #4299e1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Vedi Dettagli nel Portale
                    </a>
                </div>

                <p style="margin-top: 30px;">Cordiali saluti,<br>
                <strong>Il team di {cer_name}</strong></p>

                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                <p style="font-size: 12px; color: #718096;">
                    Report generato automaticamente per il periodo dal {period_start.strftime("%d/%m/%Y")} al {period_end.strftime("%d/%m/%Y")}.
                </p>
            </div>
        </body>
        </html>
        """

        notification = {
            "type": NotificationType.MONTHLY_REPORT,
            "priority": NotificationPriority.MEDIUM,
            "channel": NotificationChannel.EMAIL,
            "recipient": member_email,
            "subject": email_subject,
            "body_html": email_body_html,
            "scheduled_at": datetime.now(),
            "status": "pending",
            "metadata": {
                "member_name": member_name,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "energy_data": energy_data,
                "financial_data": financial_data
            }
        }

        logger.info(f"Monthly report notification prepared for {member_email}")
        return notification

    @staticmethod
    def send_deadline_alert(
        recipient_email: str,
        recipient_name: str,
        deadline_type: str,
        deadline_date: datetime,
        days_remaining: int,
        action_required: str,
        entity: str,
        portal_url: str
    ) -> Dict[str, Any]:
        """
        Send deadline alert notification

        Args:
            recipient_email: Recipient email
            recipient_name: Recipient name
            deadline_type: Type of deadline (GSE, Terna, DSO, etc.)
            deadline_date: Deadline date
            days_remaining: Days until deadline
            action_required: What action is needed
            entity: Entity (GSE, Terna, DSO, etc.)
            portal_url: Portal URL

        Returns:
            Notification dictionary
        """
        # Determine urgency based on days remaining
        if days_remaining >= 30:
            urgency_level = "info"
            urgency_color = "#4299e1"
            icon = "ℹ️"
        elif days_remaining >= 7:
            urgency_level = "warning"
            urgency_color = "#ed8936"
            icon = "⚠️"
        elif days_remaining >= 1:
            urgency_level = "urgent"
            urgency_color = "#f56565"
            icon = "🚨"
        else:
            urgency_level = "critical"
            urgency_color = "#c53030"
            icon = "❗"

        email_subject = f"{icon} Scadenza {entity} - {days_remaining} giorni rimanenti"
        email_body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {urgency_color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h2 style="margin: 0; font-size: 24px;">{icon} Promemoria Scadenza</h2>
                </div>

                <div style="border: 2px solid {urgency_color}; border-top: none; padding: 20px; border-radius: 0 0 8px 8px;">
                    <p>Gentile {recipient_name},</p>

                    <div style="background-color: #fff5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #742a2a;">Dettagli Scadenza</h3>
                        <table style="width: 100%;">
                            <tr>
                                <td style="padding: 8px 0;"><strong>Ente:</strong></td>
                                <td style="padding: 8px 0;">{entity}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Tipo:</strong></td>
                                <td style="padding: 8px 0;">{deadline_type}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Data Scadenza:</strong></td>
                                <td style="padding: 8px 0; font-weight: bold; color: {urgency_color};">{deadline_date.strftime("%d/%m/%Y")}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0;"><strong>Giorni Rimanenti:</strong></td>
                                <td style="padding: 8px 0; font-weight: bold; font-size: 18px; color: {urgency_color};">{days_remaining} giorni</td>
                            </tr>
                        </table>
                    </div>

                    <div style="background-color: #f7fafc; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4299e1;">
                        <h4 style="margin-top: 0;">Azione Richiesta</h4>
                        <p style="margin-bottom: 0;">{action_required}</p>
                    </div>

                    <div style="background-color: #fff5f5; border-left: 4px solid #fc8181; padding: 15px; margin: 20px 0;">
                        <h4 style="margin-top: 0; color: #c53030;">⚠️ Importante</h4>
                        <p style="margin-bottom: 0;">Il mancato rispetto della scadenza può comportare la perdita di incentivi o sanzioni amministrative.</p>
                    </div>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{portal_url}" style="background-color: {urgency_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Accedi al Portale
                        </a>
                    </div>
                </div>

                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                <p style="font-size: 12px; color: #718096;">
                    Questo è un promemoria automatico. Riceverai ulteriori notifiche man mano che la scadenza si avvicina.
                </p>
            </div>
        </body>
        </html>
        """

        # Determine priority based on urgency
        if urgency_level == "critical":
            priority = NotificationPriority.URGENT
        elif urgency_level == "urgent":
            priority = NotificationPriority.HIGH
        elif urgency_level == "warning":
            priority = NotificationPriority.MEDIUM
        else:
            priority = NotificationPriority.LOW

        notification = {
            "type": NotificationType[f"DEADLINE_{days_remaining}_DAYS"] if days_remaining in [30, 15, 7, 3, 1] else NotificationType.SYSTEM_ALERT,
            "priority": priority,
            "channel": NotificationChannel.EMAIL,
            "recipient": recipient_email,
            "subject": email_subject,
            "body_html": email_body_html,
            "scheduled_at": datetime.now(),
            "status": "pending",
            "metadata": {
                "deadline_type": deadline_type,
                "deadline_date": deadline_date.isoformat(),
                "days_remaining": days_remaining,
                "entity": entity,
                "urgency_level": urgency_level
            }
        }

        logger.info(f"Deadline alert notification prepared for {recipient_email} ({days_remaining} days)")
        return notification

    @staticmethod
    def schedule_compliance_reminders(
        plant_commissioning_date: datetime,
        administrator_email: str,
        administrator_name: str,
        plant_name: str,
        portal_url: str
    ) -> List[Dict[str, Any]]:
        """
        Schedule all compliance deadline reminders for a new plant

        Args:
            plant_commissioning_date: Plant commissioning date
            administrator_email: Administrator email
            administrator_name: Administrator name
            plant_name: Plant name
            portal_url: Portal URL

        Returns:
            List of scheduled notifications
        """
        notifications = []

        # GSE Application Deadline (120 days from commissioning)
        gse_deadline = plant_commissioning_date + timedelta(days=NotificationService.GSE_APPLICATION_DEADLINE_DAYS)

        # Schedule reminders at 90, 60, 30, 15, 7, 3, 1 days before GSE deadline
        gse_reminder_days = [90, 60, 30, 15, 7, 3, 1]

        for days_before in gse_reminder_days:
            reminder_date = gse_deadline - timedelta(days=days_before)
            if reminder_date > datetime.now():
                notification = NotificationService.send_deadline_alert(
                    recipient_email=administrator_email,
                    recipient_name=administrator_name,
                    deadline_type="Domanda Incentivi TCEC",
                    deadline_date=gse_deadline,
                    days_remaining=days_before,
                    action_required=f"Presentare domanda per gli incentivi TCEC sul portale GSE per l'impianto {plant_name}",
                    entity="GSE",
                    portal_url=portal_url
                )
                notification["scheduled_at"] = reminder_date
                notifications.append(notification)

        # Terna GAUDÌ Deadline (30 days from grid connection)
        terna_deadline = plant_commissioning_date + timedelta(days=NotificationService.TERNA_REGISTRATION_DEADLINE_DAYS)

        # Schedule reminders at 15, 7, 3, 1 days before Terna deadline
        terna_reminder_days = [15, 7, 3, 1]

        for days_before in terna_reminder_days:
            reminder_date = terna_deadline - timedelta(days=days_before)
            if reminder_date > datetime.now():
                notification = NotificationService.send_deadline_alert(
                    recipient_email=administrator_email,
                    recipient_name=administrator_name,
                    deadline_type="Registrazione GAUDÌ",
                    deadline_date=terna_deadline,
                    days_remaining=days_before,
                    action_required=f"Registrare l'impianto {plant_name} sul portale GAUDÌ di Terna per ottenere il codice CENSIMP",
                    entity="Terna",
                    portal_url=portal_url
                )
                notification["scheduled_at"] = reminder_date
                notifications.append(notification)

        logger.info(f"Scheduled {len(notifications)} compliance reminders for plant {plant_name}")
        return notifications


# Export service instance
notification_service = NotificationService()
