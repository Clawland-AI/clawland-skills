# Aeration Response Playbook

Use this playbook when dissolved oxygen crosses the warning or critical bands in `skill.yaml`.

## Warning Band

Condition: dissolved oxygen below 5.5 mg/L while water temperature is above 26 C.

1. Force `aerator_relay` on.
2. Pause non-essential feeding for the current cycle.
3. Re-sample dissolved oxygen after 10 minutes.
4. If dissolved oxygen rises above 6.2 mg/L, return to normal monitoring and record recovery time.

## Critical Band

Condition: dissolved oxygen below 4.5 mg/L.

1. Force `aerator_relay` on and keep it latched until manual or automated recovery.
2. Deactivate `feeder_relay`.
3. Send critical operator notification.
4. Re-sample every 5 minutes until dissolved oxygen is above 6.2 mg/L for two consecutive samples.
5. Record aerator runtime, recovery time, and any mortality or stress observations.

## Escalation

Escalate to the pond manager when critical oxygen persists for more than 10 minutes or when the aerator relay does not change state after activation.
