#%%

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Evaluate the following ratings for success:
ratings = ['Profit factor', 'CAGR/Max DD %']
#ratings = ['Profit factor', 'Net profit', 'Ret/DD Ratio', 'Avg. Trade', 'Stability', 'Stagnation', 'CAGR/Max DD %', 'CAGR/Max DD % (MC retest, Conf. level 95%)']

oos_file = './OOS_Databank.csv'
oos_df = pd.read_csv(oos_file, sep=";")

def get_success_rate(percentile_df, rating, value):
    closest_value = percentile_df.iloc[(percentile_df[rating] - value).abs().argsort()[:1]]
    percentile = closest_value.values[0][1] * 100
    return round(100 - percentile,1)

# %%
#plt.figure(figsize=(15, 10))
#percentiles = [0.05, 0.25, 0.50, 0.75, 0.95]
#labels = ['5th Percentile', '25th Percentile', '50th Percentile', '75th Percentile', '95th Percentile']

print('Success ratings:')
for i, rating in enumerate(ratings):
    #print('Calculating percentiles for', rating)
    oos_df['percentile'] = oos_df[rating].rank(pct=True)
    percentile_df = oos_df[[rating, 'percentile']].sort_values(rating)

    """ plt.subplot(3, 3, i+1)
    sns.lineplot(data=percentile_df, x=rating, y='percentile', color='blue')
    plt.title(rating)
    plt.xlabel('')
    plt.ylabel('') """

    """ for percentile, label in zip(percentiles, labels):
        closest_percentile = percentile_df.iloc[(percentile_df['percentile'] - percentile).abs().argsort()[:1]]
        percentile_value = closest_percentile[rating].values[0]
        plt.axhline(y=percentile, color='red', linestyle='--', label=label)
        plt.text(percentile_value, percentile, f'{percentile_value:.2f}', color='black', ha='right')
     """
    if rating == 'CAGR/Max DD %':
        key_values = ['1  ', '1.2', '1.5']
        print(f'  {rating}:')
        for key_value in key_values:
            print(f'    >= {key_value}: {get_success_rate(percentile_df, rating, float(key_value))}%')
    if rating == 'Profit factor':
        key_values = ['1  ', '1.2', '1.5']
        print(f'  {rating}:')
        for key_value in key_values:
            print(f'    >= {key_value}: {get_success_rate(percentile_df, rating, float(key_value))}%')
    
#plt.legend()
#plt.tight_layout()
#plt.show()
# %%
