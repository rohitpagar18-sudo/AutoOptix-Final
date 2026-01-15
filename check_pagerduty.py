import pandas as pd

df = pd.read_excel('Old Lookup File/lookup.xlsx')

# Check for PagerDuty
pagerduty = df[df['Subgroup'].str.contains('pager', case=False, na=False)]
print("PagerDuty matches:")
print(pagerduty[['Subgroup', 'UseCase']])

print("\n---")

# Check for On-Call or related
oncall = df[df['Subgroup'].str.contains('on-call|oncall|escalation|alert', case=False, na=False)]
print("\nAlert/Escalation/On-Call keywords:")
print(oncall[['Subgroup', 'UseCase']].head(10))
