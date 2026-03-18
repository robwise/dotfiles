#!/bin/sh
# Disable press-and-hold for key repeat in apps that use Vim keybindings
defaults write com.microsoft.VSCode ApplePressAndHoldEnabled -bool false
defaults write com.mitchellh.ghostty ApplePressAndHoldEnabled -bool false

# Optional: system-wide key repeat speed (comment out if you don't want this)
# defaults write NSGlobalDomain KeyRepeat -int 2
# defaults write NSGlobalDomain InitialKeyRepeat -int 15
