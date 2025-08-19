import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Trade } from '@/lib/api';
import { formatCurrency } from '../lib/utils';
import { DollarSign, Clock, TrendingDown } from 'lucide-react';

interface FundingCostProps {
  trades: Trade[];
  fundingRateAnnual: number;
}

export function FundingCost({ trades, fundingRateAnnual }: FundingCostProps) {
  const calculateFundingCost = () => {
    if (!trades || trades.length === 0) {
      return {
        totalFundingCost: 0,
        totalPositionValue: 0,
        averageDuration: 0,
        totalDuration: 0,
        tradesWithFunding: 0,
        totalPnL: 0,
        totalFees: 0,
        netPnL: 0
      };
    }

    let totalFundingCost = 0;
    let totalPositionValue = 0;
    let totalDuration = 0;
    let tradesWithFunding = 0;
    let totalPnL = 0;
    let totalFees = 0;

    trades.forEach(trade => {
      if (trade.entry_date && trade.exit_date && trade.size > 0) {
        // Calcular duración en días
        const entryDate = new Date(trade.entry_date);
        const exitDate = new Date(trade.exit_date);
        const durationDays = (exitDate.getTime() - entryDate.getTime()) / (1000 * 60 * 60 * 24);
        
        // Calcular valor de la posición (tamaño * precio de entrada)
        const positionValue = trade.size * trade.entry_price;
        
        // Calcular coste de funding (valor * tasa anual * días / 365)
        const fundingCost = positionValue * (fundingRateAnnual / 100) * (durationDays / 365);
        
        totalFundingCost += fundingCost;
        totalPositionValue += positionValue;
        totalDuration += durationDays;
        tradesWithFunding++;
      }
      
      // Sumar P&L y comisiones de todos los trades
      totalPnL += trade.pnl || 0;
      totalFees += (trade.entry_fees || 0) + (trade.exit_fees || 0);
    });

    const averageDuration = tradesWithFunding > 0 ? totalDuration / tradesWithFunding : 0;
    // El P&L de trades ya incluye las comisiones, solo restamos el funding
    const netPnL = totalPnL - totalFundingCost;

    return {
      totalFundingCost,
      totalPositionValue,
      averageDuration,
      totalDuration,
      tradesWithFunding,
      totalPnL,
      totalFees,
      netPnL
    };
  };

  const fundingData = calculateFundingCost();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="h-5 w-5 text-muted-foreground" />
          <span>Coste de Funding</span>
          <span className="text-sm text-muted-foreground">
            ({fundingRateAnnual}% anual)
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {trades && trades.length > 0 ? (
          <>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Coste Total de Funding</p>
                <p className="text-2xl font-bold text-red-600">
                  {formatCurrency(fundingData.totalFundingCost)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Valor Total Posiciones</p>
                <p className="text-lg font-semibold">
                  {formatCurrency(fundingData.totalPositionValue)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">P&L Neto Total</p>
                <p className={`text-2xl font-bold ${fundingData.netPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(fundingData.netPnL)}
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div>
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  Duración Promedio
                </p>
                <p className="text-lg font-semibold">
                  {fundingData.averageDuration.toFixed(1)} días
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <TrendingDown className="h-4 w-4" />
                  Trades con Funding
                </p>
                <p className="text-lg font-semibold">
                  {fundingData.tradesWithFunding} / {trades.length}
                </p>
              </div>
            </div>

            {/* Desglose del P&L Neto */}
            <div className="pt-2 border-t">
              <p className="text-sm font-medium text-muted-foreground mb-2">Desglose del P&L Neto:</p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>P&L de Trades (con comisiones):</span>
                  <span className={fundingData.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {formatCurrency(fundingData.totalPnL)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>- Coste de Funding:</span>
                  <span className="text-red-600">
                    -{formatCurrency(fundingData.totalFundingCost)}
                  </span>
                </div>
                <div className="flex justify-between font-medium border-t pt-1">
                  <span>= P&L Neto Total:</span>
                  <span className={fundingData.netPnL >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {formatCurrency(fundingData.netPnL)}
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2 border-t">
              <p className="text-sm text-muted-foreground">
                Coste de funding calculado sobre {fundingData.tradesWithFunding} trades 
                con una duración total de {fundingData.totalDuration.toFixed(1)} días
              </p>
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No hay trades para calcular el coste de funding</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
