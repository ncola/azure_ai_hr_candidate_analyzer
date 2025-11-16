import os
import json
from pathlib import Path

class Loader:
    """
    Class for loading CVs and job offers
    """

    def __init__(self, cv_folder: str = "data/results", job_offer_folder: str = "data/job_offers"):
        self.cv_folder = Path(cv_folder)
        self.job_offer_folder = Path(job_offer_folder)

    def cv_loader(self) -> list[dict]:
        """
        Function to load all CV JSON files from cv_folder and assign candidate_id based on filename
        It returns list of proccesed cv
        """
        cvs = []
        for filename in os.listdir(self.cv_folder):
            if filename.endswith(".json"):
                with open(self.cv_folder/filename, "r", encoding="utf-8") as f:
                    cv_data = json.load(f)
                    stem = Path(filename).stem  
                    if stem.startswith("candidate") and stem[9:].isdigit():
                        cv_data["candidate_id"] = int(stem[9:])
                    else:
                        cv_data["candidate_id"] = None 
                    cvs.append(cv_data)
        return cvs

    def job_offer_loader(self, filename: str):
        """
        Function to load a job_offer
        """
        file_path = self.job_offer_folder/filename
        if not file_path.exists():
            raise FileNotFoundError(f"Job offer not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            job_offer = f.read()
        
        return job_offer
