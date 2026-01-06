---
name: book-chapter
description: Write or refine a specific chapter with interactive or auto-generate mode
argument-hint: "[chapter-number]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - AskUserQuestion
  - Task
---

# Chapter Writing

Write or refine a specific chapter of the book, with support for both interactive dialogue and auto-generation modes.

## Prerequisites Check

Verify:
1. `.claude/book-creator.local.md` exists with `status: outline-complete` or later
2. `outline.md` exists with chapter definitions

If prerequisites not met, direct user to complete earlier steps.

## Process

### Step 1: Identify Target Chapter

If chapter number provided as argument:
- Parse the chapter number from the command argument
- Validate it exists in the outline

If no chapter number:
- Read outline and show list of chapters
- Ask which chapter to work on
- Show status of each (not started, in progress, complete)

### Step 2: Load Context

Read and understand:
1. **Book profile** - audience, voice, style, credentials, positioning
2. **Outline** - chapter's purpose, key points, summary, image opportunities
3. **Previous chapters** - if any exist, for continuity
4. **Existing chapter draft** - if revising

### Step 3: Choose Writing Mode

Ask the user:
1. **Interactive mode** - "Walk me through this chapter with questions and dialogue"
2. **Auto-generate mode** - "Generate a complete draft from the outline"
3. **Revise mode** - "Help me improve the existing draft" (only if draft exists)

### Step 4A: Interactive Mode

For interactive writing, guide the user through the chapter:

**Opening:**
- "How do you want to open this chapter? A story, a question, a bold statement?"
- "What's the hook that will grab readers?"

**For each key point from outline:**
- "Tell me more about [key point]. What do readers need to understand?"
- "Do you have a personal story or example for this?"
- "What's a common misconception about this?"
- "How does this connect to your overall framework?"

**Transitions:**
- "How should we bridge from [previous section] to [next section]?"

**Closing:**
- "What's the key takeaway for this chapter?"
- "How does this set up the next chapter?"

**Images:**
- For each image opportunity: "The outline suggests an image here: [description]. Should I include this placeholder?"

Build the chapter iteratively, showing drafts and getting feedback.

### Step 4B: Auto-Generate Mode

Use the book-writer agent to generate a complete chapter draft:

Launch the agent with:
- Full book profile (voice, style, audience)
- Chapter outline (purpose, key points, summary)
- Previous chapter endings (for continuity)
- Image placeholder locations

The agent should generate a complete chapter with:
- Engaging opening hook
- All key points covered with depth
- Examples, stories, or case studies where appropriate
- Smooth transitions between sections
- Image placeholders at appropriate locations
- Strong chapter summary/conclusion
- Bridge to next chapter

Present the draft to the user for review and refinement.

### Step 4C: Revise Mode

Read the existing chapter and ask:
- "What aspects need improvement? (clarity, depth, examples, flow, voice)"
- "Any specific sections to focus on?"
- "Should I add more image placeholders?"

Make targeted revisions based on feedback.

### Step 5: Format Chapter

Ensure the chapter follows this structure:

```markdown
# Chapter [N]: [Title]

[Opening hook - story, question, or bold statement]

## [Section 1 Title]

[Content...]

<!-- IMAGE: [description for image generation] -->

[More content...]

## [Section 2 Title]

[Content...]

## [Section 3 Title]

[Content...]

---

## Key Takeaways

- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]

---

*[Bridge to next chapter]*
```

### Markdown Formatting Rules (Critical for PDF Generation)

**IMPORTANT**: Follow these rules to ensure proper PDF output with Pandoc/WeasyPrint:

#### 1. Lists Need Blank Lines Before Them

Pandoc requires a blank line before list items. Without it, lists render as inline text.

**WRONG:**
```markdown
Pay attention to:
- Item one
- Item two
```

**CORRECT:**
```markdown
Pay attention to:

- Item one
- Item two
```

This applies to ALL lists, especially those following text ending with `:`.

#### 2. Image Placeholders

Use this format for image placeholders:
```markdown
![Alt Text Description](https://placehold.co/800x400?text=Description+Here)
```

For placehold.co URLs:
- URL-encode special characters (`%20` for space, `%0A` for newline)
- Keep descriptions concise but meaningful
- Standard sizes: `800x400` for diagrams, `600x300` for inline images

When real images exist, use relative paths:
```markdown
![Monaco Editor](../images/01-monaco-screenshot.png)
```

#### 3. Code Blocks

Always specify the language for syntax highlighting:
```markdown
```java
public class Hello {
    // code here
}
```(close)
```

#### 4. Consistent Heading Hierarchy

- `# ` for chapter title only (one per chapter)
- `## ` for main sections
- `### ` for subsections
- Don't skip levels (no `#` to `###` without `##`)

### Step 6: Save Chapter

Save to `chapters/[NN]-[chapter-title-kebab-case].md`

Examples:
- `chapters/00-introduction.md`
- `chapters/01-the-board-game-test.md`
- `chapters/02-defining-your-process.md`

### Step 7: Update Status

Update `.claude/book-creator.local.md`:
- Track completed chapters
- Update word count
- Update `status: writing-in-progress`

### Step 8: Next Steps

Tell the user:
- "Chapter [N] '[Title]' is saved at `chapters/[filename]`"
- "Word count: [X] words"
- "Image placeholders: [Y]"
- "Run `/book-chapter [N+1]` to continue with the next chapter."
- "Run `/book-status` to see overall progress."
