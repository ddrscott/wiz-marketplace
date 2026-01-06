---
name: book-status
description: View book project progress, completed chapters, and next steps
allowed-tools:
  - Read
  - Glob
---

# Book Status

Display the current status of the book project, including progress, word counts, and next steps.

## Process

### Step 1: Find Book Project

Look for book project indicators:
1. `.claude/book-creator.local.md` in current directory
2. If not found, check parent directory
3. If still not found, report no active book project

### Step 2: Read Project State

Read:
- `.claude/book-creator.local.md` - project metadata and status
- `outline.md` - chapter structure
- `chapters/*.md` - existing chapter files

### Step 3: Calculate Progress

Determine:
- **Workflow stage**: profile → new → outline → writing → complete
- **Chapters planned**: from outline
- **Chapters written**: from chapters/ directory
- **Total word count**: sum of all chapter word counts
- **Image placeholders**: count of `<!-- IMAGE: -->` markers

### Step 4: Display Status Report

Format output like this:

```
=== BOOK STATUS ===

Title: [Book Title]
Status: [Current Stage]

PROGRESS
--------
Profile:     [Complete/Incomplete]
Project:     [Initialized/Not Started]
Outline:     [Complete/In Progress/Not Started]
Chapters:    [X] of [Y] complete

CHAPTERS
--------
[x] Chapter 1: [Title] (2,450 words, 3 images)
[x] Chapter 2: [Title] (1,890 words, 2 images)
[ ] Chapter 3: [Title] (not started)
[ ] Chapter 4: [Title] (not started)
...

STATISTICS
----------
Total Words:     [X,XXX]
Avg Words/Ch:    [X,XXX]
Image Placeholders: [XX]
Est. Page Count: [~XXX pages at 250 words/page]

NEXT STEPS
----------
→ [Recommended next action based on current state]
```

### Step 5: Provide Recommendations

Based on current state, suggest:

**If profile incomplete:**
- "Run `/book-profile` to complete your book profile."

**If project not initialized:**
- "Run `/book-new` to create your book project."

**If outline incomplete:**
- "Run `/book-outline` to develop your chapter structure."

**If writing in progress:**
- "Run `/book-chapter [next-chapter]` to continue writing."
- If stuck: "Consider switching to interactive mode for the next chapter."

**If all chapters complete:**
- "Congratulations! Your first draft is complete."
- "Consider a revision pass to strengthen transitions and consistency."
- "Export chapters for editing or publishing workflow."

### Step 6: Image Placeholder Summary

If there are image placeholders, offer:
- "You have [X] image placeholders. Want me to list them for image generation?"

If requested, list all placeholders with chapter locations:
```
IMAGE PLACEHOLDERS
------------------
Chapter 1:
  - <!-- IMAGE: A flowchart showing... -->
  - <!-- IMAGE: A diagram of... -->

Chapter 2:
  - <!-- IMAGE: A comparison chart... -->
...
```
