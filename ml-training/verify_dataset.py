import csv

f = open('ml-training/dataset/requirements_dataset_final.csv', 'r', encoding='utf-8')
reader = csv.reader(f)
header = next(reader)
rows = list(reader)
f.close()

print("=== FINAL DATASET INSPECTION ===")
print(f"Header: {header}")
print(f"Total: {len(rows)}")
print()

cats = ['Functionality','Security','Efficiency','Usability','Reliability','Maintainability','Portability']
for c in cats:
    cr = [r for r in rows if r[2]==c]
    print(f"  {c}: {len(cr)}")

print()
print("--- Sample rows (first 2 per category) ---")
for c in cats:
    cr = [r for r in rows if r[2]==c]
    print(f"\n  [{c}]")
    for r in cr[:2]:
        print(f"    Sub: {r[3]} | {r[1][:90]}")

print()
lengths = [len(r[1]) for r in rows]
print(f"Min length: {min(lengths)}, Max: {max(lengths)}, Avg: {sum(lengths)//len(lengths)}")

bad = [r for r in rows if "'" in r[1]]
print(f"Rows with encoding artifacts: {len(bad)}")
