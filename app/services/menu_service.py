from app.schemas.menu import MenuProductItem, MenuRead
from db import crud
from db.models import Menu


def build_menu_read(menu: Menu) -> MenuRead:
    """Convertit un objet SQLModel Menu en schéma JSON MenuRead."""
    if menu.id is None:
        raise ValueError("Le menu doit avoir un ID")
    product_items=[]
    for mp in menu.menu_products:
        product_items.append(MenuProductItem(product_id=mp.product_id, quantity=mp.quantity))
    return MenuRead(id=menu.id,name=menu.name,description=menu.description,price=menu.price,
        start_date=menu.start_date,end_date=menu.end_date,
        is_available=menu.is_available,is_deleted=menu.is_deleted,
        available_stock=crud.get_menu_available_stock(menu),products=product_items)