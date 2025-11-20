"""
Invoice Generation Service
Generates PDF invoices for CER billing statements
"""

from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from io import BytesIO
import logging

from app.models.billing import BillingStatement, Settlement
from app.models.cer import CER, CERMember
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class InvoiceGenerator:
    """Generate PDF invoices for billing statements"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='InvoiceHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            spaceAfter=5
        ))

        self.styles.add(ParagraphStyle(
            name='InvoiceFooter',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        ))

    def generate_invoice_pdf(
        self,
        db: Session,
        statement: BillingStatement,
        cer: CER,
        member: CERMember,
        settlement: Optional[Settlement] = None
    ) -> BytesIO:
        """
        Generate a PDF invoice for a billing statement

        Args:
            db: Database session
            statement: Billing statement
            cer: CER community
            member: CER member
            settlement: Optional settlement details

        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        # Build document content
        story = []

        # Header
        story.extend(self._build_header(cer, statement))
        story.append(Spacer(1, 1 * cm))

        # Invoice details
        story.extend(self._build_invoice_details(statement, member))
        story.append(Spacer(1, 1 * cm))

        # Line items table
        story.extend(self._build_line_items(statement))
        story.append(Spacer(1, 1 * cm))

        # Summary
        story.extend(self._build_summary(statement))
        story.append(Spacer(1, 2 * cm))

        # Footer
        story.extend(self._build_footer(cer))

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        return buffer

    def _build_header(self, cer: CER, statement: BillingStatement) -> List:
        """Build invoice header"""
        elements = []

        # Title
        title = Paragraph(
            f"INVOICE #{statement.statement_number or statement.id}",
            self.styles['InvoiceTitle']
        )
        elements.append(title)

        # CER Details
        cer_info = f"""
        <b>{cer.name}</b><br/>
        {cer.legal_name or ''}<br/>
        VAT: {cer.vat_number or 'N/A'}<br/>
        Fiscal Code: {cer.fiscal_code or 'N/A'}
        """
        elements.append(Paragraph(cer_info, self.styles['Normal']))

        return elements

    def _build_invoice_details(self, statement: BillingStatement, member: CERMember) -> List:
        """Build invoice details section"""
        elements = []

        # Create two-column layout for dates and member info
        data = [
            ['Invoice Date:', statement.statement_date.strftime('%d/%m/%Y'),
             'Member:', member.name or 'Unknown'],
            ['Period Start:', statement.period_start.strftime('%d/%m/%Y'),
             'Member Code:', str(member.member_code)],
            ['Period End:', statement.period_end.strftime('%d/%m/%Y'),
             'Status:', statement.status.value],
            ['Due Date:', (statement.due_date.strftime('%d/%m/%Y') if statement.due_date else 'N/A'),
             '', '']
        ]

        table = Table(data, colWidths=[3 * cm, 4 * cm, 3 * cm, 7 * cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(table)

        return elements

    def _build_line_items(self, statement: BillingStatement) -> List:
        """Build line items table"""
        elements = []

        # Table header
        title = Paragraph('<b>Energy Transactions</b>', self.styles['Heading2'])
        elements.append(title)
        elements.append(Spacer(1, 0.5 * cm))

        # Build table data
        data = [['Description', 'Energy (kWh)', 'Amount (€)']]

        # Add line items
        if statement.energy_produced:
            data.append([
                'Energy Produced',
                f"{statement.energy_produced:.2f}",
                f"€{(statement.energy_produced_value or 0):.2f}"
            ])

        if statement.energy_consumed:
            data.append([
                'Energy Consumed',
                f"{statement.energy_consumed:.2f}",
                f"€{(statement.energy_consumed_value or 0):.2f}"
            ])

        if statement.shared_energy:
            data.append([
                'Shared Energy',
                f"{statement.shared_energy:.2f}",
                f"€{(statement.shared_energy_value or 0):.2f}"
            ])

        if statement.incentive_amount:
            data.append([
                'Incentives',
                '-',
                f"€{statement.incentive_amount:.2f}"
            ])

        if statement.grid_fees:
            data.append([
                'Grid Fees',
                '-',
                f"-€{statement.grid_fees:.2f}"
            ])

        if statement.community_fund:
            data.append([
                'Community Fund Contribution',
                '-',
                f"-€{statement.community_fund:.2f}"
            ])

        # Create table
        table = Table(data, colWidths=[10 * cm, 3 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEABOVE', (0, 1), (-1, 1), 0.5, colors.grey),
        ]))

        elements.append(table)

        return elements

    def _build_summary(self, statement: BillingStatement) -> List:
        """Build invoice summary"""
        elements = []

        # Summary table
        data = [
            ['Subtotal:', f"€{statement.amount:.2f}"],
            ['VAT (if applicable):', f"€{(statement.vat_amount or 0):.2f}"],
            ['<b>Total Amount:</b>', f"<b>€{statement.total_amount:.2f}</b>"]
        ]

        table = Table(data, colWidths=[13 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1a73e8')),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1a73e8')),
            ('TOPPADDING', (0, -1), (-1, -1), 12),
        ]))

        elements.append(table)

        return elements

    def _build_footer(self, cer: CER) -> List:
        """Build invoice footer"""
        elements = []

        footer_text = f"""
        <para alignment="center">
        <i>This invoice was generated electronically by {cer.name}</i><br/>
        For inquiries, please contact the community administrator.<br/>
        Payment instructions will be provided separately.
        </para>
        """

        elements.append(Paragraph(footer_text, self.styles['InvoiceFooter']))

        return elements


# Singleton instance
invoice_generator = InvoiceGenerator()
