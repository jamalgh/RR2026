import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# ==========================================
# 1. SETUP DIRECTORIES & CREATE DATASET
# ==========================================
Path('data').mkdir(exist_ok=True)
Path('images').mkdir(exist_ok=True)
Path('reports').mkdir(exist_ok=True)

# Viewership data sourced from Wikipedia (List of Suits episodes)
df = pd.DataFrame({
    'season': range(1, 10),
    'episodes': [12, 16, 16, 16, 16, 16, 16, 16, 10],
    'first_aired': ['2011-06-23', '2012-06-14', '2013-07-16', '2014-06-11',
                    '2015-06-24', '2016-07-13', '2017-07-12', '2018-07-18', '2019-07-17'],
    'last_aired': ['2011-09-08', '2013-02-21', '2014-04-10', '2015-03-04',
                   '2016-03-02', '2017-03-01', '2018-04-25', '2019-02-27', '2019-09-25'],
    'avg_viewers_millions': [4.16, 3.60, 2.73, 2.26, 2.01, 1.60, 1.30, 1.02, 0.99]
})
df.to_csv('data/viewership.csv', index=False)

# ==========================================
# 2. CALCULATE STATISTICS
# ==========================================
df['change_abs'] = df['avg_viewers_millions'].diff()
df['change_pct'] = df['avg_viewers_millions'].pct_change() * 100

s1 = df.loc[0, 'avg_viewers_millions']
s9 = df.loc[8, 'avg_viewers_millions']
total_drop = s1 - s9
pct_drop = (total_drop / s1) * 100
peak_s = df.loc[df['avg_viewers_millions'].idxmax()]
low_s = df.loc[df['avg_viewers_millions'].idxmin()]
max_drop_idx = df['change_abs'].idxmin()
max_drop_val = df.loc[max_drop_idx, 'change_abs']
max_drop_from = int(df.loc[max_drop_idx, 'season'] - 1)
max_drop_to = int(df.loc[max_drop_idx, 'season'])

# ==========================================
# 3. GENERATE VISUALIZATIONS
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Graph 1: Viewership Over Time
plt.figure(figsize=(10, 6))
plt.plot(df['season'], df['avg_viewers_millions'], marker='o', linewidth=2.5, 
         color='#2E86AB', markersize=8)
