"""
Italian Tax Calculator Service
Handles all tax calculations for CER operations in Italy including IVA, ritenute, and detrazioni
"""

from typing import Dict, Any, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from enum import Enum
import logging

from app.models.cer import CERLegalType

logger = logging.getLogger(__name__)


class IVARateType(str, Enum):
    """Italian VAT (IVA) rates"""
    EXEMPT = "exempt"
    REDUCED_4 = "reduced_4"
    REDUCED_5 = "reduced_5"
    REDUCED_10 = "reduced_10"
    STANDARD_22 = "standard_22"


class TransactionCategory(str, Enum):
    """Tax transaction categories"""
    GSE_INCENTIVE = "gse_incentive"
    PNRR_FUNDING = "pnrr_funding"
    ENERGY_SALE_GRID = "energy_sale_grid"
    MEMBER_SHARING = "member_sharing"
    INSTALLATION_SERVICE = "installation_service"
    ENERGY_EFFICIENCY_GOODS = "energy_efficiency_goods"
    GENERIC_SERVICE = "generic_service"


class ItalianTaxCalculator:
    """
    Service for calculating Italian taxes for CER operations

    Legal References:
    - D.Lgs. 34/2020, art. 119, paragraph 16-bis (CER non-commercial activity)
    - DPR 600/1973, art. 28, paragraph 2 (withholding tax)
    - Tax Agency response 201/2024 (VAT treatment)
    """

    # IVA (VAT) rates in Italy
    IVA_RATES = {
        IVARateType.EXEMPT: Decimal("0.00"),
        IVARateType.REDUCED_4: Decimal("0.04"),
        IVARateType.REDUCED_5: Decimal("0.05"),
        IVARateType.REDUCED_10: Decimal("0.10"),
        IVARateType.STANDARD_22: Decimal("0.22"),
    }

    # Ritenuta d'acconto (withholding tax) rate for GSE payments to cooperatives
    RITENUTA_ACCONTO_RATE = Decimal("0.04")  # 4%

    # IRES (corporate income tax) rate
    IRES_RATE = Decimal("0.24")  # 24%

    # Detrazioni fiscali (tax deductions) for photovoltaic installations
    DETRAZIONE_50_PERCENT = Decimal("0.50")  # 50% deduction over 10 years
    DETRAZIONE_70_PERCENT = Decimal("0.70")  # 70% Superbonus (ex-110%, now reduced)

    @staticmethod
    def calculate_iva(
        amount: Decimal,
        transaction_category: TransactionCategory,
        cer_legal_type: CERLegalType
    ) -> Dict[str, Any]:
        """
        Calculate Italian VAT (IVA) for a transaction

        Args:
            amount: Transaction amount (before VAT)
            transaction_category: Type of transaction
            cer_legal_type: Legal structure of the CER

        Returns:
            Dictionary with IVA calculation details
        """
        amount = Decimal(str(amount))

        # Determine IVA rate based on transaction category and legal type
        iva_rate_type = ItalianTaxCalculator._determine_iva_rate(
            transaction_category,
            cer_legal_type
        )

        iva_rate = ItalianTaxCalculator.IVA_RATES[iva_rate_type]
        iva_amount = (amount * iva_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_amount = amount + iva_amount

        return {
            "base_amount": float(amount),
            "iva_rate_type": iva_rate_type.value,
            "iva_rate_percentage": float(iva_rate * 100),
            "iva_amount": float(iva_amount),
            "total_amount": float(total_amount),
            "is_iva_exempt": iva_rate == Decimal("0.00"),
            "exemption_reason": ItalianTaxCalculator._get_exemption_reason(
                transaction_category,
                cer_legal_type
            )
        }

    @staticmethod
    def _determine_iva_rate(
        transaction_category: TransactionCategory,
        cer_legal_type: CERLegalType
    ) -> IVARateType:
        """Determine appropriate IVA rate for transaction"""

        # GSE incentives are ALWAYS exempt (non-repayable contribution)
        if transaction_category == TransactionCategory.GSE_INCENTIVE:
            return IVARateType.EXEMPT

        # PNRR funding is ALWAYS exempt (non-repayable contribution)
        if transaction_category == TransactionCategory.PNRR_FUNDING:
            return IVARateType.EXEMPT

        # For non-commercial associations (up to 200 kW): exempt
        if cer_legal_type == CERLegalType.ASSOCIATION:
            if transaction_category == TransactionCategory.ENERGY_SALE_GRID:
                return IVARateType.EXEMPT
            if transaction_category == TransactionCategory.MEMBER_SHARING:
                return IVARateType.EXEMPT

        # For cooperatives and consortiums: standard VAT applies
        if transaction_category == TransactionCategory.ENERGY_SALE_GRID:
            return IVARateType.REDUCED_10  # Reduced rate for energy

        if transaction_category == TransactionCategory.MEMBER_SHARING:
            return IVARateType.STANDARD_22  # Standard rate

        if transaction_category == TransactionCategory.INSTALLATION_SERVICE:
            return IVARateType.STANDARD_22

        if transaction_category == TransactionCategory.ENERGY_EFFICIENCY_GOODS:
            return IVARateType.REDUCED_10

        # Default: standard rate
        return IVARateType.STANDARD_22

    @staticmethod
    def _get_exemption_reason(
        transaction_category: TransactionCategory,
        cer_legal_type: CERLegalType
    ) -> Optional[str]:
        """Get legal reason for IVA exemption"""
        if transaction_category == TransactionCategory.GSE_INCENTIVE:
            return "Non-repayable contribution from public entity (GSE)"

        if transaction_category == TransactionCategory.PNRR_FUNDING:
            return "PNRR non-repayable contribution"

        if cer_legal_type == CERLegalType.ASSOCIATION:
            return "D.Lgs. 34/2020, art. 119, paragraph 16-bis - Non-commercial entity up to 200 kW"

        return None

    @staticmethod
    def calculate_ritenuta_acconto(
        gse_payment_amount: Decimal,
        cer_legal_type: CERLegalType
    ) -> Dict[str, Any]:
        """
        Calculate withholding tax (ritenuta d'acconto) on GSE payments

        Legal Reference: DPR 600/1973, art. 28, paragraph 2

        Args:
            gse_payment_amount: GSE incentive payment amount
            cer_legal_type: Legal structure of the CER

        Returns:
            Dictionary with ritenuta calculation details
        """
        gse_payment_amount = Decimal(str(gse_payment_amount))

        # Ritenuta only applies to cooperatives and commercial entities
        if cer_legal_type == CERLegalType.ASSOCIATION:
            return {
                "gross_amount": float(gse_payment_amount),
                "ritenuta_rate_percentage": 0.0,
                "ritenuta_amount": 0.0,
                "net_amount": float(gse_payment_amount),
                "applies": False,
                "reason": "Non-commercial association - no withholding tax"
            }

        # Calculate 4% withholding
        ritenuta_amount = (gse_payment_amount * ItalianTaxCalculator.RITENUTA_ACCONTO_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        net_amount = gse_payment_amount - ritenuta_amount

        return {
            "gross_amount": float(gse_payment_amount),
            "ritenuta_rate_percentage": 4.0,
            "ritenuta_amount": float(ritenuta_amount),
            "net_amount": float(net_amount),
            "applies": True,
            "reason": "DPR 600/1973, art. 28 - Withholding on public contributions to businesses",
            "deductible": True,
            "deductible_note": "Deductible from final IRES tax liability"
        }

    @staticmethod
    def calculate_ires_tax(
        gross_income: Decimal,
        deductible_expenses: Decimal,
        ritenute_paid: Decimal,
        cer_legal_type: CERLegalType
    ) -> Dict[str, Any]:
        """
        Calculate IRES (corporate income tax) for CER

        Args:
            gross_income: Total gross income
            deductible_expenses: Total deductible expenses
            ritenute_paid: Total ritenute d'acconto already paid
            cer_legal_type: Legal structure of the CER

        Returns:
            Dictionary with IRES calculation details
        """
        gross_income = Decimal(str(gross_income))
        deductible_expenses = Decimal(str(deductible_expenses))
        ritenute_paid = Decimal(str(ritenute_paid))

        # Calculate taxable income
        if cer_legal_type == CERLegalType.ASSOCIATION:
            # Associations: taxed on net income
            taxable_income = gross_income - deductible_expenses
        else:
            # Cooperatives/Consortiums: taxed on gross income with limited deductions
            taxable_income = gross_income - deductible_expenses

        # Cannot have negative taxable income
        if taxable_income < 0:
            taxable_income = Decimal("0.00")

        # Calculate IRES (24%)
        ires_amount = (taxable_income * ItalianTaxCalculator.IRES_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Deduct ritenute already paid
        ires_due = ires_amount - ritenute_paid

        if ires_due < 0:
            ires_due = Decimal("0.00")
            ritenute_credit = abs(ires_amount - ritenute_paid)
        else:
            ritenute_credit = Decimal("0.00")

        return {
            "gross_income": float(gross_income),
            "deductible_expenses": float(deductible_expenses),
            "taxable_income": float(taxable_income),
            "ires_rate_percentage": 24.0,
            "ires_gross_amount": float(ires_amount),
            "ritenute_paid": float(ritenute_paid),
            "ires_due": float(ires_due),
            "ritenute_credit": float(ritenute_credit),
            "tax_regime": "net_income" if cer_legal_type == CERLegalType.ASSOCIATION else "gross_income"
        }

    @staticmethod
    def calculate_member_detrazione(
        installation_cost: Decimal,
        detrazione_type: str = "50_percent"
    ) -> Dict[str, Any]:
        """
        Calculate tax deduction (detrazione fiscale) for CER member

        Args:
            installation_cost: Cost of photovoltaic installation
            detrazione_type: Type of deduction ("50_percent" or "70_percent")

        Returns:
            Dictionary with detrazione calculation details
        """
        installation_cost = Decimal(str(installation_cost))

        if detrazione_type == "50_percent":
            detrazione_rate = ItalianTaxCalculator.DETRAZIONE_50_PERCENT
            years = 10
            max_deductible = Decimal("96000.00")  # Maximum €96,000
            description = "50% deduction over 10 years for photovoltaic installations"
        elif detrazione_type == "70_percent":
            detrazione_rate = ItalianTaxCalculator.DETRAZIONE_70_PERCENT
            years = 10
            max_deductible = Decimal("200000.00")  # Higher limit for Superbonus
            description = "70% Superbonus deduction over 10 years (ex-110%, now reduced)"
        else:
            raise ValueError(f"Invalid detrazione_type: {detrazione_type}")

        # Apply maximum deductible limit
        if installation_cost > max_deductible:
            deductible_cost = max_deductible
        else:
            deductible_cost = installation_cost

        # Calculate total deduction
        total_detrazione = (deductible_cost * detrazione_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Annual deduction
        annual_detrazione = (total_detrazione / years).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return {
            "installation_cost": float(installation_cost),
            "deductible_cost": float(deductible_cost),
            "detrazione_type": detrazione_type,
            "detrazione_rate_percentage": float(detrazione_rate * 100),
            "total_detrazione": float(total_detrazione),
            "years": years,
            "annual_detrazione": float(annual_detrazione),
            "max_deductible_limit": float(max_deductible),
            "limit_applied": installation_cost > max_deductible,
            "description": description,
            "requirements": [
                "Installation must be on owned or rented property",
                "Payment must be via bank transfer with causale 'Riqualificazione energetica'",
                "CAF or commercialista certification required",
                "Annual declaration in tax return (Modello 730 or Unico)"
            ]
        }

    @staticmethod
    def generate_invoice_with_taxes(
        base_amount: Decimal,
        transaction_category: TransactionCategory,
        cer_legal_type: CERLegalType,
        include_ritenuta: bool = False
    ) -> Dict[str, Any]:
        """
        Generate complete invoice calculation with all applicable taxes

        Args:
            base_amount: Base transaction amount
            transaction_category: Type of transaction
            cer_legal_type: Legal structure of the CER
            include_ritenuta: Whether to apply ritenuta d'acconto

        Returns:
            Dictionary with complete invoice breakdown
        """
        base_amount = Decimal(str(base_amount))

        # Calculate IVA
        iva_calc = ItalianTaxCalculator.calculate_iva(
            base_amount,
            transaction_category,
            cer_legal_type
        )

        # Calculate ritenuta if applicable
        ritenuta_calc = None
        if include_ritenuta and transaction_category == TransactionCategory.GSE_INCENTIVE:
            ritenuta_calc = ItalianTaxCalculator.calculate_ritenuta_acconto(
                base_amount,
                cer_legal_type
            )

        # Build invoice
        total_with_iva = Decimal(str(iva_calc["total_amount"]))

        if ritenuta_calc and ritenuta_calc["applies"]:
            ritenuta_amount = Decimal(str(ritenuta_calc["ritenuta_amount"]))
            net_to_pay = total_with_iva - ritenuta_amount
        else:
            ritenuta_amount = Decimal("0.00")
            net_to_pay = total_with_iva

        return {
            "invoice_date": datetime.now().isoformat(),
            "line_items": [
                {
                    "description": f"{transaction_category.value} - Base amount",
                    "amount": float(base_amount)
                }
            ],
            "subtotal": float(base_amount),
            "iva_details": iva_calc,
            "ritenuta_details": ritenuta_calc,
            "total_with_iva": float(total_with_iva),
            "ritenuta_amount": float(ritenuta_amount),
            "net_to_pay": float(net_to_pay),
            "payment_terms": "30 days",
            "notes": [
                f"IVA regime: {iva_calc['iva_rate_type']}",
                f"Legal entity type: {cer_legal_type.value}"
            ]
        }

    @staticmethod
    def generate_f24_payment_data(
        iva_to_pay: Decimal,
        ritenute_to_pay: Decimal,
        ires_to_pay: Decimal,
        tax_period: str,
        taxpayer_cf: str,
        taxpayer_name: str
    ) -> Dict[str, Any]:
        """
        Generate F24 payment form data for tax payments

        F24 is the unified tax payment form in Italy

        Args:
            iva_to_pay: IVA amount to pay
            ritenute_to_pay: Ritenute d'acconto to pay
            ires_to_pay: IRES amount to pay
            tax_period: Tax period (MMYYYY format)
            taxpayer_cf: Taxpayer fiscal code
            taxpayer_name: Taxpayer name

        Returns:
            Dictionary with F24 form data
        """
        iva_to_pay = Decimal(str(iva_to_pay))
        ritenute_to_pay = Decimal(str(ritenute_to_pay))
        ires_to_pay = Decimal(str(ires_to_pay))

        total_to_pay = iva_to_pay + ritenute_to_pay + ires_to_pay

        return {
            "form_type": "F24",
            "taxpayer": {
                "fiscal_code": taxpayer_cf,
                "name": taxpayer_name
            },
            "tax_period": tax_period,
            "sections": [
                {
                    "section": "Erario",
                    "items": [
                        {
                            "tax_code": "6099",
                            "description": "IVA - Liquidazione periodica",
                            "amount": float(iva_to_pay)
                        } if iva_to_pay > 0 else None,
                        {
                            "tax_code": "1040",
                            "description": "Ritenute su redditi da lavoro autonomo",
                            "amount": float(ritenute_to_pay)
                        } if ritenute_to_pay > 0 else None,
                        {
                            "tax_code": "2003",
                            "description": "IRES - Acconto prima rata",
                            "amount": float(ires_to_pay)
                        } if ires_to_pay > 0 else None
                    ]
                }
            ],
            "total_to_pay": float(total_to_pay),
            "payment_deadline": ItalianTaxCalculator._get_payment_deadline(tax_period),
            "payment_method": "Home banking or authorized intermediary",
            "notes": [
                "F24 form must be paid through authorized channels",
                "Keep proof of payment for tax records",
                "Consult with commercialista for verification"
            ]
        }

    @staticmethod
    def _get_payment_deadline(tax_period: str) -> str:
        """Get payment deadline based on tax period"""
        # Simplified: IVA quarterly payments are due by 16th of following month
        # IRES/IRPEF payments have specific deadlines (June 30, November 30)
        # This should be expanded based on actual Italian tax calendar
        return "Consult commercialista for specific deadline"


# Export service instance
italian_tax_calculator = ItalianTaxCalculator()
