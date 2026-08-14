# The GitHub CLI (`gh`)

**[Intermediate]** — `git` talks to a repository; `gh` talks to GitHub. Pull requests, issues, releases, CI runs and the raw API, from the terminal — without the browser round-trip that breaks your flow.

## Why it exists

`git` predates GitHub and knows nothing about it. Pull requests, issues, reviews, Actions runs, releases — none of those are Git concepts. They're GitHub's, and until `gh` the only way to touch them was the web UI.

That matters more than convenience. The browser round-trip — alt-tab, find the tab, wait for the SPA, click through — is where a train of thought dies. `gh pr create` from the branch you're already on skips all of it.

The other half is scripting. `gh` is an authenticated GitHub API client that already knows who you are and which repo you're in, so `gh api` turns any GitHub data into something you can pipe into `jq`.

## Setup

```bash
# Fedora / RHEL
sudo dnf install gh
# Debian / Ubuntu
sudo apt install gh
# macOS
brew install gh

gh auth login          # interactive: choose GitHub.com, HTTPS, browser auth
gh auth status         # which account, which scopes, which host
gh auth refresh -s project,read:org   # add scopes later without re-logging in
```

One thing worth doing immediately:

```bash
gh auth setup-git      # make gh git's credential helper
```

That's what stops HTTPS pushes asking for a password. `gh` holds the token and hands it to `git` on demand — no personal access token pasted into a config file where it can leak. See [[git/02-configuration-and-setup|Configuration and Setup]] for the `credential.helper` setting this replaces.

## Repositories

```bash
gh repo create my-project --public --source=. --push   # create FROM an existing local repo
gh repo create my-project --private --clone            # create empty and clone it
gh repo clone owner/name                               # clone without typing the URL
gh repo fork --clone                                   # fork + clone + set upstream, in one
gh repo view                                           # summary in the terminal
gh repo view --web                                     # ...or just open it
gh repo list <user> --limit 100                        # someone's repos
```

`gh repo fork --clone` is the one that saves real work: it forks, clones your fork, and adds the original as `upstream` — the three-step setup from [[git/08-remotes-and-collaboration|Remotes and Collaboration]] done correctly by default.

## Pull requests — the main event

```bash
gh pr create                          # interactive: title, body, base branch
gh pr create --fill                   # use the commit message as title+body
gh pr create --draft                  # open as a draft
gh pr create --base develop --title "feat: add auth" --body "Closes #42"
gh pr create --web                    # open the browser form pre-filled

gh pr list                            # open PRs on this repo
gh pr list --author "@me"             # just yours
gh pr status                          # the useful one: yours, assigned to you, needing review

gh pr view 42                         # description + comments, in the terminal
gh pr view 42 --comments
gh pr diff 42                         # the diff, without leaving the shell
gh pr checks 42                       # CI status per check
```

**The single most useful command in the whole tool:**

```bash
gh pr checkout 42
```

It fetches PR #42's branch — *including from a fork you have no remote for* — and checks it out locally. Reviewing a PR by reading a web diff is a much worse experience than reviewing it in your editor, with your tooling, able to actually run it. Doing that manually means adding the contributor's fork as a remote and fetching their branch; `gh` does it in one command.

```bash
gh pr review 42 --approve
gh pr review 42 --request-changes --body "Auth check is missing on the delete route"
gh pr review 42 --comment --body "Nice catch on the null handling"

gh pr merge 42 --squash --delete-branch
gh pr merge 42 --rebase
gh pr merge 42 --merge
gh pr merge 42 --auto --squash     # merge as soon as checks pass
gh pr ready 42                     # draft → ready for review
gh pr close 42
```

`--auto` is worth knowing: it queues the merge behind the required status checks from [[git/14-github-and-ci|branch protection]], so you don't sit watching CI.

## Issues

```bash
gh issue create --title "Bug: login fails on Safari" --body "..." --label bug
gh issue list --state open --label bug
gh issue list --assignee "@me"
gh issue view 17
gh issue close 17 --comment "Fixed in #42"
gh issue develop 17 --checkout      # create a branch for this issue and switch to it
```

`gh issue develop` links the branch to the issue on GitHub, so the issue page shows the work in progress — a small thing that removes a whole class of "which branch was that?" questions.

## CI runs

Directly useful here: this vault publishes through a GitHub Actions workflow, so after every push there's a run to watch.

