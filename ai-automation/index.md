# AI Automation

## What workflow automation is

**Workflow automation is getting tasks to run by themselves: when something happens, or on a schedule, a series of steps runs across your apps without anyone clicking anything.**

For example: when a customer fills in a form, add them to a spreadsheet, send them a welcome email, and post a message in the team's chat. Each step uses a different app, and an automation tool connects them. **n8n**, the tool this course uses, lets you build these as a diagram of connected boxes, and it can include AI steps, such as having a model sort incoming emails or draft replies.

You could write a small script for each task instead. The trouble starts when you have fifty of them: where are the passwords for twenty services kept, what happened on last Tuesday's run, what retries when a service is down, who gets told when something fails, and can anyone else understand or change it? An automation platform handles all of that around your steps.

## What you'll be able to do

By the end you will be able to:
- decide when a task deserves an automation platform and when a script is enough;
- build workflows in n8n that connect different apps;
- connect to any service's API, and receive messages from services when something happens (webhooks);
- add AI steps safely, without letting a stranger's text take control of your workflow;
- make workflows survive failures, and get alerted when they stop;
- run your own n8n server.

## Where to start

**Before you start:** knowing what an [[backend/02-api-design/01-apis-and-rest|API]] is helps. For note 06 you'll need some [[devops/03-docker/index|Docker]].

Read in order.

1. [[ai-automation/01-what-workflow-automation-is|What Workflow Automation Is]]: triggers and actions, the point where a platform beats scripts, the main tools, and what AI changed.
2. [[ai-automation/02-n8n-core-concepts|n8n Core Concepts]]: boxes (nodes), runs, saved logins, and how data flows between boxes, which confuses almost everyone at first.
3. [[ai-automation/03-connecting-apis-and-webhooks|Connecting APIs and Webhooks]]: logging in to services, fetching data in pages, staying within rate limits, and making sure a repeated message doesn't do something twice.
4. [[ai-automation/04-ai-agent-workflows|AI and Agent Workflows]]: the four ways to use AI in a workflow, from safest to riskiest, getting answers in a fixed format, and protecting against instructions hidden in the text an AI reads.
5. [[ai-automation/05-error-handling-and-retries|Error Handling and Retries]]: sorting failures into kinds, retrying sensibly, and getting alerted when a workflow silently stops running.
6. [[ai-automation/06-self-hosting-n8n|Self-Hosting n8n]]: running n8n on your own server, the one key you must never lose, and when hosting it yourself is the wrong choice.

## Practice

- **Build one real workflow** with the setup from note 06: something you actually want automated.
- **Break it on purpose:** a wrong password, a broken incoming message, an expired login. Watch what happens.
- **Send the same webhook twice** and see whether your workflow does the job twice. Most first workflows do.

## Key ideas to remember

1. **You're paying for everything around each step,** not the step: logins, history, retries, alerts. → [[ai-automation/01-what-workflow-automation-is|01]]
2. **n8n passes a list of items between boxes, and most boxes run once per item.** Almost every beginner confusion comes back to this. → [[ai-automation/02-n8n-core-concepts|02]]
3. **Expect every incoming message to arrive twice,** and make sure that's harmless. → [[ai-automation/03-connecting-apis-and-webhooks|03]]
4. **A "success" reply doesn't mean it worked.** Check what the service actually sent back. → [[ai-automation/03-connecting-apis-and-webhooks|03]]
5. **If you can draw the steps as a flowchart, do that instead of using an AI agent.** Agents are for when you can't. → [[ai-automation/04-ai-agent-workflows|04]]
6. **An AI step will follow instructions from anyone who can get text in front of it.** Give it access to as little as possible. → [[ai-automation/04-ai-agent-workflows|04]]
7. **The most valuable alert is for the workflow that didn't run.** A stopped trigger produces no errors at all. → [[ai-automation/05-error-handling-and-retries|05]]
8. **Back up n8n's encryption key separately.** Lose it and every saved login is gone for good. → [[ai-automation/06-self-hosting-n8n|06]]

## Related

- [[ai-engineering/index|AI Engineer]]: AI agents, structured answers and safety in depth.
- [[using-ai/index|Using AI]]: using AI chatbots well, without code.
- [[devops/06-secret-management/index|Secret Management]]: keeping passwords and keys safe.
- [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|Site Reliability Engineering]]: how to think about alerts, on a bigger scale.

---

## About this course

- **Size:** 6 notes, about 5,500 words, written in August 2026.
- **Where it came from:** written from documentation, not from running n8n. Every claim about running it is read rather than experienced, which matters here because the subject is mostly about running things.
- **Not covered yet:** Zapier, Make and Temporal in depth; n8n's code boxes and building your own boxes; testing workflows; cost at large volumes; and the legal side of sending personal data through other companies' AI models.
