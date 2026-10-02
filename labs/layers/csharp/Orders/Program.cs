// Three layers. Domain errors are exceptions; one switch expression maps them to statuses.
var stock = new Dictionary<string, int> { ["mug"] = 1 };
var service = new OrdersService(new OrdersRepository(stock));

Check(Controller.Create(service, []).Status == 400, "empty order is 400");
Check(Controller.Create(service, [new Item("mug", 5)]) == new Response(409, "out of stock: mug"), "out of stock is 409");
Check(Controller.Create(service, [new Item("mug", 1)]) == new Response(201, "{\"id\":1}"), "success is 201");
Check(stock["mug"] == 0, "stock was reserved");
Console.WriteLine("ok: domain errors mapped to 400, 409 and 201");

static void Check(bool condition, string what)
{
    if (!condition) throw new Exception($"FAIL: {what}");
}

record Item(string Sku, int Quantity);
record Response(int Status, string Body);

sealed class EmptyOrderException() : Exception("an order needs at least one item");
sealed class OutOfStockException(string sku) : Exception($"out of stock: {sku}")
{
    public string Sku { get; } = sku;
}

// Repository: the only code that knows how data is stored.
sealed class OrdersRepository(Dictionary<string, int> stock)
{
    private int _orders;
    public int StockOf(string sku) => stock.GetValueOrDefault(sku);
    public void Reserve(string sku, int quantity) => stock[sku] -= quantity;
    public int Create() => ++_orders;
}

// Service: business rules, no HTTP.
sealed class OrdersService(OrdersRepository repo)
{
    public int Place(IReadOnlyList<Item> items)
    {
        if (items.Count == 0) throw new EmptyOrderException();
        foreach (var item in items)
            if (repo.StockOf(item.Sku) < item.Quantity) throw new OutOfStockException(item.Sku);
        foreach (var item in items) repo.Reserve(item.Sku, item.Quantity);
        return repo.Create();
    }
}

// Controller. In ASP.NET Core the mapping becomes an IExceptionHandler returning ProblemDetails.
static class Controller
{
    public static Response Create(OrdersService service, IReadOnlyList<Item> items)
    {
        try
        {
            return new Response(201, $"{{\"id\":{service.Place(items)}}}");
        }
        catch (Exception e) when (e is EmptyOrderException or OutOfStockException)
        {
            return new Response(e switch
            {
                EmptyOrderException => 400,
                OutOfStockException => 409,
                _ => 500,
            }, e.Message);
        }
    }
}
