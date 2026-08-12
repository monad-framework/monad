# Engineering Operating System

Monad is built under a repository-native Engineering Operating System (EOS).

| Layer | Purpose |
| --- | --- |
| EOSB | Bootstrap |
| EOSP | Planning |
| EOSE | Execution |
| EOSV | Verification |
| EOSR | Review |
| EOSC | Change Control |
| EOSL | Release Lifecycle |
| EOSM | Maintenance |

The normal flow is product intent → accepted authority → planning → Ready Work Packet → explicit authorization → execution → verification → review → merge/release evidence → maintenance.

Canonical EOS detail lives in the repository. `.eos/` contains machine/control state and does not outrank accepted canonical artifacts.
