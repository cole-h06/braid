# Agreement Weighting

## Motivation

In the baseline reliability propagation fraemwork, we treat each assertion equally. But, it does not know that, when several sources are referring to the same attribute, their assertions may be divided across conflicting claims.

For example, let's suppose a source reports a 30 day return window while another reports a 14 day return window. Both claims and their supporting sources are recorded by the graph, but the baseline propagation equation does not use the amount of agreement each assertion has.

That information is introduced into source-to-claim propagation via agreement-weighting. Essentially, it increases each assertion's influence that agrees with a larger share of sources referring to the same attribute.

## Agreement Framework

Let $j$ represent a claim about an underlying attribute.

Let

- $A(j)$ denote the sources asserting claim $j$, and
- $P(j)$ denote the sources asserting any claim about the same underlying attribute as claim $j$.

We can define the agreement weight for claim $j$ as

$$ w_j = \frac{|A(j)|}{|P(j)|}. $$

For an assertion edge connecting source $i$ to claim $j$, we define

$$ w_{ij}=w_j. $$

The agreement weight is constrained to

$$ 0 < w_{ij} \le 1. $$

A weight of $1$ means that every source addressing the attribute asserts the same claim. A smaller value means that the sources are divided across conflicting claims.

If every source provides at most one value for an attribute, the agreement weights of the conflicting claims for that attribute sum to $1$.

## Agreement-Weighted Claim Support

Agreement weighting modifies source-to-claim propagation.

Without agreement weighting, we calculate claim support as

$$ c_j^{(t)}=\sum_{i\in A(j)}\frac{s_i^{(t)}}{d_i}. $$

After introducing $w_{ij}$, the calculation becomes

$$ c_j^{(t)}=\sum_{i\in A(j)}\frac{s_i^{(t)}w_{ij}}{d_i}. $$

where

- $s_i^{(t)}$ is the reliability of source $i$ at iteration $t$,
- $w_{ij}$ is the agreement weight for the assertion, and
- $d_i$ is the number of claims asserted by source $i$.

Source degree controls how a source's reliability is distributed. Agreement weighting then adjusts the contribution based on how many sources referring to the attribute assert the same claim.

## Example

Suppose four equally reliable sources address the same return-window attribute.

Three sources assert a 30-day return window. One source asserts a 14-day return window.

The agreement weights are

$$ w_{30}=\frac{3}{4} $$

and

$$ w_{14}=\frac{1}{4}. $$

If every source begins with reliability $\frac{1}{4}$ and asserts only one claim, the agreement-weighted support for the 30-day claim is

$$ c_{30}=3\left(\frac{1}{4}\right)\left(\frac{3}{4}\right)=\frac{9}{16}. $$

The support for the 14-day claim is

$$ c_{14}=\left(\frac{1}{4}\right)\left(\frac{1}{4}\right)=\frac{1}{16}. $$

Notice that the majority claim ends up receiving the most support because it has both more supporting sources and a larger agreement-weight.

Prior to the next iteration, these values continue to move through claim-to-source propagation and source normalization.

## Matrix Representation

Let

$$ M_w\in[0,1]^{|S|\times|C|} $$

be the agreement-weighted assertion matrix, where

$$ (M_w)_{ij}=\begin{cases}w_{ij}, & \text{if source } i \text{ asserts claim } j \\ 0, & \text{otherwise}\end{cases}. $$

Agreement-weighted source-to-claim propagation can then be written as

$$ c^{(t)}=M_w^\mathsf{T}D_S^{-1}s^{(t)}. $$

Claim-to-source propagation continues to use the unweighted assertion matrix:

$$ \tilde{s}^{(t+1)}=Mc^{(t)}. $$

Combining both steps gives

$$ \tilde{s}^{(t+1)}=MM_w^\mathsf{T}D_S^{-1}s^{(t)}, $$

followed by normalization of the updated source vector.

## Interpretation

When there are conflicting claims for the same attribute, agreement weighting measures how assertions are distributed across the claims. It does not actually decide if the most common claim is correct.

A large group of sources can still repeat information from the same origin. That said, agreement alone is incapable of distinguishing independent support from copied or otherwise related evidence.

[Hybrid source dependency estimation](hybrid_source_dependencies.md) expands this framework by adjusting assertion contributions based on the estimated independence of the supporting sources.
