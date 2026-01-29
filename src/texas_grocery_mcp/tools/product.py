"""Product-related MCP tools."""

from typing import Annotated, Literal

from pydantic import Field

from texas_grocery_mcp.clients.graphql import HEBGraphQLClient
from texas_grocery_mcp.tools.store import get_default_store_id

_graphql_client: HEBGraphQLClient | None = None


def _get_client() -> HEBGraphQLClient:
    """Get or create GraphQL client."""
    global _graphql_client
    if _graphql_client is None:
        _graphql_client = HEBGraphQLClient()
    return _graphql_client


async def product_search(
    query: Annotated[str, Field(description="Search query (e.g., 'milk', 'chicken breast')", min_length=1)],
    store_id: Annotated[
        str | None, Field(description="Store ID for pricing/availability. Uses default if not provided.")
    ] = None,
    limit: Annotated[
        int, Field(description="Maximum results to return", ge=1, le=50)
    ] = 20,
    fields: Annotated[
        list[Literal["minimal", "standard", "all"]] | None,
        Field(description="Field set to return: minimal (sku, name, price), standard (+brand, size, image), all (+nutrition)")
    ] = None,
) -> dict:
    """Search for products at an HEB store.

    Returns products matching the query with pricing and availability
    for the specified store.
    """
    # Validate query
    query = query.strip()
    if not query:
        return {
            "error": True,
            "code": "INVALID_QUERY",
            "message": "Search query cannot be empty or whitespace.",
        }

    # Resolve store ID
    effective_store_id = store_id or get_default_store_id()

    if not effective_store_id:
        return {
            "error": True,
            "code": "NO_STORE_SET",
            "message": "No store specified. Set a default store with store_set_default or provide store_id.",
        }

    client = _get_client()
    products = await client.search_products(
        query=query,
        store_id=effective_store_id,
        limit=limit,
    )

    # Determine field set (default to standard)
    field_set = (fields or ["standard"])[0] if fields else "standard"

    result_products = []
    for p in products:
        product_data = {
            "sku": p.sku,
            "name": p.name,
            "price": p.price,
            "available": p.available,
        }

        if field_set in ("standard", "all"):
            product_data.update({
                "brand": p.brand,
                "size": p.size,
                "price_per_unit": p.price_per_unit,
                "image_url": p.image_url,
                "aisle": p.aisle,
                "section": p.section,
            })

        if field_set == "all":
            product_data.update({
                "nutrition": p.nutrition.model_dump() if p.nutrition else None,
                "ingredients": p.ingredients,
                "on_sale": p.on_sale,
                "original_price": p.original_price,
                "rating": p.rating,
            })

        result_products.append(product_data)

    return {
        "products": result_products,
        "count": len(result_products),
        "store_id": effective_store_id,
        "query": query,
    }
