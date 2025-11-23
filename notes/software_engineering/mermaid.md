# Mermaid

Mermaid is a JavaScript based diagramming and charting tool that renders Markdown text into visual diagrams such as flow charts, gantt charts, DAGs, and other visualizations.

You need the `Markdown Preview Mermaid Support` Extension in VS Code in order to preview the diagrams being created.

### Flowchart

```mermaid

graph LR
  A[Start] --> B{Is it working?}
  B -->|Yes| C[Continue]
  B -->|No| D[Fix it]
  D --> B
```

### Sequence

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello, Bob!
    B->>A: Hi, Alice!
    A->>B: How are you?
    B->>A: I’m good, thanks!
```

### Class

```mermaid
classDiagram
    Animal <|-- Dog
    Animal <|-- Cat
    Animal: +String name
    Animal: +int age
    Dog: +String breed
    Dog: +bark()
    Cat: +String color
    Cat: +meow()
```

### State

```mermaid
stateDiagram-v2
    [*] --> Start
    Start --> Running
    Running --> Paused
    Paused --> Running
    Running --> [*]
```

### Gantt

```mermaid
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Section 1
    Task 1        :done,    des1, 2025-01-01, 2025-01-07
    Task 2        :active,  des2, 2025-01-08, 2025-01-14
    section Section 2
    Task 3        :         des3, after des2, 5d
    Task 4        :         des4, after des3, 10d

```

### Pie Chart

```mermaid
pie
    title Pets
    "Cats" : 50
    "Dogs" : 30
    "Birds" : 20
```

### ERD

```mermaid
erDiagram
    CUSTOMER {
        string name
        string email
    }
    ORDER {
        int order_id
        string product
        float price
    }
    CUSTOMER ||--o| ORDER : places
```

### User Journey

```mermaid
journey
    title User Journey
    section Login Process
      User logs in: 5: Logged In
    section Browsing
      User views products: 3: Browsing
      User adds product to cart: 4: Added to Cart
    section Checkout
      User enters payment info: 5: Payment Entered
      User completes purchase: 5: Purchase Complete
```

### Mind Map

```mermaid
mindmap
    root
        subgraph A
            direction TB
            Idea 1
            Idea 2
        end
        subgraph B
            direction LR
            Idea 3
            Idea 4
        end
```
