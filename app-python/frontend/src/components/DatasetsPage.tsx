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
    <div className="max-w-7xl mx-auto p-4 space-y-4">
      <div className="flex items-center gap-3 mb-4">
        <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
        </svg>
        <h1 className="text-2xl font-bold text-gray-900">Gestión de Datasets</h1>
      </div>

      <p className="text-gray-600 -mt-2 mb-4">
        Sube archivos CSV, gestiona la actualización automática y visualiza todos los datasets disponibles.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Columna Izquierda - Subir CSV y Actualización */}
        <div className="space-y-4">
          {/* Subir Archivo CSV */}
          <FileUploader
            onFileUpload={onFileUpload}
            isUploading={isUploading}
            uploadResult={uploadResult || undefined}
          />

          {/* Actualización Automática de Datasets */}
          <DatasetUpdater />
        </div>

        {/* Columna Derecha - Datasets Disponibles */}
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
