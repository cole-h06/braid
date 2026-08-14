## Structural Redundancy

We estimate structural redundancy between each pair of sources. It is the first graph-derived signal for the v1 source dependency model.

Let $C_i$ and $C_k$ denote the sets of assertions made by sources $i$ and $k$.

The directional inclusion between the sources is

$$ I_{ik} = \max\left(\frac{|C_i \cap C_k|}{|C_i|}, \frac{|C_i \cap C_k|}{|C_k|}\right) $$

This measures the extent to which one source's information is contained within the other, but not vice versa.

For each assertion $j$, we define rarity as:

$$ r_j = \frac{1}{|A(j)|} $$

where $A(j)$ is the set of sources asserting $j$. We therefore assign greater weight to assertions made by fewer sources.

The average rarity of the assertions shared by sources $i$ and $k$ is

$$ R_{ik} = \frac{1}{|C_i \cap C_k|}\sum_{j \in C_i \cap C_k} r_j $$

We then define the structural redundancy signal as

$$ g_{ik} = I_{ik}R_{ik} $$

If no assertions are shared by the sources, then $g_{ik}=0$.

A high value of $g_{ik}$ therefore needs both a high degree of inclusion between the sources and the sharing of relatively uncommon assertions. High overlap consisting of assertions that appear more frequently across the graph contributes less structural evidence.

## Limitations

It is important to note that structural redundancy does not mean that one source actually depends on another.

For this reason, $g_{ik}$ is treated as one signal within the broader hybrid source dependency model, not the sole estimator for source dependency.

## Role in Source Dependency Estimation

The structural redundancy signal $g_{ik}$ is combined with provenance and metadata signals in the v1 source dependency estimator:

$$ \delta_{ik} = \alpha_u u_{ik} + \alpha_c c_{ik} + \alpha_a a_{ik} + \alpha_o o_{ik} + \alpha_t t_{ik} + \alpha_g g_{ik} $$

You can find the complete v1 source dependency estimation model in [Source Dependency Estimation](source_dependency_estimation.md).