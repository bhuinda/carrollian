# v32 MOG canonicity boundary certificate
status = `MOG_COLUMN_SEXTET_CANONICITY_CERTIFIED_FULL_ROW_GOLAY_SELECTOR_STILL_EXTERNAL`
sha256 = `7c67fdbda1c0c3b2b5314720e0ad489889252e63dffa894257d3d78b6fb17452`
## Main result
The 15 pair-octads determine the six MOG tetrad columns intrinsically: two coordinates are equivalent exactly when they have the same incidence profile across all 15 pair-octads.
```text
coordinate-profile classes:      6
atom sizes:                      [4, 4, 4, 4, 4, 4]
equals v31 MOG columns:          True
pair octads = unions of atoms:   True
```
Thus the certified invariant is not merely a displayed 4x6 array; its six tetrad columns are recoverable from the pair-octad incidence hypergraph.
## Intrinsic atom columns
```text
B-: [0, 6, 12, 18]
B+: [1, 7, 13, 19]
V-: [2, 8, 14, 20]
V+: [3, 9, 15, 21]
S-: [4, 10, 16, 22]
S+: [5, 11, 17, 23]
```
## Active K4 / 6j tetrahedron
```text
active K4 labels:                ['B+', 'V+', 'S-', 'S+']
active edge labels:              [['B+', 'V+'], ['B+', 'S-'], ['B+', 'S+'], ['V+', 'S-'], ['V+', 'S+'], ['S-', 'S+']]
active graph degrees:            [0, 3, 0, 3, 3, 3]
unique K4:                       True
```
The support-nullspace pair-octads select a unique K4 on the column sextet. Its six edges are the 6j/tetrahedral edge carrier.
## Wu edge
```text
Wu edge:                         ['B+', 'S-']
opposite edge:                   ['V+', 'S+']
Wu edge intrinsic in K4:          True
```
## Residual boundary
The column sextet is intrinsic, but the row alignment inside the 4x6 display is not yet selected by the current pair-octad/Wu/6j data. The residual coordinate symmetry includes independent S4 permutations inside each tetrad.
```text
(S4)^6 order:                    191102976
S6 column order:                 720
pair-octad hypergraph aut order: 137594142720
preserve_active_graph_only: 48
preserve_active_graph_and_wu_edge_unoriented: 8
preserve_active_graph_and_wu_edge_oriented: 4
preserve_all_H6_labels: 1
```
Therefore the correct canonicity statement is: the MOG column sextet, Wu edge, and K4/6j tetrahedron are intrinsic; the full row-refined Golay/MOG selector remains external.
## Edge-code check
```text
active edge span rank over F2:    3
active edge code size:            8
active edge code weights:         {'0': 1, '8': 6, '16': 1}
```
