---
name: book-profile
description: Survey for intended audience, writing style, purpose, credentials, and book positioning
allowed-tools:
  - Read
  - Write
  - Glob
  - AskUserQuestion
---

# Book Profile Survey

Guide the user through a comprehensive book profile survey to establish the foundation for their non-fiction book. This information will inform all subsequent writing.

## Process

### Step 1: Check for Existing Profile

First, check if a profile already exists at `.claude/book-creator.local.md` in the current directory.

If it exists, read it and ask the user:
- "I found an existing book profile. Would you like to update it or start fresh?"

### Step 2: Gather Profile Information

Use AskUserQuestion to gather information in these categories. Ask 2-3 questions at a time to avoid overwhelming the user.

#### Target Audience
- Who is the primary reader of this book?
- What problem or pain point does your reader have?
- What does your reader hope to achieve by reading this book?
- What's their current level of knowledge on this topic?

#### Purpose & Transformation
- Why are you writing this book? (legacy, business growth, share knowledge, establish authority)
- What transformation do you want readers to experience?
- What's the ONE core message you want readers to remember?

#### Writing Style & Voice
- What tone should the book have? (formal, conversational, inspirational, practical, academic)
- First person ("I") or third person?
- Should it include personal stories and anecdotes?
- Any authors whose style you admire or want to emulate?

#### Author Credentials
- What qualifies you to write this book?
- What's your professional background related to this topic?
- Any notable achievements, clients, or results to mention?

#### Book Positioning
- What are 2-3 comparable books in this space?
- How is your book different or better?
- What's your unique angle or framework?
- What will readers get from your book that they won't get elsewhere?

### Step 3: Create Profile Document

After gathering all information, create the profile at `.claude/book-creator.local.md`:

```markdown
---
title: "[Working Title if provided]"
created: "[date]"
status: profile-complete
---

# Book Profile

## Target Audience

**Primary Reader:** [description]

**Pain Points:**
- [pain point 1]
- [pain point 2]

**Goals:**
- [what they want to achieve]

**Current Knowledge Level:** [beginner/intermediate/advanced]

## Purpose & Transformation

**Why This Book:** [author's motivation]

**Reader Transformation:** [before → after]

**Core Message:** [the ONE thing]

## Writing Style

**Tone:** [formal/conversational/etc.]
**Person:** [first/third]
**Personal Stories:** [yes/no]
**Style Influences:** [authors or books]

## Author Credentials

**Background:** [relevant experience]

**Qualifications:**
- [qualification 1]
- [qualification 2]

**Notable Achievements:** [if any]

## Book Positioning

**Comparable Titles:**
1. [book 1] - [how yours differs]
2. [book 2] - [how yours differs]

**Unique Angle:** [your differentiation]

**Unique Value:** [what readers get only from you]
```

### Step 4: Confirm and Next Steps

Show the user a summary of their profile and confirm it's accurate.

Tell them:
- "Your book profile is complete! Run `/book-new` to initialize your book project."
