// src/features/products/components/ProductList.tsx — verified (lints clean)
type Product = { id: string; name: string };

export function ProductList({ renderAction }: { renderAction: (p: Product) => React.ReactNode }) {
  const products: Product[] = [{ id: "1", name: "Mug" }];
  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>
          {p.name} {renderAction(p)}
        </li>
      ))}
    </ul>
  );
}
