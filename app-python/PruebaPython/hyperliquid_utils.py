#!/usr/bin/env python3
"""
Utilidades comunes para los scripts de Hyperliquid
"""

# Mapeo de activos principales con sus IDs
ASSET_IDS = {
    "BTC": 0, "ETH": 1, "ATOM": 2, "MATIC": 3, "DYDX": 4, "SOL": 5, "AVAX": 6, "BNB": 7,
    "APE": 8, "OP": 9, "LTC": 10, "ARB": 11, "DOGE": 12, "INJ": 13, "SUI": 14, "kPEPE": 15,
    "CRV": 16, "LDO": 17, "LINK": 18, "STX": 19, "RNDR": 20, "CFX": 21, "FTM": 22, "GMX": 23,
    "SNX": 24, "XRP": 25, "BCH": 26, "APT": 27, "AAVE": 28, "COMP": 29, "MKR": 30, "WLD": 31,
    "FXS": 32, "HPOS": 33, "RLB": 34, "UNIBOT": 35, "YGG": 36, "TRX": 37, "kSHIB": 38, "UNI": 39,
    "SEI": 40, "RUNE": 41, "OX": 42, "FRIEND": 43, "SHIA": 44, "CYBER": 45, "ZRO": 46, "BLZ": 47,
    "DOT": 48, "BANANA": 49, "TRB": 50, "FTT": 51, "LOOM": 52, "OGN": 53, "RDNT": 54, "ARK": 55,
    "BNT": 56, "CANTO": 57, "REQ": 58, "BIGTIME": 59, "KAS": 60, "ORBS": 61, "BLUR": 62, "TIA": 63,
    "BSV": 64, "ADA": 65, "TON": 66, "MINA": 67, "POLYX": 68, "GAS": 69, "PENDLE": 70, "STG": 71,
    "FET": 72, "STRAX": 73, "NEAR": 74, "MEME": 75, "ORDI": 76, "BADGER": 77, "NEO": 78, "ZEN": 79,
    "FIL": 80, "PYTH": 81, "SUSHI": 82, "ILV": 83, "IMX": 84, "kBONK": 85, "GMT": 86, "SUPER": 87,
    "USTC": 88, "NFTI": 89, "JUP": 90, "kLUNC": 91, "RSR": 92, "GALA": 93, "JTO": 94, "NTRN": 95,
    "ACE": 96, "MAV": 97, "WIF": 98, "CAKE": 99, "PEOPLE": 100, "ENS": 101, "ETC": 102, "XAI": 103,
    "MANTA": 104, "UMA": 105, "ONDO": 106, "ALT": 107, "ZETA": 108, "DYM": 109, "MAVIA": 110, "W": 111,
    "PANDORA": 112, "STRK": 113, "PIXEL": 114, "AI": 115, "TAO": 116, "AR": 117, "MYRO": 118, "kFLOKI": 119,
    "BOME": 120, "ETHFI": 121, "ENA": 122, "MNT": 123, "TNSR": 124, "SAGA": 125, "MERL": 126, "HBAR": 127,
    "POPCAT": 128, "OMNI": 129, "EIGEN": 130, "REZ": 131, "NOT": 132, "TURBO": 133, "BRETT": 134, "IO": 135,
    "ZK": 136, "BLAST": 137, "LISTA": 138, "MEW": 139, "RENDER": 140, "kDOGS": 141, "POL": 142, "CATI": 143,
    "CELO": 144, "HMSTR": 145, "SCR": 146, "NEIROETH": 147, "kNEIRO": 148, "GOAT": 149, "MOODENG": 150,
    "GRASS": 151, "PURR": 152, "PNUT": 153, "XLM": 154, "CHILLGUY": 155, "SAND": 156, "IOTA": 157, "ALGO": 158,
    "HYPE": 159, "ME": 160, "MOVE": 161, "VIRTUAL": 162, "PENGU": 163, "USUAL": 164, "FARTCOIN": 165, "AI16Z": 166,
    "AIXBT": 167, "ZEREBRO": 168, "BIO": 169, "GRIFFAIN": 170, "SPX": 171, "S": 172, "MORPHO": 173, "TRUMP": 174,
    "MELANIA": 175, "ANIME": 176, "VINE": 177, "VVV": 178, "JELLY": 179, "BERA": 180, "TST": 181, "LAYER": 182,
    "IP": 183, "OM": 184, "KAITO": 185, "NIL": 186, "PAXG": 187, "PROMPT": 188, "BABY": 189, "WCT": 190,
    "HYPER": 191, "ZORA": 192, "INIT": 193, "DOOD": 194, "LAUNCHCOIN": 195, "NXPC": 196, "SOPH": 197, "RESOLV": 198,
    "SYRUP": 199, "PUMP": 200, "PROVE": 201
}

def get_asset_id(coin):
    """Obtener el ID del activo por su símbolo"""
    return ASSET_IDS.get(coin, 1)  # Por defecto ETH si no se encuentra

def show_payload(coin, is_buy, size, reduce_only=False):
    """Mostrar el payload que se enviará a la API de Hyperliquid"""
    import json
    from hyperliquid.utils.signing import order_request_to_order_wire, order_wires_to_order_action
    
    # Obtener el ID del activo
    asset_id = get_asset_id(coin)
    
    # Crear el OrderRequest
    order_request = {
        "coin": coin,
        "is_buy": is_buy,
        "sz": size,  # float, no string
        "limit_px": 0.0,  # Market price (float, no string)
        "reduce_only": reduce_only,
        "order_type": {"limit": {"tif": "Ioc"}}
    }
    
    # Convertir a OrderWire
    order_wire = order_request_to_order_wire(order_request, asset_id)
    
    # Convertir a OrderAction
    order_action = order_wires_to_order_action([order_wire])
    
    print("🔗 URL: https://api.hyperliquid.xyz/exchange")
    print("📋 Método: POST")
    print("📦 Payload:")
    print(json.dumps(order_action, indent=2))
    print("="*60) 