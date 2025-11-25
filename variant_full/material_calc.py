PRODUCT_COEFFICIENTS = {
    1: 1.20,
    2: 1.10,
    3: 1.35
}

MATERIAL_WASTE = {
    1: 0.05,
    2: 0.08,
    3: 0.02
}


def calculate_material(product_type_id, material_type_id,
                       quantity, param1, param2) -> int:

    if product_type_id not in PRODUCT_COEFFICIENTS:
        return -1
    if material_type_id not in MATERIAL_WASTE:
        return -1
    if not isinstance(quantity, int) or quantity <= 0:
        return -1
    if param1 <= 0 or param2 <= 0:
        return -1

    coef = PRODUCT_COEFFICIENTS[product_type_id]
    waste = MATERIAL_WASTE[material_type_id]

    base_one = param1 * param2 * coef
    total = base_one * quantity
    total_with_waste = total * (1 + waste)

    return int(total_with_waste)