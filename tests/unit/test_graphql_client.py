"""Tests for HEB GraphQL client."""

import pytest
import respx
from httpx import Response

from texas_grocery_mcp.clients.graphql import HEBGraphQLClient


@pytest.fixture
def client():
    """Create test client."""
    return HEBGraphQLClient()


@pytest.mark.asyncio
@respx.mock
async def test_search_stores_success(client):
    """Should parse store search response."""
    mock_response = {
        "data": {
            "searchStoresByAddress": {
                "stores": [
                    {
                        "store": {
                            "id": "590",
                            "name": "H-E-B Mueller",
                            "address1": "1801 E 51st St",
                            "city": "Austin",
                            "state": "TX",
                            "postalCode": "78723",
                        },
                        "distance": 2.3,
                    }
                ]
            }
        }
    }

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_response)
    )

    stores = await client.search_stores(address="Austin, TX", radius_miles=10)

    assert len(stores) == 1
    assert stores[0].store_id == "590"
    assert stores[0].name == "H-E-B Mueller"


@pytest.mark.asyncio
@respx.mock
async def test_search_products_success(client):
    """Should parse product search response."""
    mock_response = {
        "data": {
            "searchProducts": {
                "products": [
                    {
                        "productId": "123456",
                        "description": "HEB Whole Milk 1 Gallon",
                        "price": 3.49,
                        "isAvailable": True,
                        "brand": "H-E-B",
                    }
                ]
            }
        }
    }

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_response)
    )

    products = await client.search_products(query="milk", store_id="590")

    assert len(products) == 1
    assert products[0].sku == "123456"
    assert products[0].price == 3.49


@pytest.mark.asyncio
@respx.mock
async def test_handles_graphql_error(client):
    """Should raise on GraphQL errors."""
    mock_response = {
        "errors": [{"message": "Store not found"}],
        "data": None,
    }

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_response)
    )

    with pytest.raises(Exception, match="GraphQL error"):
        await client.search_stores(address="Invalid", radius_miles=10)
