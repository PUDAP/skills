---
name: labware
description: Available labware definitions, usage, and valid row/column coordinates.
---

# Critical Rule

If you are unsure which labware or well should be used when generating commands, **ask the user** before proceeding.  
Do **not** assume.

If there is only one well, `well_name` can be assumed to be `A1`

# Labware Reference

This reference defines each available labware, what it is used for, and its valid row/column coordinates.

## `MEA_cell_MTP`

- **Purpose:** Single-position plate location used for the MEA cell target.
- **Rows:** `A` (1 row)
- **Columns:** `1` (1 column)
- **Total wells:** 1

## `opentrons_96_tiprack_300ul`

- **Purpose:** 300 uL pipette tip rack for standard liquid handling steps.
- **Rows:** `A-H` (8 rows)
- **Columns:** `1-12` (12 columns)
- **Total well:** 96

## `polyelectric_8_wellplate_30000ul`

- **Purpose:** 8-well high-volume plate (30,000 uL per well) for large-volume samples/reagents.
- **Rows:** `A-B` (2 rows)
- **Columns:** `1-4` (4 columns)
- **Total wells:** 8

## `sartorious_96_tiprack_1000ul`

- **Purpose:** 1000 uL pipette tip rack for high-volume transfers.
- **Rows:** `A-H` (8 rows)
- **Columns:** `1-12` (12 columns)
- **Total wells:** 96

## `trash_bin`

- **Purpose:** Single-position waste location for tip discard.
- **Rows:** `A` (1 row)
- **Columns:** `1` (1 column)
- **Total wells:** `A1`
