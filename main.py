import yaml
import os
from datetime import datetime
from src.data_fetcher import DataFetcher
from src.signal_generator import SignalGenerator

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def generate_html_report(results):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Eliz-Style Crypto Analyzer</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-gray-100 font-sans p-8">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold text-blue-400 mb-2">Eliz-Style Crypto Analysis Engine</h1>
            <p class="text-gray-400 mb-6">Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") + """</p>
            <div class="space-y-6">
    """
    
    if not results:
        html += """
        <div class="bg-red-900 border-l-4 border-red-500 p-6 mb-2 rounded shadow-lg">
            <p class="font-bold text-xl text-red-300">⚠️ Gagal Mengambil Data</p>
            <p class="text-sm mt-2 text-gray-200">Mesin tidak dapat mengambil data dari exchange. Periksa log GitHub Actions untuk detail error.</p>
            <p class="text-xs mt-2 text-gray-400">Kemungkinan penyebab: IP GitHub Actions diblokir, rate limit, atau simbol tidak tersedia.</p>
        </div>
        """
    else:
        for res in results:
            status = res.get('status', 'UNKNOWN')
            reason = res.get('reason', 'No detailed reason provided.')
            
            status_color = "text-green-400" if status == "SIGNAL FOUND" else ("text-red-400" if status == "NO TRADE" else "text-yellow-400")
            
            html += f"""
            <div class="bg-gray-800 rounded-lg p-6 shadow-lg border border-gray-700">
                <h2 class="text-2xl font-bold mb-4">{res.get('symbol', 'Unknown')}</h2>
                <p class="text-lg font-semibold mb-2">Status: <span class="{status_color}">{status}</span></p>
                <p class="text-gray-400 mb-4">{reason}</p>
            """
            
            # Tampilkan Monday Range jika ada
            monday = res.get('monday_range', {})
            if monday and monday.get('high') is not None:
                html += f"""
                <div class="grid grid-cols-2 gap-4 mb-4 text-sm bg-gray-900 p-4 rounded">
                    <div><span class="text-gray-500">Monday High:</span> <span class="text-white">{monday['high']:.4f}</span></div>
                    <div><span class="text-gray-500">Monday Low:</span> <span class="text-white">{monday['low']:.4f}</span></div>
                </div>
                """
            
            # Tampilkan Boxes jika ada
            boxes = res.get('boxes', {})
            if boxes and boxes.get('support') is not None:
                html += f"""
                <div class="grid grid-cols-2 gap-4 mb-4 text-sm bg-gray-900 p-4 rounded">
                    <div><span class="text-gray-500">Support (Box):</span> <span class="text-green-300">{boxes['support']:.4f}</span></div>
                    <div><span class="text-gray-500">Resistance (Box):</span> <span class="text-red-300">{boxes['resistance']:.4f}</span></div>
                </div>
                """
                
            # Tampilkan Signals jika ada
            if status == "SIGNAL FOUND":
                signals = res.get('signals', [])
                for sig in signals:
                    sig_color = "bg-green-900 border-green-500" if sig.get('type') == "LONG" else "bg-red-900 border-red-500"
                    html += f"""
                    <div class="{sig_color} border-l-4 p-4 mb-2 rounded">
                        <p class="font-bold">{sig.get('type', 'UNKNOWN')} - {sig.get('setup', '')}</p>
                        <p class="text-sm">Entry: {sig.get('entry_price', 0):.4f} | SL (Invalidation): {sig.get('invalidation', 0):.4f}</p>
                        <p class="text-xs text-gray-300 mt-1">{sig.get('reason', '')}</p>
                    </div>
                    """
            html += "</div>"
            
    html += """
            </div>
            <div class="mt-8 text-center text-sm text-gray-500">
                <p>Disclaimer: This is an automated analysis tool, not financial advice.</p>
                <p class="mt-2">"Strategy gets you in. Discipline makes you money." - @eliz883</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Report generated at docs/index.html")

def main():
    config = load_config()
    fetcher = DataFetcher(config['exchange'])
    all_results = []
    
    for symbol in config['symbols']:
        print(f"--- Analyzing {symbol} ---")
        
        df_htf = fetcher.fetch_ohlcv(symbol, config['timeframes']['htf'], limit=200)
        df_ltf = fetcher.fetch_ohlcv(symbol, config['timeframes']['ltf'], limit=200)
        
        if df_htf is None or df_ltf is None:
            print(f"Skipping {symbol} due to data fetch failure.")
            continue
            
        analyzer = SignalGenerator(df_htf, df_ltf)
        result = analyzer.analyze()
        result['symbol'] = symbol
        all_results.append(result)
        
    generate_html_report(all_results)

if __name__ == "__main__":
    main()
