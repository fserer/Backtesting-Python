import React from 'react';
import { FileUploader } from './FileUploader';
import { DatasetManager } from './DatasetManager';
import DatasetUpdater from './DatasetUpdater';
import { UploadResponse } from '../lib/api';

interface DatasetsPageProps {
  onFileUpload: (file: File, datasetName: string, datasetDescription?: string) => Promise<void>;
  isUploading: boolean;
  uploadResult: UploadResponse | null;
}

const DatasetsPage: React.FC<DatasetsPageProps> = ({ onFileUpload, isUploading, uploadResult }) => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">Gestión de Datasets</h2>
        <p className="text-muted-foreground">
          Sube archivos CSV, gestiona la actualización automática y visualiza todos los datasets disponibles.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Primer tercio - Subir CSV y Actualización automática */}
        <div className="space-y-6">
          {/* Subir Archivo CSV */}
          <FileUploader
            onFileUpload={onFileUpload}
            isUploading={isUploading}
            uploadResult={uploadResult || undefined}
          />

          {/* Actualización Automática de Datasets */}
          <DatasetUpdater />
        </div>

        {/* Dos tercios - Listado de Datasets */}
        <div className="lg:col-span-2">
          <DatasetManager
            onDatasetSelect={() => {}} // No necesitamos selección aquí
            selectedDataset={undefined}
            showSelectionButton={false} // Ocultar botón de selección
          />
        </div>
      </div>
    </div>
  );
};

export default DatasetsPage;
