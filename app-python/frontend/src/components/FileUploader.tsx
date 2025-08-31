import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { cn } from '@/lib/utils';

interface FileUploaderProps {
  onFileUpload: (file: File, datasetName: string, datasetDescription?: string) => void;
  isUploading: boolean;
  uploadResult?: {
    ok: boolean;
    rows: number;
    freq_detected: string;
    dataset_id: number;
  };
}

export function FileUploader({ onFileUpload, isUploading, uploadResult }: FileUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState('');
  const [datasetDescription, setDatasetDescription] = useState('');
  const [showForm, setShowForm] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setSelectedFile(file);
        setDatasetName(file.name.replace('.csv', ''));
        setShowForm(true);
      }
    }
  }, []);

  const handleUpload = () => {
    if (selectedFile && datasetName.trim()) {
      onFileUpload(selectedFile, datasetName.trim(), datasetDescription.trim() || undefined);
      setShowForm(false);
      setSelectedFile(null);
      setDatasetName('');
      setDatasetDescription('');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setSelectedFile(null);
    setDatasetName('');
    setDatasetDescription('');
  };

  const { getRootProps, getInputProps, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false,
    disabled: isUploading || showForm
  });

  return (
    <Card className="border border-gray-200">
      <div className="min-h-[3rem] flex items-center px-6 py-3 rounded-t-lg">
        <div className="flex items-center gap-2 text-lg text-blue-900 font-semibold">
          <Upload className="h-5 w-5" />
          Subir Archivo CSV
        </div>
      </div>
      <CardContent className="px-4 py-4">
        {showForm ? (
          <div className="space-y-4">
            <div className="p-4 border rounded-lg bg-gray-50">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4" />
                <span className="text-sm font-medium">{selectedFile?.name}</span>
              </div>
              <p className="text-xs text-gray-600">Archivo seleccionado</p>
            </div>
            
            <div className="space-y-3">
              <div>
                <Label htmlFor="dataset-name">Nombre del Dataset *</Label>
                <Input
                  id="dataset-name"
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                  placeholder="Ej: Bitcoin Daily Data 2023"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="dataset-description">Descripción (opcional)</Label>
                <Input
                  id="dataset-description"
                  value={datasetDescription}
                  onChange={(e) => setDatasetDescription(e.target.value)}
                  placeholder="Descripción del dataset..."
                />
              </div>
              
              <div className="flex gap-2">
                <Button
                  onClick={handleUpload}
                  disabled={isUploading || !datasetName.trim()}
                  className="flex-1"
                >
                  {isUploading ? 'Subiendo...' : 'Crear Dataset'}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleCancel}
                  disabled={isUploading}
                >
                  Cancelar
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div
            {...getRootProps()}
            className={cn(
              "border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors",
              dragActive ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-gray-400",
              isDragReject && "border-destructive bg-destructive/5",
              isUploading && "opacity-50 cursor-not-allowed"
            )}
          >
            <input {...getInputProps()} />
            
            {isUploading ? (
              <div className="flex flex-col items-center gap-2">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="text-sm text-muted-foreground">Subiendo archivo...</p>
              </div>
            ) : uploadResult ? (
              <div className="flex flex-col items-center gap-2">
                {uploadResult.ok ? (
                  <CheckCircle className="h-8 w-8 text-green-500" />
                ) : (
                  <AlertCircle className="h-8 w-8 text-red-500" />
                )}
                <p className="text-sm font-medium">
                  {uploadResult.ok ? 'Dataset creado correctamente' : 'Error al crear dataset'}
                </p>
                {uploadResult.ok && (
                  <div className="text-xs text-muted-foreground">
                    {uploadResult.rows} filas | Frecuencia: {uploadResult.freq_detected}
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <FileText className="h-8 w-8 text-gray-400" />
                <div>
                  <p className="text-gray-600 mb-1">
                    <strong>Arrastra y suelta tu archivo CSV aquí</strong>
                  </p>
                  <p className="text-sm text-gray-500 mb-2">o haz clic para seleccionar</p>
                </div>
                <p className="text-xs text-gray-400 mb-3">Formato requerido: t, v, usd</p>
                <label
                  htmlFor="csv-upload"
                  className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
                >
                  Seleccionar Archivo
                </label>
              </div>
            )}
          </div>
        )}

        {isDragReject && (
          <p className="text-xs text-destructive mt-2 text-center">
            Solo se permiten archivos CSV
          </p>
        )}
      </CardContent>
    </Card>
  );
}

