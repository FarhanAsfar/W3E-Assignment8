import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.db import transaction

from listings.models import Location, Property, PropertyImage


def _parse_bool(value: str) -> bool:
    """
    Accepts: true/false, 1/0, yes/no (case-insensitive).
    """
    v = (value or "").strip().lower()
    if v in {"true", "1", "yes", "y"}:
        return True
    if v in {"false", "0", "no", "n", ""}:
        return False
    raise ValueError(f"Invalid boolean value: '{value}' (use true/false)")


def _read_csv(path: Path) -> List[dict]:
    if not path.exists():
        raise CommandError(f"CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise CommandError(f"CSV has no header: {path}")
        return list(reader)


@dataclass
class SeedPaths:
    base_dir: Path
    locations_csv: Path
    properties_csv: Path
    images_csv: Path


class Command(BaseCommand):
    help = "Seed database from CSV files (locations, properties, images) and copy images into MEDIA_ROOT."

    def add_arguments(self, parser):
        parser.add_argument(
            "--base",
            default="seed_data",
            help="Base folder containing CSV files (default: seed_data).",
        )
        parser.add_argument(
            "--locations",
            default="locations.csv",
            help="Locations CSV filename inside base (default: locations.csv).",
        )
        parser.add_argument(
            "--properties",
            default="properties.csv",
            help="Properties CSV filename inside base (default: properties.csv).",
        )
        parser.add_argument(
            "--images",
            default="images.csv",
            help="Images CSV filename inside base (default: images.csv).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Danger: clears existing Location/Property/PropertyImage before seeding.",
        )

    def handle(self, *args, **options):
        base_dir = Path(options["base"]).resolve()
        paths = SeedPaths(
            base_dir=base_dir,
            locations_csv=base_dir / options["locations"],
            properties_csv=base_dir / options["properties"],
            images_csv=base_dir / options["images"],
        )

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding from CSV..."))
        self.stdout.write(f"- Base: {paths.base_dir}")
        self.stdout.write(f"- Locations: {paths.locations_csv}")
        self.stdout.write(f"- Properties: {paths.properties_csv}")
        self.stdout.write(f"- Images: {paths.images_csv}")
        self.stdout.write(f"- MEDIA_ROOT: {settings.MEDIA_ROOT}")

        # Read CSVs first (fail early with good errors)
        locations_rows = _read_csv(paths.locations_csv)
        properties_rows = _read_csv(paths.properties_csv)
        images_rows = _read_csv(paths.images_csv)

        # Basic header validation (prevents silent wrong imports)
        self._require_headers(paths.locations_csv, locations_rows, {"name"})
        self._require_headers(paths.properties_csv, properties_rows, {
            "external_id", "location_name", "property_name", "country", "address", "title", "description"
        })
        self._require_headers(paths.images_csv, images_rows, {
            "property_external_id", "file_path", "is_primary", "alt_text"
        })

        with transaction.atomic():
            if options["clear"]:
                self._clear_existing()

            locations = self._seed_locations(locations_rows)
            properties = self._seed_properties(properties_rows, locations)
            self._seed_images(images_rows, properties)

        self.stdout.write(self.style.SUCCESS("✅ Seeding completed successfully."))

    def _require_headers(self, path: Path, rows: List[dict], required: set):
        if not rows:
            raise CommandError(f"CSV is empty (no rows): {path}")
        headers = set(rows[0].keys())
        missing = required - headers
        if missing:
            raise CommandError(f"CSV missing columns {sorted(missing)}: {path}")

    def _clear_existing(self):
        # Order matters due to FK constraints
        PropertyImage.objects.all().delete()
        Property.objects.all().delete()
        Location.objects.all().delete()
        self.stdout.write(self.style.WARNING("⚠️ Cleared existing data."))

    def _seed_locations(self, rows: List[dict]) -> Dict[str, Location]:
        """
        Returns a map: location_name -> Location object
        """
        out: Dict[str, Location] = {}
        for i, r in enumerate(rows, start=2):  # start=2 because header is line 1
            name = (r.get("name") or "").strip()
            if not name:
                raise CommandError(f"locations.csv line {i}: 'name' is required")

            # get_or_create avoids duplicates if you seed multiple times without --clear
            loc, _ = Location.objects.get_or_create(name=name)
            out[name.lower()] = loc  # store normalized for easy lookup

        self.stdout.write(self.style.SUCCESS(f"Locations seeded: {len(out)}"))
        return out

    def _seed_properties(self, rows: List[dict], locations: Dict[str, Location]) -> Dict[str, Property]:
        """
        Returns a map: external_id -> Property object
        """
        out: Dict[str, Property] = {}
        for i, r in enumerate(rows, start=2):
            external_id = (r.get("external_id") or "").strip()
            location_name = (r.get("location_name") or "").strip()
            if not external_id:
                raise CommandError(f"properties.csv line {i}: 'external_id' is required")
            if not location_name:
                raise CommandError(f"properties.csv line {i}: 'location_name' is required")

            loc = locations.get(location_name.lower())
            if not loc:
                raise CommandError(
                    f"properties.csv line {i}: unknown location_name='{location_name}'. "
                    f"Add it to locations.csv."
                )

            # Create or update by external_id (stable key)
            obj, _ = Property.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "location": loc,
                    "property_name": (r.get("property_name") or "").strip(),
                    "country": (r.get("country") or "").strip(),
                    "address": (r.get("address") or "").strip(),
                    "title": (r.get("title") or "").strip(),
                    "description": (r.get("description") or "").strip(),
                },
            )

            out[external_id] = obj

        self.stdout.write(self.style.SUCCESS(f"Properties seeded: {len(out)}"))
        return out

    def _seed_images(self, rows: List[dict], properties: Dict[str, Property]):
        """
        Copies files into MEDIA_ROOT through ImageField saving.
        Enforces: only one primary image per property.
        """
        # Track primary per property (fail fast if CSV is wrong)
        primary_seen: Dict[str, int] = {}

        created = 0
        for i, r in enumerate(rows, start=2):
            prop_ext = (r.get("property_external_id") or "").strip()
            file_path = (r.get("file_path") or "").strip()
            alt_text = (r.get("alt_text") or "").strip()

            if not prop_ext:
                raise CommandError(f"images.csv line {i}: 'property_external_id' is required")
            if not file_path:
                raise CommandError(f"images.csv line {i}: 'file_path' is required")

            prop = properties.get(prop_ext)
            if not prop:
                raise CommandError(
                    f"images.csv line {i}: unknown property_external_id='{prop_ext}'. "
                    f"Add it to properties.csv."
                )

            try:
                is_primary = _parse_bool(r.get("is_primary", "false"))
            except ValueError as e:
                raise CommandError(f"images.csv line {i}: {e}")

            if is_primary:
                primary_seen[prop_ext] = primary_seen.get(prop_ext, 0) + 1
                if primary_seen[prop_ext] > 1:
                    raise CommandError(
                        f"images.csv invalid: property '{prop_ext}' has more than one primary image."
                    )

            src = Path(file_path).resolve()
            if not src.exists():
                raise CommandError(
                    f"images.csv line {i}: file not found: '{file_path}' (resolved to {src})"
                )
            if src.is_dir():
                raise CommandError(f"images.csv line {i}: file_path points to a directory: {src}")

            # If the same CSV is imported twice, avoid duplicating identical entries:
            # (simple approach: check by filename + property)
            existing = PropertyImage.objects.filter(property=prop, alt_text=alt_text, is_primary=is_primary)
            # NOTE: this is intentionally simple; you can tighten later.
            if existing.exists():
                continue

            img_obj = PropertyImage(property=prop, is_primary=is_primary, alt_text=alt_text)

            # Save file into the ImageField; Django will copy it into MEDIA_ROOT using upload_to()
            with src.open("rb") as f:
                img_obj.image.save(src.name, File(f), save=True)

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Images seeded: {created}"))
