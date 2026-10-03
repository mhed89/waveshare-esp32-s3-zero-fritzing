#!/usr/bin/env python3
"""Generate the Waveshare ESP32-S3-Zero Fritzing part from one pin list."""
import os, sys, zipfile, shutil

OUT = sys.argv[1]
NAME = "waveshare_esp32_s3_zero"
MM = 39.3701  # svg units (1/1000 in) per mm

# ---------------------------------------------------------------- pin list
# (name, kind, description)   kind: L=left header, R=right header, F=front pad, B=back pad
def gpio(n, extra=""):
    adc = ""
    if n <= 10: adc = f"ADC1_CH{n-1}, "
    elif 11 <= n <= 20: adc = f"ADC2_CH{n-11}, "
    base = {"UART": 1, "PWM": 1, "I2S": 1, "I2C": 1, "SPI": 1}
    return f"GPIO{n}: {adc}UART, PWM, I2S, I2C, SPI{extra}"

PINS = [("5V", "L", "5V (USB VBUS / external 5V input)"),
        ("GND", "L", "Ground"),
        ("3V3", "L", "3.3V output from the on-board regulator (3V3 OUT)")]
for n in range(1, 7):
    PINS.append((f"GP{n}", "L", gpio(n, ", strapping pin" if n == 3 else "")))
PINS += [("GP43/TX", "R", "GPIO43: UART0 TX"),
         ("GP44/RX", "R", "GPIO44: UART0 RX")]
for n in (13, 12, 11, 10, 9, 8, 7):
    PINS.append((f"GP{n}", "R", gpio(n)))
for n in (16, 15, 14):
    PINS.append((f"GP{n}", "F", gpio(n) + " (pad on the top face of the board)"))
for n in (45, 42, 41, 40, 39, 38, 18, 17):
    extra = ""
    if n == 45: extra = "GPIO45: UART, PWM, I2S, I2C, SPI, strapping pin (VDD_SPI voltage)"
    elif n in (42, 41, 40, 39): extra = f"GPIO{n}: UART, PWM, I2S, I2C, SPI, JTAG by default"
    elif n == 38: extra = "GPIO38: UART, PWM, I2S, I2C, SPI"
    PINS.append((f"GP{n}", "B", (extra or gpio(n)) + " (pad on the bottom face of the board)"))
N = len(PINS)
assert N == 29

def ctype(kind): return "male" if kind in "LR" else "pad"

# ---------------------------------------------------------------- geometry (svg units, 1000/in)
BW, BH = 18.0 * MM, 23.5 * MM            # board
def board_geom(dx, dy):
    """Return board origin and per-connector centre (x, y) for the physical layout."""
    bx, by = 45.7 + dx, 143.7 + dy
    pos = []
    li = ri = fi = bi = 0
    for name, kind, _ in PINS:
        if kind == "L":
            pos.append((100 + dx, 200 + dy + 100 * li)); li += 1
        elif kind == "R":
            pos.append((700 + dx, 200 + dy + 100 * ri)); ri += 1
        elif kind == "F":
            pos.append((bx + 14.7 * MM, by + (19.3 + 1.65 * fi) * MM)); fi += 1
        else:
            pos.append((bx + 14.7 * MM, by + (9.0 + 1.65 * bi) * MM)); bi += 1
    return bx, by, pos

def f(v): return f"{v:.1f}"

