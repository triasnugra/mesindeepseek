import yaml
import os
from datetime import datetime, timezone, timedelta
from src.data_fetcher import DataFetcher
from src.signal_generator import SignalGenerator

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def generate_html_report(results):
    # Waktu awal (akan diupdate oleh JavaScript di browser)
    utc_now = datetime.now(timezone.utc)
    wib_now = utc_now.astimezone(timezone(timedelta(hours=7)))
    
    time_str_utc = utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")
    time_str_wib = wib_now.strftime("%Y-%m-%d %H:%M:%S WIB")
    
    # Hitung Sinyal
    total_signals = sum(1 for res in results if res.get('status') == "SIGNAL FOUND")
    total_wait = sum(1 for res in results if res.get('status') == "WAIT")
    total_no_trade = sum(1 for res in results if res.get('status') == "NO TRADE")
    total_error = sum(1 for res in results if res.get('status') == "ERROR")

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Eliz-Style Crypto Analyzer</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>body {{ background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }}</style>
        <script>
            // JavaScript untuk Jam Real-time
            function updateClock() {{
                const now = new Date();
                const utcString = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
                
                // WIB adalah UTC+7
                const wibDate = new Date(now.getTime() + (7 * 60 * 60 * 1000));
                const wibString = wibDate.toISOString().replace('T', ' ').substring(0, 19) + ' WIB';
                
                document.getElementById('live-clock').innerHTML = `Generated: <span class="text-gray-200">${{utcString}}</span> | <span class="text-yellow-300">${{wibString}}</span>`;
            }}
            setInterval(updateClock, 1000);
            window.onload = updateClock;
        </script>
    </head>
    <body class="p-6">
        <div class="max-w-6xl mx-auto">
            
            <!-- HEADER -->
            <div class="mb-8 border-b border-gray-700 pb-4">
                <h1 class="text-4xl font-bold text-blue-400 mb-2">Eliz-Style Crypto Engine</h1>
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center text-sm text-gray-400">
                    <p id="live-clock">Generated: <span class="text-gray-200">{time_str_utc}</span> | <span class="text-yellow-300">{time_str_wib}</span></p>
                    <p class="mt-2 md:mt-0">Rules: Monday Range • Sweep • Deviation • Reclaim</p>
                </div>
            </div>

            <!-- DASHBOARD RINGKASAN -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div class="bg-gray-800 p-4 rounded-lg border border-green-500/30 text-center">
                    <p class="text-3xl font-bold text-green-400">{total_signals}</p>
                    <p class="text-xs text-gray-400 uppercase tracking-wide">Signals Found</p>
                </div>
                <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30 text-center">
                    <p class="text-3xl font-bold text-yellow-400">{total_wait}</p>
                    <p class="text-xs text-gray-400 uppercase tracking-wide">Waiting</p>
                </div>
                <div class="bg-gray-800 p-4 rounded-lg border border-red-500/30 text-center">
                    <p class="text-3xl font-bold text-red-400">{total_no_trade}</p>
                    <p class="text-xs text-gray-400 uppercase tracking-wide">No Trade Zone</p>
                </div>
                <div class="bg-gray-800 p-4 rounded-lg border border-gray-600 text-center">
                    <p class="text-3xl font-bold text-gray-400">{total_error}</p>
                    <p class="text-xs text-gray-400 uppercase tracking-wide">Data Errors</p>
                </div>
            </div>

            <!-- GRID KOIN -->
            <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
    """
    
    if not results:
        html += "<p class='text-red-400 col-span-full'>Tidak ada data yang berhasil diproses.</p>"
    else:
        priority = {"SIGNAL FOUND": 1, "WAIT": 2, "NO TRADE": 3, "ERROR": 4}
        results = sorted(results, key=lambda x: priority.get(x.get('status', 'ERROR'), 5))

        for res in results:
            status = res.get('status', 'UNKNOWN')
            symbol = res.get('symbol', 'N/A').replace('/USDT', '')
            reason = res.get('reason', 'No reason provided')
            current_price = res.get('current_price', 0)
            
            if status == "SIGNAL FOUND": 
                badge = "bg-green-500 text-white shadow-[0_0_10px_rgba(34,197,94,0.5)]"
                border = "border-green-500/50"
            elif status == "NO TRADE": 
                badge = "bg-red-500 text-white"
                border = "border-gray-700"
            elif status == "WAIT": 
                badge = "bg-yellow-500 text-black"
                border = "border-gray-700"
            else: 
                badge = "bg-gray-500 text-white"
                border = "border-gray-700"
            
            html += f"""
            <div class="bg-gray-800 rounded-xl shadow-lg p-5 border {border} flex flex-col justify-between">
                <div>
                    <div class="flex justify-between items-center mb-1">
                        <h2 class="text-xl font-bold text-gray-100">{symbol}</h2>
                        <span class="{badge} px-2 py-1 rounded text-[10px] font-bold tracking-wider">{status}</span>
                    </div>
                    <!-- CURRENT PRICE DITAMBAHKAN DI SINI -->
                    <p class="text-sm font-semibold text-blue-300 mb-2">Price: ${current_price:.4f}</p>
                    <p class="text-xs text-gray-400 mb-4 h-8 leading-tight">{reason}</p>
                </div>
            """
            
            monday = res.get('monday_range', {})
            boxes = res.get('boxes', {})
            if monday.get('high') and boxes.get('support'):
                html += f"""
                <div class="grid grid-cols-2 gap-x-2 gap-y-1 text-[11px] mb-3 bg-gray-900 p-2 rounded-lg">
                    <div class="text-gray-500">MR High:</div>
                    <div class="text-right text-gray-200">{monday['high']:.4f}</div>
                    <div class="text-gray-500">MR Low:</div>
                    <div class="text-right text-gray-200">{monday['low']:.4f}</div>
                    <div class="text-red-400/80 mt-1">Box Res:</div>
                    <div class="text-right text-red-300 mt-1">{boxes['resistance']:.4f}</div>
                    <div class="text-green-400/80">Box Sup:</div>
                    <div class="text-right text-green-300">{boxes['support']:.4f}</div>
                </div>
                """
                
            if status == "SIGNAL FOUND":
                for sig in res.get('signals', []):
                    color = "border-green-500 bg-green-900/20 text-green-100" if sig.get('type') == "LONG" else "border-red-500 bg-red-900/20 text-red-100"
                    html += f"""
                    <div class="border-l-4 {color} p-3 rounded-r-lg mt-2 text-sm">
                        <p class="font-bold mb-2">{sig.get('type')} - {sig.get('setup')}</p>
                        
                        <!-- ENTRY, SL, TP DITAMPILKAN LEBIH JELAS -->
                        <div class="grid grid-cols-3 gap-1 text-[11px] bg-black/20 p-2 rounded">
                            <div class="text-center">
                                <span class="block text-gray-400">Entry</span>
                                <strong>{sig.get('entry_price', 0):.4f}</strong>
                            </div>
                            <div class="text-center border-l border-white/10">
                                <span class="block text-red-400">Stop Loss</span>
                                <strong>{sig.get('invalidation', 0):.4f}</strong>
                            </div>
                            <div class="text-center border-l border-white/10">
                                <span class="block text-green-400">Target (1:2)</span>
                                <strong>{sig.get('take_profit', 0):.4f}</strong>
                            </div>
                        </div>
                    </div>
                    """
            html += "</div>"
            
    html += """
            </div>
            <div class="mt-12 text-center text-xs text-gray-500 border-t border-gray-700 pt-6">
                <p>Disclaimer: Bukan financial advice. Gunakan Risk Management 1-2% per trade.</p>
                <p class="mt-1 text-gray-400">"Strategy gets you in. Discipline makes you money. Risk management keeps you in the market." — @eliz883</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Report generated. Found {total_signals} signals.")

def main():
    config = load_config()
    fetcher = DataFetcher(config['exchange'])
    all_results = []
    
    print(f"Total coins to analyze: {len(config['symbols'])}")
    
    for i, symbol in enumerate(config['symbols']):
        print(f"[{i+1}/{len(config['symbols'])}] Analyzing {symbol}...", end=" ")
        try:
            df_htf = fetcher.fetch_ohlcv(symbol, config['timeframes']['htf'], limit=200)
            df_ltf = fetcher.fetch_ohlcv(symbol, config['timeframes']['ltf'], limit=200)
            
            if df_htf is None or df_ltf is None:
                raise ValueError("Gagal fetch data API")
                
            analyzer = SignalGenerator(df_htf, df_ltf)
            result = analyzer.analyze()
            result['symbol'] = symbol
            all_results.append(result)
            print(f"-> {result['status']}")
            
        except Exception as e:
            print(f"-> ERROR: {e}")
            all_results.append({
                "symbol": symbol,
                "status": "ERROR",
                "reason": f"System Error: {str(e)}",
                "current_price": 0,
                "monday_range": {"high": None, "low": None},
                "boxes": {"support": None, "resistance": None},
                "signals": []
            })
            
    generate_html_report(all_results)

if __name__ == "__main__":
    main()
