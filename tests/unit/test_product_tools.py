"""Tests for product tools."""

import pytest
import respx
from httpx import Response


@pytest.fixture(autouse=True)
def reset_tool_state():
    """Reset global state before each test."""
    from texas_grocery_mcp.tools import product as product_module
    from texas_grocery_mcp.tools import store as store_module

    store_module._default_store_id = None
    store_module._graphql_client = None
    product_module._graphql_client = None
    yield
    store_module._default_store_id = None
    store_module._graphql_client = None
    product_module._graphql_client = None


@pytest.fixture
def mock_product_response():
    """Mock GraphQL product response."""
    return {
        "data": {
            "searchProducts": {
                "products": [
                    {
                        "productId": "123456",
                        "description": "HEB Whole Milk 1 Gallon",
                        "price": 3.49,
                        "isAvailable": True,
                        "brand": "H-E-B",
                        "imageUrl": "https://example.com/milk.jpg",
                    }
                ]
            }
        }
    }


@pytest.mark.asyncio
@respx.mock
async def test_product_search_with_store_id(mock_product_response):
    """product_search should work with explicit store_id."""
    from texas_grocery_mcp.tools.product import product_search

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_product_response)
    )

    result = await product_search(query="milk", store_id="590")

    assert len(result["products"]) == 1
    assert result["products"][0]["sku"] == "123456"
    assert result["products"][0]["price"] == 3.49


@pytest.mark.asyncio
@respx.mock
async def test_product_search_uses_default_store(mock_product_response):
    """product_search should use default store when not specified."""
    from texas_grocery_mcp.tools.product import product_search
    from texas_grocery_mcp.tools.store import store_set_default

    store_set_default(store_id="590")

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_product_response)
    )

    result = await product_search(query="milk")

    assert result["store_id"] == "590"
    assert len(result["products"]) == 1


@pytest.mark.asyncio
async def test_product_search_requires_store():
    """product_search should error when no store available."""
    from texas_grocery_mcp.tools.product import product_search

    result = await product_search(query="milk")

    assert "error" in result
    assert "store" in result["message"].lower()
