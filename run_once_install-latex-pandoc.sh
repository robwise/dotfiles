#!/bin/sh
# Idempotent LaTeX + Pandoc setup for document formatting
# Requires: brew, tlmgr (from TinyTeX or BasicTeX)
# Uses TinyTeX (user-space, no sudo needed) as the TeX distribution

# Install TinyTeX if xelatex not present
if ! command -v xelatex >/dev/null 2>&1 && [ ! -f "$HOME/Library/TinyTeX/bin/universal-darwin/xelatex" ]; then
  curl -sL "https://yihui.org/tinytex/install-bin-unix.sh" | sh || true
fi

# Ensure TinyTeX is on PATH for this script
if [ -d "$HOME/Library/TinyTeX/bin/universal-darwin" ]; then
  export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
fi

# Update tlmgr and install required packages
tlmgr update --self || true
tlmgr install \
  adjustbox babel-german background bidi collectbox csquotes \
  everypage filehook footmisc footnotebackref framed fvextra letltxmacro ly1 \
  mdframed mweights needspace pagecolor sourcecodepro sourcesans titling \
  ucharcat ulem unicode-math upquote xecjk xurl zref awesomebox \
  koma-script colortbl setspace parskip soul multirow caption float \
  listings microtype babel-english hyphen-english fontawesome5 || true

# Install eisvogel template
mkdir -p "$HOME/.local/share/pandoc/templates/"
if [ ! -f "$HOME/.local/share/pandoc/templates/eisvogel.latex" ]; then
  curl -sL https://github.com/Wandmalfarbe/pandoc-latex-template/releases/latest/download/Eisvogel.tar.gz | tar xz -C /tmp/
  # Find the extracted eisvogel.latex (may be inside a versioned folder)
  EISVOGEL=$(find /tmp -name 'eisvogel.latex' -newer /tmp 2>/dev/null | head -1)
  if [ -n "$EISVOGEL" ]; then
    cp "$EISVOGEL" "$HOME/.local/share/pandoc/templates/eisvogel.latex"
  fi
fi

# Create pandoc defaults directory
mkdir -p "$HOME/.local/share/pandoc/defaults/"
