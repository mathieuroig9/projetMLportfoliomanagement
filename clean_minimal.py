# clean_minimal.py
import os
import re
import unicodedata

def clean_minimal(in_dir="txt", out_dir="txt_clean"):
    """
    Nettoyage minimal des fichiers texte :
      - garde la ponctuation et la casse
      - supprime les phrases contenant des liens (http/https)
      - supprime les phrases commençant par "Note:" ou "note:"
      - supprime les entêtes inutiles
      - remplace les retours à la ligne multiples par des espaces
      - enregistre dans un dossier txt_clean/ avec la même arborescence
    """

    for root, _, files in os.walk(in_dir):
        for fn in files:
            if not fn.endswith(".txt"):
                continue

            in_path = os.path.join(root, fn)
            rel_path = os.path.relpath(in_path, in_dir)  # ex: 2018/06/2018-06-ny.txt
            out_path = os.path.join(out_dir, rel_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            # lecture
            with open(in_path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()

            # --- Nettoyage léger ---
            txt = unicodedata.normalize("NFC", txt).replace("\u00A0", " ")
            txt = txt.replace("‹ Back to Archive Search", "")
            txt = re.sub(
                r"For more information about District economic conditions,? visit: URL",
                "",
                txt,
            )

            # --- Supprimer les phrases contenant un lien OU commençant par "Note:" ---
            sentences = re.split(r'(?<=[.!?])\s+', txt)
            cleaned_sentences = []
            for s in sentences:
                s_stripped = s.strip()
                if (
                    "http://" in s_stripped
                    or "https://" in s_stripped
                    or s_stripped.lower().startswith("note:")
                ):
                    continue  # on saute cette phrase
                cleaned_sentences.append(s_stripped)
            txt = " ".join(cleaned_sentences)

            # --- Normalisation espaces et lignes ---
            txt = txt.replace("\r\n", "\n").replace("\r", "\n")
            txt = re.sub(r"\s+", " ", txt).strip()

            # écriture
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(txt)

            print(f"✓ cleaned → {out_path}")

if __name__ == "__main__":
    clean_minimal()
