# Working with the Synced Lab 3 Repository

This document explains how each group member can continue using their own personal repository while contributing to the synced group repository for Lab 3.

The goal is:

* each person can keep their own personal repository;
* personal repositories can still contain Lab 1, Lab 2, and other files;
* the synced repository contains only the final Lab 3 code;
* the synced repository receives commits from each group member;
* the professor can inspect one repository and see individual contributions.

---

# Repository Setup

Each person has their own personal repository, for example:

```text
personal-repo/
├── lab1-ipv8-pow/
├── lab2-group-signing/
└── lab3-pow-blockchain/
```

The synced repository contains only the final Lab 3 code structure:

```text
cs4160-lab3-blockchain/
├── README.md
├── SYNC_INSTRUCTIONS.md
├── requirements.txt
├── .gitignore
├── client.py
├── community.py
├── config.py
├── payloads.py
├── blockchain/
│   ├── __init__.py
│   ├── block.py
│   ├── blockchain.py
│   ├── mempool.py
│   ├── miner.py
│   ├── pow.py
│   ├── transaction.py
│   └── utils.py
├── registration/
│   ├── __init__.py
│   ├── community.py
│   └── payloads.py
└── keys/
    └── .gitkeep
```

The synced repo should **not** contain Lab 1 or Lab 2 folders.

---

# Main Idea

The personal repo can still contain all labs.

However, when contributing to the synced Lab 3 repo, do **not** push personal `main` directly to the synced repository.

Do **not** do this:

```bash
git push synced main
```

That would try to push the full personal repository structure, including Lab 1 and Lab 2.

Instead, each person should create a local branch based on `synced/main`, work on that branch, and push that branch to the synced repository.

The workflow is:

```text
personal repo
    ├── main              = personal structure with all labs
    └── lab3-synced-work  = branch based on synced/main

synced repo
    └── main              = final shared Lab 3 structure
```

---

# Add the Synced Repository as a Remote

Each person should add the synced repository as an extra remote inside their personal repository.

Run this inside your personal repository:

```bash
git remote add synced git@github.com:jayran-d/cs4160-lab3-blockchain.git
```

Check that the remotes are correct:

```bash
git remote -v
```

You should see something like:

```text
origin  git@github.com:PERSONAL_USERNAME/blockchain-engineering-labs.git
synced  git@github.com:jayran-d/cs4160-lab3-blockchain.git
```

Here:

* `origin` is your own personal repository.
* `synced` is the shared Lab 3 repository.

---

# First-Time Setup for Working on Lab 3

After the synced repository has the shared file structure on `main`, each person should create a local branch from `synced/main`.

Run this inside your personal repository:

```bash
git fetch synced
git checkout -b lab3-synced-work synced/main
```

Now you are on a local branch called:

```text
lab3-synced-work
```

This branch contains the synced repo's Lab 3 structure, not your personal repo's Lab 1/Lab 2 structure.

---

# Important Branch Rule

Your personal repo will now have at least two kinds of branches:

```text
main
    Personal repository structure.
    May contain Lab 1, Lab 2, Lab 3, old experiments, etc.

lab3-synced-work
    Local branch based on synced/main.
    Used for contributing to the synced Lab 3 repository.
```

Use personal `main` only for your own personal repo work.

Use `lab3-synced-work` for final Lab 3 synced work.

Before making synced Lab 3 changes, check that you are on the right branch:

```bash
git branch
```

You should see:

```text
* lab3-synced-work
```

---

# Making a New Lab 3 Change

## 1. Switch to the synced work branch

```bash
git checkout lab3-synced-work
```

## 2. Receive the latest changes from the synced repo

Before editing, always update your branch with the latest synced `main`:

```bash
git fetch synced
git merge synced/main
```

You can also use rebase instead:

```bash
git fetch synced
git rebase synced/main
```

Use `merge` if you want the safer/simple option.

Use `rebase` only if you are comfortable with it.

## 3. Make your changes

Edit the shared Lab 3 files, for example:

```text
client.py
community.py
payloads.py
blockchain/miner.py
registration/community.py
```

You can copy or adapt code from your personal Lab 3 folder, but the final code should fit the synced repo structure.

For example, useful code from:

```text
main: lab3-pow-blockchain/
```

can be adapted into:

```text
lab3-synced-work: blockchain/
lab3-synced-work: community.py
lab3-synced-work: payloads.py
```

## 4. Commit your change locally

