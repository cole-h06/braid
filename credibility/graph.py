from dataclasses import dataclass, field


GRAPH_ATTRIBUTES = {

    "ram_gb",
    "storage_gb",

    "cpu_model",
    "cpu_cores",

    "gpu_model",

    "wifi_standard",
    "bluetooth_version",

    "display_resolution",
    "screen_size",

    "battery_life_hr",

    "weight_lb",

    "operating_system",

    "touchscreen",
}


@dataclass
class CredibilityGraph:

    source_to_claims: dict
    claim_to_sources: dict
    source_names: dict
    agreement_weights: dict
    claim_lookup: dict = field(default_factory=dict)
    source_to_assertions: dict = field(default_factory=dict)

    dependency_matrix: dict = field(default_factory=dict)