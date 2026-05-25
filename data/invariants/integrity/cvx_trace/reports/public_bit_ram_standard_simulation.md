# Public Bit-RAM Standard Simulation

## Statement

Every finite_public_bit_ram execution admitted by the repository program schema and compiled by the universal trace compiler is simulated by a standard deterministic polynomial-time RAM/Turing machine with polynomial overhead, while preserving public decisions and using only public C operations.

Bound: For runtime T, public word width W, and program size P, a RAM simulation costs O(T*(W+log P)); a multitape Turing simulation costs O(T*(W+log P)^2).

## Decision

- Public bit-RAM is in standard P: `True`
- Standard P to P_CVX: `False`
- P_CVX equals standard P: `False`

## Opcode Simulation Cases

- `bit_and`: read two public bits, write their conjunction
- `bit_not`: read one public bit, write its complement
- `bit_or`: read two public bits, write their disjunction
- `bit_xor`: read two public bits, write their public xor
- `branch`: read a public condition bit and update the program counter
- `compare_zero`: scan a public word and emit whether all bits are zero
- `const`: write a public constant word
- `copy`: copy a public word between public registers or memory cells
- `emit_decision`: copy the public decision register to the output channel
- `halt_accept`: enter the accepting halt state
- `halt_reject`: enter the rejecting halt state
- `input_read`: copy a public input bit or word into public memory
- `loop_tick`: increment a public step counter and continue
- `ram_load`: read a public-addressed public memory cell
- `ram_store`: write a public-addressed public memory cell

## Next

Define a uniform compiler from standard deterministic Turing/RAM machine executions into finite_public_bit_ram programs and prove polynomial overhead.
