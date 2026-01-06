---
name: Non-Fiction Book Writing
description: |
  This skill provides guidance on non-fiction book writing best practices, structure patterns,
  and image placeholder conventions. Use this skill when the user asks about:
  - How to structure non-fiction books
  - Chapter writing techniques
  - Book outline best practices
  - Image placeholder syntax
  - Non-fiction writing tips
version: 1.0.0
---

# Non-Fiction Book Writing

## Book Structure Patterns

### The Problem-Solution Arc
Best for: Business books, self-help, methodology books

```
Part I: The Problem
  - Chapter 1: The pain point (reader recognition)
  - Chapter 2: Why existing solutions fail
  - Chapter 3: The hidden cause

Part II: The Solution
  - Chapter 4: Introduce your framework
  - Chapter 5-7: Deep dive on each element
  - Chapter 8: Implementation guide

Part III: The Transformation
  - Chapter 9: Case studies / success stories
  - Chapter 10: Your action plan
  - Conclusion: The new reality
```

### The Progressive Mastery Arc
Best for: How-to, educational, skill-building books

```
Part I: Foundations
  - Chapter 1: Why this matters
  - Chapter 2-3: Core concepts

Part II: Building Skills
  - Chapter 4-7: Progressive techniques
  - Each chapter builds on previous

Part III: Mastery
  - Chapter 8-9: Advanced applications
  - Chapter 10: Putting it all together
```

### The Thematic Arc
Best for: Essay collections, thought leadership, exploration

```
Introduction: The unifying theme

Chapters 1-10: Independent essays
  - Each explores one facet of theme
  - Can be read in any order
  - Connected by recurring motifs

Conclusion: Synthesis and call to action
```

## Chapter Structure

### The AIDA Chapter Formula

**Attention**: Open with a hook
- Personal story
- Surprising statistic
- Provocative question
- Bold claim

**Interest**: Build context
- Why this matters
- What's at stake
- Common misconceptions

**Desire**: Deliver value
- Core teaching
- Examples and evidence
- Frameworks and tools

**Action**: Close with clarity
- Key takeaways
- Exercises or reflection
- Bridge to next chapter

### Recommended Chapter Length

| Book Type | Words/Chapter | Chapters | Total Words |
|-----------|--------------|----------|-------------|
| Business/Thought Leadership | 3,000-5,000 | 10-12 | 40,000-60,000 |
| How-To/Educational | 2,500-4,000 | 12-15 | 35,000-50,000 |
| Memoir/Narrative | 4,000-6,000 | 15-20 | 60,000-80,000 |
| Quick Read/Gift Book | 1,500-2,500 | 8-10 | 15,000-25,000 |

## Image Placeholder Conventions

### Syntax

```markdown
<!-- IMAGE: [Detailed description for image generation] -->
```

### Best Practices

**Be Specific**:
```markdown
<!-- IMAGE: A circular diagram showing the 4 phases of the Board Game Test:
1) Define Start State (green), 2) Map Rules (blue), 3) Set Win Condition (gold),
4) Handle Edge Cases (red), with arrows connecting each phase in clockwise order -->
```

**Include Style Cues**:
```markdown
<!-- IMAGE: A minimalist illustration of a person at a crossroads,
business professional style, muted earth tones, metaphor for decision-making -->
```

**Specify Chart Types**:
```markdown
<!-- IMAGE: A horizontal bar chart comparing implementation time (weeks)
for Traditional Approach (12 weeks) vs Board Game Test Approach (4 weeks),
clean business style with teal and gray colors -->
```

### Image Types to Include

1. **Conceptual Diagrams**: Visualize frameworks and mental models
2. **Process Flowcharts**: Show step-by-step procedures
3. **Comparison Charts**: Before/after, this vs that
4. **Timeline Graphics**: Show progression or history
5. **Infographics**: Summarize key statistics or lists
6. **Metaphor Illustrations**: Visual representations of abstract concepts

### Placement Guidelines

- **After introducing a concept**: Reinforce with visual
- **Complex processes**: Break down with flowchart
- **Key frameworks**: Make memorable with diagram
- **Chapter summaries**: Infographic of takeaways
- **Aim for 2-4 images per chapter**

## Writing Voice Guidelines

### First Person ("I/We")
**Use when**:
- Sharing personal stories
- Establishing authority through experience
- Creating intimacy with reader
- The author is the brand

**Example**: "When I first discovered this, I was skeptical. But after testing it with 50 clients..."

### Second Person ("You")
**Use when**:
- Giving direct instructions
- Making content feel personal
- Engaging the reader actively

**Example**: "You've probably experienced this: you walk into a meeting thinking you understand the process, only to discover..."

### Third Person ("They/One")
**Use when**:
- Academic or formal tone
- Discussing case studies
- Maintaining objectivity

**Example**: "Organizations that implement this approach typically see..."

## Common Pitfalls to Avoid

1. **Starting with backstory**: Hook first, context after
2. **Too much theory, not enough examples**: Show, don't just tell
3. **Jargon overload**: Define terms, use plain language
4. **Uneven chapter lengths**: Aim for consistency (±20%)
5. **Missing transitions**: Bridge sections and chapters
6. **No clear takeaways**: End every chapter with action items
7. **Image afterthought**: Plan visuals during outlining

## Reference Materials

For additional guidance, see:
- `${CLAUDE_PLUGIN_ROOT}/templates/chapter-template.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/outline-template.md`
