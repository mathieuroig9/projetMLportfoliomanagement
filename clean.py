import os
import re
import cleantext
from tools import *  # gen, get_txt_file

def clean():
    for t in gen(skip=True):
        filename = get_txt_file(t)

        # --- Vérifie que le fichier existe ---
        if not os.path.exists(filename):
            # Optionnel : afficher un message léger pour debug
            # print(f"skip missing file {filename}")
            continue

        with open(filename, "r", encoding="utf-8") as f:
            old_txt = f.read()

        new_txt = cleantext.clean(old_txt)

        # Remplacements et nettoyage
        new_txt = re.sub(r"For more information about District economic conditions,? visit: URL", "", new_txt)
        new_txt = new_txt.replace("%-", " percent to ").replace("%", " percent")
        new_txt = new_txt.replace(" & ", " and ")
        new_txt = new_txt.replace("=", " equals ")
        new_txt = re.sub(r"[<>~*]", "", new_txt)
        new_txt = re.sub(r"\-\-+", " , ", new_txt)
        new_txt = re.sub(r"\?(?=[\w])", "? ", new_txt).replace(" ?", "?")
        new_txt = re.sub(r"\s+,", ",", new_txt).replace(",,", ",")
        new_txt = re.sub(r"\s+\.(?=[^0-9])", " ", new_txt)
        new_txt = new_txt.replace("...", " ")
        new_txt = new_txt.replace("..", ".").replace(",.", ",")
        new_txt = new_txt.replace("[", "").replace("]", "")
        new_txt = re.sub(r"\s+", " ", new_txt).strip()

        # --- Réécriture du fichier nettoyé ---
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_txt)

        print(f"cleaned {filename}")

if __name__ == "__main__":
    clean()