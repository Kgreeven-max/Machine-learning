# Complete N8N Setup Guide for Kendall's AI API

## What This Guide Does
This guide will walk you through setting up Kendall's AI API in N8N from start to finish. After this, you'll be able to use AI in your workflows to automate tasks.

---

## ⚙️ Prerequisites
- You have N8N installed and running
- You can access your N8N dashboard (usually at http://localhost:5678)
- Kendall's API is running (you'll know it works when the test at the end succeeds)

---

## 📋 Information You Need (Copy These Values)

**Save these somewhere - you'll need them:**

| What | Value |
|------|-------|
| API Key | `sk-oatisawesome-2024-ml-api` |
| API Base URL | `https://api.kendall-max.org/v1` |
| Model Name | `llama3.1:8b` |

---

## 🚀 Part 1: Setting Up Your First AI Workflow

### Step 1: Create a New Workflow

1. Open your N8N dashboard
2. Click the **"+ New Workflow"** button (usually top right)
3. You'll see an empty canvas with a "Start" node

**✅ You should now have a blank workflow**

---

### Step 2: Add an OpenAI Node

1. Click the **"+"** button on the canvas (or click the plus icon next to the Start node)
2. A search panel will appear
3. Type: `OpenAI`
4. Click on **"OpenAI"** in the results (it has the OpenAI logo)
5. The OpenAI node will appear on your canvas

**✅ You should now see an OpenAI node connected to your Start node**

---

### Step 3: Configure API Credentials (MOST IMPORTANT STEP)

This tells N8N to use Kendall's AI instead of OpenAI's servers.

1. **Click on the OpenAI node** you just added
2. A settings panel will open on the right side
3. Look for **"Credential to connect with"** (near the top)
4. Click the dropdown next to it
5. Select **"Create New Credential"**

A credential form will appear. Fill it out **EXACTLY** like this:

#### Field 1: API Key
- **Copy and paste this exactly:** `sk-oatisawesome-2024-ml-api`
- ⚠️ **Do NOT type it manually** - copy/paste to avoid typos
- Make sure there are NO spaces before or after

#### Field 2: Base URL (Advanced Settings)
- You might need to click **"Show Advanced Options"** or scroll down
- Look for **"Base URL"** field
- **Copy and paste this exactly:** `https://api.kendall-max.org/v1`
- ⚠️ **Important:** Must include `/v1` at the end
- ⚠️ **Important:** Must start with `https://`

#### Field 3: Name Your Credential (Optional but Helpful)
- At the top, there's a "Credential Name" field
- Type: `Kendall's AI` (or whatever you want to call it)
- This helps you find it later

6. Click the **"Save"** button at the bottom
7. Click **"Back to Node"** to return to the OpenAI node

**✅ Your credential is now saved! You only do this ONCE - you can reuse it in all workflows**

---

### Step 4: Select the Model

Now that credentials are set up, you need to tell it which AI model to use.

1. You should still be in the OpenAI node settings
2. Look for the **"Model"** dropdown field
3. Click it and type: `llama3.1:8b`
4. Press Enter or select it if it appears in the list

**✅ Model is configured**

---

### Step 5: Choose the Operation

1. Look for **"Resource"** dropdown
2. Select: **"Message"** (or "Chat" depending on your N8N version)
3. Look for **"Operation"** dropdown
4. Select: **"Create"** or **"Send Message"**

**✅ Operation is set**

---

### Step 6: Write Your First Prompt

This is where YOU control what the AI does!

1. Look for a large text field labeled **"Prompt"** or **"Text"** or **"Message"**
2. Click in it
3. Type your first test prompt:

```
Hello! Please introduce yourself and tell me what you can help with.
```

**✅ Your prompt is ready**

---

### Step 7: Test It!

1. Click the **"Execute Node"** button (usually top right of the node panel)
2. Wait a few seconds
3. Look at the **output panel** (usually appears below or on the right)

**What you should see:**
- A green checkmark on the node (success!)
- Output data showing the AI's response
- The response should be a friendly introduction

**✅ If you see a response, IT WORKS! You're done with basic setup!**

---

## 🎯 Part 2: Using AI in Real Workflows

