# Working with the Synced Lab 3 Repository

This document explains how each group member can continue working in their own personal repository while contributing Lab 3 changes to the synced group repository.

The goal is:

* each person can keep working in their own personal repository;
* personal repositories can still contain Lab 1, Lab 2, and other files;
* each person's Lab 3 folder follows the same structure as the synced repository;
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

The personal repository may contain older labs. That is fine.

However, the Lab 3 folder inside each personal repository should match the synced repository structure.

For example, Jayran's personal repo should have:

```text
personal-repo/
└── lab3-pow-blockchain/
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
    └──
```

The synced repository should contain the same Lab 3 structure at the root:

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

The synced repo should not contain Lab 1 or Lab 2 folders.

---

# Main Idea

Each person works in their own personal repository.

However, only the Lab 3 folder is pushed to the synced repository.

Because personal repositories contain multiple labs, do not push personal `main` directly to the synced repository.

Do not do this:

```bash
git push synced main
```

That would try to push the full personal repository structure, including Lab 1 and Lab 2.

Instead, use `git subtree split` to create a temporary branch containing only the Lab 3 folder contents. Then push that Lab 3-only branch to a feature branch in the synced repository.

The workflow is:

```text
personal repo
    ├── main / personal branches
    │       └── contains Lab 1, Lab 2, Lab 3, etc.
    │
    └── Lab 3 folder
            └── same structure as synced repo

git subtree split
    ↓

lab3-only branch
    └── contains only Lab 3 files at the root

git push synced lab3-only:<feature-branch>
    ↓

Pull request into synced/main
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

# One-Time Setup: Replace Your Current Lab 3 Folder with the Synced Structure

Before using the normal pull/push workflow, each person should do a one-time setup step.

The goal is to:

1. keep a backup of your current Lab 3 folder;
2. remove the old Lab 3 folder from your personal repo;
3. add the synced repo's `main` branch as the new Lab 3 folder;
4. make Git recognize the Lab 3 folder as a real subtree;
5. allow future pulls using `git subtree pull`.

This only needs to be done once.

---

## Step 1: Go to Your Personal Repo

```bash
cd path/to/your/personal-repo
```

Switch to the branch where you want to work on Lab 3:

```bash
git checkout <your-personal-lab3-branch>
```

Example:

```bash
git checkout jayran-lab3-work
```

---

## Step 2: Make Sure Your Current Work Is Saved

Check your status:

```bash
git status
```

If you have uncommitted work, commit it first:

```bash
git add .
git commit -m "Save current Lab 3 work before synced setup"
```

This makes sure your current work is not lost.

---

## Step 3: Back Up Your Current Lab 3 Folder

Create a backup outside the repository.

This is important because the backup should not accidentally become part of the synced Lab 3 structure.

So just copy your current lab 3 folder and name is lab3-backup or soemthing.

After this, your old Lab 3 code is safely backed up one folder above the personal repo.

---

## Step 4: Remove the Old Lab 3 Folder from the Personal Repo

Remove the old Lab 3 folder from your personal repo.

You can also do this manually. 

### Jayran

```bash
rm -rf lab3-pow-blockchain
```

### Darian

```bash
rm -rf lab1-ipv8-pow/lab3
```

### Yves

```bash
rm -rf lab3
```

Then commit the removal:

```bash
git add -A
git commit -m "Remove old Lab 3 folder before synced subtree setup"
```

---

## Step 5: Add the Synced Repo as the New Lab 3 Folder

Make sure the synced remote exists:

```bash
git remote -v
```

If you do not see `synced`, add it:

```bash
git remote add synced git@github.com:jayran-d/cs4160-lab3-blockchain.git
```

Fetch the latest synced repo state:

```bash
git fetch synced
```

Now add `synced/main` as your new Lab 3 folder.

### Jayran

```bash
git subtree add --prefix=lab3-pow-blockchain synced main --squash
```

### Darian

```bash
git subtree add --prefix=lab1-ipv8-pow/lab3 synced main --squash
```

### Yves

```bash
git subtree add --prefix=lab3 synced main --squash
```

This makes the synced repository's `main` branch become your new Lab 3 folder.

For example, Jayran's personal repo will now contain:

```text
personal-repo/
├── lab1-ipv8-pow/
├── lab2-group-signing/
└── lab3-pow-blockchain/
    ├── README.md
    ├── client.py
    ├── community.py
    ├── config.py
    ├── payloads.py
    ├── blockchain/
    ├── registration/
    └── keys/
