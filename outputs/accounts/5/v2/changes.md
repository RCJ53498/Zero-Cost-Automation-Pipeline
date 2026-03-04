## Changelog

## Additions
- Added "HVAC" to the list of services supported.
- Specified the start and end times of business hours (24/7) and the timezone (UTC-5).
- Specified the transfer number for emergency routing rules (555-1122).

## Modifications
- Modified the business hours to reflect 24/7 operation.
- Modified the start and end times of business hours to be more specific (00:00 to 23:59).

## Removals
- None

## Changes
- Updated the emergency routing rules to include a fallback option.
- Updated the integration constraints to reflect the addition of HVAC services.

## Notes
- The authentication module's handling of store IDs with varying lengths remains unclear.
- The expected volume of calls during extreme weather events remains unknown.