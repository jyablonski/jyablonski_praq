# Tiptap Overview

Tiptap is a headless rich text editor framework built on top of ProseMirror which is a framework-agnostic toolkit. It provides a developer-friendly API for building custom text editing experiences in web applications, but no built-in user interface.

## What Problem Does It Solve?

Building rich text editing from scratch is hard. You need to handle:

- Content modeling (paragraphs, headings, lists, etc.)
- Inline formatting (bold, italic, links)
- Cursor management and selections
- Copy/paste behavior
- Undo/redo
- Keyboard shortcuts
- Custom embeds (images, videos, mentions)

Tiptap gives you a foundation for all of this while remaining flexible enough to customize heavily.

## How It Relates to ProseMirror

ProseMirror is the underlying engine - a powerful but low-level toolkit for building editors. It has a steep learning curve and requires you to wire up a lot yourself.

Tiptap wraps ProseMirror with:

- A simpler, more approachable API
- An extension/plugin system for adding features
- Better out-of-the-box defaults
- Framework bindings (React, Vue, vanilla JS)

Think of ProseMirror as the engine and Tiptap as the car built around it.

## Core Concepts

### The Document Model

Tiptap represents content as a tree structure (inherited from ProseMirror). A document contains nodes, and nodes can contain other nodes or text.

```
doc
├── paragraph
│   ├── text "Hello "
│   ├── text "world" (bold mark)
│   └── text "!"
├── heading (level 2)
│   └── text "A Subtitle"
└── paragraph
    └── text "More content here."
```

### Nodes

Nodes are the building blocks of a document. Examples:

- `doc` - the root node
- `paragraph` - a block of text
- `heading` - a heading with a level (1-6)
- `bulletList` / `orderedList` - lists
- `listItem` - an item within a list
- `image` - an embedded image
- `codeBlock` - a block of code

### Marks

Marks are formatting applied to text nodes. Examples:

- `bold`
- `italic`
- `underline`
- `link` (with href attribute)
- `code` (inline code)

A single text node can have multiple marks (e.g., bold AND italic).

### Extensions

Extensions add functionality to the editor. Tiptap is modular - you only include what you need.

```javascript
import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";

const editor = new Editor({
  extensions: [
    StarterKit, // includes common nodes/marks
    Link,
    Image,
  ],
  content: "<p>Initial content</p>",
});
```

## Basic Usage Example

### Setup (React)

```javascript
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";

function MyEditor() {
  const editor = useEditor({
    extensions: [StarterKit],
    content: "<p>Hello world!</p>",
    onUpdate: ({ editor }) => {
      // Called on every change
      const json = editor.getJSON();
      console.log(json);
    },
  });

  return <EditorContent editor={editor} />;
}
```

### Toolbar Commands

```javascript
// Toggle bold on selected text
editor.chain().focus().toggleBold().run();

// Set a heading
editor.chain().focus().toggleHeading({ level: 2 }).run();

// Insert an image
editor.chain().focus().setImage({ src: "https://example.com/image.jpg" }).run();

// Add a link
editor.chain().focus().setLink({ href: "https://example.com" }).run();
```

### Getting Content

```javascript
// As JSON (preferred for storage)
const json = editor.getJSON();

// As HTML
const html = editor.getHTML();

// As plain text
const text = editor.getText();
```

## JSON Document Structure

When you call `editor.getJSON()`, you get a tree structure like this:

```json
{
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": { "level": 1 },
      "content": [{ "type": "text", "text": "Welcome" }]
    },
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "This is " },
        {
          "type": "text",
          "text": "bold and italic",
          "marks": [{ "type": "bold" }, { "type": "italic" }]
        },
        { "type": "text", "text": " text." }
      ]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [{ "type": "text", "text": "First item" }]
            }
          ]
        },
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [{ "type": "text", "text": "Second item" }]
            }
          ]
        }
      ]
    },
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Here is a " },
        {
          "type": "text",
          "text": "link",
          "marks": [
            { "type": "link", "attrs": { "href": "https://example.com" } }
          ]
        },
        { "type": "text", "text": " to somewhere." }
      ]
    }
  ]
}
```

Key observations:

- Every element has a `type`
- Block nodes have a `content` array of children
- Text nodes have a `text` property
- Formatting is stored as `marks` on text nodes
- Attributes (like heading level or link href) go in `attrs`

______________________________________________________________________

# Backend Storage

## Simple Approach: Store the Full JSON

For most use cases, store the entire document JSON in a single column.

### Schema

```sql
create table documents (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    content jsonb not null default '{"type": "doc", "content": []}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    published_at timestamptz,
    created_by uuid references users(id),
    updated_by uuid references users(id)
);

create index idx_documents_created_by on documents(created_by);
create index idx_documents_published_at on documents(published_at);
```

### Saving Content

```javascript
// Frontend: get JSON from editor
const content = editor.getJSON();

// Send to API
await fetch("/api/documents/123", {
  method: "PUT",
  body: JSON.stringify({ content }),
});
```

