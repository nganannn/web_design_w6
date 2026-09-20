from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


app = FastAPI(title="Item API")


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=str(frontend_dir)),
    name="static",
)


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)


class ItemPublic(BaseModel):
    id: int
    name: str
    price: float


class ItemListResponse(BaseModel):
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None


class HousePriceRequest(BaseModel):
    area_sqm: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    distance_to_center_km: float


class HousePricePrediction(BaseModel):
    predicted_price: float
    currency: str = "VND"


_items: list[ItemPublic] = []
_next_id = 0


def _find(item_id: int) -> ItemPublic | None:
    for item in _items:
        if item.id == item_id:
            return item

    return None


def _check_name_exists(
    name: str,
    exclude_id: int | None = None,
) -> bool:
    normalized_name = name.lower().strip()

    for item in _items:
        if exclude_id is not None and item.id == exclude_id:
            continue

        if item.name.lower().strip() == normalized_name:
            return True

    return False


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/items", response_model=ItemListResponse)
def read_items(
    min_price: float | None = Query(
        None,
        ge=0,
        description="Minimum price filter",
    ),
    max_price: float | None = Query(
        None,
        ge=0,
        description="Maximum price filter",
    ),
    q: str | None = Query(
        None,
        min_length=2,
        description="Search item name",
    ),
    sort_by: str = Query(
        "id",
        pattern="^(id|name|price)$",
        description="Field to sort by",
    ),
    order: str = Query(
        "asc",
        pattern="^(asc|desc)$",
        description="Sort order",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of items to skip",
    ),
    limit: int = Query(
        10,
        ge=1,
        description="Maximum number of items to return",
    ),
):
    filtered_items = _items.copy()

    if min_price is not None:
        filtered_items = [
            item
            for item in filtered_items
            if item.price >= min_price
        ]

    if max_price is not None:
        filtered_items = [
            item
            for item in filtered_items
            if item.price <= max_price
        ]

    if q is not None:
        search_text = q.lower()

        filtered_items = [
            item
            for item in filtered_items
            if search_text in item.name.lower()
        ]

    if sort_by == "id":
        key_function = lambda item: item.id
    elif sort_by == "name":
        key_function = lambda item: item.name.lower()
    else:
        key_function = lambda item: item.price

    filtered_items = sorted(
        filtered_items,
        key=key_function,
        reverse=(order == "desc"),
    )

    total = len(filtered_items)

    paginated_items = filtered_items[
        skip: skip + limit
    ]

    return ItemListResponse(
        items=paginated_items,
        total=total,
        skip=skip,
        limit=limit,
    )


@app.get("/items/{item_id}", response_model=ItemPublic)
def get_item(item_id: int):
    item = _find(item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    return item


@app.post(
    "/items",
    response_model=ItemPublic,
    status_code=201,
)
def create_item(item: ItemCreate):
    global _next_id

    if _check_name_exists(item.name):
        raise HTTPException(
            status_code=409,
            detail="Item with this name already exists",
        )

    new_item = ItemPublic(
        id=_next_id,
        name=item.name.lower().strip(),
        price=item.price,
    )

    _items.append(new_item)
    _next_id += 1

    return new_item


@app.put(
    "/items/{item_id}",
    response_model=ItemPublic,
)
def update_item(
    item_id: int,
    data: ItemCreate,
):
    item = _find(item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    if _check_name_exists(
        data.name,
        exclude_id=item_id,
    ):
        raise HTTPException(
            status_code=409,
            detail="Item with this name already exists",
        )

    updated_item = ItemPublic(
        id=item.id,
        name=data.name.lower().strip(),
        price=data.price,
    )

    index = _items.index(item)
    _items[index] = updated_item

    return updated_item


@app.patch(
    "/items/{item_id}",
    response_model=ItemPublic,
)
def patch_item(
    item_id: int,
    data: ItemUpdate,
):
    item = _find(item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        new_name = update_data["name"]

        if _check_name_exists(
            new_name,
            exclude_id=item_id,
        ):
            raise HTTPException(
                status_code=409,
                detail="Item with this name already exists",
            )

    updated_item = ItemPublic(
        id=item.id,
        name=update_data.get(
            "name",
            item.name,
        ).lower().strip(),
        price=update_data.get(
            "price",
            item.price,
        ),
    )

    index = _items.index(item)
    _items[index] = updated_item

    return updated_item


@app.delete(
    "/items/{item_id}",
    status_code=204,
)
def delete_item(item_id: int):
    item = _find(item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    _items.remove(item)

    return None


@app.post(
    "/predict/house-price",
    response_model=HousePricePrediction,
)
def predict_house_price(
    data: HousePriceRequest,
):
    price = (
        data.area_sqm * 15_000_000
        - data.distance_to_center_km * 5_000_000
        + data.bedrooms * 20_000_000
    )

    return HousePricePrediction(
        predicted_price=price,
        currency="VND",
    )