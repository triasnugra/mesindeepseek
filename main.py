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
        <style>body { background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }</style>
    </head>
    <body class="p-6">
        <div class="max-w-5xl mx-auto">
            <h1 class="text-3xl font-bold text-blue-400 mb-2">Eliz-Style Crypto Engine</h1>
            <p class="text-gray-400 mb-8">Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") + """ | Rules: Monday Range, Sweep, Deviation, Reclaim.</p>
            <div class="grid gap-6 md:grid-cols-2">
    """
    
    if not results:
        html += "<p class='text-red-400'>Tidak ada data yang berhasil diproses.</p>"
    else:
        for res in results:
            status = res.get('status', 'UNKNOWN')
            symbol = res.get('symbol', 'N/A')
            reason = res.get('reason', 'No reason provided')
            
            # Pewarnaan Status
            if status == "SIGNAL FOUND": badge = "bg-green-500 text-white"
            elif status == "NO TRADE": badge = "bg-red-500 text-white"
            elif status == "WAIT": badge = "bg-yellow-500 text-black"
            else: badge = "bg-gray-500 text-white"
            
            html += f"""
            <div class="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-2xl font-bold">{symbol}</h2>
                    <span class="{badge} px-3 py-1 rounded-full text-xs font-bold">{status}</span>
                </div>
                <p class="text-sm text-gray-300 mb-4">{reason}</p>
            """
            
            # Tampilkan Levels
            monday = res.get('monday_range', {})
            boxes = res.get('boxes', {})
            if monday.get('high') and boxes.get('support'):
                html += f"""
                <div class="grid grid-cols-2 gap-2 text-xs mb-4 bg-gray-900 p-3 rounded-lg">
                    <div><span class="text-gray-500">Mon High:</span> {monday['high']:.4f}</div>
                    <div><span class="text-gray-500">Mon Low:</span> {monday['low']:.4f}</div>
                    <div><span class="text-red-400">Box Res:</span> {boxes['resistance']:.4f}</div>
                    <div><span class="text-green-400">Box Sup:</span> {boxes['support']:.4f}</div>
                </div>
                """
                
            # Tampilkan Sinyal
            if status == "SIGNAL FOUND":
                for sig in res.get('signals', []):
                    color = "border-green-500 bg-green-900/30" if sig.get('type') == "LONG" else "border-red-500 bg-red-900/30"
                    html += f"""
                    <div class="border-l-4 {color} p-4 mb-2 rounded-r-lg">
                        <p class="font-bold text-lg">{sig.get('type')} - {sig.get('setup')}</p>
                        <div class="flex justify-between text-sm mt-2">
                            <span>Entry: <strong>{sig.get('entry_price', 0):.4f}</strong></span>
                            <span class="text-gray-400">SL: {sig.get('invalidation', 0):.4f}</span>
                        </div>
                        <p class="text-xs text-gray-400 mt-2 italic">{sig.get('reason', '')}</p>
                    </div>
                    """
            html += "</div>"
            
    html += """
            </div>
            <div class="mt-12 text-center text-xs text-gray-500 border-t border-gray-700 pt-4">
                <p>Disclaimer: Bukan financial advice. Gunakan Risk Management 1-2%.</p>
                <p class="mt-1">"Strategy gets you in. Discipline makes you money."</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML Report generated at docs/index.html")

def main():
    config = load_config()
    fetcher = DataFetcher(config['exchange'])
    all_results = []
    
    for symbol in config['symbols']:
        print(f"--- Analyzing {symbol} ---")
        try:
            df_htf = fetcher.fetch_ohlcv(symbol, config['timeframes']['htf'], limit=200)
            df_ltf = fetcher.fetch_ohlcv(symbol, config['timeframes']['ltf'], limit=200)
            
            if df_htf is None or df_ltf is None:
                raise ValueError("Gagal mengambil data dari Exchange (API Limit/Error)")
                
            analyzer = SignalGenerator(df_htf, df_ltf)
            result = analyzer.analyze()
            result['symbol'] = symbol
            all_results.append(result)
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            # Jika ETH error, tetap dimasukkan ke report dengan status ERROR
            all_results.append({
                "symbol": symbol,
                "status": "ERROR",
                "reason": f"System Error: {str(e)}",
                "monday_range": {"high": None, "low": None},
                "boxes": {"support": None, "resistance": None},
                "signals": []
            })
            
    generate_html_report(all_results)

if __name__ == "__main__":
    main()
