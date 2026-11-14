# Frontend

## What a frontend is

**The frontend is the part of an app you see and touch: the screens, buttons, text and pictures, and everything that happens when you click or type.**

On a website, the frontend is what your browser shows you. It's built from three languages that every browser understands:
- **HTML** describes what's on the page: a heading, a paragraph, a button, an image.
- **CSS** describes how it looks: colours, sizes, fonts, layout.
- **JavaScript** makes it respond: what happens when you click, type or scroll, and fetching new information without reloading the page.

The frontend talks to a [[backend/index|backend]] for anything it can't do alone, such as logging you in or saving your order.

Frontend work is harder than it looks because your code runs on someone else's device: a cheap phone or a fast laptop, on a strong connection or a weak one, for a user who may be in a hurry, using a screen reader, or on a tiny screen. Most of this course is about making apps that work well for all of them.

This course teaches the ideas that are true whichever tool you use. The [[frontend/frameworks/index|frameworks]] section then shows how to do them in React, Next.js and others.

## What you'll be able to do

By the end you will be able to:
- explain how a browser turns code into the page you see;
- break a page into reusable pieces called **components**;
- manage the information a page keeps track of, and fetch data from a backend without bugs;
- organise CSS so styles don't fight each other;
- build pages that people using screen readers or keyboards can use;
- choose whether a page should be built in the browser or on a server, and why it matters;
- measure and improve how fast a page feels, and test it automatically.

## Where to start

**Never built a web page?** Start with note 0, which builds a small working page with HTML, CSS and JavaScript from scratch. Basic programming ([[programming-fundamentals/index|Programming Fundamentals]]) helps for the JavaScript.

Read in the order below; the section numbers follow it.

### The browser

0. [[frontend/01-foundations/00-your-first-web-page|Your First Web Page]]: build a small menu page with a working order total, using HTML, CSS and JavaScript, and look inside it with the browser's developer tools.
1. [[frontend/01-foundations/01-what-a-frontend-is|What a Frontend Actually Is]]: a frontend's four jobs, and why the browser itself lasts longer than any framework.
2. [[frontend/01-foundations/02-the-browser-and-the-dom|The Browser and the DOM]]: how a browser goes from a web address to pixels on screen, and the page structure your code changes (the DOM).

### Building pages from pieces

3. [[frontend/02-structuring-a-frontend/01-components-and-composition|Components and Composition]]: splitting a page into reusable pieces, and the trap of passing data down through too many layers.

### Keeping track of information (the heart of the course)

4. [[frontend/03-state-and-data/01-state-management|State Management]]: the information a page remembers while you use it, such as what's in your cart, and where to keep it.
5. [[frontend/03-state-and-data/02-data-fetching-and-server-state|Data Fetching and Server State]]: getting data from a backend, and the timing bug almost every hand-written version has.
6. [[frontend/03-state-and-data/03-content-modeling-and-headless-cms|Content Modelling and the Headless CMS]]: designing content that non-programmers edit, like blog posts and product pages.

### Making it look right

7. [[frontend/04-styling/01-css-architecture|CSS Architecture]]: why CSS gets messy as a site grows, and the ways teams keep it under control.

### Making it work for everyone

8. [[frontend/05-cross-cutting/01-accessibility|Accessibility]]: making pages usable by people with disabilities. It's a requirement, often a legal one, not an extra.

### Where the page gets built

9. [[frontend/06-rendering/01-rendering-strategies|Rendering Strategies]]: building the page in the browser, on a server for each visit, or once ahead of time, and when to use each.
10. [[frontend/06-rendering/02-hydration-and-the-server-boundary|Hydration and the Server Boundary]]: the moment a server-built page "wakes up" in the browser, and the bugs that live in that gap.

### Practices

11. [[frontend/07-practices/01-frontend-best-practices|Frontend Best Practices]]: habits that keep a frontend healthy.
12. [[frontend/07-practices/02-performance|Performance]]: measuring how fast a page feels to real users, and keeping it fast.
13. [[frontend/07-practices/03-testing-a-frontend|Testing a Frontend]]: checking your components work, automatically.
14. [[frontend/07-practices/04-end-to-end-with-playwright|End-to-End with Playwright]]: testing whole user journeys in a real browser, like signing up and checking out.

## Frameworks: the same ideas with real tools

- [[frontend/frameworks/react/index|React]]: the most popular library for building interfaces from components.
- [[frontend/frameworks/next/index|Next.js]]: a framework built on React that adds pages, routing and server rendering.
- [[frontend/frameworks/css/index|CSS tools]]: [[frontend/frameworks/css/tailwind|Tailwind]] and [[frontend/frameworks/css/sass|Sass]].
- [[frontend/frameworks/sanity/index|Sanity]]: a content management system for editing site content.
- [[frontend/frameworks/gsap/index|GSAP]] and [[frontend/frameworks/framer-motion/index|Framer Motion]]: animation.
- [[frontend/frameworks/threejs/index|Three.js]]: 3D graphics in the browser.

**For deeper React and Next.js:** about 44,000 words of notes teach them through real projects, including the bugs that came up: routing, state, login, uploads, live updates, payments and performance. They're listed from the [[frontend/frameworks/react/index|React]] and [[frontend/frameworks/next/index|Next.js]] pages.

## Practice

- [[frontend/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- [[frontend/interview/index|Frontend interview prep]]: React and rendering, the JavaScript and TypeScript round, and state, data and accessibility.

## Key ideas to remember

1. **Your code runs on hardware you don't own, over a network you don't control.** Test on a slow phone and a slow connection, not just your laptop. → [[frontend/01-foundations/01-what-a-frontend-is|What a Frontend Is]]
2. **Data from a server is a copy that can go out of date,** not something your page owns. Treat it like a cache. → [[frontend/03-state-and-data/02-data-fetching-and-server-state|Data Fetching]]
3. **Accessibility is part of "working",** not polish to add later. → [[frontend/05-cross-cutting/01-accessibility|Accessibility]]
4. **A page can look ready before it actually responds to clicks.** That gap is where many server-rendering bugs live. → [[frontend/06-rendering/02-hydration-and-the-server-boundary|Hydration]]

## Related

- [[backend/index|Backend]]: the other half of a full app.
- [[networking/index|Networking]]: how the page and its data travel to the browser.
- [[concepts/index|Concepts]]: ideas that apply to all code.

---

## About this course

- **How it's organised:** sections 01–07 are true in any framework; how one tool does something goes in `frameworks/`; ideas that apply beyond frontend go in [[concepts/index|Concepts]]; notes from real projects stay in [[projects/index|Projects]].
- **History:** restructured in August 2026 to mirror the [[backend/index|Backend]] course; the general ideas used to live in a separate `concepts/02-frontend/` folder. Renumbered in November 2026 so the sections follow the reading order, with rendering moved after the basics.
- **Where it came from:** the course sections are written from reference sources; the animation and 3D courses and the project notes came from building real things.
- **Note 0** (your first web page) was added in November 2026.
- **Not covered yet:** a full JavaScript course; forms in depth; translating a site into other languages; working offline; build tools like Vite; and Vue or Svelte beyond a comparison.