Now that you know it works, here's how to use it for real tasks.

### Example 1: Email Summarizer

**What it does:** Takes an email and summarizes it in one sentence

**Setup:**
1. Add a trigger (like "Manual Trigger" for testing)
2. Add an "Edit Fields" node (optional, to create test data)
3. Add your OpenAI node (use the credential you already created)
4. In the OpenAI node prompt field, type:

```
Summarize this email in one sentence:

{{$json.emailBody}}
```

5. Execute and test!

**How it works:**
- `{{$json.emailBody}}` pulls data from the previous node
- Replace "emailBody" with whatever field name you have
- The AI reads the email and returns a one-sentence summary

---

### Example 2: Customer Service Response Generator

**What it does:** Writes professional responses to customer messages

**Prompt:**
```
Write a professional, friendly response to this customer message:

{{$json.customerMessage}}

Keep the response under 100 words and be empathetic.
```

---

### Example 3: Data Classifier

**What it does:** Categorizes support tickets automatically

**Prompt:**
```
Classify this support ticket as either: BUG, FEATURE_REQUEST, or QUESTION

Ticket: {{$json.ticketText}}

Respond with only one word - the category.
```

---

### Example 4: Language Translator

**What it does:** Translates text to any language

**Prompt:**
```
Translate the following text to Spanish:

{{$json.textToTranslate}}
```

---

### Example 5: Content Generator

**What it does:** Generates blog posts, social media content, etc.

**Prompt:**
```
Write a professional LinkedIn post about {{$json.topic}}

Requirements:
- 150-200 words
- Include 3 relevant hashtags
- Professional but friendly tone
```

---

## 💡 Understanding Prompts

**The prompt is YOUR instruction to the AI. You control everything!**

### Basic Prompt Rules:
1. **Be specific** - The more detail, the better the result
2. **Use examples** - Show the AI what you want
3. **Set constraints** - Word limits, format requirements, tone, etc.
4. **Use N8N variables** - Pull in data with `{{$json.fieldName}}`

### Prompt Template:
```
[Task description]

[Data to process]: {{$json.data}}

[Requirements/constraints]
- Requirement 1
- Requirement 2

[Output format instructions]
```

---

## 🔧 Part 3: Advanced Setup Options

### Using Multiple AI Nodes in One Workflow

You can use the same credential in multiple nodes:

1. Add another OpenAI node
2. In "Credential to connect with", select "Kendall's AI" (the one you created earlier)
3. Use a different prompt for a different task

**Example workflow:**
```
Start → Get Email → AI Node 1 (Summarize) → AI Node 2 (Generate Response) → Send Email
```

---

### Using Variables from Previous Nodes

**To use data from previous steps:**

1. In the prompt field, type `{{`
2. N8N will show you available variables
3. Select the one you need, like `{{$json.email}}`

**Common variables:**
- `{{$json.fieldName}}` - Data from previous node
- `{{$node["NodeName"].json.fieldName}}` - Data from specific node
- `{{$input.all()}}` - All input data

---

### HTTP Request Method (Alternative Setup)

**Only use this if the OpenAI node doesn't work!**

1. Add "HTTP Request" node
2. Configure:
   - **Method:** `POST`
   - **URL:** `https://api.kendall-max.org/v1/chat/completions`
3. Click "Add Header"
   - **Name:** `Authorization`
   - **Value:** `Bearer sk-oatisawesome-2024-ml-api`
4. Set **Body Content Type** to `JSON`
5. In **Body**, paste:

```json
{
  "model": "llama3.1:8b",
  "messages": [
    {
      "role": "user",
      "content": "YOUR PROMPT HERE"
    }
  ]
}
```

6. Replace `YOUR PROMPT HERE` with your actual prompt

**To get the response:**
- The AI's answer is in: `{{$json.choices[0].message.content}}`

---

## ❓ Troubleshooting

### Error: "Invalid API Key"

