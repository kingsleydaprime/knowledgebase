namespace Shop.Users;

// public: the users feature's API.
public sealed class UsersService
{
    private readonly HashSet<string> _ids = ["u1"];

    public bool Exists(string userId) => _ids.Contains(userId);
}
