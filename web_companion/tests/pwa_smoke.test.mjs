import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, dirname } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

const swSrc = readFileSync(join(ROOT, "sw.js"), "utf8");
const appSrc = readFileSync(join(ROOT, "app.js"), "utf8");
const indexSrc = readFileSync(join(ROOT, "index.html"), "utf8");
const manifestSrc = JSON.parse(readFileSync(join(ROOT, "manifest.webmanifest"), "utf8"));

// Bug #1: sw.js caches.match ohne ignoreSearch:true
test("sw.js caches.match hat ignoreSearch:true (Bug #1)", () => {
  assert.ok(
    swSrc.includes("ignoreSearch: true"),
    "sw.js muss { ignoreSearch: true } in caches.match enthalten"
  );
});

// Bug #2: sw.js fehlte self.skipWaiting()
test("sw.js ruft self.skipWaiting() im install-Handler auf (Bug #2)", () => {
  assert.ok(
    swSrc.includes("self.skipWaiting()"),
    "sw.js muss self.skipWaiting() enthalten"
  );
});

// Bug #3: sw.js fehlte self.clients.claim()
test("sw.js ruft self.clients.claim() im activate-Handler auf (Bug #3)", () => {
  assert.ok(
    swSrc.includes("self.clients.claim()"),
    "sw.js muss self.clients.claim() enthalten"
  );
});

// Bug #4+5: app.js escHtml-Funktion vorhanden und in renderResults + buildStatCards genutzt
test("app.js definiert escHtml-Funktion (Bug #4/#5)", () => {
  assert.ok(
    appSrc.includes("function escHtml("),
    "app.js muss escHtml-Funktion definieren"
  );
});

test("app.js nutzt escHtml für entry.name in renderResults (Bug #4)", () => {
  assert.ok(
    appSrc.includes("escHtml(entry.name)"),
    "renderResults muss entry.name mit escHtml absichern"
  );
});

test("app.js nutzt escHtml für entry.output.message in renderResults (Bug #4)", () => {
  assert.ok(
    appSrc.includes("escHtml(entry.output.message"),
    "renderResults muss entry.output.message mit escHtml absichern"
  );
});

test("app.js nutzt escHtml für job.ocr_language in buildStatCards (Bug #5)", () => {
  assert.ok(
    appSrc.includes("escHtml(value)"),
    "buildStatCards muss value (inkl. ocr_language) mit escHtml absichern"
  );
});

// Bug #6: manifest.webmanifest - Icons 192/512 ohne purpose:'any'
test("manifest.webmanifest hat 4 Icons (Bug #6)", () => {
  assert.equal(manifestSrc.icons.length, 4, "Manifest muss 4 Icons haben");
});

test("manifest.webmanifest hat 2 any-Icons (Bug #6)", () => {
  const anyIcons = manifestSrc.icons.filter(i => i.purpose === "any");
  assert.equal(anyIcons.length, 2, "Manifest muss 2 Icons mit purpose:any haben");
});

test("manifest.webmanifest hat 2 maskable-Icons", () => {
  const maskable = manifestSrc.icons.filter(i => i.purpose === "maskable");
  assert.equal(maskable.length, 2, "Manifest muss 2 maskable-Icons haben");
});

// Bug #7: index.html apple-touch-icon fehlt
test("index.html hat apple-touch-icon (Bug #7)", () => {
  assert.ok(
    indexSrc.includes("apple-touch-icon"),
    "index.html muss einen apple-touch-icon-Link haben"
  );
});

// Bug #8: exportCurrentState Anchor ohne DOM-Anhang (iOS Safari / Firefox)
test("app.js hängt Export-Anchor ins DOM (Bug #8)", () => {
  assert.ok(
    appSrc.includes("document.body.appendChild(anchor)"),
    "exportCurrentState muss den Anchor vor click() ins DOM einhängen"
  );
});

test("app.js entfernt Export-Anchor nach click() wieder aus dem DOM (Bug #8)", () => {
  assert.ok(
    appSrc.includes("document.body.removeChild(anchor)"),
    "exportCurrentState muss den Anchor nach click() aus dem DOM entfernen"
  );
});

describe("iOS PWA-Härtung", () => {
  const html = readFileSync(join(ROOT, "index.html"), "utf8");
  const css = readFileSync(join(ROOT, "style.css"), "utf8");
  const sw = readFileSync(join(ROOT, "sw.js"), "utf8");

  test("viewport enthält viewport-fit=cover (Notch/Dynamic Island)", () => {
    assert.match(html, /viewport-fit=cover/);
  });

  test("apple-touch-icon zeigt auf apple-touch-icon-180.png", () => {
    assert.match(html, /apple-touch-icon.*apple-touch-icon-180\.png/s);
  });

  test("apple-mobile-web-app-title ist vorhanden", () => {
    assert.match(html, /apple-mobile-web-app-title/);
  });

  test("apple-mobile-web-app-status-bar-style ist vorhanden", () => {
    assert.match(html, /apple-mobile-web-app-status-bar-style/);
  });

  test("KEIN apple-mobile-web-app-capable (deprecated seit iOS 11.3)", () => {
    assert.doesNotMatch(html, /apple-mobile-web-app-capable/, "deprecated seit iOS 11.3 — darf nicht gesetzt sein");
  });

  test("apple-touch-icon-180.png existiert physisch in icons/", () => {
    assert.ok(existsSync(join(ROOT, "icons", "apple-touch-icon-180.png")));
  });

  test("style.css enthält safe-area-inset-top", () => {
    assert.match(css, /safe-area-inset-top/);
  });

  test("style.css enthält safe-area-inset-bottom", () => {
    assert.match(css, /safe-area-inset-bottom/);
  });

  test("sw.js enthält apple-touch-icon-180.png in ASSETS", () => {
    assert.match(sw, /apple-touch-icon-180\.png/);
  });
});
