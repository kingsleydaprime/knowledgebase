# Django

> **[Intermediate]** · Batteries included — the ORM, migrations, the admin, and the "fat model" structure that fights every layering convention in this vault.

Django is the **maximalist** end of the trade. It ships an ORM, migrations, an admin interface, auth with permissions, forms, templates, caching, i18n, security middleware and a test framework. You assemble almost nothing.

**Its bet:** most web applications need the same things, so provide them, opinionated and integrated. When the bet pays off, a working authenticated CRUD application with a database and an admin UI is an afternoon. When it doesn't, you're fighting a framework that has already decided.

## The structure

Django splits a project into **apps** — self-contained feature modules:

```
myproject/
├── manage.py
├── myproject/          # settings, root urls, wsgi/asgi
└── orders/             # an app
    ├── models.py       # schema
    ├── views.py        # request handlers
    ├── urls.py
    ├── admin.py
    ├── serializers.py  # (with DRF)
    └── migrations/
```

**Note the split is by *layer* within each app**, and the app is the vertical slice. That's closer to a modular monolith than it looks → [[backend/03-structuring-a-backend/README|structuring a backend]].

| Course concept | Django |
|---|---|
| **Controller** | view (function or class-based) |
| **Model / entity** | `models.Model` — **also the repository** |
| **Repository** | the model's `Manager` / `QuerySet` |
| **DTO / validation** | Form, or DRF `Serializer` |
| **Middleware** | `MIDDLEWARE` list — genuine onion layering |
| **DI** | **none** — imports and settings |
| **Router** | `urls.py`, `path()` |

## The ORM

Django's ORM is **Active Record**: the model class is the schema, the query interface and the domain object at once.

```python
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total    = models.DecimalField(max_digits=10, decimal_places=2)
    status   = models.CharField(max_length=20, choices=Status.choices)
    created  = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["status", "created"])]
```

```python
Order.objects.filter(status="pending").select_related("customer")[:20]
```

**Migrations are its best feature and are genuinely ahead of most ecosystems:**

```bash
python manage.py makemigrations     # diffs models against migration history
python manage.py migrate
```

It generates the migration by comparing your models to the recorded state — you review and edit rather than write from scratch. Alembic (SQLAlchemy) can autogenerate too, but Django's is more reliable because the ORM owns the schema definition outright.

**Always read generated migrations before applying.** Renames get detected as drop-and-create, which is data loss. → [[databases/12-operating-a-database|operating a database]].

### The N+1 problem

**The single most common Django performance bug**, and it's a direct consequence of lazy attribute access:

```python
for order in Order.objects.all():        # 1 query
    print(order.customer.name)           # + 1 query PER ORDER
```

A hundred orders, a hundred and one queries. Locally with ten rows it's imperceptible; in production it's a timeout.

```python
Order.objects.select_related("customer")          # SQL JOIN — for FK / one-to-one
Order.objects.prefetch_related("items")           # 2nd query + join in Python — for many-to-many / reverse FK
```

**Install `django-debug-toolbar` and look at the query count on every page you build.** It's the cheapest defence there is → [[databases/07-join-algorithms-and-the-optimiser|joins]].

## The admin

```python
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ("id", "customer", "total", "status")
    list_filter   = ("status", "created")
    search_fields = ("customer__name",)
```

A production-usable CRUD interface with search, filtering, permissions and audit history, from six lines. **Nothing else in any ecosystem gives you this**, and it's frequently the deciding reason to pick Django — internal tools that would be a month elsewhere are an hour here.

**Its limit:** it's for *staff*, modelled on your database tables. Bending it into a customer-facing product surface is a well-worn path to regret.

## Django REST Framework

Django's own JSON support is minimal; **DRF** is the de-facto standard for APIs:

```python
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "customer", "total", "status"]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("customer")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
```

That's full CRUD with pagination, filtering, auth and a browsable API. Mature, powerful, and heavy — the class hierarchy takes real time to learn, and "which method do I override" is a recurring question. `django-ninja` is the lighter alternative, borrowing FastAPI's Pydantic approach.

## Async

Django added ASGI support (3.0+) and async views (3.1+), and it's genuinely partial:

- **Async views** — yes
- **Async ORM** — `aget()`, `afilter()` etc. exist (4.1+) but much of the ecosystem is still sync
- **Most third-party packages** — sync

**Calling the sync ORM from an async view raises `SynchronousOnlyOperation`** unless wrapped in `sync_to_async`. Mixing the two is where the sharp edges are.

**Practically: run Django sync unless you have a specific reason.** Its threaded, process-per-worker model is well understood and fine for most loads. If you need heavy async I/O, that's a point for [[backend/frameworks/python/01-fastapi/README|FastAPI]].

## What it does badly, honestly

**Fat models.** The convention puts business logic on the model class, which is also the persistence layer. It's productive at small scale and becomes a 2,000-line `models.py` coupling domain rules to the database. The remedy — a service layer — is fighting the grain, and Django won't help you → [[backend/03-structuring-a-backend/README|layering]].

**Settings are a Python module of globals**, imported everywhere. Environment-specific configuration is a solved-by-convention problem with several competing conventions.

**Testing touches the database by default.** `TestCase` wraps each test in a transaction, which is fast but means most Django test suites are integration tests wearing a unit-test label.

**It's large.** If you need a JSON API and nothing else, most of Django is weight you carry and configure.

## Related
- [[backend/frameworks/python/01-fastapi/README|FastAPI]] — the opposite trade
- [[backend/frameworks/python/README|Python backends]] — how to choose
- [[databases/README|databases]] — what the ORM is generating
- [[backend/04-data-and-persistence/README|data and persistence]] — ORMs in general
- [[backend/frameworks/java/README|Spring Boot]] — the other batteries-included framework

*Source: [reference] — from the Django and DRF documentation.*
