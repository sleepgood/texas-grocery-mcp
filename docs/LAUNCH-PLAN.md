# 🚀 Texas Grocery MCP Launch Plan

> Launch checklist and promotional content for public release

---

## 📅 Pre-Launch Checklist

- [ ] Make GitHub repository public
- [ ] Create GitHub release tag (v0.1.1)
- [ ] Verify PyPI package works: `pip install texas-grocery-mcp`
- [ ] Test installation on clean environment
- [ ] Prepare demo GIF or video (optional but recommended)

---

## 📣 Launch Channels

### 1. 🦀 Moltbook

**Priority:** High - MCP-focused community

**Post Title:**
```
🛒 Texas Grocery MCP - Let Claude do your HEB grocery shopping!
```

**Post Content:**
```
Just released my first MCP server that connects Claude to H-E-B grocery stores!

✨ What it does:
- 🔍 Search products with real-time pricing
- 🛒 Add items to your cart (with confirmation)
- 🎟️ Find and clip digital coupons
- 📋 Get ingredient lists, nutrition facts, allergens
- 🔄 Automatic session refresh (~15 seconds)

It's like having a personal shopping assistant that knows every product at HEB.

📦 Install: `pip install texas-grocery-mcp[browser]`
🔗 GitHub: https://github.com/mgwalkerjr95/texas-grocery-mcp
📖 PyPI: https://pypi.org/project/texas-grocery-mcp/

Built with FastMCP + Playwright for handling HEB's bot detection. Human-in-the-loop confirmation for cart operations so Claude won't accidentally buy 100 gallons of milk 😅

Would love feedback from fellow MCP builders! 🤠
```

**Submolts to post in:** (check which are relevant)
- MCP development
- AI agents
- Show & Tell

---

### 2. 🤖 Reddit - r/ClaudeAI

**Priority:** High - Active Claude user community

**Post Title:**
```
I built an MCP that lets Claude do my grocery shopping at HEB
```

**Post Content:**
```
Hey everyone! I've been working on an MCP server that connects Claude to H-E-B grocery stores (Texas grocery chain).

**What Claude can do now:**
- Search for any product with real-time prices
- Add items to my actual HEB cart
- Find and clip digital coupons
- Look up ingredients, nutrition facts, allergens
- Handle the annoying bot detection automatically

**Example conversation:**
> Me: "Add eggs, milk, and bread to my cart"
> Claude: *searches for each item, shows me options with prices, asks for confirmation, then adds to cart*

The coolest part is the human-in-the-loop confirmation - Claude always asks before modifying your cart, so no surprise purchases!

**Links:**
- GitHub: https://github.com/mgwalkerjr95/texas-grocery-mcp
- Install: `pip install texas-grocery-mcp[browser]`

It's MIT licensed and I'd love feedback from the community. Anyone else building grocery/shopping MCPs?

*Note: Not affiliated with H-E-B, just a Texan who wanted to automate grocery shopping* 🤠
```

---

### 3. 📰 Reddit - r/LocalLLaMA

**Priority:** Medium - AI tooling enthusiasts

**Post Title:**
```
Open source MCP server for grocery shopping automation (HEB stores)
```

**Post Content:**
```
Released an MCP server that enables AI agents to interact with H-E-B grocery stores.

**Technical highlights:**
- Built with FastMCP 2.0
- Playwright integration for handling bot detection (reese84 tokens)
- ~15 second session refresh vs 4 min manual
- Human-in-the-loop confirmation for cart mutations
- Secure credential storage via system keyring
- 296 unit tests, full type hints

**Tools provided:**
- Product search with pricing/availability
- Cart management (add/remove with confirmation)
- Digital coupon clipping
- Product details (ingredients, nutrition, allergens)
- Store locator

GitHub: https://github.com/mgwalkerjr95/texas-grocery-mcp
PyPI: `pip install texas-grocery-mcp[browser]`

Works with Claude Desktop and any MCP-compatible client. MIT licensed.

Interested in feedback on the architecture - especially the session management approach for handling aggressive bot detection.
```

---

### 4. 🧡 Hacker News - Show HN

**Priority:** Medium - Developer community

**Post Title:**
```
Show HN: Texas Grocery MCP – Let AI agents shop at HEB grocery stores
```

**Post Content:**
```
I built an MCP (Model Context Protocol) server that connects AI agents like Claude to H-E-B grocery stores.

Features:
- Product search with real-time pricing
- Cart management with human confirmation
- Digital coupon discovery and clipping
- Nutrition/ingredient lookups
- Automatic session refresh handling bot detection

The interesting technical challenge was handling HEB's bot detection (reese84 tokens that expire every ~11 minutes). Solved it with embedded Playwright that refreshes sessions in ~15 seconds.

GitHub: https://github.com/mgwalkerjr95/texas-grocery-mcp

Install: pip install texas-grocery-mcp[browser]

MIT licensed. Not affiliated with H-E-B.
```

**Best posting time:** Tuesday-Thursday, 9-10 AM EST

---

### 5. 🐦 Twitter/X

**Priority:** Medium

**Tweet:**
```
🛒 Just released Texas Grocery MCP!

Let Claude do your grocery shopping at @HEB:
✅ Search products with live prices
✅ Add to cart (with confirmation)
✅ Clip digital coupons
✅ Get nutrition & ingredients

pip install texas-grocery-mcp

GitHub: github.com/mgwalkerjr95/texas-grocery-mcp

#MCP #ClaudeAI #AI
```

**Tags:** @AnthropicAI (optional)

---

### 6. 📋 MCP Servers Registry

**Priority:** High - Official discovery channel

**Action:** Submit PR to https://github.com/modelcontextprotocol/servers

**Entry to add:**
```markdown
### Texas Grocery MCP
- **Repository:** https://github.com/mgwalkerjr95/texas-grocery-mcp
- **PyPI:** texas-grocery-mcp
- **Description:** Connect AI agents to H-E-B grocery stores for product search, cart management, and coupon clipping
- **Features:** Product search, cart add/remove, digital coupons, nutrition info, session management
```

---

## 🎬 Demo Content Ideas

### Quick GIF (30 seconds)
1. Show Claude Desktop with the MCP loaded
2. Ask: "Search for organic milk at HEB"
3. Show results with prices
4. Ask: "Add the first one to my cart"
5. Show confirmation flow

### Full Demo Video (2-3 minutes)
1. Introduction - what is Texas Grocery MCP
2. Installation walkthrough
3. Live demo:
   - Store search
   - Product search
   - Adding to cart
   - Clipping a coupon
4. Show the confirmation safety feature
5. Call to action - GitHub link

---

## 📊 Launch Day Schedule

| Time | Action |
|------|--------|
| Morning | Make GitHub repo public |
| Morning | Create GitHub release v0.1.1 |
| Morning | Post to Moltbook |
| Mid-day | Post to r/ClaudeAI |
| Afternoon | Post to r/LocalLLaMA |
| Next day | Submit to MCP Servers Registry |
| Next day | Hacker News (if momentum) |

---

## 📈 Success Metrics

- [ ] GitHub stars: Target 50+ first week
- [ ] PyPI downloads: Track via pypistats
- [ ] GitHub issues/feedback received
- [ ] Moltbook engagement
- [ ] Reddit upvotes/comments

---

## 🔗 Quick Links

- **GitHub:** https://github.com/mgwalkerjr95/texas-grocery-mcp
- **PyPI:** https://pypi.org/project/texas-grocery-mcp/
- **Install:** `pip install texas-grocery-mcp[browser]`

---

*Last updated: 2026-02-02*
