# AI & ML

## What AI and machine learning are

**Machine learning is getting a computer to learn a task from examples instead of following rules a programmer wrote by hand. AI (artificial intelligence) is the wider goal: computers doing things that used to need human intelligence.**

To spot spam the old way, a programmer would write rules: "if the email says 'you've won', it's spam". Spammers soon learn to dodge the rules. With machine learning, you show the computer thousands of emails already labelled "spam" or "not spam", and it works out the patterns itself. The result of that learning is called a **model**: a program that takes new input (a new email) and makes a prediction (spam or not).

Chatbots like ChatGPT and Claude are built on a kind of model called a **large language model (LLM)**, trained on huge amounts of text until it can write, answer questions and follow instructions.

## Which path is for you?

"AI/ML" covers three different jobs. They share some basics but need different skills, so this course is split the same way.

| Path | The question it answers | What you produce | Do you train models? |
|---|---|---|---|
| [[ai-ml/01-data-scientist/index\|Data Scientist]] | "What does the data tell us?" | an answer or insight, often a report | sometimes, mostly simpler models |
| [[ai-ml/02-ml-engineer/index\|ML Engineer]] | "How do we build a model and run it reliably in a real product?" | a trained model running as software | **yes** |
| [[ai-ml/03-ai-engineer/index\|AI Engineer]] | "How do we build a product on top of models others have trained?" | an app that uses models like Claude or GPT | **no**, you use existing ones |

The biggest difference is between the last two. An ML engineer trains models, which needs a lot of maths. An AI engineer uses ready-made models through an API and needs much less maths but more software skill. Many real jobs mix two of these.

**Not a programmer, and just want to use AI tools well?** Start with [[using-ai/index|Using AI]], an eight-note course on using chatbots well, with no code.

## What you'll be able to do

Depending on the path you take, you'll be able to:
- explain what a model is, how it learns, and how to tell whether it's any good;
- analyse data, run fair experiments, and avoid misleading conclusions (data scientist);
- train models, including neural networks for images and text, and run them in production (ML engineer);
- build apps with LLMs: prompting, giving a model your own documents to answer from, letting it use tools, and testing its output (AI engineer).

## Where to start

1. **Everyone:** [[ai-ml/00-foundations/index|Foundations]]: what AI and a model are, the maths (needed mostly for the data scientist and ML engineer paths), and Python's data tools.
2. **Then pick a path:**
   - [[ai-ml/01-data-scientist/index|Data Scientist]]: 7 notes on statistics, exploring data, charts, experiments and A/B tests, and telling cause from coincidence.
   - [[ai-ml/02-ml-engineer/index|ML Engineer]]: 10 sections, from how machine learning works and preparing data, through classic methods and testing models, to deep learning, images, text, fine-tuning and running models in production (MLOps).
   - [[ai-ml/03-ai-engineer/index|AI Engineer]]: about 20 notes on building with LLMs: how they work, calling them from code, writing prompts, giving them your documents (RAG), tools and agents, testing their answers, cost and speed, and running models on your own machine. It ends with practice exercises.

## Practice

- [[ai-ml/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- [[ai-ml/interview/index|AI and ML interview prep]]: AI engineering, and machine learning and statistics basics.

## Key ideas to remember

1. **A model learns patterns from examples,** so it's only as good as its examples. Biased or messy data gives a biased or messy model.
2. **Always test a model on data it didn't learn from.** Doing well on its own training examples proves nothing.
3. **An LLM predicts likely text; it doesn't look facts up.** That's why it can sound confident and be wrong, and why you check its output.
4. **For most products, use an existing model before training your own.** Training is expensive and rarely needed.

## Related

- [[using-ai/index|Using AI]]: using AI tools well, without code.
- [[ai-automation/index|AI Automation]]: connecting AI to everyday tools with little or no code.
- [[data-engineering/index|Data Engineering]]: the pipelines that collect and clean the data models learn from.
- [[data-analysis/index|Data Analysis]]: working with data before any machine learning.
- [[mathematics/index|Mathematics]]: the maths behind machine learning.

---

## About this course

- **How it's organised:** restructured on 31 July 2026 into the three paths, following roadmap.sh's separate data scientist, machine learning, MLOps and AI engineer roadmaps. Nothing from the earlier single course was dropped; each note moved to the path it belonged to.
- **Where it came from:** the AI engineer path is the most developed, and matches real work in other projects here (the AI SDK, MCP tools and agents). The others were written from reference sources.
