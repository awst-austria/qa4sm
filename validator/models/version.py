import logging
from django.db import models
from validator.models.filter import DataFilter
from django.core.exceptions import ObjectDoesNotExist
import os
import json
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)

class DatasetVersion(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=30)
    pretty_name = models.CharField(max_length=40)
    help_text = models.CharField(max_length=150)
    time_range_start = models.TextField(blank=True, null=True)
    time_range_end = models.TextField(blank=True, null=True)
    geographical_range = models.JSONField(blank=True, null=True)
    filters = models.ManyToManyField(DataFilter, related_name='filters', blank=True)

    def __str__(self):
        return self.short_name

    def save(self, *args, **kwargs):
        try:
            # save first
            super(DatasetVersion, self).save(*args, **kwargs)

            # Trigger the fixture update function after saving the object
            update_fixture_entry(self)

        except Exception as e:
            logger.error(f"Error while saving DatasetVersion {self.pk}: {e}")
            raise


def update_fixture_entry(version):
    """Update the fixture entry with the current version data."""
    fixture_path = os.path.join(settings.BASE_DIR, 'validator', 'fixtures', 'versions.json')

    try:
        # Read the existing fixture file
        with open(fixture_path, 'r', encoding='utf-8') as f:
            fixture_data = json.load(f)

        # Find the entry matching the updated version
        entry_updated = False
        for entry in fixture_data:
            if entry["model"] == "validator.datasetversion" and entry["pk"] == version.pk:
                entry_fields = entry["fields"]
                for key in entry_fields.keys():
                    try:
                        # Handle many-to-many relationships
                        if hasattr(version, key) and isinstance(getattr(version, key), (list, set, tuple)):
                            entry_fields[key] = list(getattr(version, key).values_list('id', flat=True))
                        elif hasattr(version, key) and hasattr(getattr(version, key),
                                                               'all'):  # For ManyRelatedManager
                            entry_fields[key] = list(getattr(version, key).all().values_list('id', flat=True))
                        # Handle foreign key relationships
                        elif hasattr(version, key) and hasattr(getattr(version, key), 'pk'):
                            entry_fields[key] = getattr(version, key).pk
                        else:
                            # Default: Use the attribute directly
                            entry_fields[key] = getattr(version, key)
                    except AttributeError:
                        pass  # Skip keys that don't map directly to the version object
                entry_updated = True
                break  # Exit the loop once the relevant entry is updated

        if not entry_updated:
            logger.warning(f"DatasetVersion {version.pk} not found in the fixture file.")
            return

        # Write the updated data back to the fixture file
        with open(fixture_path, 'w', encoding='utf-8') as f:
            json.dump(fixture_data, f, cls=DjangoJSONEncoder, indent=4)

    except FileNotFoundError:
        logger.error(f"Fixture file not found at {fixture_path}.")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from the fixture file: {e}")
    except Exception as e:
        logger.error(f"Error updating fixture entry for DatasetVersion {version.pk}: {e}")
