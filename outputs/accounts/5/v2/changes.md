## Changelog

### Additions

- **office_address**: Added an empty string to indicate that the office address is not specified.
- **emergency_routing_rules** and **non_emergency_routing_rules**: Added empty strings to indicate that these rules are not specified.
- **after_hours_flow_summary** and **office_hours_flow_summary**: Added empty strings to indicate that these summaries are not specified.
- **questions_or_unknowns**: Added "Contract renewal details (e.g. price, timeline)" to the list of questions or unknowns.

### Modifications

- **emergency_routing_rules**:
  - Changed `transfer_number` from "Not specified in the transcript" to an empty string.
  - Changed `fallback` from "Not specified in the transcript" to an empty string.
- **non_emergency_routing_rules**: Changed from "Not specified in the transcript" to an empty string.

### Removals

- None