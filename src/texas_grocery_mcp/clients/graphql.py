"""HEB GraphQL API client."""

from typing import Any

import httpx
import structlog

from texas_grocery_mcp.models import Product, Store
from texas_grocery_mcp.reliability import CircuitBreaker, RetryConfig, with_retry
from texas_grocery_mcp.utils.config import get_settings

logger = structlog.get_logger()


class GraphQLError(Exception):
    """Raised when GraphQL returns errors."""

    def __init__(self, errors: list[dict]):
        self.errors = errors
        messages = [e.get("message", "Unknown error") for e in errors]
        super().__init__(f"GraphQL error: {'; '.join(messages)}")


# GraphQL Queries
STORE_SEARCH_QUERY = """
query SearchStores($address: String!, $radius: Int!) {
    searchStoresByAddress(address: $address, radius: $radius) {
        stores {
            store {
                id
                name
                address1
                city
                state
                postalCode
                phoneNumber
                latitude
                longitude
            }
            distance
        }
    }
}
"""

PRODUCT_SEARCH_QUERY = """
query SearchProducts($query: String!, $storeId: String!, $limit: Int) {
    searchProducts(searchTerm: $query, storeId: $storeId, limit: $limit) {
        products {
            productId
            description
            brand
            price
            isAvailable
            imageUrl
            unitPrice
            unitOfMeasure
        }
    }
}
"""


class HEBGraphQLClient:
    """Client for HEB's GraphQL API."""

    def __init__(self, base_url: str | None = None):
        settings = get_settings()
        self.base_url = base_url or settings.heb_graphql_url
        self.circuit_breaker = CircuitBreaker("heb_graphql")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @with_retry(config=RetryConfig(max_attempts=3, base_delay=1.0))
    async def _execute(
        self,
        query: str,
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Response data

        Raises:
            GraphQLError: If GraphQL returns errors
            CircuitBreakerOpenError: If circuit is open
        """
        self.circuit_breaker.check()

        client = await self._get_client()

        try:
            response = await client.post(
                self.base_url,
                json={"query": query, "variables": variables},
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data and data["errors"]:
                raise GraphQLError(data["errors"])

            self.circuit_breaker.record_success()
            return data["data"]

        except (httpx.HTTPError, GraphQLError) as e:
            self.circuit_breaker.record_failure()
            logger.error(
                "GraphQL request failed",
                error=str(e),
                query_type=query.split("(")[0].strip().split()[-1],
            )
            raise

    async def search_stores(
        self,
        address: str,
        radius_miles: int = 25,
    ) -> list[Store]:
        """Search for HEB stores near an address.

        Args:
            address: Address or zip code to search near
            radius_miles: Search radius in miles

        Returns:
            List of stores sorted by distance
        """
        data = await self._execute(
            STORE_SEARCH_QUERY,
            {"address": address, "radius": radius_miles},
        )

        stores = []
        for result in data.get("searchStoresByAddress", {}).get("stores", []):
            store_data = result.get("store", {})
            stores.append(
                Store(
                    store_id=store_data.get("id", ""),
                    name=store_data.get("name", ""),
                    address=(
                        f"{store_data.get('address1', '')}, "
                        f"{store_data.get('city', '')}, "
                        f"{store_data.get('state', '')} "
                        f"{store_data.get('postalCode', '')}"
                    ),
                    phone=store_data.get("phoneNumber"),
                    distance_miles=result.get("distance"),
                    latitude=store_data.get("latitude"),
                    longitude=store_data.get("longitude"),
                )
            )

        return stores

    async def search_products(
        self,
        query: str,
        store_id: str,
        limit: int = 20,
    ) -> list[Product]:
        """Search for products at a store.

        Args:
            query: Search query
            store_id: Store ID for inventory/pricing
            limit: Maximum results to return

        Returns:
            List of matching products
        """
        data = await self._execute(
            PRODUCT_SEARCH_QUERY,
            {"query": query, "storeId": store_id, "limit": limit},
        )

        products = []
        for item in data.get("searchProducts", {}).get("products", []):
            products.append(
                Product(
                    sku=item.get("productId", ""),
                    name=item.get("description", ""),
                    price=item.get("price", 0.0),
                    available=item.get("isAvailable", False),
                    brand=item.get("brand"),
                    image_url=item.get("imageUrl"),
                    price_per_unit=(
                        f"${item.get('unitPrice', 0)}/{item.get('unitOfMeasure', 'ea')}"
                        if item.get("unitPrice")
                        else None
                    ),
                )
            )

        return products

    def get_status(self) -> dict:
        """Get client status for health checks."""
        return {
            "circuit_breaker": self.circuit_breaker.get_status(),
        }
