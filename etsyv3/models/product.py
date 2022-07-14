from typing import Any, Dict, List


class Product:
    def __init__(
        self,
        sku: str,
        property_values: List[Dict[str, Any]],
        offerings: List[Dict[str, Any]],
    ):
        self.sku = sku
        self.property_values = property_values
        self.offerings = offerings
