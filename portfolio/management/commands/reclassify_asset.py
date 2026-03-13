from django.core.management.base import BaseCommand
from portfolio.models import Asset
from portfolio.utils import db_assets_classify


class Command(BaseCommand):
    help = "Reclassify existing assets using DB-only rules"

    def handle(self, *args, **options):
        updated = 0

        for asset in Asset.objects.all():
            new_type = db_assets_classify(asset.symbol, asset.name)

            if asset.asset_type != new_type:
                old_type = asset.asset_type
                asset.asset_type = new_type
                asset.save(update_fields=["asset_type"])

                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{asset.symbol}: {old_type} → {new_type}"
                    )
                )

        self.stdout.write(
            self.style.WARNING(
                f"\nReclassification complete. Updated {updated} assets."
            )
        )
