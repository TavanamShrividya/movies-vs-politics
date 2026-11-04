import pandas as pd
import matplotlib.pyplot as plt

war_data = pd.read_csv("correlation/correlation_results/war_movie_peak_after_each_war.csv")

fig, ax1 = plt.subplots(figsize=(10, 6))

line1, = ax1.plot(
    war_data["war_year"],
    war_data["years_until_peak"],
    color="blue",
    marker="o",
    label="Years to reach peak movie making"
)
ax1.set_xlabel("War Year")
ax1.set_ylabel("Year after which most war movies produced for that war", color="blue")

ax1.set_title("War movies reaction time over the years")
ax1.legend([line1], [line1.get_label()], loc="best")

plt.tight_layout()
plt.savefig("analysis/generated_charts/war_years_until_peak.png", dpi=300, bbox_inches="tight")
plt.show()