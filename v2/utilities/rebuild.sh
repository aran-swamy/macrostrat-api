#! /bin/bash
python scripts/build_autocomplete.py &&
python scripts/build_lookup_strat_names.py &&
python scripts/build_lookup_unit_attrs_api.py &&
python scripts/build_lookup_unit_intervals.py &&
python scripts/build_pbdb_matches.py &&
python scripts/update_unit_boundaries.py