```

The important difference is that Git now knows `lab3-pow-blockchain/` came from the synced repo. This allows future subtree pulls to work correctly.

---

## Step 6: Reapply Any Useful Code from Your Backup

Your old Lab 3 code is still available in the backup folder.

For example:

```text
../lab3-pow-blockchain-backup/
```

Manually copy or adapt any useful code from the backup into the new Lab 3 folder.

Do not blindly copy the entire old folder back, because that may undo the synced structure.

Instead, copy useful code into the matching files, for example:

```text
old backup file                 new synced structure file
----------------------------------------------------------
community.py                    lab3-pow-blockchain/community.py
payloads.py                     lab3-pow-blockchain/payloads.py
block.py                        lab3-pow-blockchain/blockchain/block.py
miner.py                        lab3-pow-blockchain/blockchain/miner.py
```

After adapting your code, commit it:

```bash
git add .
git commit -m "Reapply personal Lab 3 work to synced structure"
git push origin <your-personal-lab3-branch>
```

---

## Step 7: Future Pulls Will Now Work

After this one-time setup, you can pull new synced changes into your Lab 3 folder using:

### Jayran

```bash
git fetch synced
git subtree pull --prefix=lab3-pow-blockchain synced main --squash
```

### Darian

```bash
git fetch synced
git subtree pull --prefix=lab1-ipv8-pow/lab3 synced main --squash
```

### Yves

```bash
git fetch synced
git subtree pull --prefix=lab3 synced main --squash
```

This is why the one-time setup is useful: future updates from `synced/main` can be merged into your personal Lab 3 folder instead of manually copied.

---

## Summary of the One-Time Setup

The pattern is:

```bash
# 1. Save current work
git status
git add .
git commit -m "Save current Lab 3 work before synced setup"

# 2. Back up the old Lab 3 folder outside the repo
cp -a <your-lab3-folder-path> ../lab3-backup

# 3. Remove the old Lab 3 folder
rm -rf <your-lab3-folder-path>
git add -A
git commit -m "Remove old Lab 3 folder before synced subtree setup"

# 4. Add synced/main as the new Lab 3 folder
git fetch synced
git subtree add --prefix=<your-lab3-folder-path> synced main --squash

# 5. Reapply useful code from the backup manually
git add .
git commit -m "Reapply personal Lab 3 work to synced structure"
git push origin <your-personal-lab3-branch>
```

After this, normal pulling uses:

```bash
git subtree pull --prefix=<your-lab3-folder-path> synced main --squash
```

# Lab 3 Folder Paths

Each person needs to know where their Lab 3 folder is located inside their personal repository.

Current paths:

```text
Jayran: lab3-pow-blockchain/
Darian: lab1-ipv8-pow/lab3/
Yves:   lab3/
```

These paths are used in the `git subtree split --prefix=...` command.

The inside of each Lab 3 folder should match the synced repo structure, even if the outer folder path is different.

---

# Working Normally in Your Personal Repo

You do not have to work on `main`.

You can work on any personal branch.

For example:

```bash
# Switch to whatever personal branch you are using
git checkout <your-personal-branch>

# Get latest changes for that branch, if it tracks origin
git pull origin <your-personal-branch>

# Make changes inside your Lab 3 folder

git add .
git commit -m "Describe your Lab 3 change"

# Push your personal branch to your personal repo
git push origin <your-personal-branch>
```

Example:

```bash
git checkout jayran-lab3-work
git pull origin jayran-lab3-work

# Make changes inside lab3-pow-blockchain/