```bash
git status
git add .
git commit -m "Describe your Lab 3 change"
```

Example commit messages:

```bash
git commit -m "Add transaction validation logic"
git commit -m "Implement mining loop"
git commit -m "Fix registration payload serialization"
git commit -m "Add block broadcast handler"
```

## 5. Push your branch to the synced repository

Push your local `lab3-synced-work` branch to a feature branch on the synced repo:

```bash
git push synced lab3-synced-work:your-feature-branch-name
```

This means:

```text
synced                 = the shared GitHub repo remote
lab3-synced-work       = your local branch
your-feature-branch    = the branch created/updated on the shared repo
```

Examples:

```bash
git push synced lab3-synced-work:jayran-registration-fix
git push synced lab3-synced-work:darian-mining-loop
git push synced lab3-synced-work:yves-block-validation
```

Then open a pull request on GitHub from your feature branch into:

```text
main
```

---

# Updating an Existing Feature Branch

If you already pushed a feature branch and want to update it, first commit your local changes:

```bash
git checkout lab3-synced-work

git status
git add .
git commit -m "Update Lab 3 change"
```

Then push to the same synced branch:

```bash
git push synced lab3-synced-work:your-feature-branch-name
```

If Git rejects the push because the remote branch has diverged, first update your local branch:

```bash
git fetch synced
git merge synced/main
```

Then push again:

```bash
git push synced lab3-synced-work:your-feature-branch-name
```

If you intentionally rewrote your local commits, use:

```bash
git push --force-with-lease synced lab3-synced-work:your-feature-branch-name
```

Only use `--force-with-lease` on your own feature branch, not on `main`.

---

# Receiving New Changes After Someone Else Merges

When another teammate's pull request is merged into synced `main`, update your local branch:

```bash
git checkout lab3-synced-work
git fetch synced
git merge synced/main
```

Now your local branch has the latest shared Lab 3 code.

If there are conflicts, resolve them, then run:

```bash
git add .
git commit
```

After that, continue working normally.

---

# Branch Naming Recommendation

Use descriptive branch names in the synced repo.

Examples:

```text
jayran-registration-fix
jayran-block-validation
darian-retry-logic
darian-config-cleanup
yves-miner-threading
yves-chain-sync
```

Avoid everyone pushing to the same branch name.

---

# What Not To Do

## Do not push personal main to the synced repo

```bash
git push synced main
```

This is wrong because personal `main` may contain Lab 1, Lab 2, and other files.

## Do not push directly to synced main

```bash
git push synced lab3-synced-work:main
```

Avoid this unless the group explicitly agrees. Prefer feature branches and pull requests.

## Do not work on synced changes from personal main

If you are on personal `main`, you are probably in the old personal repo structure.

Check your branch:

```bash
git branch
```

For synced Lab 3 work, use:

```bash
git checkout lab3-synced-work
```

---

# Optional: Keeping Personal Main Updated

Your personal repo `main` can still be used for your own old structure and experiments.

For example:

```bash
git checkout main
git pull origin main
```

This is separate from the synced Lab 3 workflow.

Do not push this branch to the synced repo.

---

# Checking the Synced Repository

After branches are merged, the synced repo should contain only Lab 3 code:

```text
cs4160-lab3-blockchain/
├── README.md
├── SYNC_INSTRUCTIONS.md
├── requirements.txt
├── .gitignore
├── client.py
├── community.py
├── config.py
├── payloads.py
├── blockchain/
├── registration/
└── keys/
```

To check the commit history:

```bash
git log --oneline
```

To check who contributed:

```bash
git log --oneline --author="Jayran"
git log --oneline --author="Darian"
git log --oneline --author="Yves"
```


---

# Summary

Use this rule:

```text
Personal main keeps the personal repo structure.
Synced main contains only final Lab 3 code.
For synced Lab 3 work, use a branch based on synced/main.
Push feature branches to synced.
Open pull requests into synced main.
```

The key command pattern is:

```bash
git fetch synced
git checkout -b lab3-synced-work synced/main

# Later, before new work:
git checkout lab3-synced-work
git fetch synced
git merge synced/main

# Commit changes:
git add .
git commit -m "Describe change"

# Push to synced feature branch:
git push synced lab3-synced-work:<feature-branch-name>
```

Examples:

```bash
git push synced lab3-synced-work:jayran-registration-fix
git push synced lab3-synced-work:darian-mining-loop
git push synced lab3-synced-work:yves-block-validation
```