**Fix:**
1. Go back to your credential
2. Delete the API key
3. Copy this again: `sk-oatisawesome-2024-ml-api`
4. Paste it (don't type it)
5. Make sure there are no spaces
6. Save

### Error: "Could not connect to API"

**Fix:**
1. Check the Base URL has `/v1` at the end
2. Should be: `https://api.kendall-max.org/v1`
3. Ask Kendall if the server is running

### Error: "Model not found"

**Fix:**
1. Check model name is exactly: `llama3.1:8b`
2. Must be lowercase
3. Must have the colon and "8b"

### No Response / Timeout

**Fix:**
1. Make sure you clicked "Execute Node"
2. Wait 10-15 seconds (AI takes time to think)
3. Check if Kendall's server is running
4. Try a shorter prompt first

### Response is Weird/Wrong

**Fix:**
1. Make your prompt more specific
2. Add examples of what you want
3. Set clear requirements
4. Test with simpler prompts first

---

## 🧪 Testing the API (Outside N8N)

Want to verify the API works before using N8N?

### Test from Terminal/Command Line:

**Mac/Linux:**
```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Say hello and tell me what you can do"}]
  }'
```

**Windows (PowerShell):**
```powershell
$headers = @{
    "Authorization" = "Bearer sk-oatisawesome-2024-ml-api"
    "Content-Type" = "application/json"
}
$body = @{
    model = "llama3.1:8b"
    messages = @(
        @{
            role = "user"
            content = "Say hello and tell me what you can do"
        }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.kendall-max.org/v1/chat/completions" -Method Post -Headers $headers -Body $body
```

**What you should see:**
- A JSON response
- Look for `"content": "..."` with the AI's hello message
- If you see this, the API works!

---

## 📊 API Capabilities & Limits

**What you get:**
- ✅ **Unlimited requests** - Use it as much as you want
- ✅ **32,768 tokens per request** - Very long conversations (8x bigger than ChatGPT)
- ✅ **Fast responses** - 96-100 words per second
- ✅ **No rate limits** - No waiting between requests
- ✅ **Multiple languages** - Works in any language
- ✅ **Context memory** - Can reference previous messages in a conversation

**What is a token?**
- Roughly 1 token = 4 characters
- "Hello" = 1 token
- Average word = 1.3 tokens
- 32,768 tokens ≈ 24,000 words (about 50 pages!)

---

## 🎯 Real-World Workflow Examples

### Workflow 1: Automatic Email Categorization
```
Gmail Trigger → OpenAI (Categorize) → Switch Node → Different Actions per Category
```

**OpenAI Prompt:**
```
Categorize this email as: URGENT, NORMAL, or SPAM

Email subject: {{$json.subject}}
Email body: {{$json.body}}

Respond with only one word.
```

---

### Workflow 2: Social Media Content Pipeline
```
Google Sheets (Topic List) → OpenAI (Generate Post) → OpenAI (Generate Image Prompt) → Save to Database
```

**OpenAI Prompt 1:**
```
Write an engaging LinkedIn post about: {{$json.topic}}

Requirements:
- 150 words
- Professional tone
- Include question at the end
- 3 relevant hashtags
```

**OpenAI Prompt 2:**
```
Create an image prompt for DALL-E based on this LinkedIn post:

{{$json.post}}

The image should be professional and relevant.
```

---

### Workflow 3: Customer Support Automation
```
Zendesk Trigger → OpenAI (Analyze Sentiment) → OpenAI (Draft Response) → Send to Slack for Approval
```

**OpenAI Prompt 1:**
```
Analyze the sentiment of this support ticket. Rate from 1-10:
- 1-3: Angry
- 4-7: Neutral
- 8-10: Happy

Ticket: {{$json.ticketText}}

Respond with just the number.
```

**OpenAI Prompt 2:**
```
Write a customer support response to this ticket:

{{$json.ticketText}}

Sentiment score: {{$json.sentiment}}

Be {{sentiment < 4 ? "extra empathetic and apologetic" : "friendly and helpful"}}
Offer a concrete solution.
Under 150 words.
```

---

## 🔐 Security Notes

1. **Keep your API key private** - Don't share it publicly
2. **The key in this doc is for you only** - Kendall created it specifically for your use
3. **If the API key stops working** - Contact Kendall for a new one
4. **Data privacy** - Your prompts and data go to Kendall's server, not OpenAI
5. **Local processing** - The AI runs on Kendall's computer, not in the cloud

---

## 💪 Pro Tips

### Tip 1: Reuse Credentials
- Create the credential once
- Use it in ALL your workflows
- No need to create new credentials each time

### Tip 2: Test Prompts Separately First
- Before building a complex workflow
- Test your prompts in a simple workflow with manual trigger
- Once the prompt works, integrate it

### Tip 3: Use System Messages for Consistency
Some N8N OpenAI nodes support "system messages":
- System message: "You are a helpful customer service agent. Always be professional and empathetic."
- User message: "{{$json.customerQuestion}}"

### Tip 4: Handle Long Responses
If responses are cut off:
- Add to your prompt: "Keep your response under 500 words"
- Or increase token limit if the option is available

### Tip 5: Chain Multiple AI Calls
For complex tasks:
1. First AI node: Extract key information
2. Second AI node: Process that information
3. Third AI node: Format the final output

### Tip 6: Save Responses to Database
- Add a database node after OpenAI
- Store questions and answers
- Build a knowledge base over time

---

## 📚 Prompt Engineering Quick Reference

### Structure of a Good Prompt:
```
[Role/Context]
You are a professional email writer.

[Task]
Write a follow-up email to this client:

[Data]
{{$json.clientMessage}}

[Constraints]
- Keep it under 150 words
- Be friendly but professional
- Include a call to action

[Output Format]
Format as plain text, ready to send.
```

### Useful Prompt Patterns:

**For Summaries:**
```
Summarize the following in [X] sentences: [content]
```

**For Decisions:**
```
Based on this information: [data]
Should I [action A] or [action B]?
Respond with just "A" or "B" and a brief reason.
```

**For Extraction:**
```
Extract the following information from this text:
- Email address
- Phone number
- Company name

Text: {{$json.text}}

Format as JSON.
```

**For Creative Tasks:**
```
Generate [number] [type of content] about [topic]
Style: [style description]
Tone: [tone description]
```

---

## ✅ Setup Checklist

Before you start building workflows, make sure:

- [ ] N8N is running and accessible
- [ ] You created the OpenAI credential with correct API key
- [ ] You added the correct Base URL with `/v1`
- [ ] You tested with a simple prompt and got a response
- [ ] You know where to find the credential (for reuse)
- [ ] You understand how to write prompts
- [ ] You know how to use `{{$json.fieldName}}` for data

---

## 🆘 Getting Help

**If you're stuck:**

1. **Check this guide** - Read the troubleshooting section
2. **Test the API directly** - Use the terminal test to verify API works
3. **Simplify your workflow** - Remove nodes until it works, then add back
4. **Check N8N logs** - Look for error messages in the execution log
5. **Contact Kendall** - He can check if the server is running

**Common mistakes to avoid:**
- ❌ Forgetting `/v1` in the URL
- ❌ Typos in the API key (always copy/paste!)
- ❌ Wrong model name (must be exactly `llama3.1:8b`)
- ❌ Not clicking "Save" after creating credential
- ❌ Not clicking "Execute Node" to test

---

## 🎉 You're Ready!

You now know how to:
- ✅ Set up Kendall's AI API in N8N
- ✅ Create AI-powered workflows
- ✅ Write effective prompts
- ✅ Use variables from previous nodes
- ✅ Troubleshoot common issues
- ✅ Build real-world automations

**Remember:** The AI is a tool that follows YOUR instructions. The better your prompts, the better your results!

**Start simple, then get creative!**

---

## 📞 Quick Reference Card

**Copy these for quick access:**

```
API KEY: sk-oatisawesome-2024-ml-api
BASE URL: https://api.kendall-max.org/v1
MODEL: llama3.1:8b

RESPONSE PATH (if using HTTP node):
{{$json.choices[0].message.content}}
```

**Test Command (Terminal):**
```bash
curl -X POST https://api.kendall-max.org/v1/chat/completions \
  -H "Authorization: Bearer sk-oatisawesome-2024-ml-api" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "messages": [{"role": "user", "content": "test"}]}'
```

---

**Last Updated:** October 2024
**API Version:** v1
**Model:** Llama 3.1 8B
**Server:** Kendall's M4 Max MacBook Pro