git add .
git commit -m "Add transaction validation logic"
git push origin jayran-lab3-work
```

This keeps your personal repo history intact.

---

# Pushing Lab 3 Changes to the Synced Repo

After committing your Lab 3 changes in your personal repo, create a Lab 3-only branch using `git subtree split`.

## Jayran

Jayran's Lab 3 path:

```text
lab3-pow-blockchain/
```

Run from the personal repo:

```bash
# Delete old lab3-only branch if it exists
git branch -D lab3-only

# Create a fresh branch containing only the Lab 3 folder contents
git subtree split --prefix=lab3-pow-blockchain -b lab3-only

# Push the local `lab3-only` branch to the synced repository.
# This creates or updates a remote branch called `jayran-lab3`.
# It does NOT push directly to `main`; open a PR from `jayran-lab3` into `main`.
git push synced lab3-only:jayran-lab3
```

If this fails:

```bash
git branch -D lab3-only
```

because the branch does not exist, that is fine. Continue with the `git subtree split` command.

Then open a pull request on GitHub:

```text
jayran-lab3 -> main
```

---

## Darian

Darian's Lab 3 path:

```text
lab1-ipv8-pow/lab3/
```

Run from the personal repo:

```bash
git branch -D lab3-only
git subtree split --prefix=lab1-ipv8-pow/lab3 -b lab3-only

# Push the local `lab3-only` branch to the synced repository.
# This creates or updates a remote branch called `darian-lab3`.
git push synced lab3-only:darian-lab3
```

Then open a pull request on GitHub:

```text
darian-lab3 -> main
```

---

## Yves

Yves's Lab 3 path:

```text
lab3/
```

Run from the personal repo:

```bash
git branch -D lab3-only
git subtree split --prefix=lab3 -b lab3-only
git push synced lab3-only:yves-lab3
```

Then open a pull request on GitHub:

```text
yves-lab3 -> main
```

---

# What the Push Command Means

Example:

```bash
git push synced lab3-only:jayran-lab3
```

This means:

```text
synced       = the shared GitHub repo remote
lab3-only    = your local branch created by git subtree split
jayran-lab3  = the branch created/updated on the synced repo
```

This does not push directly to `main`.

It creates or updates a branch in the synced repo that can be opened as a pull request into `main`.

---

# Updating an Existing Synced Branch

If you already pushed a branch to the synced repo and want to update it, recreate `lab3-only` and push again.

Example for Jayran:

```bash
git branch -D lab3-only
git subtree split --prefix=lab3-pow-blockchain -b lab3-only
git push --force-with-lease synced lab3-only:jayran-lab3
```

Examples for everyone:

```bash
git push --force-with-lease synced lab3-only:jayran-lab3
git push --force-with-lease synced lab3-only:darian-lab3
git push --force-with-lease synced lab3-only:yves-lab3
```

Use `--force-with-lease` only on your own feature branch, not on `main`.

This is useful because `git subtree split` recreates the Lab 3-only branch from the latest personal repo state.

---

# Receiving New Changes from Synced Main

When a teammate's pull request is merged into `synced/main`, everyone should update their own personal Lab 3 folder before continuing new work.

Because the synced repo contains Lab 3 files at the root, and each personal repo stores Lab 3 inside a folder, we can use `git subtree pull`.

This merges the synced repo's `main` branch into the Lab 3 folder inside the personal repo.

Aldo do the following based on whether you have uncomitted changes (not clean) or not (clean) in your working branch.
```bash
git status

# If clean:
git fetch synced
git subtree pull --prefix=lab3-pow-blockchain synced main --squash

# If not clean:
git stash push -m "temp lab3 work"
git fetch synced
git subtree pull --prefix=lab3-pow-blockchain synced main --squash
git stash pop
```

## Jayran

Jayran's Lab 3 folder is:

```text
lab3-pow-blockchain/
```

Run this from the root of the personal repo:

```bash
git fetch synced

