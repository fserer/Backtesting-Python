#!/usr/bin/env python3
"""
Script para probar la lógica de Maker/Taker
"""

def test_maker_taker_logic():
    """Prueba la lógica de determinación de Maker/Taker"""
    
    print("🧪 Probando lógica de Maker/Taker")
    print("-" * 50)
    
    # Casos de prueba
    test_cases = [
        # (fee, volume, expected_type, description)
        (0.045, 100, 'taker', 'Fee 0.045% - Debería ser Taker'),
        (0.015, 100, 'maker', 'Fee 0.015% - Debería ser Maker'),
        (0.050, 100, 'taker', 'Fee 0.050% - Debería ser Taker'),
        (0.010, 100, 'maker', 'Fee 0.010% - Debería ser Maker'),
        (0.045, 50, 'taker', 'Fee 0.045% con volumen 50 - Debería ser Taker'),
        (0.015, 50, 'maker', 'Fee 0.015% con volumen 50 - Debería ser Maker'),
    ]
    
    for fee_percent, volume, expected, description in test_cases:
        # Calcular fee absoluto
        fee_absolute = (fee_percent / 100) * volume
        
        # Aplicar la lógica del backend
        fee_percentage = (fee_absolute / volume * 100) if volume > 0 else 0
        order_type = 'maker' if fee_percentage <= 0.015 else 'taker'
        
        # Verificar resultado
        status = "✅" if order_type == expected else "❌"
        
        print(f"{status} {description}")
        print(f"   Fee: {fee_percent}% (${fee_absolute:.4f})")
        print(f"   Volume: ${volume}")
        print(f"   Calculated: {fee_percentage:.4f}%")
        print(f"   Result: {order_type.upper()}")
        print(f"   Expected: {expected.upper()}")
        print()

if __name__ == "__main__":
    test_maker_taker_logic()
