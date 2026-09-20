from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="Item API")

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)


class ItemPublic(BaseModel):
    id: int
    name: str
    price: float

class ItemListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ItemPublic]

class ItemUpdate(BaseModel):
    name: str | None
    price: float | None


_items: list[ItemPublic] = []
_next_id = 0


def _find(item_id: int) -> ItemPublic | None:
    for item in _items:
        if item.id == item_id:
            return item
    return None

def _check_name_exists(name: str) -> bool:
    name = name.lower().strip()

    for item in _items:
        if item.name == name:
            return True
    return False

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/items", response_model=ItemListResponse)
def read_items(
    min_price: float | None = Query(None, ge=0, description="Minimum price filter"),
    max_price: float | None = Query(None, ge=0, description="Maximum price filter"),
    sort_by: str | None = Query("id", pattern="^(id|name|price)$", description="Field to sort by (name or price)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, description="Maximum number of items to return"),
    q: str | None = Query(None, description="Query string for searching items"),
):
    filtered_items = _items
    if q:
        filtered_items = [item for item in filtered_items if q.lower() in item.name.lower()]
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]
    if sort_by == "name":
        filtered_items = sorted(filtered_items, key=lambda x: x.name)
    elif sort_by == "price":
        filtered_items = sorted(filtered_items, key=lambda x: x.price)

    return ItemListResponse(
        total=len(filtered_items),
        skip=skip,
        limit=limit,
        items=filtered_items[skip: skip + limit]
    )


@app.get("/items/{item_id}", response_model=ItemPublic)
def get_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(item: ItemCreate):
    if _check_name_exists(item.name):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    id = _next_id

    new_item = ItemPublic(
        id=id,
        name=item.name.lower().strip(),
        price=item.price,
    )

    _items.append(new_item)
    _next_id += 1
    return new_item


@app.put("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, data: ItemCreate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = ItemPublic(
        id=item.id,
        name=data.name.lower().strip(),
        price=data.price,
    )
    index = _items.index(item)
    _items[index] = updated_item
    return updated_item

@app.patch("/items/{item_id}", response_model=ItemPublic)
def patch_item(item_id: int, data: ItemUpdate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if _check_name_exists(data.name):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    update_data = data.model_dump(exclude_unset=True)

    updated_item = ItemPublic(
        id=item.id,
        name=update_data.get("name", item.name).lower().strip(),
        price=update_data.get("price", item.price),
    )
    index = _items.index(item)
    _items[index] = updated_item
    return updated_item

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    _items.remove(item)
    return None