# Pull synced/main into the personal Lab 3 folder.
# The synced repo root becomes the contents of lab3-pow-blockchain/.
git subtree pull --prefix=lab3-pow-blockchain synced main --squash
```

Then push the updated personal branch:

```bash
git push origin <your-personal-branch>
```

## Darian

Darian's Lab 3 folder is:

```text
lab1-ipv8-pow/lab3/
```

Run this from the root of Darian's personal repo:

```bash
git fetch synced

# Pull synced/main into Darian's personal Lab 3 folder.
git subtree pull --prefix=lab1-ipv8-pow/lab3 synced main --squash
```

Then push the updated personal branch:

```bash
git push origin <your-personal-branch>
```

## Yves

Yves's Lab 3 folder is:

```text
lab3/
```

Run this from the root of Yves's personal repo:

```bash
git fetch synced

# Pull synced/main into Yves's personal Lab 3 folder.
git subtree pull --prefix=lab3 synced main --squash
```

Then push the updated personal branch:

```bash
git push origin <your-personal-branch>
```

---

## When to Run This

Run this before starting new Lab 3 work, especially after someone else's pull request has been merged into the synced repo.

The usual flow is:

```bash
# 1. Go to your personal repo
cd path/to/personal-repo

# 2. Switch to your personal Lab 3 branch
git checkout <your-personal-branch>

# 3. Get latest synced repo state
git fetch synced

# 4. Merge synced/main into your Lab 3 folder
git subtree pull --prefix=<your-lab3-folder-path> synced main --squash

# 5. Push the updated personal branch
git push origin <your-personal-branch>
```

Example for Jayran:

```bash
cd path/to/personal-repo
git checkout jayran-lab3-work

git fetch synced
git subtree pull --prefix=lab3-pow-blockchain synced main --squash

git push origin jayran-lab3-work
```

## If There Are Conflicts

If Git reports conflicts, open the conflicted files and fix them manually.

Then run:

```bash
git add .
git commit
```

After resolving the conflicts, continue working normally.

---

# Adding New Files

It is fine if someone adds new files.

For example:

```text
blockchain/validation.py
blockchain/serializer.py
registration/utils.py
```

When those files are merged into `synced/main`, everyone else should run the `git subtree pull` command. That will bring the new files into their own personal Lab 3 folder.

This is important because if someone keeps working from an old Lab 3 folder, their next PR may accidentally miss or overwrite files that were already added to the synced repo.

---

# Summary

Use this rule:

```text
Before starting new work, pull synced/main into your personal Lab 3 folder.
```

Command pattern:

```bash
git fetch synced
git subtree pull --prefix=<your-lab3-folder-path> synced main --squash
```

Examples:

```bash
# Jayran
git subtree pull --prefix=lab3-pow-blockchain synced main --squash

# Darian
git subtree pull --prefix=lab1-ipv8-pow/lab3 synced main --squash

# Yves
git subtree pull --prefix=lab3 synced main --squash
```

# Adding New Files

It is fine to add new files.

For example, someone may add:

```text
blockchain/validation.py
blockchain/serializer.py
registration/utils.py
```

If a new file is part of the final Lab 3 code, it should be:

1. added inside that person's Lab 3 folder;
2. committed in their personal repo;
3. pushed to a synced feature branch using `git subtree split`;
4. merged into `synced/main` through a pull request.

After the PR is merged, everyone else should update their personal Lab 3 folder with the new file.

Important:

```text
If someone adds a new file and it is merged into synced/main,
everyone else needs to pull/copy/adapt that file into their own Lab 3 folder
before building on top of it.
```

Otherwise, later branches may accidentally miss or delete that file.

---

# What Not To Do

## Do not push personal main to the synced repo

```bash
git push synced main
```

This is wrong because personal `main` may contain Lab 1, Lab 2, and other files.

## Do not push directly to synced main

```bash
git push synced lab3-only:main
```

Avoid this unless the group explicitly agrees.

Prefer feature branches and pull requests.

## Do not ignore synced main after PRs are merged

If someone else's PR is merged and you keep working from an older Lab 3 folder, your next PR may accidentally remove or overwrite their changes.

Before starting a new change, update your personal Lab 3 folder from the latest `synced/main`.

---

# Optional Scripts

## Pushing Script

To avoid typing the subtree commands manually, each person can create a script like:

```text
scripts/push_lab3_to_synced.sh
```

Example script:

```bash
#!/usr/bin/env bash

