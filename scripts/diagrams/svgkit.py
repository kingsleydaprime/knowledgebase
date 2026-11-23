"""Shared SVG drawing helpers for the diagram scripts in this folder. No libraries needed."""
import os

INK = '#1f2933'        # text and outlines
GRID = '#cbd2d9'       # grid lines
PIX = '#3b82f6'        # lit pixels
PIX2 = '#93c5fd'       # mirrored / secondary pixels
TRUE = '#dc2626'       # the true (ideal) shape
ACCENT = '#059669'     # constructions, results
BG = '#ffffff'


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.title = title

    def add(self, s):
        self.parts.append(s)

    def line(self, x1, y1, x2, y2, color=INK, width=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{color}" stroke-width="{width}"{d}/>')

    def rect(self, x, y, w, h, fill, stroke='none', width=1, opacity=1):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{width}" fill-opacity="{opacity}"/>')

    def circle(self, x, y, r, fill, stroke='none'):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}"/>')

    def text(self, x, y, s, size=13, color=INK, anchor='middle', weight='normal'):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
                 f'text-anchor="{anchor}" font-weight="{weight}" '
                 f'font-family="system-ui, sans-serif">{s}</text>')

    def path(self, d, color, width=2, fill='none', dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}"{da}/>')

    def save(self, name, out):
        os.makedirs(out, exist_ok=True)
        body = '\n'.join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}" role="img">\n<title>{self.title}</title>\n'
               f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>\n{body}\n</svg>\n')
        with open(os.path.join(out, name), 'w') as f:
            f.write(svg)
        print(f'{name}: {len(svg)} bytes')
