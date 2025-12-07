# LifeOS AI-Assisted Development Workflow

This guide defines the correct method to build LifeOS using GPT-5.1-Codex-Max.

---

# 1. Use Dedicated Chats Per Role
- Architect  
- Backend  
- Frontend  
- ML  
- DB/Migrations  
- QA  
- DevOps  

Each chat uses the corresponding system prompt.

---

# 2. Use Separate Chats Per Module
Example:
- finance/accounts  
- finance/journal  
- finance/money_schedule  
- habits  
- skills  
- health  
- insights  
- assistant  
- events  

Never mix multiple modules in one chat.

---

# 3. Anchor Each Chat with the Architecture Summary

Always begin with:

> “Codex, here is the LifeOS architecture summary.”

Paste `lifeos_architecture.md`.

---

# 4. Use File-By-File Diff Workflow

For each change:

- Paste full file  
- Describe change request  
- Ask for diff  

Apply patch locally.  
Test.

---

# 5. Version Control Everything

Every Codex-generated change should be committed with:

```
git commit -m "Codex: description of change"
```

Never apply multiple Codex outputs without testing.

---

# 6. Regular Architecture Audits

Every few days:

- Ask Architect to review folder structure  
- Ask ML engineer to review ranking signals  
- Ask Backend to refactor slow code  
- Ask DB engineer to optimize schema  
- Ask DevOps to test deployment  

This ensures long-term stability.

---

# 7. Restart Chats When Long

When a chat becomes too long:

1. Ask Codex for a summary of decisions  
2. Add summary to architecture.md  
3. Begin new chat  
4. Paste architecture.md  

---

# 8. Keep Domains Strictly Separate

Finance code never touches Health code.  
Health code never touches Projects code.

Cross-domain insight is handled ONLY in:

`lifeos/intelligence/engine.py`

---

# 9. Use Tests to Lock Stability

Whenever Codex changes a system component:

- Run unit tests  
- Run integration tests  
- Fix migrations if required  

Tests are your anti-regression mechanism.

---

# 10. Never Ask Codex to “Build Everything”
Break features into micro-tasks:

- Add a model  
- Add a route  
- Add a service method  
- Add a template  
- Add a migration  
- Add a test  

Codex performs best with small, defined tasks.

---

# Summary
This workflow ensures you can scale LifeOS with Codex safely, consistently, and at production quality—without context loss, scope bleed, or architectural decay.

