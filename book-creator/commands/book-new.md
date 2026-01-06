---
name: book-new
description: Initialize a new book project with title and directory structure
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
---

# Initialize New Book Project

Create the directory structure and initial files for a new non-fiction book project.

## Prerequisites Check

First, verify that `/book-profile` has been completed by checking for `.claude/book-creator.local.md`.

If the profile doesn't exist:
- Tell the user: "You need to complete your book profile first. Run `/book-profile` to get started."
- Stop execution.

If the profile exists, read it to understand the book's context.

## Process

### Step 1: Gather Book Details

Ask the user:
1. What is the working title of your book?
2. What directory should I create for this project? (suggest: `./book-title-kebab-case/`)

### Step 2: Create Directory Structure

Create the following structure:

```
[book-directory]/
├── .claude/
│   └── book-creator.local.md    # Copy from current profile
├── outline.md                    # Initial outline template
├── chapters/                     # Empty, ready for chapters
└── images/                       # For final images
```

Use Bash to create directories:
```bash
mkdir -p [book-directory]/.claude
mkdir -p [book-directory]/chapters
mkdir -p [book-directory]/images
```

### Step 3: Copy Profile

Copy the profile from `.claude/book-creator.local.md` to the new book directory.

Update the profile's frontmatter:
- Add `title: "[Book Title]"`
- Add `directory: "[book-directory]"`
- Update `status: project-initialized`

### Step 4: Create Outline Template

Create `outline.md` with this structure:

```markdown
# [Book Title]

> [Core message from profile]

## Book Overview

**Target Reader:** [from profile]
**Transformation:** [from profile]
**Unique Angle:** [from profile]

---

## Part I: [Part Title]

### Chapter 1: [Chapter Title]
**Purpose:** [What this chapter accomplishes]
**Key Points:**
- [Key point 1]
- [Key point 2]
- [Key point 3]

**Chapter Summary:** [2-3 sentence summary]

---

### Chapter 2: [Chapter Title]
**Purpose:** [What this chapter accomplishes]
**Key Points:**
- [Key point 1]
- [Key point 2]

**Chapter Summary:** [2-3 sentence summary]

---

## Part II: [Part Title]

### Chapter 3: [Chapter Title]
...

---

## Appendices (Optional)

### Appendix A: [Title]
[Description]

---

## Notes

- Target word count: [X words]
- Target chapters: [X chapters]
- Estimated completion: [date]
```

### Step 5: Confirm and Next Steps

Tell the user:
- "Your book project '[Title]' has been created at `[directory]/`"
- "I've created an outline template based on your profile."
- "Next step: Run `/book-outline` to flesh out your chapter structure."

Also suggest they `cd [book-directory]` to work within the project.
