with open('sphinx_compliance_metrics.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Truncate at line 761 (before "if __name__")
with open('sphinx_compliance_metrics.py', 'w', encoding='utf-8') as f:
    f.writelines(lines[:761])
    f.write('\n        return aggregate\n')

print("File fixed!")
