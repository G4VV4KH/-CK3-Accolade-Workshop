# Accolade Workshop — developer notes

Version 0.1.1 targets CK3 1.21.0.3 and requires Tours & Tournaments.

`publishing/description.en.md` is the English description source for this public projection. The README and store files are generated projections; upstream authoring maintains the canonical source and reviewed platform identities. Use the [GitHub issue tracker](https://github.com/G4VV4KH/-CK3-Accolade-Workshop/issues), or email **g4vv4kh@gmail.com**. The README contains the assigned publication links. Keep the shared family catalog and sibling descriptions synchronized through scoped metadata updates without altering sibling gameplay.

The runtime files are at repository root. `tests/check_source.py` supplies portable static checks; `tests/acceptance-summary.json` records scoped native and visual evidence. The Florin release updates the supported version and the English gallery. In the installed 1.21.0.3 game, both base GUI windows and the native rank-change on-action match their 1.20.1.2 versions byte for byte. Scripts, functional GUI and all translations are byte-identical to accepted DEV.2.

Rank rules apply to new campaigns. Existing-save baseline migration is not implemented. Ranks 7–9 reuse the vanilla rank-6 ornament. Multiplayer, other language layouts and positive rank-notification delivery were not verified.

The mod overrides `gui/window_create_accolade.gui`, `gui/window_accolade.gui`, and the `on_accolade_rank_change` effect; these require merged compatibility work when another mod replaces them.

AI provenance: mod-specific code, interface additions, translations, publication copy and cover artwork were generated with AI. Interface integration and badge ornaments adapt Paradox Interactive game assets. Gallery images are actual native-rendered CK3 screenshots. The package does not grant a new open-source license; existing game and third-party asset rights remain with their owners.
