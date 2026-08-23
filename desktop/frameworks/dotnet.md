# .NET Desktop — scaffold

**[Intermediate]** · C# and XAML. The default in Windows-heavy and enterprise environments.

## The options, and they are confusingly many

| | Targets | Status |
|---|---|---|
| **WinUI 3** | Windows only | Microsoft's current Windows recommendation |
| **WPF** | Windows only | Old, stable, enormous existing codebase |
| **WinForms** | Windows only | Older still; alive for internal tools |
| **.NET MAUI** | Win, macOS, iOS, Android | Microsoft's cross-platform bet |
| **Avalonia** | Win, macOS, **Linux**, mobile, web | **Third-party, and often the better choice** |

**Avalonia is the one to know about.** It's community-driven, WPF-like, genuinely cross-platform including Linux (which MAUI does not target), and it draws its own controls so rendering is identical everywhere — with the accessibility caveat that implies → [[desktop/frameworks/README|frameworks/]].

## The things to know

**XAML plus MVVM is the model** — declarative markup, data binding, and a ViewModel holding presentation state. **Data binding is the central idea**, and it's the same concept React reinvented differently: the UI is a function of state, and you mutate state rather than widgets.

**C# is a genuinely good language** — mature generics, LINQ, async/await (which it popularised before JavaScript), strong tooling. Closest neighbour in this vault is [[languages/01-java/README|Java]].

**Single-file publish and AOT compilation** produce self-contained executables without a runtime install — a large improvement over the historical ".NET Framework version" pain.

**The honest constraint: this is a Windows-first ecosystem.** Cross-platform works, but the documentation, samples and hiring market assume Windows. **If your users are on Windows, this is the strongest option available**; if they aren't, weigh Avalonia or something else.

## Related
- [[desktop/frameworks/README|frameworks/]] · [[languages/01-java/README|Java]] (nearest neighbour here)

*Source: [reference] — scaffold, from Microsoft and Avalonia documentation.*
