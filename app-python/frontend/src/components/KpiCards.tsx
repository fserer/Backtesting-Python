import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { TrendingUp, TrendingDown, Activity, DollarSign, Wallet, Target } from 'lucide-react';
import { BacktestResults } from '@/lib/api';

interface KpiCardsProps {
  results?: BacktestResults;
  initialCapital?: number;
}

export function KpiCards({ results, initialCapital }: KpiCardsProps) {
  if (!results) {
    return (
      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Cargando...</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">--</div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatNumber = (value: number) => {
    return value.toLocaleString('es-ES', { maximumFractionDigits: 2 });
  };

  const formatCurrency = (value: number) => {
    return value.toLocaleString('en-US', { 
      style: 'currency', 
      currency: 'USD',
      maximumFractionDigits: 0 
    });
  };

  const getValueColor = (value: number, isPositive: boolean = true) => {
    if (isPositive) {
      return value >= 0 ? 'text-green-600' : 'text-red-600';
    }
    return value <= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Primera fila: Retorno Total y Ratio Sharpe */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Retorno Total</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${getValueColor(results.total_return)}`}>
            {formatPercentage(results.total_return)}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Ratio Sharpe</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatNumber(results.sharpe || 0)}
          </div>
        </CardContent>
      </Card>

      {/* Segunda fila: Retorno Buy & Hold y Retorno Solo Trades */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Retorno Buy & Hold</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${getValueColor(results.buy_and_hold_return || 0)}`}>
            {formatPercentage(results.buy_and_hold_return || 0)}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Retorno Solo Trades</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${getValueColor(results.trades_only_return || 0)}`}>
            {formatPercentage(results.trades_only_return || 0)}
          </div>
        </CardContent>
      </Card>

      {/* Tercera fila: Máx. Drawdown y Operaciones */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Máx. Drawdown</CardTitle>
          <TrendingDown className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${getValueColor(results.max_drawdown, false)}`}>
            {formatPercentage(results.max_drawdown)}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Operaciones</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {results.trades || 0}
          </div>
        </CardContent>
      </Card>

      {/* Cuarta fila: Capital Inicial y Capital Final */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Capital Inicial</CardTitle>
          <Wallet className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {initialCapital ? formatCurrency(initialCapital) : '--'}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Capital Final</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {initialCapital ? formatCurrency(initialCapital * (1 + results.total_return)) : '--'}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
