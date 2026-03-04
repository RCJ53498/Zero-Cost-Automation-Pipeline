## Changelog

## Additions
- Added `start` and `end` time ranges for business hours in V2, with a new start time of 08:00 and end time of 20:00.
- Added `behavior` and `transfer_number` to emergency routing rules in V2, with a new behavior of "Immediate routing to the summer on-call dispatcher" and a new transfer number of 555-4433.
- Added `non_emergency_routing_rules` in V2, with a new rule to capture name, address, unit make/model, and push to the custom CRM for scheduling.
- Added `questions_or_unknowns` in V2, with a new question about the expected API access timeline.

## Modifications
- Modified `emergency_definition` in V2 to include "Complete commercial chiller failure" in addition to "Critical AC failure".
- Modified `emergency_routing_rules` in V2 to change the behavior from "Escalate to priority" to "Immediate routing to the summer on-call dispatcher".

## Removals
- Removed `after_hours_flow_summary` and `office_hours_flow_summary` from V2, as their values were "None".
- Removed `notes` from V2, as its value was "None".

## Changes
- Updated `services_supported` to include the same services in both V1 and V2.
- Updated `integration_constraints` to include the same constraint in both V1 and V2.
- Updated `account_id` to include the same account ID in both V1 and V2.