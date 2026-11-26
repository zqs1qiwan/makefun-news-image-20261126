# The World in One Day — Thursday, 26 November 2026

A one-image newspaper front page summing up the world's news of
Thursday 26 November 2026, built for the make.fun competition
`news-image-20261126`.

## The stories

1. **TANKERS ABLAZE IN HORMUZ** — Two oil tankers struck naval mines,
   exploded and caught fire in the Strait of Hormuz; Iran's Revolutionary
   Guards Navy said they were on an "unauthorised" route and warned other
   ships off. (Reuters, 25 Nov 2026)
2. **REFINERY HIT IN SAUDI ARABIA** — Yemen's Houthis said they attacked
   the Ras Tanura refinery, the kingdom's largest, and Riyadh's financial
   district; the Saudi-led coalition said four drones were shot down over
   Ras Tanura. Brent crude jumped above $93. (Reuters, 25 Nov 2026)
3. **PAKISTAN'S FIRST ASTRONAUT IN ORBIT** — China's Shenzhou-24 launched
   from Jiuquan and docked with the Tiangong space station carrying
   Muhammad Zeeshan Ali, the first Pakistani in orbit and the first
   foreign astronaut aboard Tiangong. (Reuters / Xinhua, 25 Nov 2026)
4. **RUSSIA'S DEAD: NEARLY 500,000** — A BBC analysis of leaked Rosstat
   death records found at least 490,334 Russian soldiers have died since
   the February 2022 invasion; Mediazona estimates the true toll may pass
   700,000 with the missing counted. (BBC, 25 Nov 2026)
5. **US READIES NEW TARIFFS** — The Trump administration is preparing to
   unveil new tariffs on China, the EU and 15 other economies after a
   months-long USTR investigation into subsidised excess industrial
   capacity. (Wall Street Journal, reported 25 Nov 2026)
6. **PACIFIC PACT SHUTS OUT BASES** — Australia and Solomon Islands signed
   a security treaty naming Australia the Solomons' primary security
   partner and ruling out any foreign military base there. (25 Nov 2026)

Also today: the Cartagena supermarket hostages were freed in a dawn
storming; North Korea ordered Switzerland to close its diplomatic office
in Pyongyang; Kilmar Ábrego García left the US for Spain.

## How it was made

`assets/entry-source.png` is a fresh AI-generated 3×2 photo collage,
one cell per story. `build_image.py` (Python + Pillow) crops the six
cells, typesets the masthead, headlines, subheads and the ALSO band in
Noto Sans Condensed, and writes `entry.png` (1024×1024, under 1 MiB).
It ends with a `verify()` step that reopens the PNG, asserts the size
and byte limit, and prints its SHA-256.

## How to run

```sh
python3 build_image.py        # rebuild entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). Running it twice
produces byte-identical output.