for _, row in df.iterrows():
    plt.annotate(f"{row['avg_viewers_millions']:.2f}M", 
                 (row['season'], row['avg_viewers_millions']), 
                 textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
plt.title('Suits: Average Viewership by Season (2011-2019)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Season'); plt.ylabel('Average Viewers (millions)')
plt.xticks(range(1, 10)); plt.ylim(0, 5); plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('images/viewership_over_time.png', dpi=300)
plt.close()

# Graph 2: Absolute Season-to-Season Changes
plt.figure(figsize=(10, 6))
colors = ['#E94F37' if x < 0 else '#44AF69' for x in df['change_abs']]
plt.bar(df['season'], df['change_abs'], color=colors, alpha=0.7, edgecolor='black')
plt.axhline(0, color='black', linewidth=1.5)
for i, row in df.iterrows():
    if pd.notna(row['change_abs']):
        plt.text(row['season'], row['change_abs'] + (0.05 if row['change_abs'] > 0 else -0.15),
                 f'{row["change_abs"]:+.2f}', ha='center', 
                 va='bottom' if row['change_abs'] > 0 else 'top', fontsize=9, fontweight='bold')
plt.title('Suits: Season-to-Season Viewership Change', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Season'); plt.ylabel('Change in Viewers (millions)')
plt.xticks(range(1, 10)); plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('images/viewership_changes.png', dpi=300)
plt.close()

# Graph 3: Percentage Season-to-Season Changes
plt.figure(figsize=(10, 6))
colors = ['#E94F37' if x < 0 else '#44AF69' for x in df['change_pct']]
plt.bar(df['season'], df['change_pct'], color=colors, alpha=0.7, edgecolor='black')
plt.axhline(0, color='black', linewidth=1.5)
for i, row in df.iterrows():
    if pd.notna(row['change_pct']):
        plt.text(row['season'], row['change_pct'] + (2 if row['change_pct'] > 0 else -8),
                 f'{row["change_pct"]:+.1f}%', ha='center', 
                 va='bottom' if row['change_pct'] > 0 else 'top', fontsize=9, fontweight='bold')
plt.title('Suits: Season-to-Season Percentage Change', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Season'); plt.ylabel('Percentage Change (%)')
plt.xticks(range(1, 10)); plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('images/percentage_changes.png', dpi=300)
plt.close()

print("✅ Data saved to data/viewership.csv")
print("✅ Graphs saved to images/")

# ==========================================
# 4. GENERATE COMPREHENSIVE REPORT
# ==========================================
report = f"""# Comprehensive Analysis of *Suits* (2011-2019)

## Show Description

*Suits* is an American legal drama television series created by Aaron Korsh that premiered on USA Network on June 23, 2011. The show ran for nine seasons with {df['episodes'].sum()} total episodes, concluding on September 25, 2019.

Set in a New York City corporate law firm, the series follows Mike Ross (Patrick J. Adams), a college dropout with a photographic memory, as he works as an associate for the successful attorney Harvey Specter (Gabriel Macht). The show also stars Meghan Markle as Rachel Zane, Gina Torres as Jessica Pearson, Rick Hoffman as Louis Litt, and Sarah Rafferty as Donna Paulsen.

Despite ending in 2019, *Suits* experienced an unprecedented surge in popularity after being added to Netflix and Peacock in 2023, becoming the most-streamed show of the year with 57.7 billion minutes watched.

![Suits Logo](images/suits_logo.jpg)
*Note: Save a logo/screenshot as `images/suits_logo.jpg` to replace this placeholder.*

## Viewership Statistics Summary

| Metric | Value |
|--------|-------|
| **Total Seasons** | 9 |
| **Total Episodes** | {df['episodes'].sum()} |
| **Original Network** | USA Network |
| **Season 1 Average** | {s1:.2f} million viewers |
| **Season 9 Average** | {s9:.2f} million viewers |
| **Peak Season** | Season {int(peak_s['season'])} ({peak_s['avg_viewers_millions']:.2f}M) |
| **Lowest Season** | Season {int(low_s['season'])} ({low_s['avg_viewers_millions']:.2f}M) |
| **Overall Change** | -{total_drop:.2f}M viewers ({pct_drop:.1f}% decline) |
| **Series Run** | {df['first_aired'].iloc[0]} – {df['last_aired'].iloc[-1]} |

## Viewership Trends

### Overall Viewership Over Time
![Viewership Over Time](images/viewership_over_time.png)

The viewership data reveals a clear declining trend throughout the show's nine-season run. Starting with a strong **{s1:.2f} million viewers** in Season 1, the show experienced its most significant drop between Seasons {max_drop_from} and {max_drop_to}, losing **{abs(max_drop_val):.2f} million viewers** (a **{abs(df.loc[max_drop_idx, 'change_pct']):.1f}% decrease**).

### Season-to-Season Changes
![Season-to-Season Changes](images/viewership_changes.png)
![Percentage Changes](images/percentage_changes.png)

## Detailed Analysis of Changes

The viewership trajectory of *Suits* demonstrates several distinct phases:

### Phase 1: Initial Success (Seasons 1-2)
The show launched strongly with **{s1:.2f} million viewers** in Season 1. While Season 2 saw a decline to **{df.loc[1, 'avg_viewers_millions']:.2f} million viewers** (a decrease of **{abs(df.loc[1, 'change_abs']):.2f} million** or **{abs(df.loc[1, 'change_pct']):.1f}%**), the show maintained a solid audience base.

### Phase 2: Sharp Decline (Seasons 2-4)
The most dramatic drop occurred between Season 2 and Season 3, where viewership fell by **{abs(df.loc[2, 'change_abs']):.2f} million viewers** (**{abs(df.loc[2, 'change_pct']):.1f}% decrease**), dropping from {df.loc[1, 'avg_viewers_millions']:.2f}M to {df.loc[2, 'avg_viewers_millions']:.2f}M. This trend continued into Season 4, which averaged **{df.loc[3, 'avg_viewers_millions']:.2f} million viewers**, representing a further decline of **{abs(df.loc[3, 'change_abs']):.2f} million** (**{abs(df.loc[3, 'change_pct']):.1f}%**) from Season 3.

### Phase 3: Gradual Erosion (Seasons 4-7)
From Season 4 to Season 7, the show experienced steady but slower declines:
- Season 4 to 5: **-{abs(df.loc[4, 'change_abs']):.2f}M** ({df.loc[4, 'change_pct']:.1f}%)
- Season 5 to 6: **-{abs(df.loc[5, 'change_abs']):.2f}M** ({df.loc[5, 'change_pct']:.1f}%)
- Season 6 to 7: **-{abs(df.loc[6, 'change_abs']):.2f}M** ({df.loc[6, 'change_pct']:.1f}%)

By Season 7, viewership had fallen to **{df.loc[6, 'avg_viewers_millions']:.2f} million viewers**, representing a **{(s1 - df.loc[6, 'avg_viewers_millions'])/s1*100:.1f}% decrease** from the show's peak in Season 1.

### Phase 4: Final Seasons (Seasons 7-9)
The final three seasons showed continued decline but at a slower rate:
- Season 7 to 8: **-{abs(df.loc[7, 'change_abs']):.2f}M** ({df.loc[7, 'change_pct']:.1f}%), falling to {df.loc[7, 'avg_viewers_millions']:.2f}M viewers
- Season 8 to 9: **-{abs(df.loc[8, 'change_abs']):.2f}M** ({df.loc[8, 'change_pct']:.1f}%), ending at {df.loc[8, 'avg_viewers_millions']:.2f}M viewers

Notably, Season 9 consisted of only 10 episodes compared to the typical 16, which may have affected the average.

## Statistical Summary

- **Total viewership loss**: {total_drop:.2f} million viewers from Season 1 to Season 9
- **Percentage decline**: {pct_drop:.1f}% over nine seasons
- **Average seasonal decline**: {total_drop/(len(df)-1):.2f} million viewers per season
- **Largest single-season drop**: {abs(max_drop_val):.2f}M viewers (Season {max_drop_from}→{max_drop_to})
- **Smallest decline**: {abs(df.loc[8, 'change_abs']):.2f}M viewers (Season 8→9)

### Notable Patterns
1. The show **never experienced a season-to-season increase** in viewership
2. The steepest declines occurred in the middle seasons (3-6)
3. Despite declining linear viewership, the show built enough of a catalog to achieve massive streaming success years after its conclusion

## Conclusion

While *Suits* experienced a steady decline in traditional TV viewership throughout its run, losing **{pct_drop:.1f}% of its audience** from Season 1 ({s1:.2f}M) to Season 9 ({s9:.2f}M), the show found remarkable second life in streaming. The 2023 streaming explosion, where it became Netflix's most-watched acquired series, demonstrates that quality content can find new audiences long after its original broadcast ended.

The viewership decline pattern is typical for long-running cable dramas, but *Suits* maintained sufficient quality and fan engagement to remain viable for nine seasons and achieve unprecedented streaming success post-cancellation.

## References
1. Wikipedia. "Suits (American TV series)." https://en.wikipedia.org/wiki/Suits_(American_TV_series)
2. Wikipedia. "List of Suits episodes." https://en.wikipedia.org/wiki/List_of_Suits_episodes
3. Nielsen Media Research. Viewership data via Wikipedia.
4. The Hollywood Reporter. "'Suits' Sets Another Streaming Record for 2023." January 29, 2024.

---
*Report generated automatically by Python analysis script.*
"""

with open('reports/final_analysis.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("✅ Report saved to reports/final_analysis.md")
print("\n📊 Analysis complete! Open reports/final_analysis.md to view your formatted report.")