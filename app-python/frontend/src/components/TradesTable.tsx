import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Trade } from '../lib/api';

interface TradesTableProps {
  trades?: Trade[];
}

export function TradesTable({ trades }: TradesTableProps) {
  if (!trades || trades.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Operaciones Detalladas
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No hay operaciones para mostrar
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '--';
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatDuration = (duration: number) => {
    if (duration < 24) {
      return `${duration}h`;
    } else {
      const days = Math.floor(duration / 24);
      const hours = duration % 24;
      return `${days}d ${hours}h`;
    }
  };

  const getPnlColor = (pnl: number) => {
    return pnl >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getReturnColor = (returnPct: number) => {
    return returnPct >= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Operaciones Detalladas ({trades.length} operaciones)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-2 font-medium text-gray-700">#</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">Entrada</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">Precio Entrada</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">Salida</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">Precio Salida</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">Tamaño</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">Duración</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">P&L</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">Retorno</th>
                <th className="text-left py-3 px-2 font-medium text-gray-700">Comisiones</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-2 text-gray-600 font-medium">{index + 1}</td>
                  <td className="py-3 px-2 text-gray-600">{formatDate(trade.entry_date)}</td>
                  <td className="py-3 px-2 text-gray-900 font-medium">
                    {formatCurrency(trade.entry_price)}
                  </td>
                  <td className="py-3 px-2 text-gray-600">{formatDate(trade.exit_date)}</td>
                  <td className="py-3 px-2 text-gray-900 font-medium">
                    {formatCurrency(trade.exit_price)}
                  </td>
                  <td className="py-3 px-2 text-gray-600">
                    {(trade.size || 0).toFixed(2)}
                  </td>
                  <td className="py-3 px-2 text-gray-600">
                    {formatDuration(trade.duration || 0)}
                  </td>
                  <td className={`py-3 px-2 font-medium ${getPnlColor(trade.pnl)}`}>
                    {formatCurrency(trade.pnl)}
                  </td>
                  <td className={`py-3 px-2 font-medium ${getReturnColor(trade.return_pct)}`}>
                    {formatPercentage(trade.return_pct)}
                  </td>
                  <td className="py-3 px-2 text-gray-600">
                    {formatCurrency(trade.entry_fees + trade.exit_fees)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Resumen de operaciones */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {trades.filter(t => t.pnl > 0).length}
            </div>
            <div className="text-sm text-gray-600">Ganadoras</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {trades.filter(t => t.pnl < 0).length}
            </div>
            <div className="text-sm text-gray-600">Perdedoras</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(trades.reduce((sum, t) => sum + t.pnl, 0))}
            </div>
            <div className="text-sm text-gray-600">P&L Total</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(trades.reduce((sum, t) => sum + t.entry_fees + t.exit_fees, 0))}
            </div>
            <div className="text-sm text-gray-600">Comisiones Totales</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
