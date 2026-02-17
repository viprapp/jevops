# Lab 3 - GitHub Flow + merge conflict

## Goal

Demonstrate a full GitHub Flow PR and resolve a simple merge conflict.

## PR 1 (authored)

- Branch: `stage1-git-lab`
- Change: added a line to `docs/foundations/git.md`
- PR link: <https://github.com/viprapp/jevops/pull/3>
- Merge method: merge commit

## PR 2 (intentional conflict)

### Setup

- File: `ROADMAP.md`
- Line: `21`

### Branch A

- Branch: `conflict-a`
- PR link: <https://github.com/viprapp/jevops/pull/4>
- Result: merged first

### Branch B

- Branch: `conflict-b`
- PR link: <https://github.com/viprapp/jevops/pull/5>
- Conflict shown by GitHub: yes

### Resolution

- Resolved via: GitHub UI
- What I chose and why: Chose the changes from branch `conflict-b`
- Evidence:

```sh
*   089ff6d (HEAD -> main, github/main, github/HEAD) Merge pull request #5 from viprapp/conflict-b
|\
| *   a906f91 (github/conflict-b) Merge branch 'main' into conflict-b
| |\
| |/
|/|
* |   c52073b Merge pull request #4 from viprapp/conflict-a
|\ \
| * | a23b89e (github/conflict-a, conflict-a) docs: update current focus (A)
|/ /
| * 3c1e9ce (conflict-b) docs: conflict demo (b)
|/
*   592300b Merge pull request #3 from viprapp/stage1-git-lab
```

## Rebase vs merge (short)

- Merge: preserves the branching history and creates a merge commit when needed.
- Rebase: rewrites commits to create a linear history (useful, but be careful on shared
branches).

Refs: GitHub Flow, Pro Git branching/merging, Pro Git rebasing.