```bash
gh run list                     # recent workflow runs
gh run list --workflow=deploy.yml
gh run watch                    # live-follow the current run until it finishes
gh run view                     # pick a run, see its jobs
gh run view --log-failed        # ONLY the failed steps' logs — the fast path to a cause
gh run rerun <run-id>
gh run rerun <run-id> --failed  # rerun only the failed jobs
gh run cancel <run-id>
```

`gh run view --log-failed` beats the web UI decisively. A failed run in the browser means expanding jobs and scrolling collapsed step output; this prints just the part that broke. See [[devops/06-ci-cd/12-troubleshooting-workflows|Troubleshooting Workflows]] for what to do with the output.

## Releases

```bash
gh release create v1.2.3 --generate-notes          # notes auto-built from merged PRs
gh release create v1.2.3 --title "..." --notes "..."
gh release create v1.2.3 ./dist/app.tar.gz         # attach a build artifact
gh release create v1.2.3 --prerelease --target develop
gh release list
gh release download v1.2.3
```

`--generate-notes` is the payoff for the commit discipline in [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — GitHub writes the changelog from your PR titles, so conventional commits turn directly into release notes. More on the versioning side in [[git/11-tags-and-versioning|Tags and Versioning]].

## `gh api` — the escape hatch

Everything above is a convenience wrapper. When there's no wrapper for what you need, `gh api` gives you the whole REST and GraphQL API, already authenticated:

```bash
gh api repos/{owner}/{repo}/branches          # {owner}/{repo} auto-fill from cwd
gh api user
gh api repos/cli/cli/releases --paginate      # follow pagination automatically

# --jq filters the JSON without a separate jq process
gh api repos/{owner}/{repo}/pulls --jq '.[] | "\(.number) \(.title)"'
gh api repos/{owner}/{repo}/commits --jq '.[].commit.author.name' | sort | uniq -c

# Write, not just read
gh api -X PATCH repos/{owner}/{repo} -f description="A better description"

# GraphQL when REST can't express it
gh api graphql -f query='{ viewer { login name } }'
```

A worked example — reading a repository's whole file tree in one call, which is how you map a large repo without cloning it:

```bash
gh api "repos/kamranahmedse/developer-roadmap/git/trees/master?recursive=1" \
  --jq '.tree[].path | select(startswith("roadmaps/devops/content/"))'
```

Most `gh` subcommands also support `--json` + `--jq` directly, which is cleaner than dropping to `gh api`:

```bash
gh pr list --json number,title,author --jq '.[] | "\(.number)\t\(.author.login)\t\(.title)"'
gh run list --json conclusion,name --jq '.[] | select(.conclusion=="failure") | .name'
```

## Odds and ends

```bash
gh browse                    # open the current repo in a browser
gh browse src/app.js:42      # ...at a specific file and line
gh gist create notes.md --public
gh search repos "quartz static site" --language=typescript
gh status                    # your GitHub activity across repos
```

**Aliases** — worth setting up for anything you type more than twice a day:

```bash
gh alias set prc 'pr create --fill'
gh alias set prs 'pr status'
gh alias set watch 'run watch'
gh alias list
```

**Config:**

```bash
gh config set editor nvim
gh config set git_protocol ssh    # use SSH for clones gh performs
gh config list
```

## Where `gh` stops and `git` starts

Worth keeping straight, because it's the thing that confuses people:

| Task | Tool | Why |
|---|---|---|
| Commit, branch, merge, rebase, stash | `git` | Repository operations — GitHub isn't involved |
| Push, pull, fetch | `git` | Transport, though `gh` supplies the credentials |
| Open/review/merge a PR | `gh` | PRs are a GitHub concept, not a Git one |
| Issues, releases, CI runs | `gh` | Same — all GitHub-side |
| Fork and set up upstream | `gh` | It does three `git` steps correctly in one |
| Check out someone's PR | `gh` | Needs the API to find the fork's branch |

If a command changes commits, it's `git`. If it changes something you'd otherwise click in a browser, it's `gh`.

---

## Related
- [[git/14-github-and-ci|GitHub as a Platform, and Git in CI]] — the rules `gh pr merge` has to satisfy
- [[git/08-remotes-and-collaboration|Remotes and Collaboration]] — the manual fork workflow `gh repo fork` automates
- [[git/11-tags-and-versioning|Tags and Versioning]] — what `gh release create` is publishing
- [[devops/06-ci-cd/12-troubleshooting-workflows|Troubleshooting Workflows]] — where `gh run view --log-failed` leads
- [[devops/01-linux/03-file-operations|File Operations (Linux)]] — the pipes and filters `--jq` output feeds into
- [[git/README|Git course map]]
