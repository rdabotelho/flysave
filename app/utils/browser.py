from playwright.sync_api import sync_playwright
from app.config.settings import HEADLESS


def get_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=HEADLESS)
    return playwright, browser
