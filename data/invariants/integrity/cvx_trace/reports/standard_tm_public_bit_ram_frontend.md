# Standard TM to Public Bit-RAM Frontend

## Statement

Every deterministic public multi-tape Turing-machine execution with finite public transition table, no oracle/advice channel, and no hidden extractor primitive translates uniformly into a finite_public_bit_ram program/trace using only public C opcodes, preserving accept/reject decisions with polynomial overhead.

Bound: For source runtime T, input length n, k tapes, alphabet bit-width a, state bit-width q, and transition table size |delta|, the compiled execution has O(T*(k*(a+log(T+n+1)) + q + |delta|)) public bit-RAM steps.

## Frontend Phases

- `encode_public_input`: Copy the public input tape into public bit-RAM memory. Uses `input_read`, `ram_store`, `loop_tick`.
- `encode_transition_table`: Store the finite transition table as public constants and branch targets. Uses `const`, `copy`, `ram_store`.
- `fetch_current_configuration`: Read public state, head positions, and scanned tape symbols. Uses `ram_load`, `copy`, `compare_zero`.
- `select_transition`: Compare the public finite-control row and branch to the matching transition block. Uses `bit_and`, `bit_not`, `bit_or`, `bit_xor`, `compare_zero`, `branch`.
- `write_next_configuration`: Write the next state, tape symbols, and head positions into public memory. Uses `const`, `copy`, `bit_xor`, `ram_store`.
- `halt_or_continue`: Emit the public decision or advance to the next simulated step. Uses `branch`, `emit_decision`, `halt_accept`, `halt_reject`, `loop_tick`.

## Decision

- Frontend certified: `True`
- Generated opcodes total in C/V/X vocabulary: `True`
- Semantic X reclassification: `False`

## Next

Prove that any standard public algorithm implementing hidden-sector recovery is either impossible as a pure C trace or is formally retyped as X.
