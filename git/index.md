# Git & Version Control

## What Git is

**Git is a tool that keeps the full history of your code, so you can see every change ever made and go back to any earlier version.**

Without it, people end up with folders like `project-final`, `project-final-2` and `project-final-REALLY`. Git replaces all of that. Every time you save a snapshot (called a **commit**), Git remembers exactly what every file looked like at that moment, who changed it and why. It also lets several people work on the same code at the same time and combine their work safely. Almost every software team in the world uses it, and GitHub is the most popular website for sharing code stored with Git.

Most people only learn three commands: `add`, `commit` and `push`. This course explains what Git is actually doing underneath, because once you can picture that, the confusing parts of Git stop being confusing.

## What you'll be able to do

By the end you will be able to:
- save snapshots of your work and write messages that explain them;
- work on a new idea in a separate **branch** without breaking the main code;
- combine your work with other people's, and sort out the clashes when two people changed the same lines;
- find out who changed a line, when, and why;
- undo almost any mistake, including ones that look permanent;
- work the way real teams do: pull requests, code review and automatic checks on GitHub.

## Where to start

The notes build on each other, so read them in order. Notes 01–11 are Git on your own computer; 12–15 are Git with a team; 16–17 are tools you'll only need now and then.

**One rule to know before anything else:** never rewrite history that someone else may already have downloaded. Almost every other mistake in Git can be undone, but that one breaks other people's copies and you can't fix it for them.

### The basics

1. [[git/01-how-git-works|How Git Actually Works]]: what Git stores when you commit, and what's inside the hidden `.git` folder. It feels like theory, but it makes everything after it easier.
2. [[git/02-configuration-and-setup|Configuration and Setup]]: installing and setting up Git, and starting or copying a project.
3. [[git/03-the-three-trees|The Three Trees]]: the three places your files live (your folder, the staging area, and the last commit), and how files move between them.
4. [[git/04-branching|Branching]]: making a separate line of work, switching between branches, and getting unstuck.

### Combining work

5. [[git/05-merging|Merging]]: joining two branches back together, and fixing the clashes when both changed the same lines.
6. [[git/06-rebasing|Rebasing]]: another way to combine branches, by moving your commits on top of someone else's. Also tidying up your commits before sharing them.
7. [[git/07-merge-vs-rebase|Merge vs Rebase]]: when to use which, with a simple decision chart.
8. [[git/08-remotes-and-collaboration|Remotes and Collaboration]]: sending your work to GitHub and getting other people's work back.

### Looking back and fixing mistakes

9. [[git/09-investigating-history|Investigating History]]: searching the history, seeing what changed, finding who wrote a line, and tracking down which commit broke something.
10. [[git/10-undoing-things|Undoing Things]]: the different ways to undo, and which one you want. Starts with a decision chart, because this is where most Git panic happens.
11. [[git/11-tags-and-versioning|Tags and Versioning]]: marking a commit as a release, like "version 1.2.0", and what the numbers mean.

### Working with a team

12. [[git/12-conventions-and-hygiene|Conventions and Hygiene]]: writing commit messages people can read, and keeping a project tidy.
13. [[git/13-branching-strategies|Branching Strategies]]: the common ways teams organise their branches, and naming them.
14. [[git/14-github-and-ci|GitHub as a Platform, and Git in CI]]: pull requests, protecting the main branch, code owners, and automatic checks that run on every change.
15. [[git/15-the-github-cli|The GitHub CLI (`gh`)]]: doing everything from note 14 from the terminal instead of the website.

### Occasional tools

16. [[git/16-power-tools|Power Tools]]: a project inside a project, several branches checked out at once, and copying single commits between branches.
17. [[git/17-hooks-and-signing|Hooks and Signing]]: running checks automatically before each commit, and proving a commit really came from you.

## For quick lookup

- [[git/git-reference|Git command reference]]: the commands, grouped by what you're trying to do. For looking things up, not reading through.
- [[git/git-troubleshooting|Git troubleshooting]]: fixes for when something has gone wrong, such as "I committed to the wrong branch" or "I committed my passwords file". Written for the moment you're panicking.

## Practice

- [[git/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- The best practice is real use. Type every Git command yourself in your own projects instead of letting a tool do it for you. The Gees Arise and SocioBoom logs show what that looked like on real projects, mistakes included.

## Key ideas to remember

1. **A commit is a snapshot of every file, not a list of changes.** Git works out the changes when you ask for them. → [[git/01-how-git-works|01]]
2. **A branch is just a label pointing at a commit.** Making one is instant and costs nothing, so make them freely. → [[git/04-branching|04]]
3. **Most "lost" work isn't lost.** Git keeps a log of where you've been for about 30 days, so you can usually get commits back. → [[git/10-undoing-things|10]]
4. **Never rewrite history others have downloaded.** Rebase your own unshared work freely; merge shared work. → [[git/07-merge-vs-rebase|07]]
5. **Fix a merge clash by reading both sides,** not by picking one and hoping. → [[git/05-merging|05]]

## Related

- [[programming-fundamentals/index|Programming Fundamentals]]: start Git on your first project, not your fifth.
- [[software-engineering/index|Software Engineering]]: how teams work together around code.
- [[devops/index|DevOps]]: what happens to your code after it leaves Git: testing, building and shipping it.

---

## About this course

- **Size:** 17 notes, about 17,000 words, plus a command reference and a troubleshooting guide. Split in August 2026 out of one very long reference file.
- **Not covered yet:** how Git compresses and maintains its storage; tools for very large repositories (sparse checkout, partial clone, rewriting a repository's history with `git filter-repo`); GitLab and Bitbucket, which are only mentioned in passing.
