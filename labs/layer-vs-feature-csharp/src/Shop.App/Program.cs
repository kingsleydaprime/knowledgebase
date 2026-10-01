// The composition root: builds each feature and connects them.
using Shop.Orders;
using Shop.Users;

var orders = new OrdersService(new UsersService());
Console.WriteLine(orders.Place("u1", 500_000));
Console.WriteLine(orders.Place("nobody", 1)?.ToString() ?? "rejected");
