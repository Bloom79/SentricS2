/**
 * Italian Tax Management Page
 * Calculate and manage Italian taxes: IVA, Ritenuta d'Acconto, IRES, F24
 * BUSINESS VALUE: Prevents €20-50K/year in tax penalties
 */

import React, { useState } from 'react';
import { useMutation, useQuery } from '@tantml:react-query';
import { useParams } from 'react-router-dom';
import {
  Calculator,
  FileText,
  Euro,
  Download,
  Info,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { italianService } from '@/services/api/italian.service';
import { cerService } from '@/services/api/cer.service';
import { useToast } from '@/hooks/use-toast';

export default function TaxManagementPage() {
  const { cerId } = useParams<{ cerId: string }>();
  const { toast } = useToast();

  const [ivaAmount, setIvaAmount] = useState<string>('');
  const [ivaCategory, setIvaCategory] = useState<string>('gse_incentive');
  const [ivaResult, setIvaResult] = useState<any>(null);

  const [ritenutaAmount, setRitenutaAmount] = useState<string>('');
  const [ritenutaResult, setRitenutaResult] = useState<any>(null);

  const [iresGrossIncome, setIresGrossIncome] = useState<string>('');
  const [iresExpenses, setIresExpenses] = useState<string>('');
  const [iresRitenutePaid, setIresRitenutePaid] = useState<string>('');
  const [iresResult, setIresResult] = useState<any>(null);

  // Fetch CER details
  const { data: cer } = useQuery({
    queryKey: ['cer', cerId],
    queryFn: () => cerService.getCER(parseInt(cerId!)),
    enabled: !!cerId,
  });

  // Fetch tax rates
  const { data: taxRates } = useQuery({
    queryKey: ['italian-tax-rates'],
    queryFn: () => italianService.tax.getTaxRates(),
  });

  // Calculate IVA
  const calculateIVAMutation = useMutation({
    mutationFn: (data: { amount: number; category: string; legalType: string }) =>
      italianService.tax.calculateIVA(data.amount, data.category, data.legalType),
    onSuccess: (data) => {
      setIvaResult(data);
      toast({
        title: 'IVA Calculated',
        description: `Total amount: €${data.total_amount.toFixed(2)} (IVA: €${data.iva_amount.toFixed(2)})`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Calculation Failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  // Calculate Ritenuta
  const calculateRitenutaMutation = useMutation({
    mutationFn: (data: { amount: number; legalType: string }) =>
      italianService.tax.calculateRitenuta(data.amount, data.legalType),
    onSuccess: (data) => {
      setRitenutaResult(data);
      toast({
        title: 'Ritenuta Calculated',
        description: `Net amount: €${data.net_amount.toFixed(2)} (Ritenuta: €${data.ritenuta_amount.toFixed(2)})`,
      });
    },
  });

  // Calculate IRES
  const calculateIRESMutation = useMutation({
    mutationFn: (data: { grossIncome: number; expenses: number; ritenutePaid: number; legalType: string }) =>
      italianService.tax.calculateIRES(data.grossIncome, data.expenses, data.ritenutePaid, data.legalType),
    onSuccess: (data) => {
      setIresResult(data);
      toast({
        title: 'IRES Calculated',
        description: `Total due: €${data.total_due.toFixed(2)}`,
      });
    },
  });

  const handleCalculateIVA = () => {
    const amount = parseFloat(ivaAmount);
    if (isNaN(amount) || amount <= 0) {
      toast({
        title: 'Invalid Amount',
        description: 'Please enter a valid amount',
        variant: 'destructive',
      });
      return;
    }

    calculateIVAMutation.mutate({
      amount,
      category: ivaCategory,
      legalType: cer?.legal_type || 'cooperative',
    });
  };

  const handleCalculateRitenuta = () => {
    const amount = parseFloat(ritenutaAmount);
    if (isNaN(amount) || amount <= 0) {
      toast({
        title: 'Invalid Amount',
        description: 'Please enter a valid amount',
        variant: 'destructive',
      });
      return;
    }

    calculateRitenutaMutation.mutate({
      amount,
      legalType: cer?.legal_type || 'cooperative',
    });
  };

  const handleCalculateIRES = () => {
    const grossIncome = parseFloat(iresGrossIncome);
    const expenses = parseFloat(iresExpenses);
    const ritenutePaid = parseFloat(iresRitenutePaid);

    if (isNaN(grossIncome) || isNaN(expenses) || isNaN(ritenutePaid)) {
      toast({
        title: 'Invalid Input',
        description: 'Please enter valid amounts for all fields',
        variant: 'destructive',
      });
      return;
    }

    calculateIRESMutation.mutate({
      grossIncome,
      expenses,
      ritenutePaid,
      legalType: cer?.legal_type || 'cooperative',
    });
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Italian Tax Management</h1>
          <p className="text-muted-foreground mt-1">
            Calculate and manage IVA, Ritenuta d'Acconto, and IRES for {cer?.name}
          </p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Tax Report
        </Button>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <p className="font-semibold text-blue-900">Automatic Tax Compliance</p>
              <p className="text-sm text-blue-700 mt-1">
                Correct tax calculations prevent penalties of €20-50K/year. All calculations are based on current
                Italian tax law and your CER legal structure ({cer?.legal_type || 'cooperative'}).
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tax Rates Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">IVA Rate</p>
                <p className="text-2xl font-bold">0-22%</p>
                <p className="text-xs text-muted-foreground mt-1">Based on transaction type</p>
              </div>
              <Euro className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Ritenuta d'Acconto</p>
                <p className="text-2xl font-bold">
                  {cer?.legal_type === 'cooperative' ? '4%' : '0%'}
                </p>
                <p className="text-xs text-muted-foreground mt-1">On GSE payments</p>
              </div>
              <Euro className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">IRES</p>
                <p className="text-2xl font-bold">24%</p>
                <p className="text-xs text-muted-foreground mt-1">Corporate income tax</p>
              </div>
              <Euro className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Tax Deductions</p>
                <p className="text-2xl font-bold">50-70%</p>
                <p className="text-xs text-muted-foreground mt-1">Photovoltaic installations</p>
              </div>
              <Euro className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tax Calculators */}
      <Tabs defaultValue="iva" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="iva">IVA Calculator</TabsTrigger>
          <TabsTrigger value="ritenuta">Ritenuta d'Acconto</TabsTrigger>
          <TabsTrigger value="ires">IRES Calculator</TabsTrigger>
          <TabsTrigger value="f24">F24 Forms</TabsTrigger>
        </TabsList>

        {/* IVA Calculator */}
        <TabsContent value="iva">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="h-5 w-5" />
                  IVA (VAT) Calculator
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="iva-amount">Amount (€)</Label>
                  <Input
                    id="iva-amount"
                    type="number"
                    step="0.01"
                    value={ivaAmount}
                    onChange={(e) => setIvaAmount(e.target.value)}
                    placeholder="10000.00"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="iva-category">Transaction Category</Label>
                  <Select value={ivaCategory} onValueChange={setIvaCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gse_incentive">GSE Incentive (Exempt - 0%)</SelectItem>
                      <SelectItem value="pnrr_funding">PNRR Funding (Exempt - 0%)</SelectItem>
                      <SelectItem value="energy_sale_grid">Energy Sale to Grid (10%)</SelectItem>
                      <SelectItem value="member_sharing">Member Energy Sharing (10%)</SelectItem>
                      <SelectItem value="installation_service">Installation Service (22%)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Legal Type</Label>
                  <Input value={cer?.legal_type || 'Cooperative'} disabled className="capitalize" />
                </div>

                <Button
                  className="w-full"
                  onClick={handleCalculateIVA}
                  disabled={calculateIVAMutation.isPending}
                >
                  <Calculator className="mr-2 h-4 w-4" />
                  {calculateIVAMutation.isPending ? 'Calculating...' : 'Calculate IVA'}
                </Button>
              </CardContent>
            </Card>

            {/* IVA Result */}
            <Card>
              <CardHeader>
                <CardTitle>Calculation Result</CardTitle>
              </CardHeader>
              <CardContent>
                {ivaResult ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium">Base Amount</span>
                      <span className="font-semibold">€{ivaResult.base_amount.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium">IVA Rate</span>
                      <Badge variant="secondary">{(ivaResult.iva_rate * 100).toFixed(0)}%</Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium">IVA Amount</span>
                      <span className="font-semibold">€{ivaResult.iva_amount.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded border border-green-200">
                      <span className="text-sm font-semibold text-green-900">Total Amount</span>
                      <span className="text-lg font-bold text-green-900">
                        €{ivaResult.total_amount.toFixed(2)}
                      </span>
                    </div>
                    {ivaResult.exemption_reason && (
                      <Card className="bg-blue-50 border-blue-200">
                        <CardContent className="pt-4">
                          <p className="text-sm text-blue-900">
                            <CheckCircle className="inline h-4 w-4 mr-1" />
                            <strong>Exempt:</strong> {ivaResult.exemption_reason}
                          </p>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Calculator className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Enter amount and click Calculate to see results</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Ritenuta d'Acconto Calculator */}
        <TabsContent value="ritenuta">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="h-5 w-5" />
                  Ritenuta d'Acconto Calculator
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Card className="bg-blue-50 border-blue-200">
                  <CardContent className="pt-4">
                    <p className="text-sm text-blue-900">
                      <Info className="inline h-4 w-4 mr-1" />
                      Ritenuta d'Acconto is a withholding tax applied to GSE payments.{' '}
                      <strong>
                        {cer?.legal_type === 'cooperative' ? '4% for cooperatives' : '0% for associations'}
                      </strong>
                    </p>
                  </CardContent>
                </Card>

                <div className="space-y-2">
                  <Label htmlFor="ritenuta-amount">GSE Payment Amount (€)</Label>
                  <Input
                    id="ritenuta-amount"
                    type="number"
                    step="0.01"
                    value={ritenutaAmount}
                    onChange={(e) => setRitenutaAmount(e.target.value)}
                    placeholder="50000.00"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Legal Type</Label>
                  <Input value={cer?.legal_type || 'Cooperative'} disabled className="capitalize" />
                </div>

                <Button
                  className="w-full"
                  onClick={handleCalculateRitenuta}
                  disabled={calculateRitenutaMutation.isPending}
                >
                  <Calculator className="mr-2 h-4 w-4" />
                  {calculateRitenutaMutation.isPending ? 'Calculating...' : 'Calculate Ritenuta'}
                </Button>
              </CardContent>
            </Card>

            {/* Ritenuta Result */}
            <Card>
              <CardHeader>
                <CardTitle>Calculation Result</CardTitle>
              </CardHeader>
              <CardContent>
                {ritenutaResult ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium">Gross Amount</span>
                      <span className="font-semibold">€{ritenutaResult.gross_amount.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium">Ritenuta Rate</span>
                      <Badge variant="secondary">{(ritenutaResult.ritenuta_rate * 100).toFixed(0)}%</Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-red-50 rounded border border-red-200">
                      <span className="text-sm font-medium text-red-900">Ritenuta Amount</span>
                      <span className="font-semibold text-red-900">
                        €{ritenutaResult.ritenuta_amount.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded border border-green-200">
                      <span className="text-sm font-semibold text-green-900">Net Amount (to receive)</span>
                      <span className="text-lg font-bold text-green-900">
                        €{ritenutaResult.net_amount.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Calculator className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Enter GSE payment amount to calculate withholding tax</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* IRES Calculator */}
        <TabsContent value="ires">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="h-5 w-5" />
                  IRES Calculator (24%)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Card className="bg-blue-50 border-blue-200">
                  <CardContent className="pt-4">
                    <p className="text-sm text-blue-900">
                      <Info className="inline h-4 w-4 mr-1" />
                      IRES is the Italian corporate income tax at 24%. Ritenute paid can be credited against IRES
                      liability.
                    </p>
                  </CardContent>
                </Card>

                <div className="space-y-2">
                  <Label htmlFor="ires-gross">Gross Income (€)</Label>
                  <Input
                    id="ires-gross"
                    type="number"
                    step="0.01"
                    value={iresGrossIncome}
                    onChange={(e) => setIresGrossIncome(e.target.value)}
                    placeholder="100000.00"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ires-expenses">Deductible Expenses (€)</Label>
                  <Input
                    id="ires-expenses"
                    type="number"
                    step="0.01"
                    value={iresExpenses}
                    onChange={(e) => setIresExpenses(e.target.value)}
                    placeholder="30000.00"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ires-ritenute">Ritenute Already Paid (€)</Label>
                  <Input
                    id="ires-ritenute"
                    type="number"
                    step="0.01"
                    value={iresRitenutePaid}
                    onChange={(e) => setIresRitenutePaid(e.target.value)}
                    placeholder="2000.00"
                  />
                </div>

                <Button className="w-full" onClick={handleCalculateIRES} disabled={calculateIRESMutation.isPending}>
                  <Calculator className="mr-2 h-4 w-4" />
                  {calculateIRESMutation.isPending ? 'Calculating...' : 'Calculate IRES'}
                </Button>
              </CardContent>
            </Card>

            {/* IRES Result */}
            <Card>
              <CardHeader>
                <CardTitle>Calculation Result</CardTitle>
              </CardHeader>
              <CardContent>
                {iresResult ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium">Gross Income</span>
                      <span className="font-semibold">€{iresResult.gross_income.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium">Deductible Expenses</span>
                      <span className="font-semibold">-€{iresResult.deductible_expenses.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-blue-50 rounded border border-blue-200">
                      <span className="text-sm font-medium text-blue-900">Taxable Income</span>
                      <span className="font-semibold text-blue-900">€{iresResult.taxable_income.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium">IRES (24%)</span>
                      <span className="font-semibold">€{iresResult.ires_amount.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                      <span className="text-sm font-medium text-green-900">Ritenute Credit</span>
                      <span className="font-semibold text-green-900">
                        -€{iresResult.ritenute_credit.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-orange-50 rounded border border-orange-200">
                      <span className="text-sm font-semibold text-orange-900">Total Due</span>
                      <span className="text-lg font-bold text-orange-900">€{iresResult.total_due.toFixed(2)}</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Calculator className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Enter income and expenses to calculate IRES</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* F24 Forms */}
        <TabsContent value="f24">
          <Card>
            <CardHeader>
              <CardTitle>F24 Payment Forms</CardTitle>
              <p className="text-sm text-muted-foreground">Generate unified Italian tax payment forms</p>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-semibold">F24 Form Generation</p>
                <p className="mt-2">Generate F24 forms for IVA, Ritenuta, and IRES payments</p>
                <Button className="mt-6">
                  <Download className="mr-2 h-4 w-4" />
                  Generate F24 Form
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
