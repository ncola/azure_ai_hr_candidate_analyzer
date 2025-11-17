from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# ensure we can import project modules when running `streamlit run streamlit_app.py`
REPO_ROOT = Path(__file__).resolve().parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from loader import Loader  # type: ignore  # noqa: E402
from processing.matcher import Matcher  # type: ignore  # noqa: E402


@st.cache_resource(show_spinner=False)
def get_loader() -> Loader:
    return Loader()


@st.cache_resource(show_spinner=False)
def get_matcher() -> Matcher:
    return Matcher()


def _load_job_offer_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        st.error(f"Nie znaleziono pliku oferty pracy: {path}")
        return ""


def _parse_uploaded_cv(file) -> Dict[str, Any]:
    try:
        data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Plik {file.name} nie jest poprawnym JSON-em: {exc}") from exc

    candidate_id = data.get("candidate_id")
    if candidate_id is None:
        candidate_id = Path(file.name).stem
    data["candidate_id"] = candidate_id
    return data


def _prepare_display_name(cv: Dict[str, Any]) -> str:
    identifier = cv.get("candidate_id", "?")
    person = cv.get("personal_info", {}).get("name")
    if person:
        return f"{identifier} – {person}"
    return str(identifier)


def _compute_score(candidate: Dict[str, Any]) -> float:
    matched = len(candidate.get("matched_skills", []))
    missing = len(candidate.get("missing_skills", []))
    total = matched + missing
    return matched / total if total else 0.0


def main() -> None:
    st.set_page_config(
        page_title="HR CV Analyzer",
        page_icon="📄",
        layout="wide",
    )

    st.title("HR CV Analyzer")
    st.write(
        "Porównuj kandydatów z ofertami pracy, korzystając z wcześniej "
        "przetworzonych danych CV oraz modelu Azure OpenAI."
    )

    loader = get_loader()
    matcher_error: Optional[Exception] = None
    try:
        matcher = get_matcher()
    except Exception as exc:  # noqa: BLE001
        matcher = None
        matcher_error = exc

    col_job, col_cv = st.columns(2)

    with col_job:
        st.subheader("Oferta pracy")
        job_offer_source = st.radio(
            "Źródło oferty",
            ("Plik z folderu data/job_offers", "Własny opis"),
        )

        job_offer_text = ""
        if job_offer_source == "Plik z folderu data/job_offers":
            job_files = sorted(loader.job_offer_folder.glob("*.txt"))
            if not job_files:
                st.warning("Brak plików w folderze data/job_offers")
            else:
                selected_file = st.selectbox(
                    "Wybierz plik z ofertą",
                    job_files,
                    format_func=lambda p: p.name,
                )
                job_offer_text = _load_job_offer_text(selected_file)
        else:
            job_offer_text = st.text_area("Wpisz treść oferty", height=250)

        job_offer_text = st.text_area(
            "Podgląd / edycja",
            value=job_offer_text,
            height=250,
        )

    with col_cv:
        st.subheader("CV kandydatów")
        cv_mode = st.radio(
            "Źródło CV",
            ("Pliki z folderu data/results", "Prześlij pliki JSON"),
        )

        cvs: List[Dict[str, Any]] = []
        if cv_mode == "Pliki z folderu data/results":
            available_cvs = loader.cv_loader()
            if not available_cvs:
                st.warning("W katalogu data/results nie znaleziono żadnych przetworzonych CV.")
            else:
                cv_options = {idx: cv for idx, cv in enumerate(available_cvs)}
                default_keys = list(cv_options.keys())
                selected_keys = st.multiselect(
                    "Wybierz kandydatów do porównania",
                    options=cv_options.keys(),
                    default=default_keys,
                    format_func=lambda key: _prepare_display_name(cv_options[key]),
                )
                for key in selected_keys:
                    cvs.append(cv_options[key])
        else:
            uploaded_files = st.file_uploader(
                "Dodaj pliki candidate_*.json",
                type="json",
                accept_multiple_files=True,
            )
            for file in uploaded_files or []:
                try:
                    cvs.append(_parse_uploaded_cv(file))
                except ValueError as exc:
                    st.error(str(exc))

    if matcher_error:
        st.error(
            "Nie udało się zainicjalizować klienta Azure OpenAI. Upewnij się, że w pliku "
            "`src/.env` znajdują się zmienne `AZURE_OPENAI_ENDPOINT`, "
            "`AZURE_OPENAI_KEY` oraz `AZURE_OPENAI_DEPLOYMENT_NAME`, a następnie "
            "uruchom aplikację ponownie."
        )
        with st.expander("Szczegóły błędu"):
            st.exception(matcher_error)

    st.divider()
    run_clicked = st.button(
        "Porównaj kandydatów",
        type="primary",
        disabled=matcher is None,
    )

    if run_clicked:
        if not job_offer_text.strip():
            st.error("Podaj treść oferty pracy.")
            return
        if not cvs:
            st.error("Dodaj co najmniej jedno CV.")
            return

        with st.spinner("Łączę z Azure OpenAI i analizuję kandydatów..."):
            try:
                result = matcher.match(job_offer=job_offer_text, cv_list=cvs)  # type: ignore[union-attr]
            except Exception as exc:  # noqa: BLE001
                st.error(
                    "Nie udało się przeprowadzić analizy. Sprawdź konfigurację Azure i spróbuj ponownie."
                )
                st.exception(exc)
                return

        if not result:
            st.error("Brak danych do wyświetlenia.")
            return

        st.success("Analiza zakończona. Najlepiej dopasowani kandydaci:")
        top_candidates = result.get("top_3", [])

        for idx, candidate in enumerate(top_candidates, start=1):
            score = _compute_score(candidate)
            with st.expander(f"#{idx} – kandydat {candidate.get('candidate_id', '?')} (dopasowanie {score:.0%})"):
                st.metric("Współczynnik dopasowania", f"{score:.0%}")
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("**Dopasowane umiejętności**")
                    st.write(", ".join(candidate.get("matched_skills", [])) or "–")
                with cols[1]:
                    st.markdown("**Brakujące umiejętności**")
                    st.write(", ".join(candidate.get("missing_skills", [])) or "–")

        with st.expander("Surowy wynik modelu"):
            st.json(result)

    with st.sidebar:
        st.header("Jak to działa?")
        st.markdown(
            "1. Przygotuj pliki `candidate_*.json` w folderze `data/results` lub prześlij je ręcznie.\n"
            "2. Wybierz ofertę pracy (z pliku lub wpisz własny opis).\n"
            "3. Kliknij **Porównaj kandydatów** aby uruchomić model Azure OpenAI."
        )
        st.info(
            "Pliki JSON powinny być wynikiem skryptu `process_cv.py`, który parsuje CV na "
            "strukturalne dane."
        )


if __name__ == "__main__":
    main()
