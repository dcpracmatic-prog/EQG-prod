# EQG Product Overview

Edge Quantum Guard is the productized control plane for quantum workloads:

1. **Observe** hardware health without elevated privileges  
2. **Select** layout via MORPH  
3. **Decide** minimal intervention (hold / remap / conditional DD)  
4. **Actuate** via Centinela sequences  
5. **Score** outcomes with HIS (and SE/z in validation pipelines)

## Delivery targets

- Container image for local and cluster runtimes  
- Helm chart for IBM Cloud private catalog (Software → Helm)  
- CLI for automation and CI smoke  

## Validation pipeline (product)

Use the same arms A/C/D/E and HIS contrasts in the validation environment connected to IBM Quantum backends. Product configuration switches `mode: hardware` and injects credentials through Kubernetes secrets or environment variables — never through source.
