# Organising by Layer vs by Feature

**[Beginner→Intermediate]** — the folder-structure argument every team has, usually badly. It looks like bikeshedding and isn't: it determines how far you have to scroll to make one change, and how easy it is to delete something.

## The kid version first

You're organising a toolbox.

- **By type:** all screwdrivers in one drawer, all wrenches in another, all screws in a third. Tidy. But to fix the bike you open four drawers.
- **By job:** a "bike box", a "plumbing box", each holding everything for that job. To fix the bike you grab one box. But now you own three screwdrivers.

Neither is wrong. **The right one depends on whether you more often do "one job" or "one type of thing."** In software you almost always work on one *feature* at a time — which is a strong hint.

## The two layouts

**By layer (by technical role):**
```
src/
├── controllers/   orders.controller.ts  users.controller.ts  payments.controller.ts
├── services/      orders.service.ts     users.service.ts     payments.service.ts
├── repositories/  orders.repo.ts        users.repo.ts        payments.repo.ts
└── dtos/          ...
```

**By feature (by domain concept):**
```
src/
├── orders/     orders.controller.ts  orders.service.ts  orders.repo.ts  orders.dto.ts
├── users/      users.controller.ts   users.service.ts   users.repo.ts
├── payments/   ...
└── shared/     database, logging, auth middleware
```

## The case for by-feature

**1. Change locality.** Adding a field to an order touches the controller, service, repository, DTO, and tests. By feature, that's **one folder**. By layer, it's five folders and a lot of scrolling. Since most work is feature work, by-feature optimises for the common case.

**2. Deletability.** Killing a feature is `rm -rf src/orders/` plus removing one registration line. By layer, you hunt through six directories and *will* leave orphans behind. **How easily you can delete something is an underrated measure of how well it's structured.**

**3. It makes coupling visible.** If `orders/` imports from `payments/internals`, that's obvious in a diff and reviewable. By layer, `orders.service` importing `payments.service` looks identical to every other import — everything is already in the same folder, so nothing stands out.

**4. It's the extraction seam.** If a feature ever becomes its own service, a feature folder is already the boundary. A layer layout has to be untangled first. → [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|monolith → services]]

**5. It scales with the team.** Teams own features, not layers. Ownership maps to folders, and `CODEOWNERS` becomes trivial.

## The case for by-layer

Not nothing, and worth stating fairly:

- **Small projects.** Under ~15 files, feature folders each containing two files is more ceremony than the flat version.
- **It's obvious where things go** when the layers are rigid — no debate about which feature something belongs to.
- **Framework convention.** Rails and Django lean by-layer (`app/controllers`, `app/models`), and fighting your framework's conventions has a real cost in tooling and onboarding.

## The verdict

**Start by-feature, or move to it the moment you have more than a handful of features.** The by-layer structure looks tidy at the start and gets worse every month; by-feature looks slightly over-engineered at the start and gets better.

The tell that you needed it a while ago: **you have a `services/` folder with twenty-five files in it and you scroll to find things.** A folder is a bad index past about a dozen entries.

## Getting the details right

**Inside a feature, keep the layers.** By-feature doesn't mean abandoning [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|controller/service/repository]] — it means those three files sit next to each other. Both axes, feature outer, layer inner.

**`shared/` is where this rots.** Every by-feature codebase grows a `shared/`, `common/`, or `utils/`, and it becomes a junk drawer that every feature depends on — which quietly recreates the coupling you were avoiding. Two rules that keep it honest:
- Something belongs in `shared/` when **two or more features already use it** — not when you predict they might.
- `shared/` may never import from a feature. If it needs to, it isn't shared.

**Duplication across features is often correct.** Two features having similar-looking code is fine; prematurely extracting it into `shared/` couples them, and they'll diverge. **Wait for the third occurrence.** The wrong abstraction costs more than the duplication.

**Enforce boundaries mechanically, not by discipline.** Nobody remembers architectural rules under deadline. Use ESLint `import/no-restricted-paths`, a dependency-cruiser config, or `.NET`/Java module systems to make a forbidden import a build failure. NestJS modules and Java's JPMS give you some of this natively.

## Where this goes next

A well-kept feature layout with enforced boundaries **is** a modular monolith — which is the structure you want before you ever consider splitting into services, because the boundaries have already been tested in a place where getting them wrong is cheap to fix. → [[backend/03-structuring-a-backend/05-modular-monolith-to-services|modular monolith to services]]

## Key insight

Folder structure is a **bet about what changes together**. By-layer bets that you'll change all controllers at once; by-feature bets that you'll change one feature end-to-end. The second bet is almost always the right one, because features are how work arrives — from users, from tickets, from the roadmap. **Organise around the shape of the work, not the shape of the code.**

## Related
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]] — what lives inside each feature folder
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services|Modular Monolith → Services]] — where good feature boundaries pay off
- [[concepts/04-best-practices/01-clean-code|Clean Code]] — the duplication-vs-abstraction argument
