# Authorization

Authentication ([[05-authentication-flows|authentication-flows]]) answers "who are you." Authorization answers a completely separate question: "what are you allowed to do, now that I know who you are." Conflating the two is a common source of security bugs — a system can authenticate a user perfectly and still let them do things they shouldn't, if authorization checks are missing or incomplete (this is exactly the [[07-exploitation-concepts|broken access control]] vulnerability category from a defensive angle).

## RBAC — Role-Based Access Control

Users are assigned one or more **roles** (admin, editor, viewer); permissions are attached to roles, not directly to individual users. Checking access means checking whether the user's role(s) include the required permission.

```javascript
const rolePermissions = {
  admin:  ["read", "write", "delete"],
  editor: ["read", "write"],
  viewer: ["read"],
};

function canPerform(user, action) {
  return rolePermissions[user.role]?.includes(action);
}
```

Simple to reason about and administer — assign a role once, and permissions follow automatically. The limitation: RBAC struggles with fine-grained, context-dependent rules ("editors can edit their *own* posts, but not others'") without either exploding the number of roles or falling back to extra, ad-hoc checks layered on top.

## ABAC — Attribute-Based Access Control

Access decisions are made from a policy that evaluates **attributes** of the user, the resource, and the context — not just a fixed role.

```javascript
function canEdit(user, post, context) {
  return (
    user.role === "editor" &&
    post.authorId === user.id &&              // resource attribute: ownership
    context.time.getHours() >= 9 && context.time.getHours() < 17   // context attribute: business hours
  );
}
```

More expressive than RBAC — it can encode exactly the "editors can only edit their own posts" rule RBAC struggled with — at the cost of more complex policies that are harder to audit at a glance than a simple role table.

## Guards and policies — where these checks actually live in code

Most modern frameworks provide a dedicated place for authorization logic to live outside the handler itself, so it's consistently applied rather than manually re-checked (and potentially forgotten) in every individual handler:

- **Guards** (NestJS's term) — run before a handler, similar to middleware (see [[01-http-servers|http-servers]]) but specifically framed around the "is this request allowed" question, often declared declaratively via a decorator on the route.
- **Policies** — a common pattern (Laravel, and conceptually similar constructs elsewhere) that centralizes "can this user do X to this resource" logic in one dedicated class/function per resource type, called consistently from every relevant handler instead of duplicating the check.

```typescript
// conceptual NestJS-style guard
@UseGuards(RolesGuard)
@Roles('admin')
@Delete('users/:id')
deleteUser(@Param('id') id: string) { /* ... */ }
```

The value of centralizing this (guards/policies) over inline `if` checks scattered through handlers is consistency — a missed inline check in one handler is a silent, easy-to-introduce vulnerability; a centralized guard applied declaratively is much harder to accidentally skip.

## The principle of least privilege

Grant only the minimum access actually needed for a given role/task, nothing more — the same principle from [[02-cia-triad|cia-triad]]'s confidentiality discussion, applied to authorization design specifically. A support-staff role that can view customer data but not modify billing, rather than one broad "staff" role with blanket access, limits the damage of both a compromised account and an honest mistake.

## Object-level authorization — the most commonly missed check

It's not enough to check "is this user allowed to edit posts in general" — you also have to check "is this user allowed to edit *this specific post*." Skipping the second, more granular check while only implementing the first is exactly the **Insecure Direct Object Reference (IDOR)** pattern mentioned in [[07-exploitation-concepts|exploitation-concepts]] — a regular user changing an ID in a URL or request body and successfully accessing or modifying another user's resource, because the check that ran was "are you an editor," not "do you own this specific post."

```javascript
// insufficient: checks role, not ownership
if (user.role !== "editor") return res.status(403).send();
await updatePost(req.params.id, req.body);   // any editor can edit ANY post — the actual bug

// correct: also checks the specific resource
const post = await getPost(req.params.id);
if (post.authorId !== user.id) return res.status(403).send();
await updatePost(req.params.id, req.body);
```

## Gotchas

- Checking authorization only in the frontend/UI (hiding a button) provides zero actual security — see the client-side-validation gotcha in [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]]; the same principle applies here identically. Every authorization check has to be enforced server-side.
- Object-level authorization is the single most commonly missed check in real applications — role/permission checks alone are not sufficient the moment "which specific resource" matters, which is almost always.
- Overly broad roles (a "staff" role that's really "everything except admin") tend to accumulate over time as a team takes the path of least resistance — periodically auditing actual role permissions against what's genuinely needed is a real, ongoing task, not a one-time setup step.

## Related
- [[05-authentication-flows|authentication-flows]]
- [[07-exploitation-concepts|exploitation-concepts]]
- [[02-cia-triad|cia-triad]]

## Seen in the wild
- [[projects/gees-arise/interview/01-postgres-rls-and-security|gees-arise]] — Postgres row-level security, authorization enforced at the data layer
- [[concepts/interview/01-apis-auth-and-practices|Interview: Q5]] — RBAC/ABAC/ReBAC and the IDOR trap
