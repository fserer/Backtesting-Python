import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { RefreshCw, TrendingUp, TrendingDown, DollarSign, Coins, XCircle, Plus, Minus, X, Clock, Settings, AlertTriangle } from 'lucide-react';

interface HyperliquidBalance {
  coin: string;
  free: number;
  total: number;
  usdValue: number;
}

interface HyperliquidPosition {
  coin: string;
  size: number;
  entryPx: number;
  unrealizedPnl: number;
  liquidationPx: number;
  side: 'long' | 'short';
}

interface HyperliquidOpenOrder {
  id: string;
  coin: string;
  side: 'buy' | 'sell';
  size: number;
  price: number;
  orderType: 'MARKET' | 'LIMIT';
  status: 'pending' | 'filled' | 'cancelled';
  timestamp: number;
  date: string;
  time: string;
}

interface HyperliquidTrade {
  id: string;
  coin: string;
  side: 'buy' | 'sell';
  size: number;
  price: number;
  volume: number;
  fee: number;
  feePercentage: number;
  orderType: 'taker' | 'maker';
  timestamp: number;
  date: string;
  time: string;
}

interface HyperliquidSettings {
  id: string;
  api_wallet_name: string;
  api_wallet_address: string;
  api_private_key: string;
}

export default function HyperliquidPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [positions, setPositions] = useState<HyperliquidPosition[]>([]);
  const [balances, setBalances] = useState<HyperliquidBalance[]>([]);
  const [openOrders, setOpenOrders] = useState<HyperliquidOpenOrder[]>([]);
  const [trades, setTrades] = useState<HyperliquidTrade[]>([]);
  const [settings, setSettings] = useState<HyperliquidSettings | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [settingsForm, setSettingsForm] = useState({
    api_wallet_name: '',
    api_wallet_address: '',
    api_private_key: ''
  });
  const [savingSettings, setSavingSettings] = useState(false);
  const [settingsError, setSettingsError] = useState('');
  
  // Trade history pagination
  const [tradesOffset, setTradesOffset] = useState(0);
  const [hasMoreTrades, setHasMoreTrades] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  // Cargar configuración al montar el componente
  useEffect(() => {
    loadHyperliquidSettings();
  }, []);

  // Cargar datos de Hyperliquid
  useEffect(() => {
    if (settings) {
      loadHyperliquidData();
    }
  }, [settings]);

  const loadHyperliquidSettings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/hyperliquid/settings`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const settingsData = await response.json();
        setSettings(settingsData);
        setSettingsForm({
          api_wallet_name: settingsData.api_wallet_name || '',
          api_wallet_address: settingsData.api_wallet_address || '',
          api_private_key: settingsData.api_private_key || ''
        });
      } else if (response.status === 404) {
        // No hay configuración, mostrar formulario vacío
        setSettings(null);
      } else {
        setError('Error cargando configuración de Hyperliquid');
      }
    } catch (error) {
      console.error('Error cargando configuración:', error);
      setError('Error de conexión');
    }
  };

  const loadHyperliquidData = async () => {
    if (!settings) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Cargar posiciones
      const positionsResponse = await fetch(`${baseUrl}/api/hyperliquid/positions`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (positionsResponse.ok) {
        const positionsData = await positionsResponse.json();
        setPositions(positionsData.positions || []);
      }
      
      // Cargar balances
      const balancesResponse = await fetch(`${baseUrl}/api/hyperliquid/balances`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (balancesResponse.ok) {
        const balancesData = await balancesResponse.json();
        setBalances(balancesData.balances || []);
      }
      
      // Cargar órdenes abiertas
      const ordersResponse = await fetch(`${baseUrl}/api/hyperliquid/orders`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (ordersResponse.ok) {
        const ordersData = await ordersResponse.json();
        setOpenOrders(ordersData.orders || []);
      }
      
      // Cargar historial de trades
      const tradesResponse = await fetch(`${baseUrl}/api/hyperliquid/trades?limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (tradesResponse.ok) {
        const tradesData = await tradesResponse.json();
        setTrades(tradesData.trades || []);
      }
      
    } catch (error) {
      console.error('Error cargando datos de Hyperliquid:', error);
      setError('Error cargando datos de Hyperliquid');
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshData = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  const handleOpenNewPosition = () => {
    // TODO: Implementar diálogo para abrir nueva posición
    console.log('Abrir nueva posición');
  };

  const handleLoadMoreTrades = () => {
    setLoadingMore(true);
    setTimeout(() => {
      setLoadingMore(false);
      setHasMoreTrades(false); // Simular que no hay más trades
    }, 1000);
  };

  const handleSaveSettings = async () => {
    setSavingSettings(true);
    setSettingsError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/hyperliquid/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(settingsForm)
      });

      if (response.ok) {
        const savedSettings = await response.json();
        setSettings(savedSettings);
        setShowSettings(false);
        // Recargar datos de Hyperliquid
        loadHyperliquidData();
      } else {
        const errorData = await response.json();
        setSettingsError(errorData.detail || 'Error guardando configuración');
      }
    } catch (error) {
      console.error('Error guardando configuración:', error);
      setSettingsError('Error de conexión');
    } finally {
      setSavingSettings(false);
    }
  };

  const handleDeleteSettings = async () => {
    if (!confirm('¿Estás seguro de que quieres eliminar la configuración de Hyperliquid?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/hyperliquid/settings`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSettings(null);
        setSettingsForm({
          api_wallet_name: '',
          api_wallet_address: '',
          api_private_key: ''
        });
        setShowSettings(false);
        // Limpiar datos
        setPositions([]);
        setBalances([]);
        setOpenOrders([]);
        setTrades([]);
      } else {
        setSettingsError('Error eliminando configuración');
      }
    } catch (error) {
      console.error('Error eliminando configuración:', error);
      setSettingsError('Error de conexión');
    }
  };

  const formatNumber = (value: number, decimals: number = 2): string => {
    return value.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  };

  const formatUSD = (value: number): string => {
    return `$${formatNumber(value)}`;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dashboard de Hyperliquid
        </h1>
        <p className="text-gray-600">
          Visualiza tus posiciones abiertas y balances de monedas en Hyperliquid
        </p>
      </div>

      {/* Action Buttons */}
      <div className="mb-6 flex justify-between items-center">
        <div className="flex gap-4">
          <Button 
            onClick={handleRefreshData} 
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualizar Datos
          </Button>
          
          <Button 
            onClick={handleOpenNewPosition} 
            disabled={loading}
            className="bg-green-600 hover:bg-green-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Abrir Nueva Posición
          </Button>
        </div>

        <Button 
          onClick={() => setShowSettings(true)}
          variant="outline"
          className="border-gray-300 hover:bg-gray-50"
        >
          <Settings className="h-4 w-4 mr-2" />
          Configuración
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Information Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Open Positions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>Posiciones Abiertas</span>
              <Badge variant="secondary">{positions.length}</Badge>
            </CardTitle>
            <CardDescription>
              Tus posiciones abiertas actuales en Hyperliquid
            </CardDescription>
          </CardHeader>
          <CardContent>
            {positions.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No hay posiciones abiertas</p>
            ) : (
              <div className="space-y-4">
                {positions.map((position, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-lg">{position.coin}</span>
                        <Badge variant={position.side === 'long' ? 'default' : 'destructive'}>
                          {position.side === 'long' ? (
                            <TrendingUp className="w-3 h-3 mr-1" />
                          ) : (
                            <TrendingDown className="w-3 h-3 mr-1" />
                          )}
                          {position.side === 'long' ? 'LARGO' : 'CORTO'}
                        </Badge>
                      </div>
                      <div className="text-right">
                        <div className={`font-bold ${position.unrealizedPnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {position.unrealizedPnl >= 0 ? '+' : ''}{formatUSD(position.unrealizedPnl)}
                        </div>
                        <div className="text-sm text-gray-500">P&L</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                      <div>
                        <span className="text-gray-500">Tamaño:</span>
                        <span className="ml-2 font-mono">{formatNumber(Math.abs(position.size), 6)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Precio de Entrada:</span>
                        <span className="ml-2 font-mono">{formatUSD(position.entryPx)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Precio de Liquidación:</span>
                        <span className="ml-2 font-mono">{formatUSD(position.liquidationPx)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Valor de Posición:</span>
                        <span className="ml-2 font-mono">{formatUSD(Math.abs(position.size * position.entryPx))}</span>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button size="sm" variant="destructive" className="bg-red-600 hover:bg-red-700">
                        <X className="w-4 h-4 mr-1" />
                        Cerrar
                      </Button>
                      <Button size="sm" variant="default" className="bg-green-600 hover:bg-green-700">
                        <Plus className="w-4 h-4 mr-1" />
                        Ampliar
                      </Button>
                      <Button size="sm" variant="outline" className="border-orange-500 text-orange-600 hover:bg-orange-50">
                        <Minus className="w-4 h-4 mr-1" />
                        Reducir
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Open Orders */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Órdenes Abiertas</span>
              <Badge variant="secondary">{openOrders.length}</Badge>
            </CardTitle>
            <CardDescription>
              Tus órdenes limit pendientes
            </CardDescription>
          </CardHeader>
          <CardContent>
            {openOrders.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No se encontraron órdenes abiertas</p>
            ) : (
              <div className="space-y-4">
                {openOrders.map((order) => (
                  <div key={order.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-lg">{order.coin}</span>
                        <Badge variant={order.side === 'buy' ? 'default' : 'destructive'}>
                          {order.side === 'buy' ? (
                            <TrendingUp className="w-3 h-3 mr-1" />
                          ) : (
                            <TrendingDown className="w-3 h-3 mr-1" />
                          )}
                          {order.side === 'buy' ? 'COMPRAR' : 'VENDER'}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          Orden de Límite
                        </Badge>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">{order.date}</div>
                        <div className="text-sm text-gray-500">{order.time}</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                      <div>
                        <span className="text-gray-500">Tamaño de Orden:</span>
                        <span className="ml-2 font-mono">{formatNumber(order.size, 6)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Precio de Orden:</span>
                        <span className="ml-2 font-mono">{formatUSD(order.price)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Estado:</span>
                        <span className="ml-2 font-mono capitalize">{order.status}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Volumen:</span>
                        <span className="ml-2 font-mono">{formatUSD(order.size * order.price)}</span>
                      </div>
                    </div>
                    
                    <div className="flex justify-end">
                      <Button size="sm" variant="destructive" className="bg-red-600 hover:bg-red-700">
                        <X className="w-4 h-4 mr-1" />
                        Cancelar Orden
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Coin Balances */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Coins className="w-5 h-5" />
              <span>Balances de Monedas</span>
              <Badge variant="secondary">{balances.length}</Badge>
            </CardTitle>
            <CardDescription>
              Tus balances actuales de monedas en Hyperliquid
            </CardDescription>
          </CardHeader>
          <CardContent>
            {balances.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No se encontraron balances</p>
            ) : (
              <div className="space-y-4">
                {balances.map((balance, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-lg">{balance.coin}</span>
                        <DollarSign className="w-4 h-4 text-gray-400" />
                      </div>
                      <span className="font-bold text-green-600">
                        {formatUSD(balance.usdValue)}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Libre:</span>
                        <span className="ml-2 font-mono">{formatNumber(balance.free, 6)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Total:</span>
                        <span className="ml-2 font-mono">{formatNumber(balance.total, 6)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Trade History - Full Width */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Historial de Trades</span>
            <Badge variant="secondary">{trades.length}</Badge>
          </CardTitle>
          <CardDescription>
            Tu actividad de trading reciente en Hyperliquid
          </CardDescription>
        </CardHeader>
        <CardContent>
          {trades.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No se encontraron trades</p>
          ) : (
            <div className="space-y-4">
              {/* Desktop Table View */}
              <div className="hidden md:block">
                {/* Table Header */}
                <div className="grid grid-cols-8 gap-4 p-3 bg-gray-100 rounded-lg font-medium text-sm text-gray-700">
                  <div>Ticker</div>
                  <div>Lado</div>
                  <div>Precio de Entrada</div>
                  <div>Tamaño</div>
                  <div>Volumen</div>
                  <div>Fee</div>
                  <div>Fee %</div>
                  <div>Tipo</div>
                </div>
                
                {/* Trade Rows */}
                {trades.map((trade) => (
                  <div key={trade.id} className="grid grid-cols-8 gap-4 p-3 bg-gray-50 rounded-lg items-center">
                    <div className="font-bold text-lg">{trade.coin}</div>
                    <div>
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs font-medium w-fit ${
                        trade.side === 'buy' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {trade.side === 'buy' ? (
                          <TrendingUp className="w-3 h-3" />
                        ) : (
                          <TrendingDown className="w-3 h-3" />
                        )}
                        <span>{trade.side === 'buy' ? 'COMPRAR' : 'VENDER'}</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{trade.date} {trade.time}</div>
                    </div>
                    <div className="font-mono">{formatUSD(trade.price)}</div>
                    <div className="font-mono">{formatNumber(trade.size, 6)}</div>
                    <div className="font-mono">{formatUSD(trade.volume)}</div>
                    <div className="font-mono">{formatUSD(trade.fee)}</div>
                    <div className="font-mono text-sm">{trade.feePercentage.toFixed(4)}%</div>
                    <div>
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs font-medium w-fit ${
                        trade.orderType === 'maker' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        <span>{trade.orderType === 'maker' ? 'Maker' : 'Taker'}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Mobile Card View */}
              <div className="md:hidden">
                {trades.map((trade) => (
                  <div key={trade.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-lg">{trade.coin}</span>
                        <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs font-medium ${
                          trade.side === 'buy' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {trade.side === 'buy' ? (
                            <TrendingUp className="w-3 h-3" />
                          ) : (
                            <TrendingDown className="w-3 h-3" />
                          )}
                          <span>{trade.side === 'buy' ? 'COMPRAR' : 'VENDER'}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">{trade.date}</div>
                        <div className="text-sm font-mono">{trade.time}</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">📊 Tamaño:</span>
                        <span className="ml-2 font-mono">{formatNumber(trade.size, 6)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">💰 Precio:</span>
                        <span className="ml-2 font-mono">{formatUSD(trade.price)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">💵 Volumen:</span>
                        <span className="ml-2 font-mono">{formatUSD(trade.volume)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">💸 Fee:</span>
                        <span className="ml-2 font-mono">{formatUSD(trade.fee)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">📈 Fee %:</span>
                        <span className="ml-2 font-mono">{trade.feePercentage.toFixed(4)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-500">🎯 Tipo:</span>
                        <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded text-xs font-medium ${
                          trade.orderType === 'maker' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-orange-100 text-orange-800'
                        }`}>
                          <span>{trade.orderType === 'maker' ? 'Maker' : 'Taker'}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Load More Button */}
              {hasMoreTrades && (
                <div className="text-center pt-4">
                  <Button
                    onClick={handleLoadMoreTrades}
                    disabled={loadingMore}
                    variant="outline"
                    className="w-full"
                  >
                    {loadingMore ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Cargando...
                      </>
                    ) : (
                      'Cargar Más'
                    )}
                  </Button>
                </div>
              )}
              
              {!hasMoreTrades && trades.length > 0 && (
                <div className="text-center pt-4">
                  <p className="text-gray-500 text-sm">No hay más trades para cargar</p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Configuración de Hyperliquid</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSettings(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            {settingsError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800 text-sm">{settingsError}</p>
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mi Wallet
                </label>
                <input
                  type="text"
                  value={settingsForm.api_wallet_name}
                  onChange={(e) => setSettingsForm(prev => ({ ...prev, api_wallet_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0x..."
                  disabled={savingSettings}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hyperliquid Wallet
                </label>
                <input
                  type="text"
                  value={settingsForm.api_wallet_address}
                  onChange={(e) => setSettingsForm(prev => ({ ...prev, api_wallet_address: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0x..."
                  disabled={savingSettings}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Secret Key
                </label>
                <input
                  type="password"
                  value={settingsForm.api_private_key}
                  onChange={(e) => setSettingsForm(prev => ({ ...prev, api_private_key: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Tu clave secreta..."
                  disabled={savingSettings}
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <Button 
                className="flex-1 bg-blue-600 hover:bg-blue-700"
                onClick={handleSaveSettings}
                disabled={savingSettings}
              >
                {savingSettings ? 'Guardando...' : 'Guardar'}
              </Button>
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowSettings(false)}
                disabled={savingSettings}
              >
                Cancelar
              </Button>
            </div>
            
            {settings && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleDeleteSettings}
                  disabled={savingSettings}
                  className="w-full"
                >
                  Eliminar Configuración
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
