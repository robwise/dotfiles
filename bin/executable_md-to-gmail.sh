#!/bin/bash
#
# md-to-gmail.sh — Turn the Markdown on your clipboard into rich text and paste
# it into the frontmost window (e.g. a Gmail compose box you've clicked into).
#
# Meant to be called from Keyboard Maestro (Execute a Shell Script). Typical use:
#   1. Copy some Markdown.
#   2. Click into a Gmail compose draft.
#   3. Trigger this script -> formatted text appears.
#
# Requires pandoc (brew install pandoc). pbpaste / osascript are built into macOS.
#
# Env vars:
#   MD2GMAIL_PASTE=0   Only load the clipboard; let Keyboard Maestro paste itself.

set -uo pipefail

# Keyboard Maestro runs scripts with a bare PATH, so name the dirs we rely on.
# Both Homebrew prefixes are listed: /opt/homebrew (Apple Silicon), /usr/local (Intel).
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

notify() { osascript -e "display notification \"$1\" with title \"Markdown → Gmail\"" >/dev/null 2>&1; }

# 1. Grab the Markdown sitting on the clipboard.
markdown="$(pbpaste)"
if [[ -z "${markdown//[[:space:]]/}" ]]; then
  notify "Clipboard is empty — nothing to convert."
  exit 0
fi

# 2. Markdown -> HTML fragment. gfm gives tables, lists, strikethrough, autolinks.
#    Want single newlines kept as <br>? Change gfm to gfm+hard_line_breaks.
html="$(printf '%s' "$markdown" | pandoc -f gfm -t html)" || {
  notify "pandoc failed — is it installed? (brew install pandoc)"
  exit 1
}

# 3. Put the HTML on the clipboard so Gmail renders it with its own font, keeping
#    the original Markdown as the plain-text fallback for non-rich-text targets.
osascript -l JavaScript - "$html" "$markdown" <<'JXA' || { notify "Could not set the clipboard."; exit 1; }
ObjC.import("AppKit");
function run(argv) {
  var pasteboard = $.NSPasteboard.generalPasteboard;
  pasteboard.clearContents;
  pasteboard.setStringForType($(argv[0]), "public.html");
  pasteboard.setStringForType($(argv[1]), "public.utf8-plain-text");
}
JXA

# 4. Paste into whatever you've clicked into. Set MD2GMAIL_PASTE=0 to skip this and
#    let Keyboard Maestro's own Paste action do it instead (avoids needing to grant
#    Accessibility to osascript).
if [[ "${MD2GMAIL_PASTE:-1}" != "0" ]]; then
  osascript -e 'tell application "System Events" to keystroke "v" using command down'
fi