set -e

# ---------------------------------------------------------------------
# Usage:
#
#   ./scripts/push_lab3_to_synced.sh <lab3-folder-path> <synced-branch-name>
#
# Example:
#
#   ./scripts/push_lab3_to_synced.sh lab3-pow-blockchain jayran-lab3
#
# Darian example:
#
#   ./scripts/push_lab3_to_synced.sh lab1-ipv8-pow/lab3 darian-lab3
#
# Yves example:
#
#   ./scripts/push_lab3_to_synced.sh lab3 yves-lab3
# ---------------------------------------------------------------------

LAB3_PATH="$1"
SYNCED_BRANCH="$2"

# IF YOU WANT YOU CAN ALSO HARDCODE IT
# LAB3_PATH="lab3"
# SYNCED_BRANCH="yves-lab3"

LOCAL_SPLIT_BRANCH="lab3-only"
SYNCED_REMOTE="synced"

if [ -z "$LAB3_PATH" ] || [ -z "$SYNCED_BRANCH" ]; then
    echo "Usage: $0 <lab3-folder-path> <synced-branch-name>"
    echo
    echo "Example:"
    echo "  $0 lab3-pow-blockchain jayran-lab3"
    exit 1
fi

if [ ! -d "$LAB3_PATH" ]; then
    echo "Error: Lab 3 folder does not exist: $LAB3_PATH"
    exit 1
fi

if ! git remote | grep -q "^${SYNCED_REMOTE}$"; then
    echo "Error: remote '${SYNCED_REMOTE}' does not exist."
    echo "Add it first with:"
    echo "  git remote add synced git@github.com:jayran-d/cs4160-lab3-blockchain.git"
    exit 1
fi

echo "Checking Git status..."
git status --short

echo
echo "Creating fresh '${LOCAL_SPLIT_BRANCH}' branch from '${LAB3_PATH}'..."

# Delete old local split branch if it exists.
git branch -D "$LOCAL_SPLIT_BRANCH" 2>/dev/null || true

# Create a branch containing only the Lab 3 folder contents.
git subtree split --prefix="$LAB3_PATH" -b "$LOCAL_SPLIT_BRANCH"

echo
echo "Pushing '${LOCAL_SPLIT_BRANCH}' to '${SYNCED_REMOTE}/${SYNCED_BRANCH}'..."

git push --force-with-lease "$SYNCED_REMOTE" "$LOCAL_SPLIT_BRANCH:$SYNCED_BRANCH"

echo
echo "Done."
echo
echo "Now open a Pull Request on GitHub:"
echo "  ${SYNCED_BRANCH}  ->  main"
echo
echo "Synced repo:"
echo "  git@github.com:jayran-d/cs4160-lab3-blockchain.git"
```

This script does not create the pull request. It only pushes the branch to the synced repo.

---

## Pulling Script

You can use this script to pull from the synced repo. You can adjust the `SYNCED_BRANCH` name accordingly to what branch you want to pull from.

```bash
#!/usr/bin/env bash

set -e

# ---------------------------------------------------------------------
# Usage:
#
#   ./pull_lab3_from_synced.sh <lab3-folder-path> [synced-branch-name]
#
# Examples:
#
#   # Pull synced/main into Jayran's Lab 3 folder
#   ./pull_lab3_from_synced.sh lab3-pow-blockchain
#
#   # Pull synced/main explicitly
#   ./pull_lab3_from_synced.sh lab3-pow-blockchain main
#
#   # Pull Yves's synced branch into Jayran's Lab 3 folder
#   ./pull_lab3_from_synced.sh lab3-pow-blockchain yves-lab3
#
#   # Darian
#   ./pull_lab3_from_synced.sh lab1-ipv8-pow/lab3 main
#
#   # Yves
#   ./pull_lab3_from_synced.sh lab3 main
# ---------------------------------------------------------------------

