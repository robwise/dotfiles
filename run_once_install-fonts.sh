#!/bin/sh
brew install --cask font-symbols-only-nerd-font
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/fonts/MonoLisa"*.ttf ~/Library/Fonts/ 2>/dev/null && echo "MonoLisa fonts installed" || echo "WARNING: MonoLisa fonts not found"
