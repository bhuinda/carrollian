# Conditional Closure from Barrier Schur Compression

Let

\[
F_w(\theta)=\log A_w(e^\theta)-{w\over2}\log\left({1\over24}\sum_{i=1}^{24}e^{2\theta_i}\right)-\log A_w(1),
\]

so the target shell inequality is \(F_w(\theta)\le0\) for all \(\theta\in\mathbb R^{24}\).

The function is invariant under adding constants to \(\theta\), so impose \(\sum_i\theta_i=0\). Let \(g(\theta)=\nabla F_w(\theta)\). Then also \(\sum_i g_i(\theta)=0\).

## Barrier Schur Compression Lemma

For \(w\in\{12,16\}\), whenever \(F_w(\theta)\ge0\),

\[
(\theta_i-\theta_j)(g_i(\theta)-g_j(\theta))\le0
\qquad\forall i,j.
\]

## Consequence

Using the identity

\[
24\,\langle\theta,g(\theta)\rangle
=
\sum_{1\le i<j\le24}(\theta_i-\theta_j)(g_i(\theta)-g_j(\theta)),
\]

the lemma implies

\[
\langle\theta,g(\theta)\rangle\le0
\quad\text{whenever }F_w(\theta)\ge0.
\]

Now define the radial compression path

\[
\phi(s)=F_w((1-s)\theta),\qquad s\in[0,1].
\]

Then

\[
\phi'(s)=-\langle\theta,g((1-s)\theta)\rangle.
\]

As long as \(\phi(s)\ge0\), the barrier Schur compression lemma gives

\[
\phi'(s)\ge0.
\]

If \(F_w(\theta)>0\), then \(\phi(0)>0\) and \(\phi(1)=F_w(0)=0\). But a function that is nondecreasing on every portion where it is nonnegative cannot move from a positive value down to \(0\). Contradiction. Therefore \(F_w(\theta)\le0\).

This proves the shell-domination theorem for \(w=12,16\), conditional on the Barrier Schur Compression Lemma.

## Role of the exact two-level certificate

The exact all-two-level certificate supplies a certified endpoint and obstruction check for threshold compressions:

\[
\operatorname{Gap}_{w,k}(z)=(z-1)^2Q_{w,k}(z),\qquad Q_{w,k}\in\mathbb Z_{\ge0}[z].
\]
