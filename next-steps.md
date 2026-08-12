Inspect the complete control plane:

  ./scripts/eos doctor
  ./scripts/eos layers
  ./scripts/eos state-machine WP
  ./scripts/eos policy list
  ./scripts/eos gate explain WP_AUTHORIZE WP-0001
  ./scripts/eos planning check PI-001
  ./scripts/eos planning order PI-001
  ./scripts/eos trace coverage
  ./scripts/eos stale list
  ./scripts/eos events --limit 20
  ./scripts/eos status
  ./scripts/eos next

Enable dynamic tab completion (Bash/Zsh/Fish):

  ./scripts/eos completion install

Or inspect/source repository-local completion files under `completions/`.

After EOSB-020, continue directly into the permanent lifecycle, for example:

  ./scripts/eos plan PI-002
  ./scripts/eos create-wc --pi PI-002
  ./scripts/eos create-wp --wc WC-0002 --domain CORE
  ./scripts/eos ready WP-CORE-0001
  ./scripts/eos authorize WP-CORE-0001
  ./scripts/eos start WP-CORE-0001
  ./scripts/eos codex WP-CORE-0001
  ./scripts/eos validate WP-CORE-0001
  ./scripts/eos review WP-CORE-0001
  ./scripts/eos close WP-CORE-0001
  ./scripts/eos trace REQ-0042
  ./scripts/eos impact ADR-0014
  ./scripts/eos github-sync
  ./scripts/eos release 0.1.0
