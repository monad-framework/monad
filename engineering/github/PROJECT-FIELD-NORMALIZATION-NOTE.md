# GitHub Project field normalization note

The GitHub Project bootstrap treats field names case-insensitively and punctuation-insensitively for idempotent lookup. This allows historical field names such as `Work-Packet`, `Start date`, and `Target date` to be reused by requested names such as `Work Packet`, `Start Date`, and `Target Date` without creating duplicate near-equivalent fields.

Canonical Monad semantics remain defined by repository artifacts; Project field spellings are coordination-surface details.
