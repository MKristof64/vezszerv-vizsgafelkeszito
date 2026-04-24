from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Önálló, részletes vizsgafelkészítő HTML app generálása a témaköri JSON-ból."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "output" / "topics.generated.json",
        help="A build_topic_data.py által előállított JSON fájl.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "vezszerv-tanuloapp.html",
        help="A létrejövő önálló HTML app útvonala.",
    )
    return parser.parse_args()


def build_html(payload: dict) -> str:
    topic_json = json.dumps(payload, ensure_ascii=False)
    generated_at = str(payload.get("generatedAt", ""))[:10]
    topic_count = len(payload.get("topics", []))

    template = """<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VezSzerv vizsgafelkészítő</title>
  <style>
    :root {
      --paper: #f3ede0;
      --paper-strong: #fbf7ef;
      --paper-soft: rgba(255, 255, 255, 0.82);
      --ink: #1f2a27;
      --muted: #5f6f6a;
      --line: rgba(31, 42, 39, 0.12);
      --accent: #b85d3d;
      --accent-soft: rgba(184, 93, 61, 0.12);
      --accent-strong: #964327;
      --secondary: #1f6155;
      --secondary-soft: rgba(31, 97, 85, 0.12);
      --warning: #9b6a19;
      --warning-soft: rgba(155, 106, 25, 0.12);
      --shadow-lg: 0 24px 52px rgba(20, 31, 28, 0.14);
      --shadow-md: 0 16px 32px rgba(20, 31, 28, 0.1);
      --radius-xl: 30px;
      --radius-lg: 22px;
      --radius-md: 18px;
      --radius-sm: 14px;
      --sidebar-width: 360px;
    }

    * {
      box-sizing: border-box;
    }

    html,
    body {
      margin: 0;
      min-height: 100%;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(184, 93, 61, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(31, 97, 85, 0.20), transparent 24%),
        linear-gradient(180deg, #eee4d4 0%, var(--paper) 42%, #ebe1d0 100%);
      font-family: "Aptos", "Segoe UI", Calibri, sans-serif;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      display: grid;
      grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
    }

    body.sidebar-open,
    body.sheet-open,
    body.quiz-open {
      overflow: hidden;
    }

    .sidebar {
      position: sticky;
      top: 0;
      height: 100vh;
      padding: 24px 20px 28px 24px;
      border-right: 1px solid var(--line);
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(255, 255, 255, 0.55)),
        rgba(249, 244, 236, 0.82);
      backdrop-filter: blur(14px);
      overflow: auto;
      scrollbar-gutter: stable;
      z-index: 10;
    }

    .brand {
      display: grid;
      gap: 12px;
      margin-bottom: 18px;
    }

    .eyebrow {
      display: inline-flex;
      width: fit-content;
      padding: 6px 12px;
      border-radius: 999px;
      background: var(--secondary-soft);
      color: var(--secondary);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .brand h1 {
      margin: 0;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: clamp(1.9rem, 2vw, 2.4rem);
      line-height: 1.05;
    }

    .brand p {
      margin: 0;
      color: var(--muted);
      line-height: 1.58;
      font-size: 0.96rem;
    }

    .search-shell {
      position: relative;
      margin: 18px 0 12px;
    }

    .search-shell input {
      width: 100%;
      border: 1px solid rgba(31, 42, 39, 0.14);
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.94);
      padding: 14px 16px 14px 44px;
      font: inherit;
      color: var(--ink);
      outline: none;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.84);
    }

    .search-shell input:focus {
      border-color: rgba(31, 97, 85, 0.55);
      box-shadow: 0 0 0 4px rgba(31, 97, 85, 0.14);
    }

    .search-icon {
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--muted);
      pointer-events: none;
    }

    .sidebar-meta {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 16px;
      color: var(--muted);
      font-size: 0.88rem;
    }

    .sidebar-guide {
      margin-bottom: 18px;
      padding: 14px 15px;
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(31, 97, 85, 0.1), rgba(255, 255, 255, 0.74));
      border: 1px solid rgba(31, 97, 85, 0.12);
    }

    .sidebar-guide strong {
      display: block;
      margin-bottom: 6px;
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--secondary);
    }

    .sidebar-guide p {
      margin: 0;
      line-height: 1.58;
      color: #334541;
      font-size: 0.92rem;
    }

    .module-list {
      display: grid;
      gap: 18px;
      padding-bottom: 24px;
    }

    .module-group {
      display: grid;
      gap: 10px;
    }

    .module-header {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .module-count {
      padding: 3px 9px;
      border-radius: 999px;
      background: rgba(31, 42, 39, 0.08);
      color: var(--ink);
      font-size: 0.75rem;
    }

    .topic-button {
      width: 100%;
      display: grid;
      gap: 8px;
      text-align: left;
      padding: 14px;
      border-radius: 18px;
      border: 1px solid transparent;
      background: rgba(255, 255, 255, 0.74);
      color: inherit;
      cursor: pointer;
      overflow: hidden;
      transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease, background 150ms ease;
    }

    .topic-button:hover {
      transform: translateY(-2px);
      border-color: rgba(184, 93, 61, 0.28);
      box-shadow: 0 12px 24px rgba(20, 31, 28, 0.08);
    }

    .topic-button.active {
      background:
        linear-gradient(135deg, rgba(184, 93, 61, 0.15), rgba(31, 97, 85, 0.08)),
        rgba(255, 255, 255, 0.95);
      border-color: rgba(184, 93, 61, 0.38);
      box-shadow: 0 16px 28px rgba(20, 31, 28, 0.1);
    }

    .topic-kicker {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      font-size: 0.77rem;
      color: var(--muted);
    }

    .topic-title {
      font-size: 1rem;
      font-weight: 700;
      line-height: 1.35;
      overflow-wrap: break-word;
      hyphens: auto;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .topic-subtitle {
      color: #42544f;
      font-size: 0.84rem;
      line-height: 1.45;
      overflow-wrap: break-word;
      hyphens: auto;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .topic-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .topic-meta span {
      padding: 4px 8px;
      border-radius: 999px;
      background: rgba(31, 97, 85, 0.1);
      color: var(--secondary);
      font-size: 0.74rem;
    }

    .main {
      min-width: 0;
      width: min(100%, 1380px);
      margin-inline: auto;
      padding: 26px clamp(16px, 3vw, 38px) 34px;
    }

    .section-nav {
      position: sticky;
      top: 16px;
      z-index: 8;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 18px;
      padding: 12px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.74);
      border: 1px solid rgba(31, 42, 39, 0.08);
      box-shadow: 0 14px 28px rgba(20, 31, 28, 0.08);
      backdrop-filter: blur(14px);
      overflow-x: auto;
      scrollbar-width: none;
    }

    .section-nav::-webkit-scrollbar {
      display: none;
    }

    .section-jump {
      border: 0;
      border-radius: 999px;
      padding: 10px 14px;
      background: rgba(31, 97, 85, 0.08);
      color: var(--secondary);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      transition: transform 150ms ease, background 150ms ease;
    }

    .section-jump:hover {
      transform: translateY(-1px);
      background: rgba(31, 97, 85, 0.16);
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 18px;
    }

    .topbar-left {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
      min-width: 0;
    }

    .menu-toggle {
      display: none;
      border: 0;
      border-radius: 14px;
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.88);
      box-shadow: var(--shadow-md);
      color: var(--ink);
      font: inherit;
      cursor: pointer;
    }

    .status-pills,
    .topbar-actions {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }

    .status-pill {
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.82);
      border: 1px solid rgba(31, 42, 39, 0.1);
      font-size: 0.84rem;
      color: var(--muted);
      white-space: nowrap;
    }

    .status-pill strong {
      color: var(--ink);
    }

    .book-link {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 0;
      padding: 11px 15px;
      border-radius: 999px;
      text-decoration: none;
      color: #fff;
      background: linear-gradient(135deg, var(--accent), var(--accent-strong));
      font: inherit;
      box-shadow: 0 14px 28px rgba(184, 93, 61, 0.26);
      font-weight: 700;
      cursor: pointer;
      transition: transform 150ms ease, box-shadow 150ms ease, opacity 150ms ease;
    }

    .book-link:hover {
      transform: translateY(-2px);
      box-shadow: 0 18px 30px rgba(184, 93, 61, 0.3);
    }

    .book-link.is-disabled {
      opacity: 0.52;
      pointer-events: none;
      box-shadow: none;
    }

    .book-link.is-local::after {
      content: "helyi";
      display: inline-flex;
      align-items: center;
      padding: 3px 7px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.18);
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .quiz-link {
      background: linear-gradient(135deg, var(--secondary), #16483f);
      box-shadow: 0 14px 28px rgba(31, 97, 85, 0.24);
    }

    .quiz-link:hover {
      box-shadow: 0 18px 30px rgba(31, 97, 85, 0.28);
    }

    .hero-card {
      position: relative;
      overflow: hidden;
      border-radius: var(--radius-xl);
      padding: clamp(22px, 3vw, 34px);
      border: 1px solid rgba(31, 42, 39, 0.1);
      background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 242, 232, 0.88)),
        var(--paper-strong);
      box-shadow: var(--shadow-lg);
    }

    .hero-card::before {
      content: "";
      position: absolute;
      right: -70px;
      bottom: -70px;
      width: 220px;
      height: 220px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(184, 93, 61, 0.18), transparent 70%);
      pointer-events: none;
    }

    .hero-inner {
      position: relative;
      z-index: 1;
      display: grid;
      gap: 18px;
    }

    .hero-layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(280px, 320px);
      gap: 24px;
      align-items: start;
    }

    .hero-copy {
      display: grid;
      gap: 14px;
    }

    .module-badge {
      display: inline-flex;
      width: fit-content;
      padding: 6px 12px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .hero-title {
      margin: 0;
      max-width: 18ch;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1.06;
      text-wrap: balance;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .hero-overview {
      margin: 0;
      max-width: 72ch;
      color: #344541;
      font-size: 1.02rem;
      line-height: 1.75;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .hero-summary-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .hero-stat {
      padding: 15px 16px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid rgba(31, 42, 39, 0.08);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.78);
    }

    .hero-stat span,
    .summary-card span {
      display: block;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--muted);
      text-transform: uppercase;
      margin-bottom: 6px;
    }

    .hero-stat strong {
      display: block;
      font-size: 1.7rem;
      line-height: 1;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      color: var(--ink);
    }

    .hero-stat p {
      margin: 8px 0 0;
      color: #42544f;
      font-size: 0.9rem;
      line-height: 1.45;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .summary-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.95fr) minmax(0, 0.9fr);
      gap: 14px;
    }

    .summary-card {
      padding: 16px 18px;
      border-radius: 22px;
      border: 1px solid rgba(31, 42, 39, 0.08);
      background: rgba(255, 255, 255, 0.9);
      min-width: 0;
    }

    .summary-card p {
      margin: 0;
      line-height: 1.65;
      color: #2d3e39;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .keyword-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .keyword-row span {
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(31, 97, 85, 0.11);
      color: var(--secondary);
      font-size: 0.84rem;
      font-weight: 600;
    }

    .study-route {
      display: grid;
      gap: 10px;
      margin: 0;
    }

    .study-route-step {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 10px;
      align-items: start;
    }

    .study-route-index {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      display: inline-grid;
      place-items: center;
      background: rgba(184, 93, 61, 0.12);
      color: var(--accent);
      font-weight: 700;
      font-size: 0.8rem;
    }

    .study-route-text {
      color: #32443f;
      line-height: 1.55;
      font-size: 0.92rem;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .content-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.22fr) minmax(300px, 0.82fr);
      gap: 22px;
      margin-top: 22px;
      align-items: start;
    }

    .panel {
      border-radius: var(--radius-lg);
      padding: 22px;
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid rgba(31, 42, 39, 0.08);
      box-shadow: var(--shadow-md);
      min-width: 0;
    }

    .panel h2,
    .panel h3 {
      margin: 0 0 14px;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
    }

    .panel h2 {
      font-size: 1.35rem;
      overflow-wrap: break-word;
      hyphens: auto;
      text-wrap: balance;
    }

    .panel h3 {
      font-size: 1.08rem;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .panel-heading {
      display: grid;
      gap: 8px;
      margin-bottom: 16px;
    }

    .section-label {
      display: inline-flex;
      width: fit-content;
      padding: 6px 11px;
      border-radius: 999px;
      background: rgba(31, 97, 85, 0.1);
      color: var(--secondary);
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .panel-heading p,
    .panel-intro {
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
      font-size: 0.94rem;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .aside-stack {
      display: grid;
      gap: 22px;
      position: sticky;
      top: 24px;
    }

    .exam-focus-list {
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 12px;
    }

    .exam-focus-item {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 12px;
      align-items: start;
      padding: 14px 15px;
      border-radius: 16px;
      background: linear-gradient(180deg, rgba(31, 97, 85, 0.08), rgba(31, 97, 85, 0.03));
    }

    .focus-index {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      display: inline-grid;
      place-items: center;
      background: rgba(31, 97, 85, 0.12);
      color: var(--secondary);
      font-weight: 700;
      font-size: 0.82rem;
    }

    .focus-text {
      color: #31433f;
      line-height: 1.62;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .trap-card,
    .scenario-card {
      padding: 15px 16px;
      border-radius: 18px;
      margin-top: 14px;
    }

    .trap-card {
      background: linear-gradient(180deg, var(--warning-soft), rgba(255, 255, 255, 0.7));
      border: 1px solid rgba(155, 106, 25, 0.18);
    }

    .scenario-card {
      background: linear-gradient(180deg, rgba(184, 93, 61, 0.12), rgba(255, 255, 255, 0.76));
      border: 1px solid rgba(184, 93, 61, 0.16);
    }

    .trap-card strong,
    .scenario-card strong {
      display: block;
      margin-bottom: 6px;
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .trap-card p,
    .scenario-card p {
      margin: 0;
      line-height: 1.6;
      color: #354641;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .study-card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
      gap: 14px;
      align-items: stretch;
    }

    .study-card {
      display: flex;
      flex-direction: column;
      border: 1px solid rgba(31, 42, 39, 0.08);
      border-radius: 20px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 238, 228, 0.86));
      padding: 18px;
      text-align: left;
      color: inherit;
      cursor: pointer;
      min-height: 340px;
      overflow: hidden;
      box-shadow: 0 12px 22px rgba(20, 31, 28, 0.07);
      transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
    }

    .study-card:hover {
      transform: translateY(-2px);
      border-color: rgba(184, 93, 61, 0.28);
      box-shadow: 0 16px 28px rgba(20, 31, 28, 0.1);
    }

    .study-card-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 0.8rem;
    }

    .study-card-title {
      margin: 0;
      font-size: 1rem;
      line-height: 1.45;
      overflow-wrap: break-word;
      hyphens: auto;
      display: -webkit-box;
      -webkit-line-clamp: 5;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .study-card-preview {
      margin: 10px 0 0;
      color: #42544f;
      font-size: 0.9rem;
      line-height: 1.58;
      overflow-wrap: break-word;
      hyphens: auto;
      display: -webkit-box;
      -webkit-line-clamp: 6;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .study-card-hint {
      margin-top: 12px;
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(184, 93, 61, 0.1);
      color: var(--accent);
      font-size: 0.8rem;
      font-weight: 700;
    }

    .study-card-footer {
      margin-top: auto;
      padding-top: 14px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .study-badge {
      display: inline-flex;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(31, 97, 85, 0.1);
      color: var(--secondary);
      font-size: 0.78rem;
      font-weight: 700;
    }

    .related-list {
      display: grid;
      gap: 10px;
    }

    .related-button {
      border: 0;
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      border-radius: 18px;
      padding: 14px 16px;
      cursor: pointer;
      font: inherit;
      background: rgba(31, 97, 85, 0.1);
      color: var(--secondary);
      font-weight: 700;
      text-align: left;
      line-height: 1.4;
      white-space: normal;
      overflow-wrap: break-word;
      hyphens: auto;
      transition: transform 150ms ease, background 150ms ease;
    }

    .related-button:hover {
      transform: translateY(-1px);
      background: rgba(31, 97, 85, 0.16);
    }

    .related-button::after {
      content: "→";
      flex: 0 0 auto;
      color: var(--accent);
      font-size: 1rem;
      line-height: 1;
    }

    .nav-panel {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-top: 22px;
    }

    .nav-button {
      flex: 1 1 0;
      display: grid;
      gap: 6px;
      border: 0;
      border-radius: 18px;
      padding: 16px 18px;
      text-align: left;
      cursor: pointer;
      color: inherit;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(244, 238, 228, 0.92));
      box-shadow: var(--shadow-md);
      transition: transform 150ms ease, opacity 150ms ease;
    }

    .nav-button:hover:not(:disabled) {
      transform: translateY(-2px);
    }

    .nav-button:disabled {
      opacity: 0.48;
      cursor: not-allowed;
    }

    .nav-label {
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }

    .nav-title {
      font-weight: 700;
      line-height: 1.35;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .footer-note {
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.86rem;
    }

    .empty-state {
      padding: 24px 18px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.84);
      color: var(--muted);
      line-height: 1.6;
    }

    .overlay {
      display: none;
    }

    .content-shell {
      opacity: 0;
      transform: translateY(12px);
      transition: opacity 220ms ease, transform 220ms ease;
    }

    .content-shell.is-visible {
      opacity: 1;
      transform: translateY(0);
    }

    .sheet-overlay {
      position: fixed;
      inset: 0;
      background: rgba(18, 27, 24, 0.5);
      backdrop-filter: blur(5px);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      z-index: 50;
    }

    .sheet-overlay.open {
      display: flex;
    }

    .study-sheet {
      width: min(760px, 100%);
      max-height: min(88vh, 860px);
      overflow: auto;
      scrollbar-gutter: stable;
      border-radius: 28px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 240, 230, 0.95));
      border: 1px solid rgba(31, 42, 39, 0.12);
      box-shadow: 0 28px 60px rgba(18, 27, 24, 0.24);
      padding: 20px 22px 22px;
    }

    .sheet-header {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 2;
      padding-bottom: 12px;
      background: linear-gradient(180deg, rgba(246, 240, 230, 0.96), rgba(246, 240, 230, 0.74));
      margin-bottom: 16px;
    }

    .sheet-back {
      border: 0;
      background: rgba(31, 97, 85, 0.1);
      color: var(--secondary);
      border-radius: 999px;
      padding: 10px 14px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    .sheet-progress {
      color: var(--muted);
      font-size: 0.9rem;
      font-weight: 600;
    }

    .sheet-title {
      margin: 0 0 14px;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: clamp(1.7rem, 3vw, 2.4rem);
      line-height: 1.08;
      text-wrap: balance;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .sheet-intro {
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.65;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .sheet-section {
      padding: 16px 18px;
      border-radius: 20px;
      margin-bottom: 14px;
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid rgba(31, 42, 39, 0.08);
    }

    .sheet-section h3 {
      margin: 0 0 10px;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: 1.08rem;
    }

    .sheet-section p {
      margin: 0;
      line-height: 1.72;
      color: #334541;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .example-followup {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-top: 18px;
    }

    .example-followup-card {
      padding: 14px 15px;
      border-radius: 18px;
      border: 1px solid rgba(31, 42, 39, 0.08);
      background: rgba(255, 255, 255, 0.86);
    }

    .example-followup-card h4 {
      margin: 0 0 10px;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: 1rem;
    }

    .example-followup-card.is-advantage {
      background: linear-gradient(180deg, rgba(31, 97, 85, 0.1), rgba(255, 255, 255, 0.88));
      border-color: rgba(31, 97, 85, 0.16);
    }

    .example-followup-card.is-disadvantage {
      background: linear-gradient(180deg, rgba(184, 93, 61, 0.12), rgba(255, 255, 255, 0.88));
      border-color: rgba(184, 93, 61, 0.18);
    }

    .sheet-bullet-list {
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 10px;
      color: #334541;
    }

    .sheet-bullet-list li {
      line-height: 1.62;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .sheet-section.is-tip {
      background: linear-gradient(180deg, rgba(31, 97, 85, 0.1), rgba(255, 255, 255, 0.88));
      border-color: rgba(31, 97, 85, 0.14);
    }

    .sheet-section.is-trap {
      background: linear-gradient(180deg, rgba(155, 106, 25, 0.12), rgba(255, 255, 255, 0.88));
      border-color: rgba(155, 106, 25, 0.18);
    }

    .sheet-actions {
      display: flex;
      justify-content: flex-end;
      position: sticky;
      bottom: 0;
      padding-top: 12px;
      background: linear-gradient(180deg, rgba(246, 240, 230, 0), rgba(246, 240, 230, 1) 36%);
      margin-top: 18px;
    }

    .sheet-confirm {
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      background: linear-gradient(135deg, var(--secondary), #16483f);
      color: #fff;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 14px 26px rgba(31, 97, 85, 0.26);
    }

    .quiz-sheet {
      width: min(860px, 100%);
    }

    .quiz-card {
      padding: 18px;
      border-radius: 24px;
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid rgba(31, 42, 39, 0.08);
    }

    .quiz-card-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .quiz-package {
      display: inline-flex;
      align-items: center;
      padding: 6px 11px;
      border-radius: 999px;
      background: rgba(184, 93, 61, 0.12);
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 700;
    }

    .quiz-counter {
      color: var(--muted);
      font-size: 0.86rem;
      font-weight: 700;
    }

    .quiz-question {
      margin: 0;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: clamp(1.3rem, 2.2vw, 1.75rem);
      line-height: 1.35;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .quiz-options {
      display: grid;
      gap: 12px;
      margin-top: 18px;
    }

    .quiz-option {
      width: 100%;
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 14px;
      align-items: start;
      text-align: left;
      border: 1px solid rgba(31, 42, 39, 0.1);
      border-radius: 18px;
      padding: 14px 15px;
      background: rgba(255, 255, 255, 0.94);
      color: inherit;
      font: inherit;
      cursor: pointer;
      transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease, background 150ms ease;
    }

    .quiz-option:hover:not(:disabled) {
      transform: translateY(-1px);
      border-color: rgba(31, 97, 85, 0.24);
      box-shadow: 0 14px 28px rgba(20, 31, 28, 0.08);
    }

    .quiz-option:disabled {
      cursor: default;
    }

    .quiz-option-letter {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      display: inline-grid;
      place-items: center;
      background: rgba(31, 97, 85, 0.1);
      color: var(--secondary);
      font-weight: 700;
      font-size: 0.9rem;
    }

    .quiz-option-text {
      line-height: 1.58;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .quiz-option.is-correct {
      border-color: rgba(31, 97, 85, 0.3);
      background: linear-gradient(180deg, rgba(31, 97, 85, 0.14), rgba(255, 255, 255, 0.96));
    }

    .quiz-option.is-correct .quiz-option-letter {
      background: rgba(31, 97, 85, 0.2);
      color: #114239;
    }

    .quiz-option.is-wrong {
      border-color: rgba(184, 93, 61, 0.32);
      background: linear-gradient(180deg, rgba(184, 93, 61, 0.16), rgba(255, 255, 255, 0.96));
    }

    .quiz-option.is-wrong .quiz-option-letter {
      background: rgba(184, 93, 61, 0.2);
      color: #7d3219;
    }

    .quiz-option.is-muted {
      opacity: 0.74;
    }

    .quiz-feedback {
      margin-top: 16px;
      padding: 15px 16px;
      border-radius: 18px;
      border: 1px solid transparent;
    }

    .quiz-feedback strong {
      display: block;
      margin-bottom: 7px;
      font-size: 0.84rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .quiz-feedback p {
      margin: 0;
      line-height: 1.65;
      overflow-wrap: break-word;
      hyphens: auto;
    }

    .quiz-feedback.is-correct {
      background: linear-gradient(180deg, rgba(31, 97, 85, 0.12), rgba(255, 255, 255, 0.9));
      border-color: rgba(31, 97, 85, 0.18);
      color: #153e37;
    }

    .quiz-feedback.is-wrong {
      background: linear-gradient(180deg, rgba(184, 93, 61, 0.16), rgba(255, 255, 255, 0.92));
      border-color: rgba(184, 93, 61, 0.2);
      color: #6d2f1b;
    }

    .quiz-actions {
      gap: 12px;
    }

    .quiz-next[disabled] {
      opacity: 0.48;
      cursor: not-allowed;
      box-shadow: none;
    }

    .quiz-close {
      background: linear-gradient(135deg, var(--accent), var(--accent-strong));
      box-shadow: 0 14px 26px rgba(184, 93, 61, 0.26);
    }

    .quiz-results {
      display: grid;
      gap: 18px;
    }

    .quiz-result-card {
      padding: 22px;
      border-radius: 24px;
      background: linear-gradient(180deg, rgba(31, 97, 85, 0.12), rgba(255, 255, 255, 0.92));
      border: 1px solid rgba(31, 97, 85, 0.16);
    }

    .quiz-result-card h3 {
      margin: 0 0 8px;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: 1.45rem;
    }

    .quiz-score {
      display: block;
      font-family: "Palatino Linotype", "Book Antiqua", Georgia, serif;
      font-size: clamp(2.2rem, 5vw, 3.1rem);
      line-height: 1;
      margin-bottom: 8px;
    }

    .quiz-percent {
      display: inline-flex;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.86);
      font-weight: 700;
      color: var(--secondary);
    }

    .quiz-result-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .quiz-result-stat {
      padding: 15px 16px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.84);
      border: 1px solid rgba(31, 42, 39, 0.08);
    }

    .quiz-result-stat span {
      display: block;
      font-size: 0.76rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
    }

    .quiz-result-stat strong {
      font-size: 1.2rem;
      color: var(--ink);
    }

    @media (max-width: 1080px) {
      .hero-layout,
      .summary-grid,
      .content-grid {
        grid-template-columns: 1fr;
      }

      .hero-summary-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }

      .aside-stack {
        position: static;
      }
    }

    @media (max-width: 900px) {
      body {
        display: block;
      }

      .menu-toggle {
        display: inline-flex;
      }

      .sidebar {
        position: fixed;
        inset: 0 auto 0 0;
        width: min(88vw, 360px);
        max-width: 360px;
        transform: translateX(-105%);
        transition: transform 220ms ease;
        box-shadow: 18px 0 48px rgba(18, 27, 24, 0.2);
      }

      body.sidebar-open .sidebar {
        transform: translateX(0);
      }

      .overlay {
        display: block;
        position: fixed;
        inset: 0;
        background: rgba(18, 27, 24, 0.38);
        opacity: 0;
        pointer-events: none;
        transition: opacity 220ms ease;
        z-index: 9;
      }

      body.sidebar-open .overlay {
        opacity: 1;
        pointer-events: auto;
      }

      .main {
        padding: 18px 14px 28px;
      }

      .summary-grid,
      .hero-summary-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 760px) {
      .topbar {
        flex-direction: column;
        align-items: stretch;
      }

      .topbar-actions {
        justify-content: flex-start;
      }

      .section-nav {
        top: 10px;
      }

      .nav-panel {
        flex-direction: column;
      }

      .study-sheet {
        padding: 18px 16px 18px;
        border-radius: 24px;
      }

      .quiz-result-grid {
        grid-template-columns: 1fr;
      }

      .example-followup {
        grid-template-columns: 1fr;
      }

      .sheet-header {
        flex-direction: column;
        align-items: stretch;
      }

      .sheet-header {
        padding-bottom: 10px;
      }
    }
  </style>
</head>
<body>
  <aside class="sidebar" id="sidebar">
    <div class="brand">
      <span class="eyebrow">Vezetés és szervezés</span>
      <h1>Vizsgafelkészítő</h1>
      <p>Részletes, kattintható témakörök. Minden kulcspont mögött rövid magyarázat, gyakorlati példa, előnyök, hátrányok és vizsgatipp van.</p>
    </div>

    <label class="search-shell" for="topic-search">
      <span class="search-icon">⌕</span>
      <input id="topic-search" type="search" placeholder="Keress témára vagy kulcsszóra">
    </label>

    <div class="sidebar-meta">
      <span id="result-meta">__TOPIC_COUNT__ témakör</span>
      <span>Bal/jobb nyíl: lapozás</span>
    </div>

    <div class="sidebar-guide">
      <strong>Gyors tanulási rend</strong>
      <p>Válassz témát, olvasd át az összefoglalót, nyisd meg a kulcspontkártyákat, majd ellenőrizd a vizsgafókuszt és a kapcsolódó témákat.</p>
    </div>

    <div class="module-list" id="module-list"></div>
  </aside>

  <div class="overlay" id="overlay"></div>

  <main class="main">
    <div class="topbar">
      <div class="topbar-left">
        <button class="menu-toggle" id="menu-toggle" type="button">☰ Témák</button>
        <div class="status-pills">
          <span class="status-pill"><strong id="status-count">__TOPIC_COUNT__</strong> témakör</span>
          <span class="status-pill"><strong id="status-position">1 / __TOPIC_COUNT__</strong></span>
          <span class="status-pill"><strong id="status-cards">0</strong> tanulókártya</span>
          <span class="status-pill"><strong id="status-module">Alapok</strong></span>
        </div>
      </div>

      <div class="topbar-actions">
        <span class="status-pill">Készítve: <strong>__GENERATED_AT__</strong></span>
        <button id="quiz-button" class="book-link quiz-link is-disabled" type="button" title="Tesztkérdések betöltése">📝 Tesztkérdések</button>
        <a id="book-link" class="book-link is-disabled" href="#" aria-disabled="true" tabindex="-1" title="Könyv-link előkészítése">📘 Könyv</a>
      </div>
    </div>

    <nav class="section-nav" aria-label="Gyors navigáció a témán belül">
      <button class="section-jump" type="button" data-scroll-target="hero-card">Áttekintés</button>
      <button class="section-jump" type="button" data-scroll-target="study-section">Kulcspontok</button>
      <button class="section-jump" type="button" data-scroll-target="focus-section">Vizsgafókusz</button>
      <button class="section-jump" type="button" data-scroll-target="related-section">Kapcsolódó témák</button>
    </nav>

    <section class="content-shell is-visible" id="content-shell">
      <article class="hero-card" id="hero-card">
        <div class="hero-inner">
          <span class="module-badge" id="module-badge"></span>
          <div class="hero-layout">
            <div class="hero-copy">
              <h2 class="hero-title" id="topic-title"></h2>
              <p class="hero-overview" id="topic-overview"></p>
            </div>

            <div class="hero-summary-grid">
              <div class="hero-stat">
                <span>Kulcspont</span>
                <strong id="hero-stat-cards">0</strong>
                <p>Kattintható magyarázatok és gyakorlati példák.</p>
              </div>

              <div class="hero-stat">
                <span>Vizsgafókusz</span>
                <strong id="hero-stat-focus">0</strong>
                <p>A feleletnél kiemelt, visszatérő szempontok.</p>
              </div>

              <div class="hero-stat">
                <span>Kapcsolódó témák</span>
                <strong id="hero-stat-related">0</strong>
                <p>Gyors továbblépés a szorosan összefüggő részekhez.</p>
              </div>
            </div>
          </div>

          <div class="summary-grid">
            <section class="summary-card">
              <span>Tipikus vizsgakérdés</span>
              <p id="sample-question"></p>
            </section>

            <section class="summary-card">
              <span>Kulcsszavak</span>
              <div class="keyword-row" id="keyword-row"></div>
            </section>

            <section class="summary-card">
              <span>Hogyan érdemes tanulni?</span>
              <div class="study-route">
                <div class="study-route-step">
                  <span class="study-route-index">1</span>
                  <div class="study-route-text">Először a fő összefüggést és a tipikus vizsgakérdést rögzítsd.</div>
                </div>
                <div class="study-route-step">
                  <span class="study-route-index">2</span>
                  <div class="study-route-text">Utána nyisd meg sorban a kulcspontkártyákat, és nézd meg a példákat.</div>
                </div>
                <div class="study-route-step">
                  <span class="study-route-index">3</span>
                  <div class="study-route-text">A végén fusd át a vizsgafókuszt és a gyakori hibát, hogy biztosabban felelj.</div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </article>

      <section class="content-grid">
        <div class="panel" id="study-section">
          <div class="panel-heading">
            <span class="section-label">Kulcspontok</span>
            <h2>Kattintható tanulókártyák</h2>
            <p>Nézd végig a legfontosabb állításokat rendezett sorrendben. Minden kártya külön megnyitható, és rövid magyarázatot, példát, vizsgatippet, valamint kiemelt előnyöket és hátrányokat is ad.</p>
          </div>
          <div class="study-card-grid" id="study-card-grid"></div>
        </div>

        <div class="aside-stack">
          <div class="panel" id="focus-section">
            <div class="panel-heading">
              <span class="section-label">Vizsgafókusz</span>
              <h2>Erre figyelj feleletnél</h2>
              <p>Itt vannak azok a kapcsolódási pontok és hangsúlyok, amelyeket érdemes biztosan megemlíteni.</p>
            </div>

            <ol class="exam-focus-list" id="exam-focus-list"></ol>

            <div class="trap-card">
              <strong>Gyakori hiba</strong>
              <p id="common-trap"></p>
            </div>

            <div class="scenario-card">
              <strong>Gyakorlati helyzet</strong>
              <p id="scenario-text"></p>
            </div>
          </div>

          <div class="panel" id="related-section">
            <div class="panel-heading">
              <span class="section-label">Kapcsolódó témák</span>
              <h2>Innen merre tovább?</h2>
              <p>Ezek a részek szorosan összefüggenek az aktuális témával, ezért gyors ismétlésre is jók.</p>
            </div>
            <div class="related-list" id="related-list"></div>
          </div>
        </div>
      </section>

      <div class="nav-panel">
        <button type="button" class="nav-button" id="prev-button"></button>
        <button type="button" class="nav-button" id="next-button"></button>
      </div>

      <p class="footer-note">A felület teljesen offline használható. A <strong>Tesztkérdések</strong> gomb 15 random kérdést indít a tesztbankból, a <strong>Könyv</strong> gomb pedig a helyi PDF-et vagy a publikus könyvoldalt nyitja meg.</p>
    </section>
  </main>

  <div class="sheet-overlay" id="sheet-overlay" aria-hidden="true">
    <div class="study-sheet" role="dialog" aria-modal="true" aria-labelledby="sheet-title">
      <div class="sheet-header">
        <button type="button" class="sheet-back" id="sheet-back">← Vissza</button>
        <div class="sheet-progress" id="sheet-progress"></div>
      </div>
      <h2 class="sheet-title" id="sheet-title"></h2>
      <p class="sheet-intro" id="sheet-intro"></p>

      <section class="sheet-section">
        <h3>Magyarázat</h3>
        <p id="sheet-explanation"></p>
      </section>

      <section class="sheet-section">
        <h3>Gyakorlati példa</h3>
        <p id="sheet-example"></p>
        <div class="example-followup">
          <section class="example-followup-card is-advantage">
            <h4>Előnyök</h4>
            <ul class="sheet-bullet-list" id="sheet-advantages"></ul>
          </section>

          <section class="example-followup-card is-disadvantage">
            <h4>Hátrányok</h4>
            <ul class="sheet-bullet-list" id="sheet-disadvantages"></ul>
          </section>
        </div>
      </section>

      <section class="sheet-section is-tip">
        <h3>Vizsgatipp</h3>
        <p id="sheet-tip"></p>
      </section>

      <section class="sheet-section is-trap">
        <h3>Tipikus hiba</h3>
        <p id="sheet-trap"></p>
      </section>

      <div class="sheet-actions">
        <button type="button" class="sheet-confirm" id="sheet-confirm">Értem</button>
      </div>
    </div>
  </div>

  <div class="sheet-overlay" id="quiz-overlay" aria-hidden="true">
    <div class="study-sheet quiz-sheet" role="dialog" aria-modal="true" aria-labelledby="quiz-title">
      <div class="sheet-header">
        <button type="button" class="sheet-back" id="quiz-back">← Vissza</button>
        <div class="sheet-progress" id="quiz-progress">Teszt</div>
      </div>

      <div id="quiz-stage">
        <span class="section-label">Tesztkérdések</span>
        <h2 class="sheet-title" id="quiz-title">VezSzerv mini teszt</h2>
        <p class="sheet-intro" id="quiz-intro"></p>

        <section class="quiz-card">
          <div class="quiz-card-head">
            <span class="quiz-package" id="quiz-package"></span>
            <span class="quiz-counter" id="quiz-counter"></span>
          </div>
          <h3 class="quiz-question" id="quiz-question"></h3>
          <div class="quiz-options" id="quiz-options"></div>
          <div class="quiz-feedback" id="quiz-feedback" hidden>
            <strong id="quiz-feedback-title"></strong>
            <p id="quiz-feedback-text"></p>
          </div>
        </section>
      </div>

      <div class="quiz-results" id="quiz-results" hidden>
        <span class="section-label">Eredmény</span>
        <div class="quiz-result-card">
          <h3>Mini teszt kiértékelés</h3>
          <span class="quiz-score" id="quiz-score"></span>
          <span class="quiz-percent" id="quiz-percent"></span>
          <p class="sheet-intro" id="quiz-result-text"></p>
        </div>

        <div class="quiz-result-grid">
          <div class="quiz-result-stat">
            <span>Helyes válasz</span>
            <strong id="quiz-correct-count"></strong>
          </div>
          <div class="quiz-result-stat">
            <span>Hibás válasz</span>
            <strong id="quiz-wrong-count"></strong>
          </div>
          <div class="quiz-result-stat">
            <span>Kérdésszám</span>
            <strong id="quiz-total-count"></strong>
          </div>
        </div>
      </div>

      <div class="sheet-actions quiz-actions">
        <button type="button" class="sheet-confirm quiz-next" id="quiz-next" disabled>Következő</button>
        <button type="button" class="sheet-confirm quiz-close" id="quiz-close" hidden>Bezárás</button>
      </div>
    </div>
  </div>

  <script id="topic-data" type="application/json">__TOPIC_DATA__</script>
  <script>
    const payload = JSON.parse(document.getElementById("topic-data").textContent);
    const topics = payload.topics || [];
    const quizBank = payload.quizBank || { selectionCount: 15, questionCount: 0, questions: [] };
    const topicById = new Map(topics.map((topic) => [topic.id, topic]));
    const modules = Array.from(new Set(topics.map((topic) => topic.module)));

    const state = {
      filter: "",
      currentId: topics.length ? topics[0].id : null,
      activeStudyIndex: null,
      quizSession: null,
      quizResultsVisible: false,
    };

    const moduleList = document.getElementById("module-list");
    const resultMeta = document.getElementById("result-meta");
    const searchInput = document.getElementById("topic-search");
    const contentShell = document.getElementById("content-shell");
    const menuToggle = document.getElementById("menu-toggle");
    const overlay = document.getElementById("overlay");
    const moduleBadge = document.getElementById("module-badge");
    const titleEl = document.getElementById("topic-title");
    const overviewEl = document.getElementById("topic-overview");
    const sampleQuestionEl = document.getElementById("sample-question");
    const keywordRow = document.getElementById("keyword-row");
    const examFocusList = document.getElementById("exam-focus-list");
    const commonTrapEl = document.getElementById("common-trap");
    const scenarioTextEl = document.getElementById("scenario-text");
    const studyCardGrid = document.getElementById("study-card-grid");
    const relatedList = document.getElementById("related-list");
    const prevButton = document.getElementById("prev-button");
    const nextButton = document.getElementById("next-button");
    const statusPosition = document.getElementById("status-position");
    const statusModule = document.getElementById("status-module");
    const statusCards = document.getElementById("status-cards");
    const statusCount = document.getElementById("status-count");
    const heroStatCards = document.getElementById("hero-stat-cards");
    const heroStatFocus = document.getElementById("hero-stat-focus");
    const heroStatRelated = document.getElementById("hero-stat-related");
    const sheetOverlay = document.getElementById("sheet-overlay");
    const sheetBack = document.getElementById("sheet-back");
    const sheetConfirm = document.getElementById("sheet-confirm");
    const sheetTitle = document.getElementById("sheet-title");
    const sheetIntro = document.getElementById("sheet-intro");
    const sheetExplanation = document.getElementById("sheet-explanation");
    const sheetExample = document.getElementById("sheet-example");
    const sheetAdvantages = document.getElementById("sheet-advantages");
    const sheetDisadvantages = document.getElementById("sheet-disadvantages");
    const sheetTip = document.getElementById("sheet-tip");
    const sheetTrap = document.getElementById("sheet-trap");
    const sheetProgress = document.getElementById("sheet-progress");
    const sectionJumpButtons = document.querySelectorAll("[data-scroll-target]");
    const quizButton = document.getElementById("quiz-button");
    const bookLink = document.getElementById("book-link");
    const quizOverlay = document.getElementById("quiz-overlay");
    const quizBack = document.getElementById("quiz-back");
    const quizProgress = document.getElementById("quiz-progress");
    const quizStage = document.getElementById("quiz-stage");
    const quizResults = document.getElementById("quiz-results");
    const quizTitle = document.getElementById("quiz-title");
    const quizIntro = document.getElementById("quiz-intro");
    const quizPackage = document.getElementById("quiz-package");
    const quizCounter = document.getElementById("quiz-counter");
    const quizQuestion = document.getElementById("quiz-question");
    const quizOptions = document.getElementById("quiz-options");
    const quizFeedback = document.getElementById("quiz-feedback");
    const quizFeedbackTitle = document.getElementById("quiz-feedback-title");
    const quizFeedbackText = document.getElementById("quiz-feedback-text");
    const quizNext = document.getElementById("quiz-next");
    const quizClose = document.getElementById("quiz-close");
    const quizScore = document.getElementById("quiz-score");
    const quizPercent = document.getElementById("quiz-percent");
    const quizResultText = document.getElementById("quiz-result-text");
    const quizCorrectCount = document.getElementById("quiz-correct-count");
    const quizWrongCount = document.getElementById("quiz-wrong-count");
    const quizTotalCount = document.getElementById("quiz-total-count");

    statusCount.textContent = String(topics.length);
    configureBookLink();
    configureQuizButton();

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function topicHash(topic) {
      return `#tema-${topic.slug}`;
    }

    function previewText(value, limit = 120) {
      const normalized = String(value || "").replace(/\\s+/g, " ").trim();
      if (!normalized) {
        return "";
      }

      if (normalized.length <= limit) {
        return normalized;
      }

      return `${normalized.slice(0, limit).trimEnd()}...`;
    }

    function shuffleArray(items) {
      const clone = [...items];
      for (let index = clone.length - 1; index > 0; index -= 1) {
        const swapIndex = Math.floor(Math.random() * (index + 1));
        [clone[index], clone[swapIndex]] = [clone[swapIndex], clone[index]];
      }
      return clone;
    }

    function optionLetter(index) {
      return String.fromCharCode(65 + index);
    }

    function configureBookLink() {
      const localUrl = payload.bookUrl || "";
      const shareUrl = payload.bookShareUrl || "";
      const isLocalContext = window.location.protocol === "file:";
      const resolvedUrl = isLocalContext && localUrl ? localUrl : shareUrl;

      bookLink.classList.remove("is-disabled", "is-local");
      bookLink.removeAttribute("aria-disabled");
      bookLink.removeAttribute("tabindex");

      if (resolvedUrl) {
        bookLink.href = resolvedUrl;
        bookLink.target = "_blank";
        bookLink.rel = "noopener noreferrer";
        if (isLocalContext && localUrl) {
          bookLink.title = "Könyv PDF megnyitása a helyi gépen";
          bookLink.classList.add("is-local");
        } else {
          bookLink.title = "A könyv hivatalos online oldalának megnyitása";
        }
        return;
      }

      bookLink.href = "#";
      bookLink.target = "";
      bookLink.rel = "";
      bookLink.classList.add("is-disabled");
      bookLink.setAttribute("aria-disabled", "true");
      bookLink.setAttribute("tabindex", "-1");
      bookLink.title = localUrl
        ? "A GitHub-változatban a könyv nincs beágyazva. Később külső könyv URL is megadható."
        : "Könyv PDF nem található.";
    }

    function configureQuizButton() {
      const questionCount = Number(quizBank.questionCount || (quizBank.questions || []).length || 0);
      quizButton.classList.remove("is-disabled");
      quizButton.disabled = false;
      quizButton.title = `Random ${Math.min(questionCount, Number(quizBank.selectionCount) || 15)} kérdés indítása a tesztbankból`;

      if (questionCount) {
        return;
      }

      quizButton.classList.add("is-disabled");
      quizButton.disabled = true;
      quizButton.title = "Tesztkérdések nem érhetők el.";
    }

    function createQuizSession() {
      const availableQuestions = Array.isArray(quizBank.questions) ? quizBank.questions : [];
      const selectionCount = Math.min(
        Math.max(Number(quizBank.selectionCount) || 15, 1),
        availableQuestions.length
      );
      const questions = shuffleArray(availableQuestions)
        .slice(0, selectionCount)
        .map((question) => ({
          id: question.id,
          prompt: question.prompt,
          package: question.package || "",
          explanation: question.explanation,
          answerIndex: null,
          answeredCorrectly: false,
          options: shuffleArray(question.options || []).map((option, optionIndex) => ({
            id: `${question.id}-${optionIndex}`,
            text: option.text,
            isCorrect: Boolean(option.isCorrect),
          })),
        }));

      return {
        currentIndex: 0,
        correctAnswers: 0,
        questions,
      };
    }

    function closeQuizOverlay() {
      state.quizSession = null;
      state.quizResultsVisible = false;
      quizOverlay.classList.remove("open");
      quizOverlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("quiz-open");
    }

    function openQuizOverlay() {
      if (!quizBank.questions || !quizBank.questions.length) {
        return;
      }

      closeStudySheet();
      closeSidebar();
      state.quizSession = createQuizSession();
      state.quizResultsVisible = false;
      renderQuizQuestion();
      quizOverlay.classList.add("open");
      quizOverlay.setAttribute("aria-hidden", "false");
      document.body.classList.add("quiz-open");
    }

    function getCurrentQuizQuestion() {
      if (!state.quizSession) {
        return null;
      }
      return state.quizSession.questions[state.quizSession.currentIndex] || null;
    }

    function renderQuizQuestion() {
      const session = state.quizSession;
      const question = getCurrentQuizQuestion();
      if (!session || !question) {
        return;
      }

      state.quizResultsVisible = false;
      quizStage.hidden = false;
      quizResults.hidden = true;
      quizClose.hidden = true;
      quizNext.hidden = false;

      const total = session.questions.length;
      const currentNumber = session.currentIndex + 1;
      const hasAnswered = Number.isInteger(question.answerIndex);
      const selectedOption = hasAnswered ? question.options[question.answerIndex] : null;
      const correctOption = question.options.find((option) => option.isCorrect) || null;

      quizProgress.textContent = `Kérdés ${currentNumber} / ${total}`;
      quizTitle.textContent = "VezSzerv mini teszt";
      quizIntro.textContent = `${total} randomizált kérdés a megadott tesztbankból. A válaszok sorrendje minden körben megkeveredik.`;
      quizPackage.textContent = question.package || "Tesztbank";
      quizPackage.hidden = !question.package;
      quizCounter.textContent = `Forráskérdés #${question.id}`;
      quizQuestion.textContent = question.prompt;

      quizOptions.innerHTML = question.options
        .map((option, optionIndex) => {
          const classes = ["quiz-option"];
          if (hasAnswered) {
            if (option.isCorrect) {
              classes.push("is-correct");
            } else if (question.answerIndex === optionIndex) {
              classes.push("is-wrong");
            } else {
              classes.push("is-muted");
            }
          }

          return `
            <button
              type="button"
              class="${classes.join(" ")}"
              data-quiz-option="${optionIndex}"
              ${hasAnswered ? "disabled" : ""}
            >
              <span class="quiz-option-letter">${optionLetter(optionIndex)}</span>
              <span class="quiz-option-text">${escapeHtml(option.text)}</span>
            </button>
          `;
        })
        .join("");

      quizOptions.querySelectorAll("[data-quiz-option]").forEach((button) => {
        button.addEventListener("click", () => submitQuizAnswer(Number(button.dataset.quizOption)));
      });

      if (hasAnswered && selectedOption && correctOption) {
        const isCorrect = Boolean(selectedOption.isCorrect);
        quizFeedback.hidden = false;
        quizFeedback.className = `quiz-feedback ${isCorrect ? "is-correct" : "is-wrong"}`;
        quizFeedbackTitle.textContent = isCorrect ? "Helyes válasz" : "Nem ez a helyes válasz";
        quizFeedbackText.textContent = isCorrect
          ? question.explanation
          : `${question.explanation} A helyes válasz: ${correctOption.text}.`;
      } else {
        quizFeedback.hidden = true;
        quizFeedback.className = "quiz-feedback";
        quizFeedbackTitle.textContent = "";
        quizFeedbackText.textContent = "";
      }

      quizNext.disabled = !hasAnswered;
      quizNext.textContent = currentNumber === total ? "Eredmény" : "Következő";
    }

    function submitQuizAnswer(optionIndex) {
      const session = state.quizSession;
      const question = getCurrentQuizQuestion();
      if (!session || !question || Number.isInteger(question.answerIndex)) {
        return;
      }

      question.answerIndex = optionIndex;
      question.answeredCorrectly = Boolean(question.options[optionIndex] && question.options[optionIndex].isCorrect);
      if (question.answeredCorrectly) {
        session.correctAnswers += 1;
      }

      renderQuizQuestion();
    }

    function showQuizResults() {
      const session = state.quizSession;
      if (!session) {
        return;
      }

      state.quizResultsVisible = true;
      quizStage.hidden = true;
      quizResults.hidden = false;
      quizNext.hidden = true;
      quizClose.hidden = false;

      const total = session.questions.length;
      const correct = session.correctAnswers;
      const wrong = total - correct;
      const percent = total ? Math.round((correct / total) * 100) : 0;

      quizProgress.textContent = "Eredmény";
      quizScore.textContent = `${correct} / ${total}`;
      quizPercent.textContent = `${percent}%`;
      quizCorrectCount.textContent = String(correct);
      quizWrongCount.textContent = String(wrong);
      quizTotalCount.textContent = String(total);

      if (percent >= 80) {
        quizResultText.textContent = "Erős eredmény. Már közel vagy a biztos vizsgateljesítéshez, érdemes még a hibás kérdéseket gyorsan átnézni.";
      } else if (percent >= 60) {
        quizResultText.textContent = "Jó alapok vannak meg. A következő körben főleg a bizonytalan vagy hibás kérdések indoklásait érdemes átismételni.";
      } else {
        quizResultText.textContent = "Van még mit erősíteni. Érdemes visszamenni a kapcsolódó témákhoz, majd újabb random tesztkört indítani.";
      }
    }

    function getCurrentTopic() {
      return topicById.get(state.currentId) || null;
    }

    function filteredTopics() {
      const query = state.filter.trim().toLowerCase();
      if (!query) {
        return topics;
      }

      return topics.filter((topic) => {
        const cardBlob = (topic.studyCards || [])
          .map((card) => [
            card.title,
            card.explanation,
            card.example,
            ...(card.advantages || []),
            ...(card.disadvantages || []),
            card.examTip,
            card.commonTrap,
          ].join(" "))
          .join(" ");
        const haystack = [
          topic.title,
          topic.module,
          topic.overview,
          topic.sampleQuestion,
          topic.commonTrap,
          topic.scenario,
          ...(topic.examFocus || []),
          ...(topic.keywords || []),
          cardBlob,
        ].join(" ").toLowerCase();
        return haystack.includes(query);
      });
    }

    function getTopicIndex(topicId) {
      return topics.findIndex((topic) => topic.id === topicId);
    }

    function closeSidebar() {
      document.body.classList.remove("sidebar-open");
    }

    function openSidebar() {
      document.body.classList.add("sidebar-open");
    }

    function closeStudySheet() {
      state.activeStudyIndex = null;
      sheetOverlay.classList.remove("open");
      sheetOverlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("sheet-open");
    }

    function openStudySheet(index) {
      const topic = getCurrentTopic();
      if (!topic || !topic.studyCards || !topic.studyCards[index]) {
        return;
      }
      const card = topic.studyCards[index];
      state.activeStudyIndex = index;
      sheetTitle.textContent = card.title;
      sheetIntro.textContent = `A(z) ${topic.title} témakör ${index + 1}. kulcspontját látod, rövid magyarázattal, példával, előnyökkel és hátrányokkal.`;
      sheetExplanation.textContent = card.explanation;
      sheetExample.textContent = card.example;
      sheetAdvantages.innerHTML = (card.advantages || [])
        .map((item) => `<li>${escapeHtml(item)}</li>`)
        .join("");
      sheetDisadvantages.innerHTML = (card.disadvantages || [])
        .map((item) => `<li>${escapeHtml(item)}</li>`)
        .join("");
      sheetTip.textContent = card.examTip;
      sheetTrap.textContent = card.commonTrap;
      sheetProgress.textContent = `${index + 1} / ${topic.studyCards.length}`;
      sheetOverlay.classList.add("open");
      sheetOverlay.setAttribute("aria-hidden", "false");
      document.body.classList.add("sheet-open");
    }

    function renderSidebar() {
      const visibleTopics = filteredTopics();
      resultMeta.textContent = `${visibleTopics.length} / ${topics.length} témakör látszik`;

      if (!visibleTopics.length) {
        moduleList.innerHTML = `<div class="empty-state">Nincs találat erre: <strong>${escapeHtml(state.filter)}</strong>. Próbálj rövidebb kulcsszót vagy töröld a keresést.</div>`;
        return;
      }

      moduleList.innerHTML = modules.map((module) => {
        const items = visibleTopics.filter((topic) => topic.module === module);
        if (!items.length) {
          return "";
        }

        const buttons = items.map((topic) => {
          const isActive = topic.id === state.currentId;
          const tags = topic.keywords.slice(0, 2).map((keyword) => `<span>${escapeHtml(keyword)}</span>`).join("");
          const cardCount = (topic.studyCards || []).length;
          const subtitle = previewText(topic.overview, 88);
          return `
            <button class="topic-button${isActive ? " active" : ""}" type="button" data-topic-id="${topic.id}">
              <div class="topic-kicker">
                <span>${String(topic.id).padStart(2, "0")}.</span>
                <span>${cardCount} kártya</span>
              </div>
              <div class="topic-title">${escapeHtml(topic.title)}</div>
              <div class="topic-subtitle">${escapeHtml(subtitle)}</div>
              <div class="topic-meta">${tags}</div>
            </button>
          `;
        }).join("");

        return `
          <section class="module-group">
            <div class="module-header">
              <span>${escapeHtml(module)}</span>
              <span class="module-count">${items.length}</span>
            </div>
            ${buttons}
          </section>
        `;
      }).join("");

      moduleList.querySelectorAll("[data-topic-id]").forEach((button) => {
        button.addEventListener("click", () => {
          setCurrentTopic(Number(button.dataset.topicId));
          if (window.innerWidth <= 900) {
            closeSidebar();
          }
        });
      });
    }

    function renderNavigation(currentIndex) {
      const previous = currentIndex > 0 ? topics[currentIndex - 1] : null;
      const next = currentIndex < topics.length - 1 ? topics[currentIndex + 1] : null;

      prevButton.disabled = !previous;
      nextButton.disabled = !next;
      prevButton.innerHTML = previous
        ? `<span class="nav-label">Előző témakör</span><span class="nav-title">${escapeHtml(previous.title)}</span>`
        : `<span class="nav-label">Előző témakör</span><span class="nav-title">Ez az első témakör.</span>`;
      nextButton.innerHTML = next
        ? `<span class="nav-label">Következő témakör</span><span class="nav-title">${escapeHtml(next.title)}</span>`
        : `<span class="nav-label">Következő témakör</span><span class="nav-title">Ez az utolsó témakör.</span>`;

      prevButton.onclick = previous ? () => setCurrentTopic(previous.id) : null;
      nextButton.onclick = next ? () => setCurrentTopic(next.id) : null;
    }

    function renderTopic() {
      const topic = getCurrentTopic();
      if (!topic) {
        return;
      }

      closeStudySheet();

      const index = getTopicIndex(topic.id);
      document.title = `${topic.title} • VezSzerv vizsgafelkészítő`;
      statusPosition.textContent = `${index + 1} / ${topics.length}`;
      statusModule.textContent = topic.module;
      statusCards.textContent = String((topic.studyCards || []).length);
      heroStatCards.textContent = String((topic.studyCards || []).length);
      heroStatFocus.textContent = String((topic.examFocus || []).length);
      heroStatRelated.textContent = String((topic.relatedTopicIds || []).length);

      moduleBadge.textContent = `${String(topic.id).padStart(2, "0")}. témakör • ${topic.module}`;
      titleEl.textContent = topic.title;
      overviewEl.textContent = topic.overview;
      sampleQuestionEl.textContent = topic.sampleQuestion;
      commonTrapEl.textContent = topic.commonTrap;
      scenarioTextEl.textContent = topic.scenario;

      keywordRow.innerHTML = topic.keywords.map((keyword) => `<span>${escapeHtml(keyword)}</span>`).join("");
      examFocusList.innerHTML = topic.examFocus.map((item, itemIndex) => `
        <li class="exam-focus-item">
          <span class="focus-index">${itemIndex + 1}</span>
          <div class="focus-text">${escapeHtml(item)}</div>
        </li>
      `).join("");

      studyCardGrid.innerHTML = topic.studyCards.map((card, cardIndex) => `
        <button type="button" class="study-card" data-study-index="${cardIndex}">
          <div class="study-card-top">
            <span>${String(cardIndex + 1).padStart(2, "0")}.</span>
            <span>Magyarázat + példa</span>
          </div>
          <h3 class="study-card-title">${escapeHtml(card.title)}</h3>
          <p class="study-card-preview">${escapeHtml(previewText(card.explanation, 132))}</p>
          <div class="study-card-footer">
            <span class="study-badge">Vizsgatipp</span>
            <span class="study-badge">Gyakorlati példa</span>
            <span class="study-badge">Előnyök + hátrányok</span>
          </div>
          <span class="study-card-hint">Részletek megnyitása →</span>
        </button>
      `).join("");

      studyCardGrid.querySelectorAll("[data-study-index]").forEach((button) => {
        button.addEventListener("click", () => openStudySheet(Number(button.dataset.studyIndex)));
      });

      relatedList.innerHTML = topic.relatedTopicIds
        .map((relatedId) => topicById.get(relatedId))
        .filter(Boolean)
        .map((relatedTopic) => `<button type="button" class="related-button" data-related-id="${relatedTopic.id}">${escapeHtml(relatedTopic.title)}</button>`)
        .join("");

      relatedList.querySelectorAll("[data-related-id]").forEach((button) => {
        button.addEventListener("click", () => setCurrentTopic(Number(button.dataset.relatedId)));
      });

      renderNavigation(index);
      renderSidebar();
      contentShell.classList.remove("is-visible");
      requestAnimationFrame(() => contentShell.classList.add("is-visible"));
    }

    function syncFromHash() {
      const raw = window.location.hash.replace(/^#/, "");
      if (!raw.startsWith("tema-")) {
        return false;
      }
      const slug = raw.replace(/^tema-/, "");
      const match = topics.find((topic) => topic.slug === slug);
      if (!match) {
        return false;
      }
      state.currentId = match.id;
      renderTopic();
      return true;
    }

    function setCurrentTopic(topicId, pushHash = true) {
      if (!topicById.has(topicId)) {
        return;
      }
      state.currentId = topicId;
      renderTopic();
      if (pushHash) {
        const nextHash = topicHash(topicById.get(topicId));
        if (window.location.hash !== nextHash) {
          window.location.hash = nextHash;
        }
      }
    }

    searchInput.addEventListener("input", () => {
      state.filter = searchInput.value;
      renderSidebar();
    });

    menuToggle.addEventListener("click", () => {
      if (document.body.classList.contains("sidebar-open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    overlay.addEventListener("click", closeSidebar);
    sheetBack.addEventListener("click", closeStudySheet);
    sheetConfirm.addEventListener("click", closeStudySheet);
    quizButton.addEventListener("click", openQuizOverlay);
    quizBack.addEventListener("click", closeQuizOverlay);
    quizNext.addEventListener("click", () => {
      const session = state.quizSession;
      if (!session) {
        return;
      }

      if (state.quizResultsVisible) {
        closeQuizOverlay();
        return;
      }

      const isLastQuestion = session.currentIndex === session.questions.length - 1;
      if (isLastQuestion) {
        showQuizResults();
        return;
      }

      session.currentIndex += 1;
      renderQuizQuestion();
    });
    quizClose.addEventListener("click", closeQuizOverlay);
    sectionJumpButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const targetId = button.dataset.scrollTarget;
        const target = targetId ? document.getElementById(targetId) : null;
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });
    sheetOverlay.addEventListener("click", (event) => {
      if (event.target === sheetOverlay) {
        closeStudySheet();
      }
    });
    quizOverlay.addEventListener("click", (event) => {
      if (event.target === quizOverlay) {
        closeQuizOverlay();
      }
    });

    window.addEventListener("hashchange", syncFromHash);
    window.addEventListener("keydown", (event) => {
      const target = event.target;
      const isEditable = target instanceof HTMLElement && (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT" ||
        target.isContentEditable
      );

      if (isEditable) {
        return;
      }

      if (sheetOverlay.classList.contains("open")) {
        if (event.key === "Escape") {
          event.preventDefault();
          closeStudySheet();
        }
        return;
      }

      if (quizOverlay.classList.contains("open")) {
        if (event.key === "Escape") {
          event.preventDefault();
          closeQuizOverlay();
        }
        return;
      }

      const currentIndex = getTopicIndex(state.currentId);
      if (event.key === "ArrowLeft" && currentIndex > 0) {
        event.preventDefault();
        setCurrentTopic(topics[currentIndex - 1].id);
      }
      if (event.key === "ArrowRight" && currentIndex < topics.length - 1) {
        event.preventDefault();
        setCurrentTopic(topics[currentIndex + 1].id);
      }
      if (event.key === "Escape") {
        closeSidebar();
      }
    });

    renderSidebar();
    if (!syncFromHash() && topics.length) {
      setCurrentTopic(topics[0].id, false);
      window.location.hash = topicHash(topics[0]);
    }
  </script>
</body>
</html>
"""

    return (
        template
        .replace("__TOPIC_DATA__", topic_json)
        .replace("__GENERATED_AT__", generated_at)
        .replace("__TOPIC_COUNT__", str(topic_count))
    )


def main() -> None:
    args = parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    html = build_html(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Vizsgafelkészítő HTML app elkészült: {args.output}")


if __name__ == "__main__":
    main()