# ---------------------------------------------------------------- breadboard
def breadboard():
    dx, dy = 130, 0
    bx, by, pos = board_geom(dx, dy)
    W, H = 1260, 1110
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" width="{W/1000}in" height="{H/1000}in" viewBox="0 0 {W} {H}">')
    a('<g id="breadboard">')
    # PCB body
    a(f'<rect x="{f(bx)}" y="{f(by)}" width="{f(BW)}" height="{f(BH)}" rx="18" fill="#1d4a99" stroke="#0c2a5e" stroke-width="4"/>')
    # USB-C
    ux = bx + BW / 2 - 175
    a(f'<rect x="{f(ux)}" y="{f(by-59)}" width="350" height="300" rx="28" fill="#c9cbd0" stroke="#8a8c92" stroke-width="4"/>')
    a(f'<rect x="{f(ux+40)}" y="{f(by-20)}" width="270" height="70" rx="30" fill="#4a4c52"/>')
    # buttons B / R, status LED
    for cx, lab in ((bx + 4.2 * MM, "B"), (bx + 13.4 * MM, "R")):
        cy = by + 8.4 * MM
        a(f'<rect x="{f(cx-65)}" y="{f(cy-45)}" width="130" height="90" fill="#d8d8d8" stroke="#777" stroke-width="3"/>')
        a(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="26" fill="#222"/>')
        a(f'<text x="{f(cx)}" y="{f(cy-62)}" font-family="Droid Sans, sans-serif" font-size="34" fill="#ffffff" text-anchor="middle">{lab}</text>')
    a(f'<rect x="{f(bx+8.7*MM-22)}" y="{f(by+8.4*MM-22)}" width="44" height="44" fill="#f2f2f2" stroke="#777" stroke-width="3"/>')
    # ESP32-S3 chip (diamond) and antenna
    cx, cy = bx + 9.1 * MM, by + 15.4 * MM
    a(f'<polygon points="{f(cx)},{f(cy-150)} {f(cx+150)},{f(cy)} {f(cx)},{f(cy+150)} {f(cx-150)},{f(cy)}" fill="#222" stroke="#000" stroke-width="3"/>')
    a(f'<rect x="{f(bx+130)}" y="{f(by+21.2*MM)}" width="300" height="66" rx="6" fill="#b32222" stroke="#6e1111" stroke-width="3"/>')
    a(f'<text x="{f(bx+280)}" y="{f(by+21.2*MM+44)}" font-family="Droid Sans, sans-serif" font-size="28" fill="#ffffff" text-anchor="middle">ESP32-S3-Zero</text>')
    # bottom-pad inset panel
    px0 = 1020
    a(f'<rect x="{px0}" y="{f(by+8.0*MM)}" width="210" height="{f(1.65*7*MM+2*0.9*MM+0.0)}" rx="10" fill="#2a2d33" stroke="#9aa0aa" stroke-width="3" stroke-dasharray="14 8"/>')
    a(f'<text x="{px0+105}" y="{f(by+8.0*MM-14)}" font-family="Droid Sans, sans-serif" font-size="26" fill="#444444" text-anchor="middle">BOTTOM-SIDE PADS</text>')
    # pins, pads, labels
    for i, ((name, kind, _), (x, y)) in enumerate(zip(PINS, pos)):
        if kind == "B":
            x = px0 + 160
        if kind in "LR":
            a(f'<rect id="connector{i}pin" x="{f(x-30)}" y="{f(y-30)}" width="60" height="60" fill="#d9ae2c" stroke="#8a6a10" stroke-width="3"/>')
            a(f'<circle cx="{f(x)}" cy="{f(y)}" r="12" fill="#6b5410"/>')
        else:
            a(f'<circle id="connector{i}pin" cx="{f(x)}" cy="{f(y)}" r="22" fill="#d9ae2c" stroke="#8a6a10" stroke-width="3"/>')
        a(f'<rect id="connector{i}terminal" x="{f(x-5)}" y="{f(y-5)}" width="10" height="10" fill="none" stroke="none"/>')
        fs = 36
        if kind == "L":
            a(f'<text x="{f(bx-8)}" y="{f(y+12)}" font-family="Droid Sans, sans-serif" font-size="{fs}" fill="#222222" text-anchor="end">{name}</text>')
        elif kind == "R":
            a(f'<text x="{f(bx+BW+8)}" y="{f(y+12)}" font-family="Droid Sans, sans-serif" font-size="{fs}" fill="#222222">{name}</text>')
        elif kind == "F":
            a(f'<text x="{f(x-34)}" y="{f(y+11)}" font-family="Droid Sans, sans-serif" font-size="30" fill="#ffffff" text-anchor="end">{name}</text>')
        else:
            a(f'<text x="{px0+20}" y="{f(y+11)}" font-family="Droid Sans, sans-serif" font-size="30" fill="#ffffff">{name}</text>')
    a('</g></svg>')
    return "\n".join(s)

# ---------------------------------------------------------------- schematic
def schematic():
    left = [i for i, p in enumerate(PINS) if p[0] in
            [f"GP{n}" for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)]]
    left.sort(key=lambda i: int(PINS[i][0][2:]))
    right_order = ["GP17", "GP18", "GP38", "GP39", "GP40", "GP41", "GP42", "GP45", "GP43/TX", "GP44/RX"]
    right = [next(i for i, p in enumerate(PINS) if p[0] == n) for n in right_order]
    top = [0, 2]       # 5V, 3V3
    bottom = [1]       # GND
    assert len(left) + len(right) + len(top) + len(bottom) == N
    W, H = 1400, 2300
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" width="{W/1000}in" height="{H/1000}in" viewBox="0 0 {W} {H}">')
    a('<g id="schematic">')
    a('<rect x="300" y="300" width="800" height="1700" fill="#ffffff" stroke="#000000" stroke-width="10"/>')
    a('<text x="700" y="1650" font-family="Droid Sans, sans-serif" font-size="56" fill="#000000" text-anchor="middle">ESP32-S3-Zero</text>')
    a('<text x="700" y="1720" font-family="Droid Sans, sans-serif" font-size="40" fill="#000000" text-anchor="middle">Waveshare</text>')
    fnt = 'font-family="Droid Sans, sans-serif"'
    def pin_line(i, x1, y1, x2, y2, tx, ty):
        a(f'<line id="connector{i}pin" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000000" stroke-width="10"/>')
        a(f'<rect id="connector{i}terminal" x="{tx}" y="{ty}" width="10" height="10" fill="none" stroke="none"/>')
    for k, i in enumerate(left):
        y = 400 + 100 * k
        pin_line(i, 100, y, 300, y, 100, y - 5)
        a(f'<text x="330" y="{y+20}" {fnt} font-size="55" fill="#000000">{PINS[i][0]}</text>')
        a(f'<text x="125" y="{y-14}" {fnt} font-size="36" fill="#000000">{i+1}</text>')
    for k, i in enumerate(right):
        y = 400 + 100 * k
        pin_line(i, 1100, y, 1300, y, 1290, y - 5)
        a(f'<text x="1070" y="{y+20}" {fnt} font-size="55" fill="#000000" text-anchor="end">{PINS[i][0]}</text>')
        a(f'<text x="1275" y="{y-14}" {fnt} font-size="36" fill="#000000" text-anchor="end">{i+1}</text>')
    for k, i in enumerate(top):
        x = 600 + 200 * k
        pin_line(i, x, 100, x, 300, x - 5, 100)
        a(f'<text x="{x}" y="375" {fnt} font-size="55" fill="#000000" text-anchor="middle">{PINS[i][0]}</text>')
        a(f'<text x="{x+16}" y="150" {fnt} font-size="36" fill="#000000">{i+1}</text>')
    for k, i in enumerate(bottom):
        x = 700
        pin_line(i, x, 2000, x, 2200, x - 5, 2190)
        a(f'<text x="{x}" y="1960" {fnt} font-size="55" fill="#000000" text-anchor="middle">{PINS[i][0]}</text>')
        a(f'<text x="{x+16}" y="2150" {fnt} font-size="36" fill="#000000">{i+1}</text>')
    a('</g></svg>')
    return "\n".join(s)

