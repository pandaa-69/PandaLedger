import requests
from django.core.management.base import BaseCommand
from portfolio.models import Asset

class Command(BaseCommand):
    help = 'Seeds the database with Indian Mutual Funds from MFAPI.in'

    def handle(self, *args, **kwargs):
        url = "https://api.mfapi.in/mf"
        self.stdout.write(f"🌍 Fetching Master List from {url}...")
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch data: {response.status_code}"))
                return
            
            data = response.json()
            total_schemes = len(data)
            self.stdout.write(f"📦 Found {total_schemes} schemes. preparing to seed...")

            # Prepare objects for Bulk Create
            assets_to_create = []
            existing_symbols = set(Asset.objects.values_list('symbol', flat=True))

            count = 0
            for scheme in data:
                code = str(scheme['schemeCode'])
                name = scheme['schemeName']

                # optimization: Skip if already exists
                if code in existing_symbols:
                    continue

                # Filter: Let's focus on "Growth" and "Direct" plans to reduce noise 
                # (Optional: Remove this 'if' to seed EVERYTHING)
                # if 'Growth' not in name: continue 

                assets_to_create.append(
                    Asset(
                        symbol=code,
                        name=name,
                        asset_type='MF',
                        sector='Unknown',
                        market_cap_category='MID',
                        last_price=0.0  # Will update when user adds it
                    )
                )
                count += 1

            # Bulk Create (Batches of 5000)
            if assets_to_create:
                self.stdout.write(f"🚀 Inserting {len(assets_to_create)} new Mutual Funds...")
                Asset.objects.bulk_create(assets_to_create, batch_size=5000, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(f"✅ Successfully seeded {len(assets_to_create)} Mutual Funds!"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ No new funds to add."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))