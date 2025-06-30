from scraper.vcb import get_vcb_rates
from scraper.bidv import get_bidv_rates
from scraper.agribank import get_agribank_rates
from scraper.vietinbank import get_vietinbank_rates
from colorama import Fore, Style

def aggregate_rates():
    all_rates = (
        get_vcb_rates() +
        get_bidv_rates() +
        get_agribank_rates() +
        get_vietinbank_rates()
    )

    currencies = ['USD', 'EUR', 'JPY', 'CNY']
    for currency in currencies:
        print(f"\nCurrency: {currency}")
        print("| Bank       | Buy       | Sell      |")
        print("|------------|-----------|-----------|")
        
        bank_rates = [r for r in all_rates if r['currency'] == currency]
        max_buy = max(bank_rates, key=lambda x: x['buy'])['buy']
        min_sell = min(bank_rates, key=lambda x: x['sell'])['sell']

        for rate in bank_rates:
            buy = f"{rate['buy']:.2f}"
            sell = f"{rate['sell']:.2f}"
            bank_name = rate['bank']
            if rate['buy'] == max_buy:
                buy = Fore.GREEN + buy + Style.RESET_ALL + " ⭐"
            if rate['sell'] == min_sell:
                sell = Fore.RED + sell + Style.RESET_ALL + " ⭐"
            print(f"| {bank_name:10} | {buy:9} | {sell:9} |")

if __name__ == "__main__":
    aggregate_rates()