# ---------------------------------------------------------------- pcb
def pcb():
    bx, by, pos = board_geom(0, 0)
    W, H = 800, 1100
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" width="{W/1000}in" height="{H/1000}in" viewBox="0 0 {W} {H}">')
    a('<g id="silkscreen">')
    a(f'<rect x="{f(bx)}" y="{f(by)}" width="{f(BW)}" height="{f(BH)}" fill="none" stroke="#000000" stroke-width="8"/>')
    ux = bx + BW / 2 - 175
    a(f'<rect x="{f(ux)}" y="{f(by-59)}" width="350" height="59" fill="none" stroke="#000000" stroke-width="8"/>')
    a(f'<rect x="{f(100-48)}" y="{f(200-48)}" width="96" height="96" fill="none" stroke="#000000" stroke-width="8"/>')
    a('</g>')
    a('<g id="copper1">')
    a('<g id="copper0">')
    for i, ((name, kind, _), (x, y)) in enumerate(zip(PINS, pos)):
        if kind in "LR":
            a(f'<circle id="connector{i}pin" cx="{f(x)}" cy="{f(y)}" r="30" fill="none" stroke="#F7BD13" stroke-width="20"/>')
    a('</g>')
    for i, ((name, kind, _), (x, y)) in enumerate(zip(PINS, pos)):
        if kind == "B":
            a(f'<rect id="connector{i}pin" x="{f(x-22)}" y="{f(y-22)}" width="44" height="44" fill="#F7BD13" stroke="none"/>')
    a('</g></svg>')
    return "\n".join(s)

