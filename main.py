from scraper.vcb import get_vcb_rates
from scraper.agribank import get_agribank_rates
from scraper.doji_gold import get_doji_gold_rates, get_gold_charts
from colorama import Fore, Style, init
import argparse
import sys

# Initialize colorama for Windows compatibility
init()

def display_currency_rates():
    """Display currency exchange rates"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"           CURRENCY EXCHANGE RATES")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    all_rates = get_vcb_rates() + get_agribank_rates()
    
    if not all_rates:
        print(f"{Fore.RED}No currency rates available{Style.RESET_ALL}")
        return
    
    currencies = ['USD', 'EUR', 'JPY', 'CNY']
    for currency in currencies:
        print(f"\n{Fore.YELLOW}Currency: {currency}{Style.RESET_ALL}")
        print("| Bank       | Buy       | Sell      |")
        print("|------------|-----------|-----------|")
        
        bank_rates = [r for r in all_rates if r['currency'] == currency]
        
        if not bank_rates:
            print(f"| {Fore.RED}No data available for {currency}{Style.RESET_ALL}")
            continue
            
        max_buy = max(bank_rates, key=lambda x: x['buy'])['buy']
        min_sell = min(bank_rates, key=lambda x: x['sell'])['sell']

        for rate in bank_rates:
            buy = f"{rate['buy']:,.2f}"
            sell = f"{rate['sell']:,.2f}"
            bank_name = rate['bank']
            
            if rate['buy'] == max_buy:
                buy = Fore.GREEN + buy + Style.RESET_ALL + " ⭐"
            if rate['sell'] == min_sell:
                sell = Fore.RED + sell + Style.RESET_ALL + " ⭐"
            print(f"| {bank_name:10} | {buy:>9} | {sell:>9} |")

def display_gold_rates():
    """Display gold prices"""
    print(f"{Fore.CYAN}{'='*80}")
    print(f"                    GOLD PRICES")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    gold_rates = get_doji_gold_rates()
    
    if not gold_rates:
        print(f"{Fore.RED}No gold rates available{Style.RESET_ALL}")
        return
    
    # Group by category
    categories = {}
    for rate in gold_rates:
        category = rate['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(rate)
    
    # Display domestic gold prices
    if 'domestic' in categories:
        print(f"\n{Fore.YELLOW}🏠 DOMESTIC GOLD PRICES{Style.RESET_ALL}")
        print("| Name                     | Buy        | Sell       | Unit      |")
        print("|--------------------------|------------|------------|-----------|")
        
        for rate in categories['domestic']:
            name = rate['name'][:24]  # Truncate long names
            buy = f"{rate['buy']:,.0f}" if rate['buy'] > 0 else "-"
            sell = f"{rate['sell']:,.0f}" if rate['sell'] > 0 else "-"
            unit = rate['unit']
            print(f"| {name:24} | {buy:>10} | {sell:>10} | {unit:9} |")
    
    # Display international gold prices
    if 'international' in categories:
        print(f"\n{Fore.YELLOW}🌍 INTERNATIONAL GOLD PRICES{Style.RESET_ALL}")
        print("| Name                     | Buy        | Sell       | Unit      |")
        print("|--------------------------|------------|------------|-----------|")
        
        for rate in categories['international']:
            name = rate['name'][:24]
            buy = f"{rate['buy']:,.0f}" if rate['buy'] > 0 else "-"
            sell = f"{rate['sell']:,.0f}" if rate['sell'] > 0 else "-"
            unit = rate['unit']
            print(f"| {name:24} | {buy:>10} | {sell:>10} | {unit:9} |")
    
    # Display jewelry prices
    if 'gold_jewelry' in categories:
        print(f"\n{Fore.YELLOW}💍 JEWELRY PRICES{Style.RESET_ALL}")
        print("| Name                     | Buy        | Sell       | Unit      |")
        print("|--------------------------|------------|------------|-----------|")
        
        jewelry_rates = sorted(categories['gold_jewelry'], key=lambda x: x['sell'] if x['sell'] > 0 else x['buy'], reverse=True)
        
        for rate in jewelry_rates:
            name = rate['name'][:24]
            buy = f"{rate['buy']:,.0f}" if rate['buy'] > 0 else "-"
            sell = f"{rate['sell']:,.0f}" if rate['sell'] > 0 else "-"
            unit = rate['unit']
            
            # Highlight pure gold (24k, 9999)
            if '24k' in name.lower() or '9999' in name.lower():
                name = Fore.YELLOW + name + Style.RESET_ALL
            
            print(f"| {name:24} | {buy:>10} | {sell:>10} | {unit:9} |")

def display_gold_charts():
    """Display available gold charts"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"           GOLD PRICE CHARTS")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    charts = get_gold_charts()
    
    if not charts:
        print(f"{Fore.RED}No gold charts available{Style.RESET_ALL}")
        return
    
    for chart in charts:
        print(f"\n{Fore.YELLOW}📊 {chart['name']}{Style.RESET_ALL}")
        print(f"   Type: {chart['type']}")
        print(f"   URL:  {chart['url']}")

def display_summary():
    """Display a summary of all data"""
    print(f"{Fore.MAGENTA}{'='*80}")
    print(f"                    MARKET SUMMARY")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    # Currency summary
    currency_rates = get_vcb_rates() + get_agribank_rates()
    print(f"\n{Fore.CYAN}💱 Currency Exchange Rates:{Style.RESET_ALL} {len(currency_rates)} rates available")
    
    if currency_rates:
        # Show USD as primary indicator
        usd_rates = [r for r in currency_rates if r['currency'] == 'USD']
        if usd_rates:
            avg_buy = sum(r['buy'] for r in usd_rates) / len(usd_rates)
            avg_sell = sum(r['sell'] for r in usd_rates) / len(usd_rates)
            print(f"   USD Average: Buy {avg_buy:,.0f} | Sell {avg_sell:,.0f}")
    
    # Gold summary
    gold_rates = get_doji_gold_rates()
    print(f"\n{Fore.YELLOW}🏆 Gold Prices:{Style.RESET_ALL} {len(gold_rates)} prices available")
    
    if gold_rates:
        # Find 24k gold price
        gold_24k = [r for r in gold_rates if '24k' in r['name'].lower()]
        if gold_24k:
            rate = gold_24k[0]
            print(f"   24k Gold: Buy {rate['buy']:,.0f} | Sell {rate['sell']:,.0f} ({rate['unit']})")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='FX Rate & Gold Price CLI')
    parser.add_argument('--currency', '-c', action='store_true', help='Show currency exchange rates')
    parser.add_argument('--gold', '-g', action='store_true', help='Show gold prices')
    parser.add_argument('--charts', action='store_true', help='Show gold chart URLs')
    parser.add_argument('--summary', '-s', action='store_true', help='Show market summary')
    parser.add_argument('--all', '-a', action='store_true', help='Show all data')
    
    args = parser.parse_args()
    
    try:
        if args.currency or args.all:
            display_currency_rates()
        
        if args.gold or args.all:
            display_gold_rates()
        
        if args.charts:
            display_gold_charts()
        
        if args.summary:
            display_summary()
        
        # If no arguments provided, show summary
        if not any(vars(args).values()):
            display_summary()
            print(f"\n{Fore.CYAN}Use --help for more options{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