# Values passed from the command line:
#   $1 = Lab 3 folder path
#   $2 = synced branch name
LAB3_PATH="$1"
SYNCED_BRANCH="${2:-main}"

# If you prefer, you can hardcode these instead:
# LAB3_PATH="lab3-pow-blockchain"
# SYNCED_BRANCH="main"

SYNCED_REMOTE="synced"

if [ -z "$LAB3_PATH" ]; then
    echo "Usage: $0 <lab3-folder-path> [synced-branch-name]"
    echo
    echo "Examples:"
    echo "  $0 lab3-pow-blockchain"
    echo "  $0 lab3-pow-blockchain main"
    echo "  $0 lab3-pow-blockchain yves-lab3"
    exit 1
fi

if [ ! -d "$LAB3_PATH" ]; then
    echo "Error: Lab 3 folder does not exist: $LAB3_PATH"
    exit 1
fi

if ! git remote | grep -q "^${SYNCED_REMOTE}$"; then
    echo "Error: remote '${SYNCED_REMOTE}' does not exist."
    echo "Add it first with:"
    echo "  git remote add synced git@github.com:jayran-d/cs4160-lab3-blockchain.git"
    exit 1
fi

echo "Checking for uncommitted changes..."
if [ -n "$(git status --porcelain)" ]; then
    echo
    echo "Error: You have uncommitted changes."
    echo "Commit or stash your changes before pulling from ${SYNCED_REMOTE}/${SYNCED_BRANCH}."
    echo
    echo "Commit option:"
    echo "  git add ."
    echo "  git commit -m \"Save current Lab 3 work\""
    echo
    echo "Stash option:"
    echo "  git stash push -u -m \"temp lab3 work\""
    echo
    exit 1
fi

echo "Fetching latest branches from ${SYNCED_REMOTE}..."
git fetch "$SYNCED_REMOTE"

if ! git rev-parse --verify --quiet "${SYNCED_REMOTE}/${SYNCED_BRANCH}" >/dev/null; then
    echo
    echo "Error: Branch '${SYNCED_REMOTE}/${SYNCED_BRANCH}' does not exist."
    echo
    echo "Available synced branches:"
    git branch -r | grep "${SYNCED_REMOTE}/" || true
    exit 1
fi

echo
echo "Pulling ${SYNCED_REMOTE}/${SYNCED_BRANCH} into ${LAB3_PATH}/..."
echo

# Pull the selected synced branch into the personal Lab 3 folder.
# The synced repo root becomes the contents of the Lab 3 folder.
git subtree pull --prefix="$LAB3_PATH" "$SYNCED_REMOTE" "$SYNCED_BRANCH" --squash

echo
echo "Done."
echo
echo "Updated ${LAB3_PATH}/ from ${SYNCED_REMOTE}/${SYNCED_BRANCH}."
echo
echo "Next steps:"
echo "  git status"
echo "  git push origin <your-personal-branch>"
```

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
Personal repo keeps all labs.
Each personal Lab 3 folder follows the synced repo structure.
Synced main contains only final Lab 3 code.
Use git subtree split to push only the Lab 3 folder.
Push feature branches to synced.
Open pull requests into synced main.
```

The key command pattern is:

```bash
git subtree split --prefix=<path-to-lab3-folder> -b lab3-only
git push synced lab3-only:<synced-feature-branch-name>
```

Examples:

```bash
# Jayran
git subtree split --prefix=lab3-pow-blockchain -b lab3-only
git push synced lab3-only:jayran-lab3

# Darian
git subtree split --prefix=lab1-ipv8-pow/lab3 -b lab3-only
git push synced lab3-only:darian-lab3

# Yves
git subtree split --prefix=lab3 -b lab3-only
git push synced lab3-only:yves-lab3
```
