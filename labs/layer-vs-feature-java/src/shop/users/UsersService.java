package shop.users;

import java.util.Set;

// Public: this is the users feature's API.
public final class UsersService {
    private final Set<String> ids = Set.of("u1");

    public boolean exists(String userId) {
        return ids.contains(userId);
    }
}
