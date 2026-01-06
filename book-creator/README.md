# Book Creator Plugin

A guided workflow for creating non-fiction books from ideation to markdown chapters.

## Features

- **Profile Survey**: Define your audience, writing style, purpose, and positioning
- **Project Initialization**: Create structured book projects with proper organization
- **Outline Generation**: Build comprehensive chapter outlines with sections and key points
- **Chapter Writing**: Interactive or auto-generate modes for drafting chapters
- **Image Placeholders**: Automatic placement of `<!-- IMAGE: prompt -->` markers for illustrations
- **Progress Tracking**: See what's complete and what's next

## Workflow

This plugin enforces a sequential workflow:

1. **`/book-profile`** - Survey for audience, style, purpose, credentials, positioning
2. **`/book-new`** - Initialize book project with title and directory structure
3. **`/book-outline`** - Create or refine the book outline
4. **`/book-chapter [num]`** - Write or refine a specific chapter
5. **`/book-status`** - View progress at any time

## Book Project Structure

```
my-book/
├── .claude/
│   └── book-creator.local.md    # Book metadata from profile
├── outline.md                    # Book outline with chapters/sections
├── chapters/
│   ├── 00-introduction.md
│   ├── 01-chapter-name.md
│   └── ...
└── images/                       # For final images (optional)
```

## Image Placeholders

Chapters include image placeholders in this format:

```markdown
<!-- IMAGE: A flowchart showing the 5-step process for customer onboarding -->
```

These can be sent to image generation tools (fal.ai, DALL-E, Midjourney) when ready.

## Installation

Copy or symlink this plugin to your Claude Code plugins directory:

```bash
# Already installed at ~/.claude/plugins/book-creator
```

## Usage

Start a new book project:

```
/book-profile
```

Follow the guided workflow from there.
