from processing.matcher import Matcher
from loader import Loader
import json
from config import AzureConfig


def main():
    loader = Loader()
    cvs = loader.cv_loader() 

    job_offer = loader.job_offer_loader(filename="data_scientist.txt")

    matcher = Matcher()
    result = matcher.match(job_offer=job_offer, cv_list=cvs)

    for candidate in result.get("top_3", []):
        matched_count = len(candidate.get("matched_skills", []))
        missing_count = len(candidate.get("missing_skills", []))
        total_required = matched_count + missing_count
        candidate["score"] = matched_count / total_required if total_required > 0 else 0

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
