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
  main_wallet?: string;
  hyperliquid_wallet?: string;
  api_secret_key?: string;
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
    main_wallet: '',
    hyperliquid_wallet: '',
    api_secret_key: ''
  });
  const [savingSettings, setSavingSettings] = useState(false);
  const [settingsError, setSettingsError] = useState('');
  
  // Trade history pagination
  const [tradesOffset, setTradesOffset] = useState(0);
  const [hasMoreTrades, setHasMoreTrades] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  // New position modal
  const [showNewPositionModal, setShowNewPositionModal] = useState(false);
  const [newPositionForm, setNewPositionForm] = useState({
    asset: '',
    orderType: 'MARKET',
    positionType: 'LONG',
    size: '0.01',
    leverage: '5',
    limitPrice: ''
  });
  const [submittingOrder, setSubmittingOrder] = useState(false);
  const [orderError, setOrderError] = useState('');

  // Position action modals
  const [showCloseModal, setShowCloseModal] = useState({ show: false, position: null });
  const [showIncreaseModal, setShowIncreaseModal] = useState({ show: false, position: null });
  const [showDecreaseModal, setShowDecreaseModal] = useState({ show: false, position: null });
  const [showCancelOrderModal, setShowCancelOrderModal] = useState({ show: false, orderId: '', coin: '' });
  const [modalAmount, setModalAmount] = useState('');
  const [modalLeverage, setModalLeverage] = useState('5');
  const [modalLoading, setModalLoading] = useState(false);
  
  // Separate result states for each modal
  const [closeModalResult, setCloseModalResult] = useState({ success: false, message: '' });
  const [increaseModalResult, setIncreaseModalResult] = useState({ success: false, message: '' });
  const [decreaseModalResult, setDecreaseModalResult] = useState({ success: false, message: '' });
  const [cancelOrderModalResult, setCancelOrderModalResult] = useState({ success: false, message: '' });

  // Available assets
  const availableAssets = [
    'BTC', 'ETH', 'SOL', 'MATIC', 'LINK', 'UNI', 'AVAX', 'LDO', 'ARB', 'OP'
  ];

  const leverageOptions = [
    { value: '2', label: '2x (Más seguro)' },
    { value: '5', label: '5x (Estándar)' },
    { value: '10', label: '10x (Más riesgo)' },
    { value: '20', label: '20x (Alto riesgo)' }
  ];

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
        setSettings(settingsData);
        setSettingsForm({
          main_wallet: settingsData.main_wallet || '',
          hyperliquid_wallet: settingsData.hyperliquid_wallet || '',
          api_secret_key: settingsData.api_secret_key || ''
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
      
      // Cargar todos los datos en una sola llamada optimizada
      const allDataResponse = await fetch(`${baseUrl}/api/hyperliquid/all-data`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (allDataResponse.ok) {
        const allData = await allDataResponse.json();
        setPositions(allData.positions || []);
        setBalances(allData.balances || []);
        setOpenOrders(allData.orders || []);
        setTrades(allData.trades || []);
      } else {
        console.error('Error cargando datos de Hyperliquid');
        setError('Error cargando datos de Hyperliquid');
      }
      
    } catch (error) {
      console.error('Error cargando datos de Hyperliquid:', error);
      setError('Error cargando datos de Hyperliquid');
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshData = () => {
    if (settings) {
      loadHyperliquidData();
    } else {
      setError('No hay configuración de Hyperliquid. Por favor, configura tus wallets primero.');
    }
  };

  const handleOpenNewPosition = () => {
    setShowNewPositionModal(true);
    setOrderError('');
    setNewPositionForm({
      asset: '',
      orderType: 'MARKET',
      positionType: 'LONG',
      size: '0.01',
      leverage: '5'
    });
  };

  const handleSubmitNewPosition = async () => {
    if (!newPositionForm.asset) {
      setOrderError('Por favor selecciona un activo');
      return;
    }

    if (!newPositionForm.size || parseFloat(newPositionForm.size) <= 0) {
      setOrderError('Por favor ingresa un tamaño de posición válido');
      return;
    }

    // Validar precio límite si es orden límite
    if (newPositionForm.orderType === 'LIMIT' && (!newPositionForm.limitPrice || parseFloat(newPositionForm.limitPrice) <= 0)) {
      setOrderError('Por favor ingresa un precio límite válido');
      return;
    }

    setSubmittingOrder(true);
    setOrderError('');

    try {
      const token = localStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const orderData = {
        coin: newPositionForm.asset,
        is_buy: newPositionForm.positionType === 'LONG',
        sz: parseFloat(newPositionForm.size),
        reduce_only: false
      };

      // Agregar precio límite si es orden límite
      if (newPositionForm.orderType === 'LIMIT') {
        orderData.limit_px = parseFloat(newPositionForm.limitPrice);
      }
      
      const response = await fetch(`${baseUrl}/api/hyperliquid/order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(orderData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Orden enviada exitosamente:', result);
        setShowNewPositionModal(false);
        setNewPositionForm({
          asset: '',
          orderType: 'MARKET',
          positionType: 'LONG',
          size: '0.01',
          leverage: '5',
          limitPrice: ''
        });
        // Recargar datos después de un momento
        setTimeout(() => {
          loadHyperliquidData();
        }, 2000);
      } else {
        const errorData = await response.json();
        setOrderError(errorData.detail || 'Error al enviar la orden');
      }
    } catch (error) {
      console.error('Error enviando orden:', error);
      setOrderError('Error de conexión al enviar la orden');
    } finally {
      setSubmittingOrder(false);
    }
  };

  // Función para cerrar posición
  const handleClosePosition = async (position: HyperliquidPosition) => {
    try {
      const token = localStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${baseUrl}/api/hyperliquid/close-position`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          coin: position.coin,
          size: Math.abs(position.size),
          is_long: position.side === 'long'
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Posición cerrada exitosamente:', result);
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Error desconocido' };
      }
    } catch (error) {
      console.error('Error cerrando posición:', error);
      return { success: false, error: 'Error de conexión al cerrar la posición' };
    }
  };

  // Función para ampliar posición
  const handleIncreasePosition = async (position: HyperliquidPosition, amount: number) => {
    try {
      const token = localStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${baseUrl}/api/hyperliquid/increase-position`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          coin: position.coin,
          amount: amount,
          is_long: position.side === 'long'
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Posición ampliada exitosamente:', result);
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Error desconocido' };
      }
    } catch (error) {
      console.error('Error ampliando posición:', error);
      return { success: false, error: 'Error de conexión al ampliar la posición' };
    }
  };

  // Función para reducir posición
  const handleDecreasePosition = async (position: HyperliquidPosition, amount: number) => {
    try {
      const token = localStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${baseUrl}/api/hyperliquid/decrease-position`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          coin: position.coin,
          amount: amount,
          is_long: position.side === 'long'
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Posición reducida exitosamente:', result);
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Error desconocido' };
      }
    } catch (error) {
      console.error('Error reduciendo posición:', error);
      return { success: false, error: 'Error de conexión al reducir la posición' };
    }
  };

  // Función para cancelar orden
  const handleCancelOrder = async (orderId: string, coin: string) => {
    try {
      const token = localStorage.getItem('token');
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${baseUrl}/api/hyperliquid/order/${orderId}?coin=${coin}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Orden cancelada exitosamente:', result);
        return { success: true, data: result };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Error desconocido' };
      }
    } catch (error) {
      console.error('Error cancelando orden:', error);
      return { success: false, error: 'Error de conexión al cancelar la orden' };
    }
  };

  const handleLoadMoreTrades = async () => {
    if (!settings) return;
    
    setLoadingMore(true);
    try {
      const token = localStorage.getItem('token');
      const currentLimit = trades.length + 20; // Cargar 20 más
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/hyperliquid/trades?limit=${currentLimit}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const tradesData = await response.json();
        const newTrades = tradesData.trades || [];
        setTrades(newTrades);
        
        // Si no hay más trades que cargar
        if (newTrades.length <= trades.length) {
          setHasMoreTrades(false);
        }
      } else {
        console.error('Error cargando más trades');
      }
    } catch (error) {
      console.error('Error cargando más trades:', error);
    } finally {
      setLoadingMore(false);
    }
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
    if (!confirm('¿Estás seguro de que quieres limpiar la configuración de Hyperliquid?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/hyperliquid/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          main_wallet: '',
          hyperliquid_wallet: '',
          api_secret_key: ''
        })
      });

      if (response.ok) {
        setSettings(null);
        setSettingsForm({
          main_wallet: '',
          hyperliquid_wallet: '',
          api_secret_key: ''
        });
        setShowSettings(false);
        // Limpiar datos
        setPositions([]);
        setBalances([]);
        setOpenOrders([]);
        setTrades([]);
      } else {
        setSettingsError('Error limpiando configuración');
      }
    } catch (error) {
      console.error('Error limpiando configuración:', error);
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
                      <Button 
                        size="sm" 
                        variant="destructive" 
                        className="bg-red-600 hover:bg-red-700"
                        onClick={() => setShowCloseModal({ show: true, position })}
                      >
                        <X className="w-4 h-4 mr-1" />
                        Cerrar
                      </Button>
                      <Button 
                        size="sm" 
                        variant="default" 
                        className="bg-green-600 hover:bg-green-700"
                        onClick={() => setShowIncreaseModal({ show: true, position })}
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Ampliar
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="border-orange-500 text-orange-600 hover:bg-orange-50"
                        onClick={() => setShowDecreaseModal({ show: true, position })}
                      >
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
                      <Button 
                        size="sm" 
                        variant="destructive" 
                        className="bg-red-600 hover:bg-red-700"
                        onClick={() => setShowCancelOrderModal({ show: true, orderId: order.id, coin: order.coin })}
                      >
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

      {/* New Position Modal */}
      {showNewPositionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold flex items-center">
                  <Plus className="h-5 w-5 text-green-600 mr-2" />
                  Abrir Nueva Posición
                </h2>
                <p className="text-gray-600 text-sm">Abrir una nueva posición en Hyperliquid</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowNewPositionModal(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            {orderError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800 text-sm">{orderError}</p>
              </div>
            )}
            
            <div className="space-y-4">
              {/* Seleccionar Activo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Seleccionar Activo
                </label>
                <select
                  value={newPositionForm.asset}
                  onChange={(e) => setNewPositionForm(prev => ({ ...prev, asset: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={submittingOrder}
                >
                  <option value="">Seleccionar Activo</option>
                  {availableAssets.map(asset => (
                    <option key={asset} value={asset}>{asset}</option>
                  ))}
                </select>
              </div>

              {/* Tipo de Orden */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Orden
                </label>
                <select
                  value={newPositionForm.orderType}
                  onChange={(e) => setNewPositionForm(prev => ({ ...prev, orderType: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={submittingOrder}
                >
                  <option value="MARKET">Precio de Mercado</option>
                  <option value="LIMIT">Precio de Límite</option>
                </select>
              </div>

              {/* Tipo de Posición */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Posición
                </label>
                <select
                  value={newPositionForm.positionType}
                  onChange={(e) => setNewPositionForm(prev => ({ ...prev, positionType: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={submittingOrder}
                >
                  <option value="LONG">Largo (Comprar)</option>
                  <option value="SHORT">Corto (Vender)</option>
                </select>
              </div>

              {/* Tamaño de la Posición */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tamaño de la Posición
                </label>
                <input
                  type="number"
                  step="0.001"
                  min="0.001"
                  value={newPositionForm.size}
                  onChange={(e) => setNewPositionForm(prev => ({ ...prev, size: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.01"
                  disabled={submittingOrder}
                />
              </div>

              {/* Precio Límite - Solo mostrar si es orden límite */}
              {newPositionForm.orderType === 'LIMIT' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Precio Límite (USD)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={newPositionForm.limitPrice}
                    onChange={(e) => setNewPositionForm(prev => ({ ...prev, limitPrice: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="4000.00"
                    disabled={submittingOrder}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Precio al que quieres que se ejecute la orden
                  </p>
                </div>
              )}

              {/* Apalancamiento */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Apalancamiento
                </label>
                <select
                  value={newPositionForm.leverage}
                  onChange={(e) => setNewPositionForm(prev => ({ ...prev, leverage: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={submittingOrder}
                >
                  {leverageOptions.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowNewPositionModal(false)}
                disabled={submittingOrder}
              >
                Cancelar
              </Button>
              <Button 
                className="flex-1 bg-green-600 hover:bg-green-700"
                onClick={handleSubmitNewPosition}
                disabled={submittingOrder}
              >
                {submittingOrder ? 'Enviando...' : 'Confirmar Apertura'}
              </Button>
            </div>
          </div>
        </div>
      )}

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
                  Main Wallet
                </label>
                <input
                  type="text"
                  value={settingsForm.main_wallet}
                  onChange={(e) => setSettingsForm(prev => ({ ...prev, main_wallet: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0x..."
                  disabled={savingSettings}
                />
                <p className="text-xs text-gray-500 mt-1">Wallet principal para ver posiciones y trades</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hyperliquid Wallet
                </label>
                <input
                  type="text"
                  value={settingsForm.hyperliquid_wallet}
                  onChange={(e) => setSettingsForm(prev => ({ ...prev, hyperliquid_wallet: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0x..."
                  disabled={savingSettings}
                />
                <p className="text-xs text-gray-500 mt-1">Wallet específica de Hyperliquid</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Secret Key
                </label>
                <input
                  type="password"
                  value={settingsForm.api_secret_key}
                  onChange={(e) => setSettingsForm(prev => ({ ...prev, api_secret_key: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Tu clave secreta..."
                  disabled={savingSettings}
                />
                <p className="text-xs text-gray-500 mt-1">Clave privada para firmar transacciones</p>
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
                  Limpiar Configuración
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal de Cerrar Posición */}
      {showCloseModal.show && showCloseModal.position && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <X className="w-5 h-5 text-red-500 mr-2" />
                Cerrar Posición
              </h3>
              <button 
                onClick={() => setShowCloseModal({ show: false, position: null })}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-4">
              ¿Estás seguro de que quieres cerrar tu posición de {showCloseModal.position.coin}?
            </p>
            
            <div className="bg-gray-50 rounded-lg p-3 mb-4">
              <div className="text-sm text-gray-600">
                <div className="flex justify-between mb-1">
                  <span>Tamaño actual:</span>
                  <span className="font-mono">{Math.abs(showCloseModal.position.size).toFixed(6)} {showCloseModal.position.coin}</span>
                </div>
                <div className="flex justify-between mb-1">
                  <span>P&L actual:</span>
                  <span className={showCloseModal.position.unrealizedPnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {showCloseModal.position.unrealizedPnl >= 0 ? '+' : ''}{formatUSD(showCloseModal.position.unrealizedPnl)}
                  </span>
                </div>
              </div>
            </div>

            {closeModalResult.message && (
              <div className={`mb-4 p-3 rounded-lg ${closeModalResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                {closeModalResult.message}
              </div>
            )}

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowCloseModal({ show: false, position: null });
                  setCloseModalResult({ success: false, message: '' });
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={modalLoading}
              >
                Cancelar
              </button>
              <button
                onClick={async () => {
                  setModalLoading(true);
                  setCloseModalResult({ success: false, message: '' });
                  
                  try {
                    const result = await handleClosePosition(showCloseModal.position);
                    if (result.success) {
                      setCloseModalResult({ success: true, message: `Posición de ${showCloseModal.position.coin} cerrada exitosamente` });
                      setTimeout(() => {
                        setShowCloseModal({ show: false, position: null });
                        setCloseModalResult({ success: false, message: '' });
                        loadHyperliquidData();
                      }, 2000);
                    } else {
                      setCloseModalResult({ success: false, message: result.error || 'Error al cerrar la posición' });
                    }
                  } catch (error) {
                    setCloseModalResult({ success: false, message: 'Error de conexión' });
                  } finally {
                    setModalLoading(false);
                  }
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                disabled={modalLoading}
              >
                {modalLoading ? 'Cerrando...' : 'Sí, Cerrar Posición'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Ampliar Posición */}
      {showIncreaseModal.show && showIncreaseModal.position && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Plus className="w-5 h-5 text-green-500 mr-2" />
                Ampliar Posición
              </h3>
              <button 
                onClick={() => setShowIncreaseModal({ show: false, position: null })}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-4">
              Ampliar tu posición de {showIncreaseModal.position.coin}
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cantidad ({showIncreaseModal.position.coin})
                </label>
                <input
                  type="number"
                  step="0.001"
                  min="0.001"
                  value={modalAmount}
                  onChange={(e) => setModalAmount(e.target.value)}
                  placeholder="0.001"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  disabled={modalLoading}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Apalancamiento (1-20x)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="20"
                  value={modalLeverage}
                  onChange={(e) => setModalLeverage(e.target.value)}
                  placeholder="5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  disabled={modalLoading}
                />
              </div>
            </div>

            {increaseModalResult.message && (
              <div className={`mt-4 p-3 rounded-lg ${increaseModalResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                {increaseModalResult.message}
              </div>
            )}

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowIncreaseModal({ show: false, position: null });
                  setIncreaseModalResult({ success: false, message: '' });
                  setModalAmount('');
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={modalLoading}
              >
                Cancelar
              </button>
              <button
                onClick={async () => {
                  if (!modalAmount || parseFloat(modalAmount) <= 0) {
                    setIncreaseModalResult({ success: false, message: 'Por favor ingresa una cantidad válida' });
                    return;
                  }
                  
                  setModalLoading(true);
                  setIncreaseModalResult({ success: false, message: '' });
                  
                  try {
                    const result = await handleIncreasePosition(showIncreaseModal.position, parseFloat(modalAmount));
                    if (result.success) {
                      setIncreaseModalResult({ success: true, message: `Posición de ${showIncreaseModal.position.coin} ampliada exitosamente` });
                      setTimeout(() => {
                        setShowIncreaseModal({ show: false, position: null });
                        setIncreaseModalResult({ success: false, message: '' });
                        setModalAmount('');
                        loadHyperliquidData();
                      }, 2000);
                    } else {
                      setIncreaseModalResult({ success: false, message: result.error || 'Error al ampliar la posición' });
                    }
                  } catch (error) {
                    setIncreaseModalResult({ success: false, message: 'Error de conexión' });
                  } finally {
                    setModalLoading(false);
                  }
                }}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                disabled={modalLoading || !modalAmount}
              >
                {modalLoading ? 'Ampliando...' : 'Ampliar Posición'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Reducir Posición */}
      {showDecreaseModal.show && showDecreaseModal.position && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Minus className="w-5 h-5 text-orange-500 mr-2" />
                Reducir Posición
              </h3>
              <button 
                onClick={() => setShowDecreaseModal({ show: false, position: null })}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-4">
              Reducir tu posición de {showDecreaseModal.position.coin}
            </p>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cantidad ({showDecreaseModal.position.coin})
              </label>
              <input
                type="number"
                step="0.001"
                min="0.001"
                value={modalAmount}
                onChange={(e) => setModalAmount(e.target.value)}
                placeholder="0.001"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                disabled={modalLoading}
              />
            </div>

            {decreaseModalResult.message && (
              <div className={`mt-4 p-3 rounded-lg ${decreaseModalResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                {decreaseModalResult.message}
              </div>
            )}

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowDecreaseModal({ show: false, position: null });
                  setDecreaseModalResult({ success: false, message: '' });
                  setModalAmount('');
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={modalLoading}
              >
                Cancelar
              </button>
              <button
                onClick={async () => {
                  if (!modalAmount || parseFloat(modalAmount) <= 0) {
                    setDecreaseModalResult({ success: false, message: 'Por favor ingresa una cantidad válida' });
                    return;
                  }
                  
                  setModalLoading(true);
                  setDecreaseModalResult({ success: false, message: '' });
                  
                  try {
                    const result = await handleDecreasePosition(showDecreaseModal.position, parseFloat(modalAmount));
                    if (result.success) {
                      setDecreaseModalResult({ success: true, message: `Posición de ${showDecreaseModal.position.coin} reducida exitosamente` });
                      setTimeout(() => {
                        setShowDecreaseModal({ show: false, position: null });
                        setDecreaseModalResult({ success: false, message: '' });
                        setModalAmount('');
                        loadHyperliquidData();
                      }, 2000);
                    } else {
                      setDecreaseModalResult({ success: false, message: result.error || 'Error al reducir la posición' });
                    }
                  } catch (error) {
                    setDecreaseModalResult({ success: false, message: 'Error de conexión' });
                  } finally {
                    setModalLoading(false);
                  }
                }}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
                disabled={modalLoading || !modalAmount}
              >
                {modalLoading ? 'Reduciendo...' : 'Reducir Posición'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Cancelar Orden */}
      {showCancelOrderModal.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <X className="w-5 h-5 text-red-500 mr-2" />
                Cancelar Orden
              </h3>
              <button 
                onClick={() => {
                  setShowCancelOrderModal({ show: false, orderId: '', coin: '' });
                  setCancelOrderModalResult({ success: false, message: '' });
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-4">
              ¿Estás seguro de que quieres cancelar tu orden de {showCancelOrderModal.coin}?
            </p>
            
            <div className="bg-gray-50 rounded-lg p-3 mb-4">
              <div className="text-sm text-gray-600">
                <div className="flex justify-between mb-1">
                  <span>Moneda:</span>
                  <span className="font-mono">{showCancelOrderModal.coin}</span>
                </div>
                <div className="flex justify-between mb-1">
                  <span>Order ID:</span>
                  <span className="font-mono text-xs">{showCancelOrderModal.orderId}</span>
                </div>
              </div>
            </div>

            {cancelOrderModalResult.message && (
              <div className={`mb-4 p-3 rounded-lg ${cancelOrderModalResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                {cancelOrderModalResult.message}
              </div>
            )}

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowCancelOrderModal({ show: false, orderId: '', coin: '' });
                  setCancelOrderModalResult({ success: false, message: '' });
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={modalLoading}
              >
                Cancelar
              </button>
              <button
                onClick={async () => {
                  setModalLoading(true);
                  setCancelOrderModalResult({ success: false, message: '' });
                  
                  try {
                    const result = await handleCancelOrder(showCancelOrderModal.orderId, showCancelOrderModal.coin);
                    if (result.success) {
                      setCancelOrderModalResult({ success: true, message: `Orden de ${showCancelOrderModal.coin} cancelada exitosamente` });
                      setTimeout(() => {
                        setShowCancelOrderModal({ show: false, orderId: '', coin: '' });
                        setCancelOrderModalResult({ success: false, message: '' });
                        loadHyperliquidData();
                      }, 2000);
                    } else {
                      setCancelOrderModalResult({ success: false, message: result.error || 'Error al cancelar la orden' });
                    }
                  } catch (error) {
                    setCancelOrderModalResult({ success: false, message: 'Error de conexión' });
                  } finally {
                    setModalLoading(false);
                  }
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                disabled={modalLoading}
              >
                {modalLoading ? 'Cancelando...' : 'Sí, Cancelar Orden'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
