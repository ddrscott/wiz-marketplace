---
name: book-outline
description: Create or refine the book outline with chapters, sections, and key points
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - AskUserQuestion
---

# Book Outline Development

Help the user create or refine their book outline with chapters, sections, key points, and logical flow.

## Prerequisites Check

Verify the book project has been initialized by checking for:
1. `.claude/book-creator.local.md` with `status: project-initialized` or later
2. `outline.md` file exists

If prerequisites not met:
- If no profile: "Run `/book-profile` first."
- If no project: "Run `/book-new` to initialize your project."

## Process

### Step 1: Read Current State

Read both:
- `.claude/book-creator.local.md` - for book context, audience, transformation
- `outline.md` - for current outline state

### Step 2: Determine Mode

Ask the user what they want to do:
1. **Build outline from scratch** - Start fresh with guided questions
2. **Expand existing outline** - Add more detail to current chapters
3. **Reorganize structure** - Reorder or restructure chapters
4. **Add new chapters** - Insert additional chapters
5. **Review and refine** - Get feedback on current outline

### Step 3: Guided Outline Development

#### For Building from Scratch:

Ask about the book's structure:
- "How many main parts or sections should your book have?" (1-5 typical)
- "What's the logical progression? (problem→solution, beginner→advanced, chronological, thematic)"

For each part, ask:
- "What's Part [X] about? What ground does it cover?"
- "How many chapters should this part have?"

For each chapter, gather:
- Chapter title
- Purpose (what does this chapter accomplish?)
- 3-5 key points to cover
- Brief summary (2-3 sentences)
- Suggested image opportunities (diagrams, illustrations, examples)

#### For Expanding Existing Outline:

For each chapter that needs expansion, ask:
- "What additional key points should this chapter cover?"
- "Are there any stories or examples to include?"
- "What images or diagrams would help explain concepts?"
- "How does this chapter connect to the next one?"

### Step 4: Add Image Placeholders to Outline

For each chapter, suggest 1-3 image opportunities:
- Conceptual diagrams
- Process flowcharts
- Comparison tables/charts
- Illustrative examples
- Framework visualizations

Add to outline as:
```markdown
**Image Opportunities:**
- <!-- IMAGE: [description of image] -->
```

### Step 5: Validate Structure

Review the outline for:
- **Logical flow**: Does each chapter build on the previous?
- **Completeness**: Are all aspects of the topic covered?
- **Balance**: Are chapters roughly similar in scope?
- **Transformation**: Does the arc deliver on the promised transformation?

Provide feedback and suggestions for improvement.

### Step 6: Update Outline File

Update `outline.md` with all the gathered information, maintaining the structure:

```markdown
# [Book Title]

> [Core message]

## Book Overview
...

---

## Part I: [Title]

### Chapter 1: [Title]
**Purpose:** ...
**Key Points:**
- ...
**Image Opportunities:**
- <!-- IMAGE: ... -->
**Chapter Summary:** ...

---
```

### Step 7: Update Profile Status

Update `.claude/book-creator.local.md` frontmatter:
- `status: outline-complete`
- `chapters: [count]`
- `parts: [count]`

### Step 8: Next Steps

Tell the user:
- "Your outline is ready with [X] chapters across [Y] parts."
- "Run `/book-chapter 1` to start writing your first chapter."
- "Run `/book-status` anytime to see your progress."
