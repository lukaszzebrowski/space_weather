import matplotlib.pyplot as plt
import numpy as np

# Lata (2015–2025)
lata = np.array([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])

# Dane ZB (słupki niebieskie)
zb_wartosci = np.array([
    15.5, 18, 26, 33, 41, 64.2, 79, 97, 120, 147, 181
])

# Dane procentowe (słupki pomarańczowe)
procenty = np.array([
    24, 16.13, 44.44, 26.92, 24.24, 56.59, 23.05, 22.78, 23.71, 22.5, 23.13
])

# Oś X w postaci indeksów 0..10
x = np.arange(len(lata))
width = 0.4  # szerokość słupka

fig, ax1 = plt.subplots(figsize=(10, 6))

# Słupki ZB (oś Y1, niebieskie) - przesunięcie w lewo o width/2
zb_bars = ax1.bar(x - width/2, zb_wartosci, width=width,
                  color='#0072B2', alpha=0.8, label="Zettabajty (ZB)")

ax1.set_xlabel("Rok", fontsize=12)
ax1.set_ylabel("Zettabajty (ZB)", fontsize=12, color='#0072B2')
ax1.tick_params(axis='y', labelcolor='#0072B2')

# Ustawienie etykiet X jako konkretnych lat
ax1.set_xticks(x)
ax1.set_xticklabels(lata)
ax1.set_xlim(-0.5, len(lata)-0.5)

# Druga oś Y (ax2) dla procentów
ax2 = ax1.twinx()

# Słupki procentowe (pomarańczowe) - przesunięcie w prawo o width/2
pct_bars = ax2.bar(x + width/2, procenty, width=width,
                   color='orange', alpha=0.8, label="Wzrost (%)")

ax2.set_ylabel("Wzrost (%)", fontsize=12, color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

# Tytuł
fig.suptitle("Porównanie wielkości danych (ZB) i wzrostu (%) w latach 2015–2025", fontsize=14)

# Legendy
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()

# Zapis do pliku PNG
plt.savefig("wykres_zb_i_proc.png", dpi=300, bbox_inches='tight')

# Jeśli chcesz jednocześnie zobaczyć w oknie:
plt.show()