```python
# Backend (Python/FastAPI example)
@app.put("/api/documents/{doc_id}")
async def update_document(doc_id: UUID, payload: dict):
    await db.execute(
        """
        UPDATE documents
        SET content = :content, updated_at = now()
        WHERE id = :doc_id
        """,
        {"doc_id": doc_id, "content": json.dumps(payload["content"])}
    )
```

### Loading Content

```python
@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: UUID):
    row = await db.fetch_one(
        "SELECT id, title, content FROM documents WHERE id = :doc_id",
        {"doc_id": doc_id}
    )
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],  # already parsed from jsonb
    }
```

```javascript
// Frontend: load into editor
const response = await fetch("/api/documents/123");
const doc = await response.json();

const editor = new Editor({
  content: doc.content, // pass the JSON directly
  extensions: [StarterKit],
});
```

## Revision History

### Option 1: Full Snapshots (Simple)

Store complete copies of the document for each revision.

```sql
create table document_revisions (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references documents(id) on delete cascade,
    content jsonb not null,
    created_at timestamptz not null default now(),
    created_by uuid references users(id)
);

create index idx_revisions_document_id on document_revisions(document_id);
create index idx_revisions_created_at on document_revisions(created_at);
```

```python
# Save a revision before updating
async def save_with_revision(doc_id: UUID, new_content: dict, user_id: UUID):
    # Get current content
    current = await db.fetch_one(
        "SELECT content FROM documents WHERE id = :doc_id",
        {"doc_id": doc_id}
    )

    # Save current as revision
    await db.execute(
        """
        INSERT INTO document_revisions (document_id, content, created_by)
        VALUES (:doc_id, :content, :user_id)
        """,
        {"doc_id": doc_id, "content": json.dumps(current["content"]), "user_id": user_id}
    )

    # Update to new content
    await db.execute(
        """
        UPDATE documents
        SET content = :content, updated_at = now(), updated_by = :user_id
        WHERE id = :doc_id
        """,
        {"doc_id": doc_id, "content": json.dumps(new_content), "user_id": user_id}
    )
```

### Option 2: Delta/Steps Storage (Advanced)

Store ProseMirror steps (operations) instead of full documents. More storage-efficient but more complex.

```sql
create table document_steps (
    id bigserial primary key,
    document_id uuid not null references documents(id) on delete cascade,
    version integer not null,
    steps jsonb not null,  -- array of serialized ProseMirror steps
    created_at timestamptz not null default now(),
    created_by uuid references users(id),

    unique(document_id, version)
);

-- Periodic snapshots for fast reconstruction
create table document_snapshots (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references documents(id) on delete cascade,
    version integer not null,
    content jsonb not null,
    created_at timestamptz not null default now()
);
```

To reconstruct a document at version N:

1. Find the nearest snapshot at version \<= N
1. Replay all steps from that snapshot's version to N

This approach is typically used when you need real-time collaboration or very granular history.

## Querying Document Content

PostgreSQL's jsonb operators let you query inside documents:

```sql
-- Find documents containing a specific text (basic)
select * from documents
where content::text ilike '%search term%';

-- Find documents with a heading containing specific text
select * from documents
where jsonb_path_exists(
    content,
    '$.content[*] ? (@.type == "heading").content[*].text ? (@ like_regex "search" flag "i")'
);

-- Extract all text content for full-text search
create or replace function extract_document_text(content jsonb)
returns text as $$
  select string_agg(value::text, ' ')
  from jsonb_path_query(content, '$..**[*].text');
$$ language sql immutable;

-- Create a generated column or materialized view for search
alter table documents
add column search_text text
generated always as (extract_document_text(content)) stored;

create index idx_documents_search on documents using gin(to_tsvector('english', search_text));
```

## Comparison: DraftJS vs Tiptap Storage

| Aspect | DraftJS | Tiptap/ProseMirror |
| ------------ | ------------------------------------------- | ------------------------------ |
| Structure | Flat array of blocks | Nested tree |
| Formatting | Offset ranges (`offset`, `length`, `style`) | Marks on text nodes |
| Entities | Separate `entityMap` referenced by key | Inline as node attributes |
| Manipulation | Must calculate offsets carefully | Tree traversal, more intuitive |
| Size | Often slightly smaller | More verbose but clearer |

DraftJS example:

```json
{
  "blocks": [
    {
      "key": "abc",
      "text": "Hello bold world",
      "type": "unstyled",
      "inlineStyleRanges": [{ "offset": 6, "length": 4, "style": "BOLD" }]
    }
  ],
  "entityMap": {}
}
```

Tiptap equivalent:

```json
{
  "type": "doc",
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Hello " },
        { "type": "text", "text": "bold", "marks": [{ "type": "bold" }] },
        { "type": "text", "text": " world" }
      ]
    }
  ]
}
```
