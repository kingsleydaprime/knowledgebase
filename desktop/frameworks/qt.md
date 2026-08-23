# Qt — scaffold

**[Intermediate → Advanced]** · Mature C++ cross-platform toolkit with real native widgets. Also excellent from Python.

## The shape

Two UI models, and you choose one:

**QtWidgets** — classic desktop controls. Ideal for tool-shaped, information-dense applications.
**QML / Qt Quick** — declarative, animated, GPU-accelerated. Better for touch, embedded HMI and modern-feeling UI.

```python
# PySide6 — Qt from Python
from PySide6.QtWidgets import QApplication, QPushButton
app = QApplication([])
btn = QPushButton("Click me")
btn.clicked.connect(lambda: print("clicked"))    # signals and slots
btn.show()
app.exec()
```

## The things to know

**Signals and slots** are Qt's event system and its most-copied idea — a decoupled observer pattern with type checking, predating most of what web frameworks reinvented.

**Licensing needs actual attention.** Qt is dual-licensed: **LGPLv3** (free, but you must allow users to relink — practically, dynamic linking) or **commercial** (paid, permits static linking and removes obligations). **Check this before building a product on it**, not after → [[foundations/systems-engineering/05-trade-studies|trade studies]].

**Python bindings are first-class.** **PySide6** is the official one (LGPL); **PyQt6** is third-party (GPL or commercial). For a Python developer wanting a genuinely native desktop app, this is the strongest option → [[languages/06-python/README|Python]].

**It's much more than a GUI toolkit** — networking, threading, serialisation, SQL, testing. Closer to a platform, which is a strength and a commitment.

**Heavily used in embedded and industrial HMI**, where a native-feeling UI on constrained hardware matters and Electron is not an option → [[hardware/README|hardware]].

## Related
- [[desktop/frameworks/README|frameworks/]] · [[languages/05-cpp/README|C++]] · [[languages/06-python/README|Python]]

*Source: [reference] — scaffold, from the Qt documentation.*