# ---------------------------------------------------------------- icon
def icon():
    return ('<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" width="0.4in" height="0.5in" viewBox="0 0 400 500">\n'
            '<g id="icon">\n'
            '<rect x="40" y="70" width="320" height="410" rx="12" fill="#1d4a99" stroke="#0c2a5e" stroke-width="4"/>\n'
            '<rect x="115" y="20" width="170" height="150" rx="14" fill="#c9cbd0" stroke="#8a8c92" stroke-width="3"/>\n'
            '<polygon points="200,250 280,330 200,410 120,330" fill="#222"/>\n'
            '</g></svg>')

# ---------------------------------------------------------------- fzp
def fzp():
    out = []
    a = out.append
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a('<module fritzingVersion="0.9.3" moduleId="WaveshareESP32S3Zero_1_ModuleID">')
    a('  <version>1</version>')
    a('  <title>Waveshare ESP32-S3-Zero</title>')
    a('  <label>U</label>')
    a('  <date>2026-10-03</date>')
    a('  <author>Markus</author>')
    a('  <tags><tag>ESP32</tag><tag>ESP32-S3</tag><tag>Waveshare</tag><tag>microcontroller</tag><tag>WiFi</tag><tag>Bluetooth</tag></tags>')
    a('  <properties>')
    a('    <property name="family">microcontroller board</property>')
    a('    <property name="variant">ESP32-S3-Zero</property>')
    a('    <property name="chip">ESP32-S3FH4R2</property>')
    a('    <property name="pins">29</property>')
    a('  </properties>')
    a('  <description>Waveshare ESP32-S3-Zero mini development board, 23.5 x 18 mm, USB-C, 4 MB flash, 2 MB PSRAM, WS2812 RGB LED on GPIO21, BOOT button on GPIO0. 2x9 header holes (2.54 mm pitch, 15.24 mm row spacing) plus 3 top pads and 8 bottom pads.</description>')
    a('  <views>')
    a(f'    <iconView><layers image="icon/{NAME}_icon.svg"><layer layerId="icon"/></layers></iconView>')
    a(f'    <breadboardView><layers image="breadboard/{NAME}_breadboard.svg"><layer layerId="breadboard"/></layers></breadboardView>')
    a(f'    <schematicView><layers image="schematic/{NAME}_schematic.svg"><layer layerId="schematic"/></layers></schematicView>')
    a(f'    <pcbView><layers image="pcb/{NAME}_pcb.svg"><layer layerId="copper0"/><layer layerId="silkscreen"/><layer layerId="copper1"/></layers></pcbView>')
    a('  </views>')
    a('  <connectors>')
    for i, (name, kind, desc) in enumerate(PINS):
        a(f'    <connector id="connector{i}" name="{name}" type="{ctype(kind)}">')
        a(f'      <description>{desc}</description>')
        a('      <views>')
        a(f'        <breadboardView><p layer="breadboard" svgId="connector{i}pin" terminalId="connector{i}terminal"/></breadboardView>')
        a(f'        <schematicView><p layer="schematic" svgId="connector{i}pin" terminalId="connector{i}terminal"/></schematicView>')
        if kind in "LR":
            a(f'        <pcbView><p layer="copper0" svgId="connector{i}pin"/><p layer="copper1" svgId="connector{i}pin"/></pcbView>')
        elif kind == "B":
            a(f'        <pcbView><p layer="copper1" svgId="connector{i}pin"/></pcbView>')
        a('      </views>')
        a('    </connector>')
    a('  </connectors>')
    a('</module>')
    return "\n".join(out)

# ---------------------------------------------------------------- write
for d in ("breadboard", "schematic", "pcb", "icon"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
files = {
    f"{NAME}.fzp": fzp(),
    f"breadboard/{NAME}_breadboard.svg": breadboard(),
    f"schematic/{NAME}_schematic.svg": schematic(),
    f"pcb/{NAME}_pcb.svg": pcb(),
    f"icon/{NAME}_icon.svg": icon(),
}
for p, c in files.items():
    with open(os.path.join(OUT, p), "w") as fh:
        fh.write(c + "\n")

with zipfile.ZipFile(os.path.join(OUT, f"{NAME}.fzpz"), "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        arc = ("part." + p) if p.endswith(".fzp") else "svg." + p.replace("/", ".")
        z.write(os.path.join(OUT, p), arc)
print("written", list(files), "+ .fzpz")
