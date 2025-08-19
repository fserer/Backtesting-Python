import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, Dataset, UpdateDatasetRequest } from '../lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Edit, Trash2, Database, Calendar, Hash } from 'lucide-react';

interface DatasetManagerProps {
  onDatasetSelect: (dataset: Dataset) => void;
  selectedDataset?: Dataset;
}

export function DatasetManager({ onDatasetSelect, selectedDataset }: DatasetManagerProps) {
  const [editingDataset, setEditingDataset] = useState<Dataset | null>(null);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const queryClient = useQueryClient();

  // Obtener datasets
  const { data: datasets = [], isLoading, error } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => apiClient.getDatasets(),
  });

  // Mutación para actualizar dataset
  const updateMutation = useMutation({
    mutationFn: ({ id, request }: { id: number; request: UpdateDatasetRequest }) =>
      apiClient.updateDataset(id, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
      setEditingDataset(null);
    },
  });

  // Mutación para eliminar dataset
  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.deleteDataset(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
      if (selectedDataset && datasets.find(d => d.id === selectedDataset.id)) {
        onDatasetSelect(datasets[0] || null);
      }
    },
  });

  const handleEdit = (dataset: Dataset) => {
    setEditingDataset(dataset);
    setEditName(dataset.name);
    setEditDescription(dataset.description || '');
  };

  const handleSave = () => {
    if (!editingDataset) return;

    updateMutation.mutate({
      id: editingDataset.id,
      request: {
        name: editName,
        description: editDescription || undefined,
      },
    });
  };

  const handleCancel = () => {
    setEditingDataset(null);
    setEditName('');
    setEditDescription('');
  };

  const handleDelete = (dataset: Dataset) => {
    if (confirm(`¿Estás seguro de que quieres eliminar el dataset "${dataset.name}"? Esta acción no se puede deshacer.`)) {
      deleteMutation.mutate(dataset.id);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Cargando datasets...</CardTitle>
        </CardHeader>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-red-600">Error al cargar datasets</CardTitle>
          <CardDescription>{error.message}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Datasets Disponibles
        </CardTitle>
        <CardDescription>
          Selecciona un dataset para ejecutar backtests
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {datasets.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No hay datasets disponibles</p>
            <p className="text-sm">Sube un archivo CSV para crear tu primer dataset</p>
          </div>
        ) : (
          <div className="space-y-3">
            {datasets.map((dataset) => (
              <div
                key={dataset.id}
                className={`p-4 border rounded-lg transition-colors ${
                  selectedDataset?.id === dataset.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {editingDataset?.id === dataset.id ? (
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor={`name-${dataset.id}`}>Nombre</Label>
                      <Input
                        id={`name-${dataset.id}`}
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        placeholder="Nombre del dataset"
                      />
                    </div>
                    <div>
                      <Label htmlFor={`description-${dataset.id}`}>Descripción</Label>
                      <Input
                        id={`description-${dataset.id}`}
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        placeholder="Descripción opcional"
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={handleSave}
                        disabled={updateMutation.isPending}
                      >
                        {updateMutation.isPending ? 'Guardando...' : 'Guardar'}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleCancel}
                        disabled={updateMutation.isPending}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Header con nombre */}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-lg">{dataset.name}</h3>
                        {selectedDataset?.id === dataset.id && (
                          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full font-medium">
                            Seleccionado
                          </span>
                        )}
                      </div>
                      {dataset.description && (
                        <p className="text-sm text-gray-600">{dataset.description}</p>
                      )}
                    </div>
                    
                    {/* Botones de acción */}
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant={selectedDataset?.id === dataset.id ? "default" : "outline"}
                        onClick={() => onDatasetSelect(dataset)}
                        disabled={selectedDataset?.id === dataset.id}
                        className="flex-1"
                      >
                        {selectedDataset?.id === dataset.id ? 'Seleccionado' : 'Seleccionar'}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(dataset)}
                        className="px-3"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(dataset)}
                        disabled={deleteMutation.isPending}
                        className="px-3 text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    {/* Footer con estadísticas */}
                    <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <Hash className="h-3 w-3" />
                          <span className="font-medium">{dataset.row_count.toLocaleString()}</span> registros
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(dataset.created_at)}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
