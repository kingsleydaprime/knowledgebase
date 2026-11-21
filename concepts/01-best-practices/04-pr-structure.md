---
id: b7e4d733-6b38-444b-be2b-23577de824cb
---

# Structuring pull requests

1. Keep PR Focused on one purpose (not a whole feature or a whole project)
2. Don't mix refactoring with making new logic. (Do a refactor first and then make the logic)
3. Clenup what is only related to your PR
4. Avoid unneccessary renames of variables and functions
5. Comment where needed (High level comment)
6. Keep PRs small

## For writing and packaging prs
<!-- bite: aa0d8645-4e0d-4c49-bc9f-5564d812c32a -->

1. Make sure your PR has a good title
2. Add a clear PR summary (what you added, changed, deleted)
3. Highlight non-obvious logic, if there was any trickery or non-obvious logic
4. Be clear what you haven't done (Like adding a TODO)

## 
<!-- bite: b20a133d-75a7-4aef-8f6a-bca28bc64197 -->
1. Add images (for UI changes)
2. Add testing instructions for new or complex features
3. Add pre-hook, automated jobs, launching block tests
4. Retest manually