# How Prompts Work - Visual Guide 🎯

## The Simple Answer:

**YOUR FRIEND TYPES HIS OWN PROMPTS!**

The API setup is just the connection. The prompts are 100% controlled by your friend.

---

## Visual Flow:

```
┌─────────────────────────────────────┐
│  YOUR FRIEND'S N8N WORKFLOW         │
│                                     │
│  1. Trigger (email, webhook, etc)  │
│          ↓                          │
│  2. OpenAI Node                     │
│     - API: api.kendall-max.org  ✅  │ ← Setup once
│     - Key: sk-oatisawesome...   ✅  │ ← Setup once
│     - Model: llama3.1:8b        ✅  │ ← Setup once
│     - Prompt: ?????????????????  │ ← HE TYPES THIS!
│          ↓                          │
│  3. AI Response comes back          │
│          ↓                          │
│  4. Use response (email, save, etc) │
└─────────────────────────────────────┘
```

---

## Model Tests - Different Prompts:

### TEST 1: Math Question
**His Prompt:** "What is 25 + 17?"
**AI Response:** "42"
✅ **Worked!**

### TEST 2: Creative Writing
**His Prompt:** "Write a haiku about coffee"
**AI Response:**
```
Rich aroma rises
Lifting fog from weary mind
Morning's warm delight
```
✅ **Worked!**

### TEST 3: Explanation
**His Prompt:** "Explain Docker in one sentence for beginners"
**AI Response:** "Docker is a tool that allows you to package, ship, and run applications in containers, which are lightweight and portable environments that include everything the application needs to run, without worrying about compatibility issues or dependencies."
✅ **Worked!**

---

## Where Does Your Friend Type Prompts?

### In N8N OpenAI Node:

```
┌──────────────────────────────────────┐
│   OpenAI Node Configuration          │
├──────────────────────────────────────┤
│                                      │
│   Credentials: ✅ (already setup)    │
│   Model: llama3.1:8b                 │
│                                      │
│   ┌────────────────────────────────┐ │
│   │ Prompt:                        │ │ ← HE TYPES HERE!
│   │                                │ │
│   │ Summarize this customer email  │ │
│   │ and suggest a response         │ │
│   │                                │ │
│   └────────────────────────────────┘ │
│                                      │
│   [Execute Node]                     │
└──────────────────────────────────────┘
```

---

## Examples of What He Can Ask:

✅ **Customer Service:**
- "Respond to this angry customer professionally"
- "Summarize this support ticket"

✅ **Data Analysis:**
- "Analyze this sales data and give insights"
- "Find patterns in this CSV"

✅ **Content Creation:**
- "Write a blog post about {{topic}}"
- "Create social media captions"

✅ **Automation:**
- "Extract key information from this document"
- "Classify this email as urgent/normal/spam"

✅ **Translation:**
- "Translate this to Spanish"

✅ **Coding:**
- "Write a Python function to calculate..."

---

## Key Point:

**The API is like a phone connection:**
- ☎️ Phone number = `api.kendall-max.org`
- 🔑 Password = `sk-oatisawesome-2024-ml-api`
- 💬 What he says = **HIS PROMPT** (whatever he wants!)

**He controls the conversation. The API just connects him to the AI.**

---

## No Limits:

✅ Unlimited prompts per day
✅ 32,768 tokens per prompt (8x ChatGPT)
✅ Any language
✅ Any topic
✅ Any format (questions, instructions, data)

**Your friend has COMPLETE freedom!**
