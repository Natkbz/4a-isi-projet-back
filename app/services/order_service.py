from app.schemas.order import OrderMenuRead, OrderProductRead, OrderRead
from db.models import Order


def build_order_read(order: Order) -> OrderRead:
    """Convertit un objet SQLModel Order en schéma OrderRead."""
    if order.id is None:
        raise ValueError("Id commande manquant")
    products = []
    for op in order.order_products:
        products.append(OrderProductRead(id=op.id,product_id=op.product_id, product_name=op.product.name if op.product else "Produit supprimé",
            quantity=op.quantity, unit_price=op.unit_price))

    menus = []
    for om in order.order_menus:
        menus.append(OrderMenuRead(id=om.id,menu_id=om.menu_id, menu_name=om.menu.name if om.menu else "Menu supprimé",
            quantity=om.quantity, unit_price=om.unit_price))


    total_price = sum(p.quantity * p.unit_price for p in products) + sum(m.quantity * m.unit_price for m in menus)

    return OrderRead(id=order.id, user_id=order.user_id, pickup_date=order.pickup_date, status=order.status,
        created_at=order.created_at, total_price=round(total_price, 2), products=products, menus=menus)