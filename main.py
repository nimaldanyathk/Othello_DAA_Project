"""Web (pygbag/WebAssembly) entry point.

For the desktop version, run: python main_pygame.py
"""
import asyncio

# Direct pygame import required here: pygbag scans main.py's top-level
# imports to decide which packages to bundle for the browser.
import pygame  # noqa: F401

from ui.pygame_gui import PyGameUI


async def main():
    app = PyGameUI()
    await app.run_async()


asyncio.run(main())
