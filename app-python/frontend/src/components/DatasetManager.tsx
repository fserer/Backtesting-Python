import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, Dataset, UpdateDatasetRequest } from '../lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Edit, Trash2, Database, Calendar, Hash } from 'lucide-react';
import { formatDate } from '../lib/utils';

interface DatasetManagerProps {
  onDatasetSelect: (dataset: Dataset) => void;
  selectedDataset?: Dataset;
  showSelectionButton?: boolean;
}

export function DatasetManager({ onDatasetSelect, selectedDataset, showSelectionButton = true }: DatasetManagerProps) {
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

  // Usar la función de utilidad que maneja la zona horaria correctamente
  const formatDatasetDate = (dateString: string) => {
    return formatDate(dateString);
  };

  if (isLoading) {
    return (
      <Card className="border border-gray-200">
        <div className="min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
          <div className="flex items-center gap-2 text-lg text-green-900 font-semibold">
            <Database className="h-5 w-5" />
            Datasets Disponibles
          </div>
        </div>
        <CardContent className="px-4 py-4">
          <p className="text-sm text-gray-600 mb-4">Gestiona y visualiza todos los datasets disponibles</p>
          <div className="text-center py-8 text-gray-500">
            <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Cargando datasets...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border border-gray-200">
        <div className="min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
          <div className="flex items-center gap-2 text-lg text-green-900 font-semibold">
            <Database className="h-5 w-5" />
            Datasets Disponibles
          </div>
        </div>
        <CardContent className="px-4 py-4">
          <p className="text-sm text-gray-600 mb-4">Gestiona y visualiza todos los datasets disponibles</p>
          <div className="text-center py-8 text-red-500">
            <p>Error al cargar datasets</p>
            <p className="text-sm">{error.message}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border border-gray-200">
      <div className="min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
        <div className="flex items-center gap-2 text-lg text-green-900 font-semibold">
          <Database className="h-5 w-5" />
          Datasets Disponibles
        </div>
      </div>
      <CardContent className="px-4 py-4">
        <p className="text-sm text-gray-600 mb-4">Gestiona y visualiza todos los datasets disponibles</p>

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
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                {editingDataset?.id === dataset.id ? (
                  <div className="flex-1 space-y-3">
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
                  <>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{dataset.name}</h4>
                      <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Hash className="h-3 w-3" />
                          {dataset.row_count.toLocaleString()} registros
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDatasetDate(dataset.created_at)}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => handleEdit(dataset)}>
                        <Edit className="h-4 w-4 text-blue-600" />
                      </Button>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => handleDelete(dataset)} disabled={deleteMutation.isPending}>
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
