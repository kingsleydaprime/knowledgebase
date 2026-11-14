# Desktop

## What desktop development is

**Desktop development is building apps you install on a computer, like VS Code, Spotify, WhatsApp Desktop or Photoshop, rather than apps that run in a web browser.**

A desktop app is mostly the same two halves as a web app: a [[frontend/index|frontend]] (what you see) and a [[backend/index|backend]] (the logic), except both run on the user's own computer. What's genuinely different is getting it there and keeping it up to date. You're sending your app to thousands of machines you don't control, running Windows, macOS or Linux in versions you didn't choose, and you can't update them all at once like a website. You also need to sign your app so the operating system trusts it, build installers for each platform, and follow each platform's look and feel.

There are three main ways to build one: put a web page inside an app window (Electron, Tauri), use each operating system's own buttons and menus, or draw everything yourself (Qt and others).

## What you'll be able to do

By the end you will be able to:
- explain how desktop apps differ from websites, and what's harder;
- choose between the main ways of building one, including the honest case for and against Electron;
- explain how a desktop app splits into a display part and a logic part, and why that split is a security boundary;
- explain what it takes to ship: signing, installers, stores and automatic updates.

## Where to start

**Before you start:** some [[frontend/index|frontend]] and [[backend/index|backend]] experience, since a desktop app is both in one.

1. [[desktop/01-what-desktop-development-is|What Desktop Development Is]]: how it differs from the web, the three ways to build, the fair version of the Electron memory argument, and how to choose.
2. [[desktop/frameworks/index|Frameworks]]: the options, and the one question they differ on: who draws the screen.

**The frameworks** (outlines for now): [[desktop/frameworks/tauri|Tauri]], [[desktop/frameworks/electron|Electron]], [[desktop/frameworks/qt|Qt]], [[desktop/frameworks/dotnet|.NET]] and [[desktop/frameworks/native|each platform's own tools]].

## Practice

**Ship one tiny Tauri app to Windows, macOS and Linux.** Not for the app, but for the pipeline: build it, sign it, and install it on a computer that isn't yours. Then release version 2 and make the automatic update work from version 1. That teaches most of this section.

## Key ideas to remember

1. **You can't update everyone at once.** Build automatic updates in from the start. → [[desktop/01-what-desktop-development-is|01]]
2. **Getting the app onto people's machines is often more work than the features.** → [[desktop/01-what-desktop-development-is|01]]
3. **Apps that ignore a platform's conventions feel cheap,** even when users can't say why. → [[desktop/01-what-desktop-development-is|01]]
4. **In Electron, security settings are off unless you turn them on.** → [[desktop/frameworks/electron|Electron]]
5. **Check Qt's licence before building a product on it.** → [[desktop/frameworks/qt|Qt]]

## Related

- [[frontend/index|Frontend]] and [[backend/index|Backend]]: the two halves of a desktop app.
- [[mobile/index|Mobile]]: the same "one app or several?" question, for phones.
- [[devops/05-ci-cd/index|CI/CD]]: building, signing and releasing automatically for three platforms.
- [[databases/index|Databases]]: SQLite is the usual local store.

---

## About this section

- **Size:** 1 note, a frameworks overview and 5 framework outlines, about 2,750 words, written in August 2026. It's deliberately small, because most of a desktop app is covered by the frontend and backend courses.
- **Where it came from:** reference sources. The author hasn't shipped a desktop app, so the material on signing, installers and updates is the part to trust least.
- **Not covered yet:** step-by-step packaging, signing and notarisation, update systems, app store rules, menus, tray icons and shortcuts, syncing offline data, and accessibility.
