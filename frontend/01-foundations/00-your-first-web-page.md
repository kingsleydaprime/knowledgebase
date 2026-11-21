---
id: 58bca2b9-312e-45dd-8ea8-6306bd514e76
---

# Your First Web Page

A web page is a file a browser reads and turns into what you see on screen. In this lesson you will build a small one from scratch using HTML for the content, CSS for the look and JavaScript for what happens when you click. Every website you visit is made from these same three things.

## Before you start
<!-- bite: dd4c9e16-5ea4-49d8-9840-058c988a0ff0 -->

You need:
- a web browser (Chrome, Firefox, Edge or Safari);
- a text editor. [VS Code](https://code.visualstudio.com) is free and popular, but any editor that saves plain text works. Word processors like Microsoft Word don't.

You don't need to install anything else or know any programming. [[programming-fundamentals/index|Programming Fundamentals]] helps for the JavaScript part, but isn't required.

**After this lesson you will be able to:**
1. write an HTML page with headings, text, a list and buttons;
2. style it with CSS: colours, spacing and layout;
3. make a button do something with JavaScript;
4. open your browser's developer tools to see what's going on.

**How to study it:** build the page yourself, one step at a time, and reload the browser after each change to see what it did.

## The kid version
<!-- bite: a42027d0-ced5-47c0-b274-14aaf4fdbca7 -->

Think of a web page as a house. **HTML is the walls, doors and rooms:** what's there and where. **CSS is the paint, furniture and decoration:** how it looks. **JavaScript is the electricity:** press a switch and something happens. You build in that order: first the structure, then the look, then the behaviour.

Your browser is the builder. It reads your three files and puts the house together on screen, every time you open the page.

**Where the picture stops working:** a house's walls don't change once built, but a web page's can. JavaScript can add, remove and rearrange the HTML while you're looking at it. That's how a page updates a total or shows a new message without reloading.

## 1. Why this exists
<!-- bite: 3c4b96c1-d704-400b-9a05-d0fdddf550f9 -->

Every website and web app, from a small shop's page to Gmail, is made of HTML, CSS and JavaScript in the end. Tools like React and Next.js, taught later in this course, are ways of producing those three more conveniently. If you understand the three underneath, the tools make sense; if you don't, they feel like magic, and magic is hard to debug.

## Terms used in this lesson
<!-- bite: 9d9da5f6-c1c4-421b-9786-eb8defbe9ef4 -->

1. **HTML**: The letters stand for HyperText Markup Language. It is the language that describes what's on a page: headings, paragraphs, lists, buttons, links and images.
2. **Element**: This is one piece of a page, such as a heading or a button. In HTML it's written as an opening tag, the content, and a closing tag: `<h1>Hello</h1>`.
3. **Tag**: This is the name in angle brackets that marks where an element starts and ends. `<p>` opens a paragraph and `</p>` closes it.
4. **Attribute**: This is extra information on an opening tag, written as `name="value"`. In `<button class="add">`, `class="add"` is an attribute.
5. **CSS**: The letters stand for Cascading Style Sheets. It is the language that describes how elements look: colours, sizes, spacing and layout.
6. **Selector**: This is the part of a CSS rule that says which elements it applies to. `h1` selects every `<h1>`, `.add` selects every element with `class="add"`, and `#total` selects the one element with `id="total"`.
7. **Property**: This is one thing a CSS rule changes, such as `color` or `padding`, followed by its value: `color: white;`.
8. **JavaScript**: This is the programming language that runs inside the browser. It makes pages respond: when you click, type or scroll, JavaScript decides what happens.
9. **DOM**: The letters stand for Document Object Model. It is the browser's live copy of your page's HTML, which JavaScript can read and change. Changing the DOM changes what you see.
10. **Event**: This is something that happens on the page, such as a click or a key press. JavaScript can "listen" for an event and run code when it happens.
11. **Developer tools**: This is a panel built into every browser for looking inside a page. Open it with F12, or by right-clicking the page and choosing "Inspect".

## 2. Getting set up
<!-- bite: 6947b0b2-dd98-4c19-9c30-1a8d7eb8dfc9 -->

Make a new folder called `my-first-page`. You'll put three files in it:

```text
my-first-page/
├── index.html    the content
├── style.css     the look
└── script.js     the behaviour
```

To view the page, open `index.html` in your browser: double-click it, or drag it onto a browser window. After every change, save the file and press F5 (or Cmd+R on a Mac) in the browser to reload.

## 3. HTML: what's on the page
<!-- bite: 0c7efb58-3602-42e4-be9d-96e7e5bb7cc3 -->

Create `index.html` with this content:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mama Ada's Kitchen</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <main class="card">
      <h1>Mama Ada's Kitchen</h1>
      <p>Hot food, made fresh every day in Yaba.</p>

      <ul class="menu">
        <li>
          <span>Jollof rice</span>
          <span class="price">₦2,500</span>
          <button class="add" data-price="2500">Add</button>
        </li>
        <li>
          <span>Fried plantain</span>
          <span class="price">₦800</span>
          <button class="add" data-price="800">Add</button>
        </li>
        <li>
          <span>Chapman</span>
          <span class="price">₦1,200</span>
          <button class="add" data-price="1200">Add</button>
        </li>
      </ul>

      <p class="total">Your order: <strong id="total">₦0</strong></p>
    </main>

    <script src="script.js"></script>
  </body>
</html>
```

Save it and open it in your browser. You'll see the text and three buttons, but plain, with no colours yet, because `style.css` doesn't exist. The buttons do nothing yet, because `script.js` doesn't exist either.

Here's what each part does:

- **`<!DOCTYPE html>`** tells the browser this is a modern HTML page. Always the first line.
- **`<head>`** holds information *about* the page that isn't shown on it: the title in the browser tab (`<title>`), the character set (`utf-8`, so symbols like ₦ display correctly), a line that makes the page fit phone screens (`viewport`), and the link to the CSS file.
- **`<body>`** holds everything you see.
- **`<h1>`** is the main heading; **`<p>`** is a paragraph.
- **`<ul>`** is a list, and each **`<li>`** is one item in it.
- **`<span>`** is a plain box around some text, so CSS can style it.
- **`<button>`** is a button. Its `data-price="2500"` attribute stores the price as a plain number, for JavaScript to read later. Any attribute starting with `data-` is yours to invent.
- **`<script src="script.js">`** loads the JavaScript. It sits at the very end of `<body>` on purpose; section 5 explains why.

**Notice the indentation.** Elements inside other elements are indented further. The browser doesn't care, but it makes the structure easy to see: the `<li>` items are inside the `<ul>`, which is inside `<main>`, which is inside `<body>`.

## 4. CSS: how it looks
<!-- bite: 9c7fe5ea-e298-430d-a3db-f42afd204f72 -->

Create `style.css` in the same folder:

```css
body {
  font-family: system-ui, sans-serif;
  background: #f1f5f9;
  margin: 0;
  padding: 24px;
}

.card {
  max-width: 420px;
  margin: 0 auto;
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

h1 {
  color: #059669;
  margin-top: 0;
}

.menu {
  list-style: none;
  padding: 0;
}

.menu li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}

.price {
  margin-left: auto;
  color: #64748b;
}

.add {
  background: #2563eb;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}

.add:hover {
  background: #1d4ed8;
}

.total {
  font-size: 1.2rem;
}
```

Save, reload the browser, and the page now looks like a card.

Each **rule** is a selector followed by properties in curly braces. Reading a few of them:

- **`body { ... }`** applies to the whole page: a font, a light grey background (`#f1f5f9` is a colour written in hexadecimal), and 24 pixels of space (`padding`) around the edges.
- **`.card { ... }`** applies to anything with `class="card"`. `max-width: 420px` stops it getting too wide on a laptop, and `margin: 0 auto` centres it. `border-radius` rounds the corners and `box-shadow` adds a soft shadow.
- **`.menu li { ... }`** applies to `<li>` elements *inside* something with `class="menu"`. `display: flex` lays out the name, price and button in a row, and `gap: 12px` puts space between them.
- **`.price { margin-left: auto; }`** pushes the price to the right, taking up all the spare space on its left.
- **`.add:hover { ... }`** applies only while the mouse is over the button, making it slightly darker so it feels clickable.

**Try it:** change `#059669` in the `h1` rule to `#dc2626`, save and reload. The heading turns red. Change it back afterwards.

## 5. JavaScript: making the buttons work
<!-- bite: dc4058dc-a3bb-4c20-8940-28f44c4d75fb -->

Create `script.js`:

```js
let total = 0;

const totalText = document.querySelector("#total");
const buttons = document.querySelectorAll(".add");

for (const button of buttons) {
  button.addEventListener("click", () => {
    total = total + Number(button.dataset.price);
    totalText.textContent = "₦" + total.toLocaleString("en-NG");
  });
}
```

Save, reload, and click "Add" a few times. The total goes up.

**Predict first:** you click Jollof rice, then Fried plantain, then Jollof rice again. What does the total say?

<details><summary>Answer</summary>

`₦5,800`: 2,500 + 800 + 2,500.

</details>

Line by line:

1. **`let total = 0;`** makes a variable called `total` that starts at 0. It will hold the order total.
2. **`document.querySelector("#total")`** finds the element with `id="total"` on the page. `document` is the page itself, and `querySelector` uses the same selectors as CSS.
3. **`document.querySelectorAll(".add")`** finds *every* element with `class="add"`: all three buttons.
4. **`for (const button of buttons)`** repeats the next part once for each button.
5. **`button.addEventListener("click", () => { ... })`** says: "when this button is clicked, run the code in the braces". That's listening for an event.
6. Inside, **`button.dataset.price`** reads the button's `data-price` attribute, the text `"2500"`. **`Number(...)`** turns that text into the number 2500, which is added to `total`.
7. **`totalText.textContent = ...`** replaces the text inside `<strong id="total">`. Because that's the DOM, the screen updates straight away. `toLocaleString("en-NG")` adds the comma, so 5800 shows as `5,800`.

**Why the `<script>` tag goes at the end of `<body>`:** the browser reads HTML from top to bottom and runs a script the moment it reaches it. If the script ran from the `<head>`, the buttons wouldn't exist yet, `querySelectorAll` would find nothing, and clicking would do nothing, with no error message. At the end of `<body>`, everything above it already exists.

## 6. Looking inside with the developer tools
<!-- bite: 72edee83-4166-4d45-8852-f13412e25add -->

Press **F12** (or right-click the page and choose **Inspect**).

- **The Elements tab** (called Inspector in Firefox) shows the live DOM. Click "Add" and watch the text inside `<strong id="total">` change. Click any element to see which CSS rules apply to it, and edit them to experiment without touching your files.
- **The Console tab** shows errors from your JavaScript, in red, with the file and line number. **It's the first place to look when something doesn't work.** You can also type JavaScript there and run it straight away: try `total`, or `"2500" + "800"`.

## Worked example: adding a "Clear order" button
<!-- bite: 6a043174-edf0-414c-91ce-92b6327a4ec7 -->

Let's add a button that resets the total to zero, from HTML through to JavaScript.

**Step 1: HTML.** Add a button just after the total paragraph, inside `<main>`:

```html
      <button id="clear">Clear order</button>
```

**Step 2: CSS.** Give it a quieter look than the Add buttons, at the end of `style.css`:

```css
#clear {
  background: none;
  border: 1px solid #cbd5e1;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
}
```

**Step 3: JavaScript.** At the end of `script.js`, find the button and listen for clicks:

```js
document.querySelector("#clear").addEventListener("click", () => {
  total = 0;
  totalText.textContent = "₦0";
});
```

Save all three and reload. Add a few items, then press "Clear order": the total goes back to ₦0. That's the pattern for almost every interactive feature: **an element in HTML, a style in CSS, and a listener in JavaScript that changes a variable and updates the page.**

## Common pitfalls
<!-- bite: f5762182-429f-409b-8271-ed02dd346825 -->

1. **The CSS or JavaScript doesn't load.** Usually the file name in `href="style.css"` or `src="script.js"` doesn't exactly match the real file, including capital letters, or the file is in a different folder. The Console shows a "not found" error.
2. **A missing closing tag.** Forget `</li>` or `</ul>` and the browser guesses where it ends, often wrongly, and the layout goes strange.
3. **Mixing up `.` and `#`.** In CSS and `querySelector`, `.add` means `class="add"` and `#total` means `id="total"`. Use a class for things there are several of, and an id for one unique thing.
4. **Adding text instead of numbers.** Everything read from HTML is text. `"2500" + "800"` joins them into `"2500800"`. Convert with `Number()` first.
5. **The script runs before the page exists.** Keep `<script>` at the end of `<body>`.
6. **Forgetting to save or reload.** The browser shows the files as they were when it last loaded them.

## Check your understanding
<!-- bite: abd8a82c-1538-4bfb-9589-37b9a11b8dc2 -->

**1. What does each of the three languages do?**

<details><summary>Answer</summary>

HTML describes what's on the page (the content and structure), CSS describes how it looks, and JavaScript describes what happens when the user does something.

</details>

**2. In CSS, what's the difference between `.price` and `#total`?**

<details><summary>Answer</summary>

`.price` selects every element with `class="price"`; there can be many. `#total` selects the single element with `id="total"`; an id should appear only once on a page.

</details>

**3. Why does the code use `Number(button.dataset.price)` instead of just `button.dataset.price`?**

<details><summary>Answer</summary>

Values read from HTML attributes are text. Adding text joins it: `0 + "2500"` gives `"02500"`, and the next click gives `"02500800"`. `Number()` turns the text into a real number so it adds up.

</details>

**4. Someone moves `<script src="script.js">` into the `<head>`. The page loads with no error, but the buttons do nothing. Why?**

<details><summary>Answer</summary>

The browser runs the script as soon as it reaches it, before the `<body>` has been read. At that moment there are no buttons, so `querySelectorAll(".add")` finds none and no click listeners are added. Nothing is wrong enough to cause an error; there's just nothing to listen to.

</details>

**5. What is the DOM, and why does changing it change the screen?**

<details><summary>Answer</summary>

The DOM is the browser's live copy of the page's HTML. The browser draws the screen from the DOM, not from your file, so when JavaScript changes the DOM (like setting `textContent`), the browser redraws that part straight away.

</details>

## Practice: count the items
<!-- bite: 76d3e039-e8c9-4038-969a-a5f38e541490 -->

Extend the page so it also shows **how many items** are in the order.

1. Add a line under the total: `Items: 0`, with the number inside an element that has an id.
2. Each time an Add button is clicked, add 1 to the count and show it.
3. Make "Clear order" (from the worked example) reset the count to 0 too.
4. Add a fourth menu item, *Puff-puff* for ₦500, without changing any JavaScript.

**Done when:** clicking Jollof rice, Puff-puff and Chapman shows `₦4,200` and `Items: 3`; "Clear order" resets both; and the Console shows no red errors.

<details><summary>Hints</summary>

- Copy the pattern for the total: a variable, an element found with `querySelector`, and a line that sets its `textContent`.
- Step 4 needs only HTML: a new `<li>` with its own `data-price`. The loop in `script.js` finds every `.add` button, including new ones. That's why storing the price on the button was worth it.

</details>

## Going further
<!-- bite: 17d43fca-e567-4689-94ac-4902771f9305 -->

- **Look at a real site:** open the developer tools on any website you use. It's built from the same elements, rules and listeners, just many more of them.
- **Learn more HTML and CSS:** [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Learn_web_development) is the standard free reference, written by the people who make Firefox.
- **Layout:** `display: flex` was used once here. It and `display: grid` handle almost every layout; both are worth learning properly.

## Before moving on
<!-- bite: 90798183-d869-4653-ad62-e378f45b5514 -->

You're ready for the next note when you can, without looking:
- write an HTML page with a heading, a list and a button;
- style it with a CSS rule using a class selector;
- make a button change some text on the page with JavaScript;
- find a JavaScript error in the Console.

**Recap:** HTML is the content, CSS is the look, JavaScript is the behaviour. CSS and JavaScript find elements with the same selectors (`.class`, `#id`, `tag`). JavaScript changes the page by listening for events and updating the DOM, and everything it reads from HTML is text until converted.

**Next:** [[frontend/01-foundations/01-what-a-frontend-is|What a Frontend Actually Is]]. Now that you've built a page, it explains the jobs a frontend does and why they get hard once a page becomes an app.

## Related
<!-- bite: 339bb4a8-ec45-42e7-b50e-783a55e9eeee -->

- [[programming-fundamentals/06-control-flow|Control Flow]] and [[programming-fundamentals/08-functions|Functions]]: the programming ideas behind the JavaScript here.
- [[frontend/01-foundations/02-the-browser-and-the-dom|The Browser and the DOM]]: what the browser does with your files, in depth.
- [[frontend/frameworks/react/index|React]]: a tool for building much bigger pages from components.

## About this lesson
<!-- bite: 501f72cf-167c-4b86-b9be-b2d1f32d5587 -->

**Level:** Beginner. **Covers:** Build a small, working web page from scratch, using the three languages every browser understands: HTML for the content, CSS for the look, and JavaScript for what happens when you click. This comes before the rest of the course.
