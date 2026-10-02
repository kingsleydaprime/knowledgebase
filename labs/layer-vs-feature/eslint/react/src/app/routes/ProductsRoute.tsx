// src/app/routes/ProductsRoute.tsx — verified (lints clean)
import { AddToCartButton } from "@/features/cart";
import { ProductList } from "@/features/products";

export function ProductsRoute() {
  return <ProductList renderAction={(p) => <AddToCartButton productId={p.id} />} />;
}
