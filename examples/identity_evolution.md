# Example: Identity Evolution

This example demonstrates how the user's persona vector and identity graph evolve over time based on observations.

## Scenario
A user who is primarily a "Software Engineer" starts spending significant time on "Gardening" and "Organic Farming".

## Timeline
- **Week 1-4**: Observations are 90% software development (GitHub, Terminal, VS Code).
- **Week 5**: User joins a local gardening group (Email, RSS).
- **Week 6**: User starts a blog about organic farming (Markdown, GitHub).

## Expected System Behavior
1. **Observation**: Observer detects the gardening and farming activity.
2. **Extraction**: Extractor produces knowledge objects related to "Organic Farming" and "Gardening".
3. **Identity Graph**: New nodes for "Organic Farming" and "Gardening" are created, linked to the user.
4. **Persona Engine**: The user's persona vector begins to shift. The similarity to "Gardening" increases.
5. **Synthesis**: The weekly summary notes: "This week you've significantly expanded your interests into organic farming."
6. **Digital Twin**: User asks "How has my focus changed recently?" and the Twin responds: "You've shifted from a primary focus on software engineering to also dedicating significant time to organic farming and gardening."

## Visual Representation
(Optional: Mermaid diagram of the graph growth)
