#!/usr/bin/env python3
"""
Actualiza incrementalmente un dataset de NodeCharts usando el último tick en SQLite.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.nodecharts_service import NodeChartsService
from services.sqlite_client import get_dataset_by_name, get_last_tick

API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdG9yZSI6MCwidXNlcmlkIjoyNTUyLCJjcmVhdGlvbnRpbWUiOjE3MTM3Nzc0NTJ9.bFd4Y_134nmvUjboy8CZRkMRc8WngTA9_zDx18qAkXE"

def main():
    # Nombre EXACTO en SQLite
    dataset_name = "SOPR CP - Hour"
    service = NodeChartsService(API_KEY)

    ds = get_dataset_by_name(dataset_name)
    if not ds:
        print(f"❌ Dataset no encontrado: {dataset_name}")
        return

    before = get_last_tick(ds['id'])
    print(f"Último tick antes: {before['t'] if before else 'None'}")

    ok, rows = service.update_dataset(dataset_name, db_client=None)
    print(f"Resultado actualización: ok={ok}, filas añadidas={rows}")

    after = get_last_tick(ds['id'])
    print(f"Último tick después: {after['t'] if after else 'None'}")

if __name__ == "__main__":
    main()
