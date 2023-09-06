from pathlib import Path
import camelot

load_src = Path("data/raw_dept_responses/")
F_PDF = list(load_src.glob("*.pdf"))

save_dest = Path("data/department_PDF2table")
save_dest.mkdir(exist_ok=True, parents=True)

for f in F_PDF:
    print(f)
    tables = camelot.read_pdf(str(f), pages="1-end")

    for k, table in enumerate(tables):
        print(table.parsing_report)
        f_save = save_dest / f"{f.stem}_{k:04d}.csv"

        table.df.to_csv(f_save, index=False)
