# Changelog

All notable changes to Kitty Mode will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2026-02-01

### Fixed
- 🐱 Fixed feedback loop issue where typing while KittyMode is inserting characters could cause infinite message generation
- Added suppress/unsuppress mechanism to prevent capturing our own output
- Added time-based guard (200ms minimum interval) to prevent rapid re-triggering
- Added post-output delay to allow synthetic keystrokes to settle

## [1.0.1] - 2026-01-28

### Fixed
- 🐱 Fixed Ctrl+Shift+K hotkey not working on Windows (Ctrl+K produces `\x0b` instead of `k`)

## [1.0.0] - 2026-01-28

### Added
- 🐱 Initial release of Kitty Mode!
- AI-powered semantic matching of typed words to contextually appropriate cat noises
- System tray integration with quick toggle
- Global keyboard capture with smart filtering
- Customizable output delay settings
- Support for Windows and macOS
- Over 50 unique cat noises including meows, purrs, chirps, and hisses
- Settings window for configuration
- Automatic startup option

### Technical
- ONNX-based inference for fast, lightweight text embeddings
- Pre-computed noise embeddings for instant similarity search
- PyInstaller-based distribution for easy installation

---

*Made with 😺 for cats and their humans*

[Unreleased]: https://github.com/aslindamood/kittymode/compare/v1.0.2...HEAD
[1.0.2]: https://github.com/aslindamood/kittymode/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/aslindamood/kittymode/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/aslindamood/kittymode/releases/tag/v1.0.0
