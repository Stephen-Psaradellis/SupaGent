
import sys
sys.path.insert(0, "pipeline")
from lead_generation import LeadGenerator
import time
import json

# Read business keywords
with open("pipeline/business_keywords.txt", "r") as f:
    business_types = [line.strip() for line in f if line.strip()]

print(f"Processing {len(business_types)} business types for Chicago, IL")
print("Generating up to 500 leads per type")
print("Sources: Web scraping with Playwright + ScraperAPI/Outscraper fallback + HunterIO/ApolloIO enrichment")

generator = LeadGenerator()
all_results = {}
total_leads = 0
start_time = time.time()

# Process all business types
for i, business_type in enumerate(business_types, 1):
    batch_start = time.time()
    print(f"\n[{i:2d}/89] {business_type}")

    try:
        leads = generator.generate_leads(
            industry=business_type,
            location="Chicago, IL",
            limit=500  # Generate up to 500 leads per type
        )

        batch_time = time.time() - batch_start

        if leads:
            total_leads += len(leads)
            emails_found = sum(1 for lead in leads if lead.email)
            print(f"  SUCCESS: {len(leads)} leads ({emails_found} with emails) in {batch_time:.1f}s")

            # Store results
            all_results[business_type] = {
                "count": len(leads),
                "emails": emails_found,
                "leads": [
                    {
                        "name": lead.name,
                        "domain": lead.domain,
                        "email": lead.email,
                        "source": lead.source
                    } for lead in leads
                ]
            }
        else:
            print(f"  NO LEADS: {batch_time:.1f}s")
            all_results[business_type] = {"count": 0, "emails": 0, "leads": []}

    except Exception as e:
        batch_time = time.time() - batch_start
        print(f"  ERROR: {str(e)[:50]} in {batch_time:.1f}s")
        all_results[business_type] = {"count": 0, "emails": 0, "error": str(e), "leads": []}

# Save results
with open("chicago_leads_results.json", "w") as f:
    json.dump(all_results, f, indent=2)

total_time = time.time() - start_time
successful_types = sum(1 for r in all_results.values() if r["count"] > 0)

print(f"\n{'='*60}")
print("FINAL SUMMARY:")
print(f"- Business types processed: {len(business_types)}")
print(f"- Successful (generated leads): {successful_types}")
print(f"- Failed: {len(business_types) - successful_types}")
print(f"- Total leads generated: {total_leads}")
print(f"- Total emails found: {sum(r.get('emails', 0) for r in all_results.values())}")
print(f"- Total time: {total_time/60:.1f} minutes")
print(f"- Average leads per successful type: {total_leads / max(successful_types, 1):.1f}")
print(f"- Results saved to: chicago_leads_results.json")
